from pydoc import doc
from indexer import Index

connectionString = 'mongodb://myuser:password@localhost:27017/?authSource=test'
dbName = 'inv_index'
index = Index(connectionString, dbName)

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
    docId = input().strip()
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
    res = index.getDocuments(query, k=5)
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

