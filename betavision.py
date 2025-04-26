#!/usr/bin/env python3

"""Live censoring (as a single file)"""

import time
from multiprocessing import shared_memory, Process
import hashlib
from pathlib import Path
import faulthandler
import argparse

import cv2
import mss
import numpy as np
import xxhash

import betaconfig
import betaconst
import betautils_model as bu_model
import betautils_vision as bu_vision
import betautils_censor as bu_censor


def get_shmem_array(name, shape, dtype, create=False, timeout=3, _hack_shmem_tracker=[]):
    """Get or create a sharedmemory-backed Numpy array

    Don't touch _hack_shmem_tracker. It's a hacky fix for
    https://stackoverflow.com/questions/63713241/segmentation-fault-using-python-shared-memory
    """
    if not create:
        # Wait a bit until memory is created, maybe
        location = Path("/dev/shm") / Path(name)
        for i in range(int(timeout * 10)):
            if location.exists():
                break
            time.sleep(0.1)
        # else:
        #     raise ValueError(f"Shared memory ${name} does not exist")
        # Ehh, just let SharedMemory fail if it's destined to fail.
    size = np.prod(shape) * np.dtype(dtype).itemsize
    shm = shared_memory.SharedMemory(name=name, create=create, size=size)
    _hack_shmem_tracker.append(shm)
    arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)

    is_faulthandler_enabled = faulthandler.is_enabled()
    if not is_faulthandler_enabled:
        faulthandler.enable()
    # Zero the array just in case.
    # If the program is going to crash with a Bus Error, it'll be here.
    # I can't find a way to guarantee that a shm allocation can actually
    # be as big as it says it is. /dev/shm is usually limited to 50% of
    # the tmpfs. If you are using Docker, `--shm-size=1GB` (or a similar
    # Docker Compose option) is your friend.
    # I'd love a cleaner solution to this.
    arr[:] = np.zeros(shape, dtype=dtype)
    if not is_faulthandler_enabled:
        # Don't keep the handler enabled if it wasn't before.
        faulthandler.disable()

    return arr


def get_shared_screenshots(create=False):
    shared_images = []
    for i, size in enumerate(betaconfig.picture_sizes):
        this_height, this_width = bu_vision.vision_adj_img_size(size)
        screenshot_shape = (this_height, this_width, 3)
        name = bu_vision.shm_name_for_screenshot(size)
        shared_images.append(get_shmem_array(name, screenshot_shape, np.float32, create=create))

    timestamp_shape = (1,)
    timestamps = []
    for name in (betaconst.bv_ss_timestamp1_name, betaconst.bv_ss_timestamp2_name):
        timestamps.append(get_shmem_array(name, timestamp_shape, np.float64, create=create))

    return shared_images, timestamps


def get_detection_shares(create=False):
    n_pictures = len(betaconfig.picture_sizes)
    remote_outs = [
        get_shmem_array(betaconst.bv_detect_shm_0_name, (n_pictures, 300, 4), np.float32, create=create),
        get_shmem_array(betaconst.bv_detect_shm_1_name, (n_pictures, 300), np.float32, create=create),
        get_shmem_array(betaconst.bv_detect_shm_2_name, (n_pictures, 300), np.int32, create=create),
    ]

    timestamp_shape = (1,)
    timestamps = []
    for name in (betaconst.bv_detect_timestamp1_name, betaconst.bv_detect_timestamp2_name):
        timestamps.append(get_shmem_array(name, timestamp_shape, np.float64, create=create))

    return remote_outs, timestamps


def do_screenshots(verbose=True):
    with mss.mss() as sct:
        adj_images = [None] * len(betaconfig.picture_sizes)
        shared_images, timestamps = get_shared_screenshots(create=True)
        time_start, time_end = timestamps

        while True:
            (sct_time, grab) = bu_vision.get_screenshot(sct)
            timestamp = np.array([sct_time])

            for i, size in enumerate(betaconfig.picture_sizes):
                adj_images[i] = bu_model.prep_img_for_nn(grab, size, bu_model.get_image_resize_scale(grab, size))
            time_start[:] = timestamp[:]
            for i, adj_image in enumerate(adj_images):
                shared_images[i][:] = adj_image[:]
            time_end[:] = timestamp[:]

            if betaconfig.debug_mode & 2:
                cv2.imwrite(
                    "debug-vision-raw-screenshot.png",
                    bu_censor.annotate_image_shape(grab),
                )
                for i, size in enumerate(betaconfig.picture_sizes):
                    cv2.imwrite(
                        "debug-vision-adj-screenshot-%d-%d.png" % (i, size),
                        bu_censor.annotate_image_shape(adj_images[i]),
                    )

            if verbose:
                print("screenshots: %6.1f ms" % ((time.monotonic() - sct_time) * 1000))


