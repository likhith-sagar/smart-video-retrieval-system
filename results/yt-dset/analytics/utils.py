import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sn

def showAvgPlots(arr, ylabel='Duration', xlabel='Answers in %'):
    arr.sort()
    plots = [0]
    for i in range(1, 101):
        x = int((i*len(arr))/100)
        avg = sum(arr[:x])/x
        plots.append(avg)
    print('100% Mean:', round(plots[-1], 2))
    print('80% Mean:', round(plots[80], 2))
    plt.plot(plots)
    plt.xticks(list(range(0,101, 10)))
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.grid()
    plt.show()

def compareVidIds(trueVals, predictedVals):
    #TN: not expected, not predicted : total_not_expected - still_predicted : (total - expected) - FP
    videoDetails = {} #VidID: [TP, FN, FP, TN]
    confused = {}
    for i in range(len(trueVals)):
        if trueVals[i] not in videoDetails:
            videoDetails[trueVals[i]] = [0, 0, 0, 0]
        if pd.isna(predictedVals[i]):
            videoDetails[trueVals[i]][1]+=1
            continue
        if predictedVals[i] not in videoDetails:
            videoDetails[predictedVals[i]] = [0, 0, 0, 0]
        if trueVals[i] == predictedVals[i]:
            videoDetails[trueVals[i]][0]+=1
        else:
            videoDetails[trueVals[i]][1]+=1
            videoDetails[predictedVals[i]][2]+=1
            k = tuple(sorted([trueVals[i], predictedVals[i]]))
            if k in confused:
                confused[k]+=1
            else:
                confused[k] = 1
    finalRes = [0, 0, 0, 0]
    ec = {} #expectedCount
    for vid in videoDetails:
        vals = videoDetails[vid]
        ec[vid] = sum(vals[:2])
        vals[0] = round((vals[0]*100)/ec[vid], 2)
        vals[1] = round((vals[1]*100)/ec[vid], 2)
        vals[3] = round(((len(trueVals) - ec[vid] - vals[2])*100)/(len(trueVals)-ec[vid]), 2)
        vals[2] = round((vals[2]*100)/(len(trueVals)-ec[vid]), 2)
        finalRes = list(map(lambda x: sum(x), zip(finalRes, map(lambda x: x*ec[vid], vals))))
    finalRes = list(map(lambda x: round(x/len(trueVals), 2), finalRes))
    vidRes = list(videoDetails.items())
    vidRes.sort(key=lambda x: x[1][0], reverse=True)
    confusedRes = list(map(lambda x: [x[0], round((x[1]*100)/(ec[x[0][0]]+ec[x[0][1]]), 2)], confused.items()))
    confusedRes = sorted(confusedRes, key=lambda x: x[1], reverse=True)[:5]
    res = {
        'totalResults': finalRes, #[TP, FN, FP, TN]
        'videoResults': vidRes, #[ (vidID, [TP, FN, FP, TN]), (...), ...]
        'confusedResults': confusedRes #[ [(vidID1, vidID2), Confusion], [...], ...]
    }
    return res

def drawConfusionMatrix(data, size=(4,3)):
    '''
    data: [TP, FN, FP, TN]
    '''
    fig, ax = plt.subplots(figsize=size)         
    mat = sn.heatmap([data[:2], data[2:]], 
    annot=True, annot_kws={"size": 10}, fmt='.2f',
    cmap='Blues', xticklabels=['T', 'N'], yticklabels=['T', 'N'], ax=ax)

    mat.set(xlabel='Predicted', ylabel='Actual')
    plt.show()

def compareRelatedVids(trueVidIds, predictedVidIds, predictedRelatedVidIds):
    count = 0
    miss = 0
    for i in range(len(trueVidIds)):
        if pd.isna(predictedVidIds[i]) or trueVidIds[i] != predictedVidIds[i]:
            miss+=1
            rel = predictedRelatedVidIds[i]
            if not pd.isna(rel):
                if str(trueVidIds[i]) in rel.split(' '):
                    count+=1
    acc = (count*100)/miss
    return [round(acc, 2), round(100-acc, 2)]

