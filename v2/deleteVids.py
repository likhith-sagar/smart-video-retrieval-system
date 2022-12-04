from project import Project
from time import sleep

# vids = [101, 102, 103, 104, 105, 106, 107, 201, 202, 203, 204, 205, 206, 207, 401, 402, 403, 404, 405, 406, 407]
# vids = [101, 102, 103, 104, 105, 201, 202, 203, 204, 205, 301, 302, 303, 304, 305, 401, 402, 403, 404, 405, 501, 502, 503, 504, 505]
vids = [505]

app = Project()

for vid in vids:
    app.deleteDocument(vid)
    print(f'Deleted video {vid} successfully!')
    sleep(1) #simply a break

print('Done')


