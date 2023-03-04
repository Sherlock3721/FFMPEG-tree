import glob, os, signal, sys, subprocess
from subprocess import call

Dir="/mnt/sftp/share/Disk2/Seriály"
Del=True

VC="libvpx-vp9"
AC="aac"
Extension="mp4"
Preset="slow"

#LOG=" 2> " + Dir + "FFMEG.log"

SkipCodec=['h264','vp9','av1','avc1','aac','ac3','mjpeg','bin_data','mov_text','hevc','unknown','dvd_subtitle','mp3','opus','truehd','dts']
SearchExtension=['avi','mp4','mkv','mpg','m4v','mov']
files=[]
TempNameUsed=False

def FFmpeg(FILE):
    if TempNameUsed:
        NewFilename = os.path.splitext(FILE)[0].replace(".","",1) + "." + Extension
    else:
        NewFilename = os.path.splitext(FILE)[0] + "." + Extension

    Command=["ffmpeg", "-nostdin", "-i", FILE, "-n", "-c:v", VC, "-c:a", AC, "-crf", "23", "-preset", Preset, "-hide_banner", "-v", "error", "-movflags", "+faststart",  NewFilename ]

    try:
        if not os.path.exists(NewFilename):
            print("Starting formating file: " + os.path.split(FILE)[1])
            subprocess.run(Command)
            if Del == True:
                print("Delete file!")
                os.remove(File)
            print("Done!")
            return True
        else:
            print("File already exists, skipping: " + FILE)
    except KeyboardInterrupt:
        print("Interupt inside formating! Deleting new file!")
        os.remove(NewFilename)
        sys.exit(0)

def FFPROBE(FILE):
    cmnd = ['ffprobe', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', '-loglevel', 'quiet', FILE]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()

    codecs = out.decode().replace(r'\n', ' ').split()

    for codec in codecs:
        if codec not in SkipCodec:
            print(FILE, codecs)
            return True

    return False

while True:
    try:
        print("Starting searching for files!")
        for Ext in SearchExtension:
            files.extend(glob.glob(Dir + '/**/*.' + Ext, recursive=True))
        print("Starting formating!")
        for File in files:
            if (File.endswith("." + Extension)):
                if FFPROBE(File):
                    TempFilename = os.path.split(File)[0] + "." + os.path.split(File)[1]
                    os.rename(File, TempFilename)
                    TempNameUsed=True
                    FFmpeg(TempFilename)
                continue
            else:
                FFmpeg(File)
    except KeyboardInterrupt:
        print('Interupt before formating!')
        break
