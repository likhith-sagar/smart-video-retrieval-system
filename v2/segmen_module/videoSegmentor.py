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
    def __init__(self, videoPath, interval=4, threadCount=4, offset=15):
        self.videoPath = videoPath
        cam = cv2.VideoCapture(videoPath)
        self.totalFrameCount = int(cam.get(cv2. CAP_PROP_FRAME_COUNT))
        self.videoFps = round(cam.get(cv2.CAP_PROP_FPS), 2)
        self.frameGap = round(self.videoFps*interval)
        self.threadCount = threadCount
        self.frameOffset = int(offset*self.videoFps)
        self.simThreshold = 0.80
        self.minBodyLen = 50
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
            currentFameCount = start
            prevVec = [0]*768
            cam.set(cv2.CAP_PROP_POS_FRAMES, currentFameCount)
            while(currentFameCount < end):
                ret,frame = cam.read()
            
                h,w,channels=frame.shape
                topSize=h//5
                widthSize = int(w*(6/7))
                topFrame = frame[:topSize]
                topLeftFrame = []
                for i in range(len(topFrame)):
                    topLeftFrame.append(topFrame[i][:widthSize])
                topLeftFrame = narray(topLeftFrame)
                botFrame = frame[topSize:-int(topSize*0.6)]
                bottomLeftFrame = []
                for i in range(len(botFrame)):
                    bottomLeftFrame.append(botFrame[i][:widthSize])
                bottomLeftFrame = narray(bottomLeftFrame)

                #title extraction
                k=pytesseract.image_to_string(topLeftFrame)
                texts = k.split('\n')
                title = ''
                if len(texts) > 1:
                    title = texts[1].strip()
                title = self.textPreprocess(title)

                #body extraction
                k=pytesseract.image_to_string(bottomLeftFrame)
                body = self.textPreprocess(k)
                if len(body) < self.minBodyLen:
                    body = ''

                timestamp = int(currentFameCount//self.videoFps)

                bag[-1][2] = timestamp
                if title != bag[-1][0]:
                    if bag[-1][0] == '' and title != '':
                        bag[-1][0] = title
                    else:
                        bag.append([title, timestamp, timestamp, []])
                if len(body):
                    curVec = model.encode(body)
                    if len(bag[-1][3]) == 0:
                        bag[-1][3].append(body)
                        prevVec = curVec
                    else:
                        similarity = round(dot(prevVec, curVec)/(norm(prevVec)*norm(curVec)), 2)
                        if similarity < self.simThreshold:
                            bag[-1][3].append(body)
                            prevVec = curVec

                currentFameCount+=self.frameGap
                progress[idx] += self.frameGap
                cam.set(cv2.CAP_PROP_POS_FRAMES, currentFameCount)
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
        framesPerThread = self.totalFrameCount//self.threadCount
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

        bag = data[0]
        for i in range(1,len(data)):
            data[i][0][1] = bag[-1][2]
            if bag[-1][0] == '':
                data[i][0][1] = bag[-1][1]
                data[i][0][3].extend(bag[-1][3])
                bag.pop()
            bag.extend(data[i])

        #case when last title is empty
        if bag[-1][0] == '':
            if len(bag) > 1:
                bag[-2][2] = bag[-1][2]
                bag[-2][3].extend(bag[-1][3])
                bag.pop()

        #combine segments that have different titles between same titles
        bottle = {}
        for entry in bag:
            if entry[0] in bottle:
                bottle[entry[0]][1] = entry[2]
                bottle[entry[0]][2].extend(entry[3])
            else:
                bottle[entry[0]] = [entry[1], entry[2], entry[3]]
        bag = sorted(map(lambda item: [item[0], item[1][0], item[1][1], item[1][2]], bottle.items()), key=lambda entry: entry[1])

        #eliminating overlapping/bounded segments
        prev = 0
        segments = []
        for entry in bag:
            if entry[1] >= prev:
                segments.append(entry)
                prev = entry[2]
            else:
                segments[-1][3].extend(entry[3])

        #converting text arrays into text by joining
        for segment in segments:
            segment[3] = ' '.join(segment[3])
             
        print('Done')
        return segments