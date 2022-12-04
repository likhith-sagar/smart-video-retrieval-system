from sentence_transformers import SentenceTransformer
import pinecone


class Index:
    
    def __init__(self, pineconeApiKey, indexName, nameSpace):
        # self.dbhandler = DbHandler(connectionString, dbName)
        self.nameSpace = nameSpace
        self.model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-cos-v1')
        pinecone.init(api_key=pineconeApiKey, environment='us-west1-gcp')
        self.index = pinecone.Index(indexName)
    
    def __getEmbeddings(self, text):
        return self.model.encode(text)
    
    def addDocument(self, id, text):
        vectorRep = self.__getEmbeddings(text).tolist()
        entry = (str(id), vectorRep)
        res = self.index.upsert(vectors=[entry], namespace=self.nameSpace)
        return True if res['upserted_count'] > 0 else False

    def deleteDocument(self, id):
        self.index.delete(ids=[str(id)], namespace=self.nameSpace)
        return True

    def getDocuments(self, query, k=5):
        vectorRep = self.__getEmbeddings(query).tolist()
        queryRes = self.index.query(vector=vectorRep, namespace=self.nameSpace, top_k=k)
        totalScore = sum([x['score'] for x in queryRes['matches']])
        return list(map(lambda x: (x['id'], x['score']/totalScore), queryRes['matches']))



