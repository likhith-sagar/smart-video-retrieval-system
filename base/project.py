from document_search.indexer import Index
from transcript_manager.transcriptManager import TranscriptManager
from qa_module.QAModel import QAModel

defaultConfig = {
    'connectionString': 'mongodb://myuser:password@localhost:27017/?authSource=test',
    'dbName': 'inv_index',
    'pineconeApiKey': '839360cd-748d-47e9-bc72-2dd0f62f27ee',
    'pineconeIndexName': 'semantic-index',
    'nameSpace': 'transcript',
    'model': "deepset/xlm-roberta-large-squad2",
    'useCuda': True
}

class Project:
    def __init__(self, config={}):
        conf = defaultConfig.copy()
        conf.update(config)
        self.conf = conf
        self.index = Index(
            connectionString=conf['connectionString'],
            dbName=conf['dbName'],
            pineconeApiKey=conf['pineconeApiKey'],
            pineconeIndexName=conf['pineconeIndexName'],
            nameSpace=conf['nameSpace']
        )
        print('Index Ready')
        self.tcManager = TranscriptManager(
            connectionString=conf['connectionString'],
            dbName=conf['dbName']
        )
        print('Transcript Manager Ready')
        
    def getQAModelReady(self):
        self.qaModel = QAModel(
            model=self.conf['model'],
            useCuda=self.conf['useCuda']
        )
        print('QA Model Ready')
    
    def addDocument(self, id, srt):
        srt = self.tcManager.preProcessSrt(srt)
        self.tcManager.addDocument(id, srt)
        tc = self.tcManager.srtToTranscript(srt)
        self.index.addDocument(id, tc)
        return True
    
    def deleteDocument(self, id):
        self.tcManager.deleteDocument(id)
        self.index.deleteDocument(id)
        return True
    
    def textSpanToTime(self, span, srt):
        '''
        span: [start, end]
        '''
        start, end = span
        entries = list(filter(lambda x: x, srt.split('\n\n')))
        startTime = ''
        endTime = ''
        parsedLen = 0
        cur = 0
        while cur < len(entries):
            entry = entries[cur]
            row = entry.split('\n')
            text = ' '.join(row[2:]).strip()
            textLen = len(text)+1
            parsedLen += textLen
            if parsedLen > start:
                startTime = row[1]
                parsedLen -= textLen
                break
            cur+=1
        while cur < len(entries):
            entry = entries[cur]
            row = entry.split('\n')
            text = ' '.join(row[2:]).strip()
            textLen = len(text)+1
            parsedLen += textLen
            endTime = row[1]
            if parsedLen >= end:
                break
            cur+=1
        return (startTime.split(' --> ')[0][:8], endTime.split(' --> ')[1][:8])

    def getDocIds(self, query, k=4, indexType=0):
        '''
        indexType:
            0 -> Both
            1 -> Keyword
            2 -> Semantic
        '''
        docs = None
        if indexType == 0:
            docs = self.index.getDocuments(query, k)
        elif indexType == 1:
            docs = self.index.keywordIndex.getDocuments(query, k)
        elif indexType == 2:
            docs = self.index.semanticIndex.getDocuments(query, k)
        else:
            docs = []
        return list(map(lambda x: x[0], docs))

    def executeQuery(self, query, docId=None):
        docs = self.index.getDocuments(query, k=4)
        if len(docs) == 0:
            return None
        docs = list(map(lambda x: x[0], docs))
        if docId:
            if docId in docs:
                docs.remove(docId)
            docs.insert(0, docId)
        topDocId = docs[0]
        tc = self.tcManager.getTranscript(topDocId)
        answers = self.qaModel.getAnswers(context=tc, question=query)
        videoSrt = self.tcManager.getTranscript(topDocId, srt=True)
        answers = list(map(lambda x: [x[0], *self.textSpanToTime([x[2], x[3]], videoSrt)], answers))
        bestAns = answers[0]
        longAns = answers[0]
        otherAns = []
        for i in range(1, len(answers)):
            if len(answers[i][0]) > len(longAns[0]):
                otherAns.append(longAns)
                longAns = answers[i]
            else:
                otherAns.append(answers[i])
        res = {
            'videoId': topDocId,
            'answers': {
                'bestAnswer': bestAns,
                'longAnswer': longAns,
                'otherAnswers': otherAns
            },
            'relatedVideoIds': docs[1:] #add score threshold
        }
        return res


