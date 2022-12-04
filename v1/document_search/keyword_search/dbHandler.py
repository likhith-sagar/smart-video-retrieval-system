from pymongo import MongoClient
from pymongo import UpdateOne

class DbHandler:
    def __init__(self, connectionString, dbName):
        self.connectionString = connectionString
        self.dbName = dbName
        self.client = MongoClient(connectionString)
        self.db = self.client[dbName]
        self.terms_col = self.db['terms']
        self.docs_col = self.db['docs']
        self.stats_col = self.db['stats']

    def getDocsCount(self):
        doc = self.stats_col.find_one({'type': 'doc_count'})
        return doc['count'] if doc != None else 0

    def bulkUpdate(self, docId, data):
        #Try Except to be used to catch possible errors
        '''
        data: [entry1, entry2, ..]
        entry: (term, tf)
        '''
        operations = []
        terms = []
        for entry in data:
            term, tf = entry
            operations.append(
                UpdateOne({"term": term}, {
                    "$push": {"docs": {
                        'doc_id': docId,
                        'tf': tf
                    }}
                }, upsert=True, hint="term")
            )
            terms.append(term)
        self.docs_col.insert_one({'doc': docId, 'terms': terms})
        res = self.terms_col.bulk_write(operations, ordered=False)
        self.stats_col.bulk_write([
            UpdateOne({"type": 'doc_count'}, {
                "$inc": {"count": 1}
            }, upsert=True, hint='type'),
            UpdateOne({"type": 'term_count'}, {
                "$inc": {"count": res.upserted_count}
            }, upsert=True, hint='type')], ordered=False
        )
        return True
    
    def delete(self, docId):
        #Try Except to be used to catch possible errors
        doc = self.docs_col.find_one({'doc': docId})
        if not doc:
            return True
        terms = doc['terms']
        operations = []
        for term in terms:
            operations.append(
                UpdateOne({"term": term}, {
                    "$pull": {"docs":{
                        'doc_id': docId
                    } }
                })
            )
        self.terms_col.bulk_write(operations, ordered=False)
        res = self.terms_col.delete_many({"docs": {
            "$exists": True,
            "$size": 0
        }})
        self.docs_col.delete_one({'doc': docId}, hint='doc')
        self.stats_col.bulk_write([
            UpdateOne({"type": 'doc_count'}, {
                "$inc": {"count": -1}
            }, hint='type'),
            UpdateOne({"type": 'term_count'}, {
                "$inc": {"count": -res.deleted_count}
            }, hint='type')], ordered=False
        )
        return True
        
    def getEntry(self, term):
        return self.terms_col.find_one({'term': term})


