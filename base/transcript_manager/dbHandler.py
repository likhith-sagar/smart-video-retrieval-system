from pymongo import MongoClient

class DbHandler:
    def __init__(self, connectionString, dbName):
        self.connectionString = connectionString
        self.dbName = dbName
        self.client = MongoClient(connectionString)
        self.db = self.client[dbName]
        self.trans_col = self.db['transcripts']

    def addDocSubtitle(self, docId, srtText, transcript):
        #catch for primary key errors
        self.trans_col.insert_one({
            'doc': str(docId),
            'srt': srtText,
            'transcript': transcript
        })
        return True
    
    def getDocSrt(self, docId):
        res = self.trans_col.find_one({'doc': str(docId)}, {'srt':1})
        return res['srt'] if res != None else res

    def getDocTranscript(self, docId):
        res = self.trans_col.find_one({'doc': str(docId)}, {'transcript':1})
        return res['transcript'] if res != None else res

    def deleteDocSubtitle(self, docId):
        self.trans_col.delete_one({'doc': str(docId)})
        return True