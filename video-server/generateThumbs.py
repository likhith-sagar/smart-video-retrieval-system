import cv2
from os import listdir
from os.path import isfile, join

def saveImg(vidPath, dest):
    secOffset = 3
    cam = cv2.VideoCapture(vidPath)
    videoFps = round(cam.get(cv2.CAP_PROP_FPS), 2)
    frameOffset = int(videoFps*secOffset)
    cam.set(cv2.CAP_PROP_POS_FRAMES, frameOffset)
    _,frame = cam.read()
    status = cv2.imwrite(dest, frame)
    cam.release()
    return status

vidFolder = r'C:\Users\likhi\Documents\capstone\phase-2\video_server\videos'
thumbFolder = r'C:\Users\likhi\Documents\capstone\phase-2\video_server\thumbnails'
files = [f for f in listdir(vidFolder) if isfile(join(vidFolder, f))]
print(f'{len(files)} files found!')

count = 0
for file in files:
    name = file.split('.')[0]
    src = join(vidFolder, file)
    dest = join(thumbFolder, f'{name}.jpg')
    count += saveImg(src, dest)

print(f"{count} Thumbnails generated.")


