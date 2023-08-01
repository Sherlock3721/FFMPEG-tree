import glob, os, sys
from subprocess import call, run, Popen, PIPE
from send2trash import send2trash as s2t
from wakepy import keep

### Configure
SearchDirectory     = "/mnt/sftp/share/Disk2/Filmy"
DeleteAfterConvert  = False
OnlyAnalyze         = False
PowerOff            = False

VideoCodec          = "libvpx-vp9" 
AudioCodec          = "libopus"
Container           = "webm"
# Preset="slow"
CRF                 = "31"
Deadline            = "good"   # good best realtime

VideoSettings       = ["-map", "0:v", "-b:v", "0"]
AudioSettings       = ["-ac", "2", "-b:a", "96k", "-map", "0:a:m:language:cze", "-map", "0:a?:m:language:eng"]
SubtitleSettings    = ["-map", "0:s?:m:language:cze"]
OtherSettings       = []

SkipCodec           = ['h264','vp9','av1','aac','eac3','opus','flac','bin_data','mov_text','subrip','unknown','dvd_subtitle']
SearchContainer     = ['ts','mkv','mov','avi']

### DON'T TOUCH BELOW THIS TITLE

files=[]
TempNameUsed=False

if not CRF == "":
    OtherSettings += ["-crf", CRF]
if not Deadline == "":
    OtherSettings += ["-deadline", Deadline]

def FFmpeg(FILE):
    if TempNameUsed:
        NewFilename = os.path.split(FILE)[0] + "/" + os.path.splitext(FILE)[0].split("/")[-1].replace(".","",1) + "." + Container
    else:
        NewFilename = os.path.splitext(FILE)[0] + "." + Container
    Command=["ffmpeg", "-nostdin", "-hide_banner", "-i", FILE, "-n", "-c:v", VideoCodec] + VideoSettings + ["-c:a", AudioCodec] + ["-row-mt", "1",  "-threads", "8", "-speed", "1", "-tile-columns", "6", "-frame-parallel", "1", "-auto-alt-ref", "1", "-lag-in-frames", "25", "-quality", "good"] + AudioSettings + SubtitleSettings + OtherSettings + [NewFilename]
    print(' '.join(Command))
    try:
        if not os.path.exists(NewFilename):
            print("Starting formating file: " + os.path.split(FILE)[1])
            run(Command)
            if DeleteAfterConvert:
                print("Sending original file to trash!")
                s2t(File)
            print("Done!")
            return True
        else:
            print("File already exists, skipping: " + FILE)
    except KeyboardInterrupt:
        print("Interupt inside formating! Deleting new file!")
        s2t(NewFilename)
        sys.exit(0)

def FFPROBE(FILE):
    cmnd = ['ffprobe', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', '-loglevel', 'quiet', FILE]
    p = Popen(cmnd, stdout=PIPE, stderr=PIPE)
    out =  p.communicate()[0]

    codecs = out.decode().replace(r'\n', ' ').split()

    for codec in codecs:
        if codec not in SkipCodec:
            print(FILE, codecs)
            return True
    return False

with keep.running() as k:
    try:
        print("Starting searching for files!")
        for Ext in SearchContainer:
            files.extend(filter(os.path.isfile, glob.glob(SearchDirectory + '/**/*.' + Ext, recursive=True)))
        files.sort(key = lambda x: os.stat(x).st_size, reverse=True)
        print('\n'.join(files))
        print("Starting formating!")
        if not OnlyAnalyze:
            for File in files:
                if (File.endswith("." + Container)):
                    if FFPROBE(File):
                        TempFilename = os.path.split(File)[0] + "/." + os.path.split(File)[1]
                        print(TempFilename)
                        os.rename(File, TempFilename)
                        TempNameUsed=True
                        FFmpeg(TempFilename)
                    continue
                else:
                    FFmpeg(File)
    except KeyboardInterrupt:
        print('Interupt before formating!')
        sys.exit(1)
if PowerOff:
    os.system('systemctl poweroff')
