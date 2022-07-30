import subprocess

def video_file_has_audio( filepath ):
    command = [ "../ffmpeg/bin/ffprobe.exe",
            '-loglevel', 'error',
            '-show_entries', 'stream=index,codec_type',
            '-of', 'csv=p=0',
            filepath
    ]

    res = subprocess.run( command, capture_output=True )
    decoded = res.stdout.decode()
    if 'audio' in decoded:
        return( True )
    else:
        return( False )
