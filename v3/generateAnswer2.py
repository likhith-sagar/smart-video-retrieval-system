import pandas as pd
from projectWoQA import Project

# {'model': "distilbert-base-cased-distilled-squad"}
app = Project()
# app.getQAModelReady()

inp_file_path = input("Enter input csv file path: ")
op_file_path = input("Enter output file path: ")

try:
    dset = pd.read_csv(inp_file_path)
except:
    print("Input file error")
    exit()

def timeInSec(hhmmss):
    nums = hhmmss.split(':')
    s = 60*60
    ans = 0
    for n in nums:
        ans+=(s*int(n))
        s//=60
    return ans

qcount = len(dset)
cols=[
    'Predicted_Video_ID',
    'BestAnswer_start',
    'BestAnswer_end',
    'Related_Video_IDs']
rows = []

def processVidsData(res):
    #video id and related video ids
    top = res[0].split('_')[0]
    others = {top}
    rel = []
    for i in range(1, len(res)):
        id = res[i].split('_')[0]
        if id not in others:
            rel.append(id)
            others.add(id)
    rel = ' '.join(rel)
    return [top, rel]

print(f'\t{len(rows)}/{qcount}', end='\r')
for question in dset['Question']:
    res = app.executeQuery(question)
    vidsData = processVidsData([res['videoId'], *res['relatedVideoIds']])
    data = [
        vidsData[0], 
        timeInSec(res['answers']['bestAnswer'][1]),
        timeInSec(res['answers']['bestAnswer'][2]),
        vidsData[1]
    ]
    rows.append(data)
    print(f'\t{len(rows)}/{qcount}', end='\r')


opdf = pd.DataFrame(data=rows, columns=cols)
opdf.to_csv(op_file_path, index=False)
print(f'results saved at {op_file_path}')
