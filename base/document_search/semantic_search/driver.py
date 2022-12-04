from indexer import Index

pineconeApiKey = '839360cd-748d-47e9-bc72-2dd0f62f27ee'
indexName = 'semantic-index'
nameSpace = 'transcript'
index = Index(pineconeApiKey, indexName, nameSpace)

def getFileText(filename):
    text = ''
    try:
        with open(filename, 'r') as f:
            text = f.read()
    except:
        print("Error reading file")
    return text.strip()

def addDoc():
    print("Enter doc ID: ")
    docId = int(input())
    print("Enter text file name: ")
    filename = input().strip()
    fileContent = getFileText(filename)
    if len(fileContent) == 0:
        print("Empty file")
    else:
        index.addDocument(docId, fileContent)
        print("Document added successfully!")

def deleteDoc():
    print("Enter doc ID: ")
    docId = int(input())
    index.deleteDocument(docId)
    print("Document deleted successfully!")

def query():
    print("Enter query: ")
    query = input().strip()
    res = index.getDocuments(query)
    print(res)

while True:
    print(" 1. Add Doc\n 2. Delete Doc\n 3.Query\n 0. Exit")
    inp = int(input())
    if inp == 1:
        addDoc()
    elif inp == 2:
        deleteDoc()
    elif inp == 3:
        query()
    elif inp == 0:
        break
    else:
        continue

