import subprocess
import betaconfig

def video_file_has_audio( filepath ):
    command = [ betaconfig.ffprobe_path,
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
