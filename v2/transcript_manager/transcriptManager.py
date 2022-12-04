from .dbHandler import DbHandler

class TranscriptManager:
    def __init__(self, connectionString, dbName):
        self.dbHandler = DbHandler(connectionString, dbName)
    
    def preProcessSrt(self, srt):
        res = ''
        allowed = ",.':-> \n?()%@#!+-&$^/*abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        allowed = set(allowed)
        for ch in srt:
            if ch in allowed:
                res+=ch
        return res
    
    def srtToTranscript(self, text):
        '''
        text: .srt format text
        '''
        entries = filter(lambda x: x, text.split('\n\n'))
        return str(' ').join(map(lambda x: ' '.join(x.split('\n')[2:]).strip(), entries))
    
    def addDocument(self, id, text):
        '''
        text: .srt formant text
        '''
        transcript = self.srtToTranscript(text)
        return self.dbHandler.addDocSubtitle(id, text, transcript)

    def getTranscript(self, docId, srt=False):
        if srt:
            return self.dbHandler.getDocSrt(docId)
        return self.dbHandler.getDocTranscript(docId)
    
    def deleteDocument(self, id):
        return self.dbHandler.deleteDocSubtitle(id)
    
    def addSegmentCount(self, docId, count):
        return self.dbHandler.addSegmentCount(docId, count)

    def getSegmentCount(self, docId):
        return self.dbHandler.getSegmentCount(docId)
    
    def deleteSegmentCount(self, docId):
        return self.dbHandler.deleteSegmentCount(docId)
    
    def segmentSrt(self, srt, segments):
        '''
        segments: [ [start, end] , ... ]
        '''
        def toSec(timestamp):
            parts = timestamp[:8].split(':')[::-1]
            cur = 1
            sec = 0
            for part in parts:
                sec += cur*int(part)
                cur *= 60
            return sec
        entries = list(filter(lambda x: x, srt.split('\n\n')))
        groups = []
        curGroup = []
        cur = 0
        for entry in entries:
                curGroup.append(entry)
                endTime = toSec(entry.split()[3])
                if cur < len(segments) and endTime >= segments[cur][1]:
                        groups.append('\n\n'.join(curGroup))
                        curGroup = []
                        cur+=1
        if len(curGroup):
            t = '\n\n'.join(curGroup)
            if cur < len(segments):
                groups.append(t)
            else:
                groups[-1] += f'\n\n{t}'
        return groups
    
        