from project import Project

app = Project()
app.getQAModelReady()

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
    print("Enter srt file name: ")
    filename = input().strip()
    fileContent = getFileText(filename)
    if len(fileContent) == 0:
        print("Empty file")
    else:
        print(app.addDocument(docId, fileContent))
        print("Document added successfully!")

def deleteDoc():
    print("Enter doc ID: ")
    docId = int(input())
    app.deleteDocument(docId)
    print("Document deleted successfully!")

def query():
    print("Enter query: ")
    query = input().strip()
    res = app.executeQuery(query)
    print(res)

while True:
    print("1. Add Doc\n2. Delete Doc\n3. Query\n0. Exit")
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

