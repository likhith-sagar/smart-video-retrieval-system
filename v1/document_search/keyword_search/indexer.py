from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from math import log10

from .dbHandler import DbHandler

class Index:
    lemmatizer = WordNetLemmatizer()
    ps = PorterStemmer()
    stop_words = set(stopwords.words("english"))
    punctuation = '''#.,'"!?(){[]};&'''
    translate_table = dict((ord(char), ' ') for char in punctuation) 
    tokenizer = RegexpTokenizer(r'\w+')
    
    def __init__(self, connectionString, dbName, preprocess=3, minLen=2):
        self.preProcess = self.__getPreprocessor(preprocess)
        self.minLen = minLen
        self.dbhandler = DbHandler(connectionString, dbName)
    
    def __preProcess3(self, text):
        '''
        preporcessing with stemming, no lemmatizing
        '''
        ptext = text.lower()
        ptext = ptext.translate(self.translate_table)
        ptext = filter(lambda word: len(word) >= self.minLen, ptext.split())
        ptext = [self.ps.stem(token) for token in ptext if token not in self.stop_words]
        ptext = ' '.join(ptext)
        return ptext

    def __preProcess2(self, text):
        '''
        Complete preporcessing
        '''
        ptext = text.lower()
        ptext = ptext.translate(self.translate_table)
        ptext = filter(lambda word: len(word) >= self.minLen, ptext.split())
        ptext = [self.lemmatizer.lemmatize(token) for token in ptext]
        ptext = [self.ps.stem(token) for token in ptext if token not in self.stop_words]
        ptext = ' '.join(ptext)
        return ptext
    
    def __preProcess1(self, text):
        '''
        Semi preprocessing
        '''
        ptext = text.lower()
        ptext = ptext.translate(self.translate_table)
        ptext = filter(lambda word: len(word) >= self.minLen, ptext.split())
        ptext = [token for token in ptext if token not in self.stop_words]
        ptext = ' '.join(ptext)
        return ptext

    def __getPreprocessor(self, preprocess):
        preProcessor = lambda x: str(x)
        if preprocess == 1:
            preProcessor = self.__preProcess1
        elif preprocess == 2:
            preProcessor = self.__preProcess2
        elif preprocess == 3:
            preProcessor = self.__preProcess3
        return preProcessor

    def tokenize(self, text):
        return self.tokenizer.tokenize(text)


    def addDocument(self, id, text):
        #preprocessing and counting term frequency in body (text)
        id = str(id)
        text = self.preProcess(text)
        textTokens = self.tokenize(text)
        tokenCount = {}
        for token in textTokens:
            if token in tokenCount:
                tokenCount[token] += 1
            else:
                tokenCount[token] = 1
        entries = []
        for token in tokenCount:
            entries.append((token, tokenCount[token]/len(textTokens)))
        if len(entries):
            self.dbhandler.bulkUpdate(id, entries)
        return len(entries)

    def deleteDocument(self, id):
        id = str(id)
        return self.dbhandler.delete(id)   
        
    def getDocuments(self, query, k=5):
        #preprocessing
        query = self.preProcess(query)
        queryTokens = self.tokenize(query)
        docCount = self.dbhandler.getDocsCount()
        #calculating TF-IDF scores
        scores = {}
        for token in queryTokens:
            #get doc list for token from db
            termDoc = self.dbhandler.getEntry(token)
            postingList = termDoc['docs'] if termDoc != None else []
            #For each doc in posting List, update TF-IDF score
            for entry in postingList:
                tfIdf = entry['tf'] * log10(1 + docCount/len(postingList))
                if entry['doc_id'] in scores:
                    scores[entry['doc_id']] += tfIdf
                else:
                    scores[entry['doc_id']] = tfIdf
        res = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        totalScore = sum([x[1] for x in res])
        return list(map(lambda x: (str(x[0]), x[1]/totalScore), res))

