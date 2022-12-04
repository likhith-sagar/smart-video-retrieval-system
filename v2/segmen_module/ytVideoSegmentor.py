import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm
class YtVideoSegmentor:
    
    def __init__(self, videoPath, interval=4):
        self.interval = interval# Target Keyframes Per Second
        self.min_SIM = 0.8
        self.Segments_Withtext = []
        self.temp_seg=[]
        self.min_SegLength=40
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
 
    def getsegments_Text(self,similarity,seconds_count,text): 
                if similarity <= self.min_SIM:
                    if seconds_count!=0:
                        self.Segments_Withtext[-1][2]=seconds_count#update the prev end point as prev second
                    self.Segments_Withtext.append(['',seconds_count,seconds_count,text])#Create entry ['',start,start,text]
                else:
                    if len(text) >len(self.Segments_Withtext[-1][0]):
                        self.Segments_Withtext[-1][3]=text #if slides are almost similar and text of new slide is slightly more ,then keep the bigger text 
                        
                    self.Segments_Withtext[-1][2]=seconds_count#change the last entry's ending second ['',start,new_end,text]
    def merge(self):
        n=len(self.Segments_Withtext)
        ep=self.Segments_Withtext[0][2]
        sp=self.Segments_Withtext[0][1]
        temp_text=""
        for i in range(0,n-1):
            temp_text+=self.Segments_Withtext[i][3]  #keep adding temp_text
            if ep-sp>=self.min_SegLength:#Merge and push to array once len>20
                
                self.temp_seg.append(['',sp,ep,temp_text])
                sp=ep
                
                temp_text="" #refresh temp_text after merging
            ep=self.Segments_Withtext[i+1][2]
                
        if ep- sp < self.min_SegLength:
         temp_text+=self.Segments_Withtext[n-1][3]
         self.temp_seg[-1][3]+=temp_text#Add text in last segment
         self.temp_seg[-1][2]=ep #new end point for last segment   
        elif ep-sp>=self.min_SegLength:
         temp_text=""#new temp_text for new segment
         temp_text+=self.Segments_Withtext[n-1][3]
         self.temp_seg.append(['',sp,ep,temp_text])
         
         
        
        
    def start(self):
        
        cam = cv2.VideoCapture(self.VIDEO_PATH)
        fps = round(cam.get(cv2.CAP_PROP_FPS))
        
        totalFrameCount = (cam.get(cv2. CAP_PROP_FRAME_COUNT))
        frameGap = round(fps*self.interval)
        currentFameCount = 0
        seconds_count=0
        prevVec = [1]*768
        while(currentFameCount < totalFrameCount):
            
            ret, frame = cam.read()
            if not ret: break
            k=pytesseract.image_to_string(frame)
            text = self.textPreprocess(k)
            vec = self.model.encode(text)
            similarity = round(dot(prevVec, vec)/(norm(prevVec)*norm(vec)), 2)
            self.getsegments_Text(similarity,seconds_count,text)#Get segments on w/o text 
            prevVec = vec
                
            seconds_count+=self.interval #Seconds will increment according to interval gap
            
            currentFameCount+=frameGap
            cam.set(cv2.CAP_PROP_POS_FRAMES, currentFameCount)
            print(f'\t{(currentFameCount*100)//totalFrameCount}%', end='\r')
        cam.release()
       
        print("Done")
        self.merge()
        return self.temp_seg
    
    