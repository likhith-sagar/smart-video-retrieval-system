from document_search.indexer import Index
from transcript_manager.transcriptManager import TranscriptManager
from qa_module.QAModel import QAModel
from segmen_module.videoSegmentor import VideoSegmentor

defaultConfig = {
    'connectionString': 'mongodb://myuser:password@localhost:27017/?authSource=test',
    'dbName': 'inv_index_2',
    'dbName2': 'inv_index_ex',
    'pineconeApiKey': '839360cd-748d-47e9-bc72-2dd0f62f27ee',
    'pineconeIndexName': 'semantic-index',
    'nameSpace': 'transcript_2',
    'nameSpace2': 'transcript_ex',
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
        print('Index-1 Ready')

        self.index2 = Index(
            connectionString=conf['connectionString'],
            dbName=conf['dbName2'],
            pineconeApiKey=conf['pineconeApiKey'],
            pineconeIndexName=conf['pineconeIndexName'],
            nameSpace=conf['nameSpace2']
        )
        print('Index-2 Ready')

        self.tcManager = TranscriptManager(
            connectionString=conf['connectionString'],
            dbName=conf['dbName']
        )
        print('Transcript Manager Ready')
        
    def getQAModelReady(self):
        print('No QA model')
    
    def addDocument(self, id, srt, vidPath):
        id = str(id)
        vidSegmentor = VideoSegmentor(vidPath, offset=15)
        groups = vidSegmentor.start()
        segmentSpans = list(map(lambda x: x[1:3], groups))
        textExtracts = list(map(lambda x: x[3], groups))
        segments = self.tcManager.segmentSrt(srt, segmentSpans)

        self.tcManager.addSegmentCount(id, len(segments))
        for i in range(len(segments)):
            segmentSrt = segments[i]
            segmentSrt = self.tcManager.preProcessSrt(segmentSrt)
            self.tcManager.addDocument(f'{id}_{i}', segmentSrt)
            tc = self.tcManager.srtToTranscript(segmentSrt)
            self.index.addDocument(f'{id}_{i}', tc)
            self.index2.addDocument(f'{id}_{i}', textExtracts[i])
        return True
    
    def deleteDocument(self, id):
        id = str(id)
        segCount = self.tcManager.getSegmentCount(id)
        for i in range(segCount):
            self.tcManager.deleteDocument(f'{id}_{i}')
            self.index.deleteDocument(f'{id}_{i}')
            self.index2.deleteDocument(f'{id}_{i}')
        self.tcManager.deleteSegmentCount(id)
        return True
    
    def textSpanToTime(self, span, srt):
        '''
        span: [start, end]
        '''
        start, end = span
        entries = list(filter(lambda x: len(x), srt.split('\n\n')))
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
            1 -> Transcript based
            2 -> Extracted text based
        '''
        docs = None
        if indexType == 0:
            share1 = .6
            share2 = .4
            docs1 = self.index.getDocuments(query, k)
            docs2 = self.index2.getDocuments(query, k)
            scores = {i[0]: i[1]*share1 for i in docs1}
            for id, score in docs2:
                if id in scores:
                    scores[id] += (score*share2)
                else:
                    scores[id] = (score*share2)
            docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        elif indexType == 1:
            docs = self.index.getDocuments(query, k)
        elif indexType == 2:
            docs = self.index2.getDocuments(query, k)
        else:
            docs = []
        return list(map(lambda x: x[0], docs))

    def executeQuery(self, query):
        docs = self.index.getDocuments(query, k=4)
        if len(docs) == 0:
            return None
        topDocId = docs[0][0]
        srt = self.tcManager.getTranscript(topDocId, srt=True)
        startTime, endTime = self.textSpanToTime([0, len(srt)], srt)
        res = {
            'videoId': topDocId,
            'answers': {
                'bestAnswer': ['', startTime, endTime],
            },
            'relatedVideoIds': list(map(lambda x: x[0], docs[1:])) #add score threshold
        }
        return res


