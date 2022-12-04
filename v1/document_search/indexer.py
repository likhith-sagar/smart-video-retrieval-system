from .keyword_search.indexer import Index as KeywordIndex
from .semantic_search.indexer import Index as SemanticIndex

class Index:
    def __init__(self, connectionString, dbName, pineconeApiKey, pineconeIndexName, nameSpace):
        self.keywordIndex = KeywordIndex(connectionString, dbName)
        self.semanticIndex = SemanticIndex(pineconeApiKey, pineconeIndexName, nameSpace)
    
    def addDocument(self, id, text):
        return (self.keywordIndex.addDocument(id, text), self.semanticIndex.addDocument(id, text))
    
    def deleteDocument(self, id):
        self.keywordIndex.deleteDocument(id)
        self.semanticIndex.deleteDocument(id)
        return True
    
    def getDocuments(self, query, k=5):
        semres = self.semanticIndex.getDocuments(query, k)
        keyres = self.keywordIndex.getDocuments(query, k)
        if len(keyres):
            res = {x[0]: x[1] for x in semres}
            for entry in keyres:
                if entry[0] in res:
                    res[entry[0]] += entry[1]
                else:
                    res[entry[0]] = entry[1]
            return sorted([(x[0], x[1]/2) for x in res.items()], key=lambda x: x[1], reverse=True)[:k]
        else:
            return semres

