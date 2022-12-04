import pandas as pd
from project import Project


app = Project()

inp_file_path = input("Enter input csv file path: ")
op_file_path = input("Enter output file path: ")
indType = int(input("Enter Index Type: "))

try:
    dset = pd.read_csv(inp_file_path)
except:
    print("Input file error")
    exit()


qcount = len(dset)
cols=[
    'Predicted_Video_ID',
    'Related_Video_IDs']
rows = []
print(f'\t{len(rows)}/{qcount}', end='\r')
for question in dset['Question']:
    res = app.getDocIds(question, indexType=indType)
    data = ['','']
    if len(res):
        data = [
            res[0],
            ' '.join(res[1:])
        ]
    rows.append(data)
    print(f'\t{len(rows)}/{qcount}', end='\r')


opdf = pd.DataFrame(data=rows, columns=cols)
opdf.to_csv(op_file_path, index=False)
print(f'results saved at {op_file_path}')
