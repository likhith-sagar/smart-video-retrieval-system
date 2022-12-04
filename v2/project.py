from document_search.indexer import Index
from transcript_manager.transcriptManager import TranscriptManager
from qa_module.QAModel import QAModel
from segmen_module.videoSegmentor import VideoSegmentor
# from segmen_module.ytVideoSegmentor import YtVideoSegmentor as VideoSegmentor

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
        self.titleWeight = 3
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
        self.qaModel = QAModel(
            model=self.conf['model'],
            useCuda=self.conf['useCuda']
        )
        print('QA Model Ready')
    
    def addDocument(self, id, srt, vidPath):
        id = str(id)
        vidSegmentor = VideoSegmentor(vidPath)
        groups = vidSegmentor.start()
        segmentSpans = list(map(lambda x: x[1:3], groups))
        textExtracts = list(map(lambda x: ' '.join([x[0]*self.titleWeight, x[3]]).strip(), groups))
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
            'relatedVideoIds': list(map(lambda x: x[0], docs[1:])) #add score threshold
        }
        return res


