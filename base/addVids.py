from project import Project
from time import sleep

# vids = [101, 102, 103, 104, 105, 201, 202, 203, 204, 205, 301, 302, 303, 304, 305, 401, 402, 403, 404, 405, 501, 502, 503, 504, 505]
vids = [103]

app = Project()

def getFileText(filename):
    text = ''
    try:
        with open(filename, 'r') as f:
            text = f.read()
    except:
        print("Error reading file")
    return text.strip()

for vid in vids:
    # videoPath = rf"C:\Users\likhi\Documents\capstone\vid-files\cc_dset\videos\pv{vid}.mp4"
    srtPath = rf"C:\Users\likhi\Documents\capstone\vid-files\cc-dset\srts\pv{vid}.srt"
    filename = srtPath.strip()
    fileContent = getFileText(filename)
    if len(fileContent) == 0:
        print("Empty file")
    else:
        print(app.addDocument(vid, fileContent))
        print(f"Video {vid} added successfully!")
    sleep(2) #simply a break

print('Done')


