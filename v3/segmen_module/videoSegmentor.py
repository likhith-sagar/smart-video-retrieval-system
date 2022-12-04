from time import sleep
import cv2
from numpy import array as narray
from numpy import dot
from numpy.linalg import norm
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from threading import Thread
from sentence_transformers import SentenceTransformer

class VideoSegmentor:
    def __init__(self, videoPath, interval=4, threadCount=4, offset=15, segLen=60):
        self.videoPath = videoPath
        cam = cv2.VideoCapture(videoPath)
        self.totalFrameCount = int(cam.get(cv2. CAP_PROP_FRAME_COUNT))
        self.videoFps = round(cam.get(cv2.CAP_PROP_FPS), 2)
        self.frameGap = round(self.videoFps*interval)
        self.threadCount = threadCount
        self.frameOffset = int(offset*self.videoFps)
        self.simThreshold = 0.80
        self.minBodyLen = 50
        self.segLen = segLen
        self.minExceptionLen = 20
        cam.release()
    
    def textPreprocess(self, title):
        maxLen = 15
        minLen = 2
        ptext = title.lower()
        words = ptext.split()
        filteredWords = filter(lambda word: len(word.strip()) >= minLen and len(word.strip()) <= maxLen, words)
        pwords = map(lambda word: str().join([ch for ch in word if ch.isalnum()]), filteredWords)
        return ' '.join(pwords).strip()

    def start(self):

        def processVideo(start, end, data, progress, idx):
            model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-cos-v1')
            cam = cv2.VideoCapture(self.videoPath)
            bag = [['', 0 , 0, []]]
            nextSplit = int(start/self.videoFps) + self.segLen
            currentFameCount = start
            prevVec = [0]*768
            cam.set(cv2.CAP_PROP_POS_FRAMES, currentFameCount)
            while(currentFameCount < end):
                ret,frame = cam.read()

                #frame extraction
                k=pytesseract.image_to_string(frame)
                body = self.textPreprocess(k)
                if len(body) < self.minBodyLen:
                    body = ''

                timestamp = int(currentFameCount/self.videoFps)
                bag[-1][2] = timestamp
                if timestamp >= nextSplit:
                    bag.append(['', timestamp, timestamp, []])
                    nextSplit += self.segLen
                if len(body):
                    curVec = model.encode(body)
                    if len(bag[-1][3]):
                        similarity = round(dot(prevVec, curVec)/(norm(prevVec)*norm(curVec)), 2)
                        if similarity < self.simThreshold:
                            bag[-1][3].append(body)
                            prevVec = curVec
                    else:
                        bag[-1][3].append(body)
                        prevVec = curVec

                currentFameCount+=self.frameGap
                progress[idx] += self.frameGap
                cam.set(cv2.CAP_PROP_POS_FRAMES, currentFameCount)

            if len(bag) > 1:
                lastEntry = bag.pop()
                if lastEntry[2]-lastEntry[1] < self.minExceptionLen:
                    bag[-1][2] = lastEntry[2]
                    bag[-1][3].extend(lastEntry[3])
                else:
                    bag.append(lastEntry)

            progress[idx] = end-start
            data[idx] = bag
            cam.release()

        def trackProgess(progress):
            count = 0
            perc = 0
            while perc <= 100 and progress[-1] == 0:
                print(f'\t{perc}%', end='\r')
                sleep(0.5)
                count = sum(progress)
                perc = (count*100)//self.totalFrameCount

        progress = [0] + [0]*self.threadCount
        data = [None]*self.threadCount
        threads = []
        timeInMins = (self.totalFrameCount/self.videoFps)/60
        framesPerThread = int(int(timeInMins/self.threadCount)*60*self.videoFps)
        ends = [i*framesPerThread for i in range(1,self.threadCount)]
        ends.append(self.totalFrameCount-self.frameOffset)
        prev = self.frameOffset
        for i in range(self.threadCount):
            args=[prev, ends[i], data, progress, i]
            threads.append(Thread(target=processVideo, args=args))
            prev = ends[i]
        progressThread = Thread(target=trackProgess, args=[progress], daemon=True)
        
        for i in range(self.threadCount):
            threads[i].start()
        progressThread.start()
        for i in range(self.threadCount):
            threads[i].join()
        progress[-1] = 1 #to stop progress thread
        print('\t100%', end='\r')

        segments = data[0]
        for i in range(1, len(data)):
            data[i][0][1] = segments[-1][2]
            segments.extend(data[i])

        #converting text arrays into text by joining
        for segment in segments:
            segment[3] = ' '.join(segment[3])
             
        print('Done')
        return segments