def do_detection():
    session = bu_model.get_session()

    raw_screenshots, in_timestamps = get_shared_screenshots()
    in_time1, in_time2 = in_timestamps
    remote_out_images, out_timestamps = get_detection_shares(create=True)
    # local_out_0 = np.ndarray((len(betaconfig.picture_sizes), 300, 4), dtype=np.float32)
    # local_out_1 = np.ndarray((len(betaconfig.picture_sizes), 300), dtype=np.float32)
    # local_out_2 = np.ndarray((len(betaconfig.picture_sizes), 300), dtype=np.int32)
    local_screenshots = []
    for size in betaconfig.picture_sizes:
        (this_height, this_width) = bu_vision.vision_adj_img_size(size)
        local_screenshots.append(np.ndarray((this_height, this_width, 3), dtype=np.float32))

    last_timestamp = 0
    image_sum = 0
    image_hash = 0
    while True:
        times = [time.perf_counter()]
        # wait for screenshot to be ready
        while in_time1[0] != in_time2[0] or in_time1[0] == last_timestamp:
            True

        times.append(time.perf_counter())

        last_timestamp = in_time1[0]
        # Get local copies of the screenshots
        for i, local in enumerate(local_screenshots):
            local[:] = raw_screenshots[i][:]

        times.append(time.perf_counter())

        ### we don't want to censor again if image is unchanged
        ### hashing at size 1280 takes 30ms, which is not nothing
        ### summing takes 10ms, which is a lot less overhead.
        ### so start with a very fast check (just sum the image)
        ### if the sum is unchanged, proceed to hash
        ### this means we will Detect the same image twice in a
        ### row, but not more than twice
        # Updated numbers: sum takes 0.210ms, and xxh64 takes 1.171ms
        new_sum = np.sum(local_screenshots[0])
        times.append(time.perf_counter())

        if new_sum == image_sum:
            # new_hash = hashlib.md5(local_screenshots[0].tobytes()).digest()
            new_hash = xxhash.xxh64(local_screenshots[0].tobytes()).digest()
        else:
            new_hash = None

        times.append(time.perf_counter())

        did_censoring = False
        if new_sum != image_sum or new_hash != image_hash:
            did_censoring = True
            (local_out_0, local_out_1, local_out_2) = bu_model.get_raw_model_output(local_screenshots, session)

        times.append(time.perf_counter())

        image_sum = new_sum
        image_hash = new_hash

        out_timestamps[0][0] = last_timestamp
        remote_out_images[0][:] = local_out_0[:]
        remote_out_images[1][:] = local_out_1[:]
        remote_out_images[2][:] = local_out_2[:]
        out_timestamps[1][0] = last_timestamp

        times.append(time.perf_counter())
        time_deltas = [f"{(times[i] - times[i-1])*1000:6.1f}" for i in range(1, len(times))]
        wait_time = times[1] - times[0]
        processing_time = times[-1] - times[1]
        print(
            "detection: deltas:",
            ", ".join(time_deltas),
            f"; wait_time: {wait_time*1000:6.1f}; processing_time: {processing_time*1000:6.3f}; {did_censoring}",
        )


