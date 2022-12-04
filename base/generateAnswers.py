import pandas as pd
from project import Project

# {'model': 'distilbert-base-cased-distilled-squad'}
app = Project({'model': 'distilbert-base-cased-distilled-squad'})
app.getQAModelReady()

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
    'BestAnswer',
    'BestAnswer_start',
    'BestAnswer_end',
    'LongAnswer',
    'LongAnswer_start',
    'LongAnswer_end',
    'Related_Video_IDs']
rows = []
print(f'\t{len(rows)}/{qcount}', end='\r')

for question in dset['Question']:
    res = app.executeQuery(question)
    data = [
        res['videoId'], 
        res['answers']['bestAnswer'][0],
        timeInSec(res['answers']['bestAnswer'][1]),
        timeInSec(res['answers']['bestAnswer'][2]),
        res['answers']['longAnswer'][0],
        timeInSec(res['answers']['longAnswer'][1]),
        timeInSec(res['answers']['longAnswer'][2]),
        ' '.join(res['relatedVideoIds'])
    ]
    rows.append(data)
    print(f'\t{len(rows)}/{qcount}', end='\r')


opdf = pd.DataFrame(data=rows, columns=cols)
opdf.to_csv(op_file_path, index=False)
print(f'results saved at {op_file_path}')
