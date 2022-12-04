import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm
class YtVideoSegmentor:
    
    def __init__(self, videoPath, interval=4):
        
        self.min_SIM = 0.8
        self.interval=interval
        self.temp_seg=[]
        self.min_SegLength=40
        self.Segments_With_Notext = [] 
        self.VIDEO_PATH = videoPath 
        
        self.model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-cos-v1')  
    
    def textPreprocess(self,text):
        text=text.strip()
        ptext = text.lower()
        sentences = ptext.split('\n')
        words = []
        for sentence in sentences:
            words.extend(sentence.split())
        filteredWords = filter(lambda word: len(word.strip()) > 1, words)
        pwords = map(lambda word: str().join([ch for ch in word if ch.isalnum()]), filteredWords)
        return ' '.join(pwords).strip()

    def getsegments_NoText(self,similarity,seconds_count): 
                if similarity <= self.min_SIM:
                    if seconds_count!=0:
                        self.Segments_With_Notext[-1][2]=seconds_count#update the prev end point as prev second
                    self.Segments_With_Notext.append(['',seconds_count,seconds_count])#Create entry ['',start,start]
                else :
                    self.Segments_With_Notext[-1][2]=seconds_count#change the last entry's ending second
                
    def merge(self):
        n=len(self.Segments_With_Notext)
        ep=self.Segments_With_Notext[0][2]
        sp=self.Segments_With_Notext[0][1]
        
        for i in range(0,n-1):
            
            if ep-sp>=self.min_SegLength:#Merge and push to array once len>20
                
                self.temp_seg.append(['',sp,ep])
                sp=ep
            ep=self.Segments_With_Notext[i+1][2]   
        if ep- sp < self.min_SegLength:
         self.temp_seg[-1][2]=ep #new end point for last segment   
        elif ep-sp >= self.min_SegLength:
         self.temp_seg.append(['',sp,ep]) #create new entry
         
         
    def start(self):
        
        cam = cv2.VideoCapture(self.VIDEO_PATH)
        fps = round(cam.get(cv2.CAP_PROP_FPS))
        seconds_count=0
        currentFameCount = 0
        totalFrameCount = (cam.get(cv2. CAP_PROP_FRAME_COUNT))
        prevVec = [1]*768
        frameGap = round(fps*self.interval)
        while(currentFameCount < totalFrameCount):
            
            ret, frame = cam.read()
            if not ret: break
            k=pytesseract.image_to_string(frame)
            text = self.textPreprocess(k)
            vec = self.model.encode(text)
            similarity = round(dot(prevVec, vec)/(norm(prevVec)*norm(vec)), 2)
            self.getsegments_NoText(similarity,seconds_count)#Get segments on w/o text 
                
            prevVec = vec
                
            seconds_count+=self.interval #Seconds will increment according to interval gap
            
            currentFameCount+=frameGap
            cam.set(cv2.CAP_PROP_POS_FRAMES, currentFameCount)
            print(f'\t{(currentFameCount*100)//totalFrameCount}%', end='\r')
        cam.release()
        print("Done")
        self.merge()
        return self.temp_seg
    
        
    
    