def do_display_censor():
    remote_out_images, out_timestamps = get_detection_shares()

    local_out_0 = np.ndarray(remote_out_images[0].shape, dtype=remote_out_images[0].dtype)
    local_out_1 = np.ndarray(remote_out_images[1].shape, dtype=remote_out_images[1].dtype)
    local_out_2 = np.ndarray(remote_out_images[2].shape, dtype=remote_out_images[2].dtype)

    last_detect_timestamp = 0

    scale_array = []
    for size in betaconfig.picture_sizes:
        scale_array.append(bu_model.get_resize_scale(betaconfig.vision_cap_width, betaconfig.vision_cap_height, size))

    ### set up for censoring
    img_buffer = []
    boxes = []
    window_name = "BetaVision"
    cv2.startWindowThread()
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, betaconfig.vision_cap_width, betaconfig.vision_cap_height)
    sct = mss.mss()

    while True:
        times = []
        times.append(time.perf_counter())
        img_buffer.append(bu_vision.get_screenshot(sct))

        if betaconfig.debug_mode & 2:
            cv2.imwrite("debug-vision-precensor.png", img_buffer[-1][1])

        times.append(time.perf_counter())
        if out_timestamps[0][0] == out_timestamps[1][0] and out_timestamps[0][0] != last_detect_timestamp:
            last_detect_timestamp = out_timestamps[0][0]
            local_out_0[:] = remote_out_images[0][:]
            local_out_1[:] = remote_out_images[1][:]
            local_out_2[:] = remote_out_images[2][:]

            all_raw_boxes = bu_model.raw_boxes_from_model_output(
                [local_out_0, local_out_1, local_out_2], scale_array, last_detect_timestamp
            )

            raw_boxes = [box for raw_boxes in all_raw_boxes for box in raw_boxes]
            this_boxes = [
                bu_censor.process_raw_box(raw, betaconfig.vision_cap_width, betaconfig.vision_cap_height)
                for raw in raw_boxes
            ]
            this_boxes = [box for box in this_boxes if box]
            boxes.extend(this_boxes)
            boxes.sort(key=lambda x: x["end"])

        times.append(time.perf_counter())
        while len(boxes) and boxes[0]["end"] < time.monotonic() - betaconfig.betavision_delay:
            boxes.pop(0)

        times.append(time.perf_counter())
        while len(img_buffer) > 1 and time.monotonic() - img_buffer[1][0] > betaconfig.betavision_delay:
            img_buffer.pop(0)

        times.append(time.perf_counter())
        frame_timestamp = time.monotonic() - betaconfig.betavision_delay

        # nothing in the buffer is old enough
        if img_buffer[0][0] > frame_timestamp:
            continue

        times.append(time.perf_counter())
        if betaconfig.betavision_interpolate:
            frame = bu_vision.interpolate_images(
                img_buffer[0][1], img_buffer[0][0], img_buffer[1][1], img_buffer[1][0], frame_timestamp
            )
        else:
            frame = img_buffer[0][1]

        times.append(time.perf_counter())
        live_boxes = [box for box in boxes if box["start"] < frame_timestamp < box["end"]]

        times.append(time.perf_counter())
        frame = bu_censor.censor_img_for_boxes(frame, live_boxes)

        if betaconfig.debug_mode & 1:
            frame = bu_censor.annotate_image_shape(frame)

        cx, cy = bu_vision.get_cursor_location()
        cx = cx - betaconfig.vision_cap_left
        cy = cy - betaconfig.vision_cap_top

        if 5 < cx < betaconfig.vision_cap_width and 5 < cy < betaconfig.vision_cap_height:
            color = tuple(reversed(betaconfig.vision_cursor_color))
            frame[cy - 5 : cy + 5, cx - 5 : cx + 5] = color
            if betaconfig.debug_mode & 1:
                frame = cv2.putText(
                    frame,
                    "(%d,%d)" % (cx, cy),
                    (max(cx - 10, 0), max(cy - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )

        if betaconfig.debug_mode & 2:
            cv2.imwrite("debug-vision-postcensor.png", frame)

        times.append(time.perf_counter())
        cv2.imshow(window_name, frame)
        times.append(time.perf_counter())
        times_display = ["%6.1f" % ((x - times[0]) * 1000) for x in times]
        print("display:", ", ".join(times_display))

        if cv2.waitKey(1) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="BetaSuite Vision", description="Live censoring")
    parser.add_argument(
        "command",
        choices=["censor", "screenshot", "detect", "display", "cursor"],
        default="censor",
        nargs="?",
        help="Censoring suite sub-command to run (defaults to the full censor process)",
    )
    args = parser.parse_args()
    if args.command == "censor":
        screenshotter = Process(target=do_screenshots, daemon=True)
        screenshotter.start()
        detector = Process(target=do_detection, daemon=True)
        detector.start()
        do_display_censor()
    elif args.command == "screenshot":
        do_screenshots()
    elif args.command == "detect":
        do_detection()
    elif args.command == "display":
        do_display_censor()
    elif args.command == "cursor":
        while True:
            cx, cy = bu_vision.get_cursor_location()
            print("x: %4d, y: %4d" % (cx, cy))
