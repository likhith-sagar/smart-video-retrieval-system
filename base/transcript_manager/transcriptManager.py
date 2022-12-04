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