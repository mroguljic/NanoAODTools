import subprocess
import ROOT as r
import json
from optparse import OptionParser
import os
import collections
import sys

def parseBlacklistDirs(option, opt, value, parser):
  setattr(parser.values, option.dest, value.split(','))

def validateFile(fileName):
    runsTreeFlag = False
    evtTreeFlag  = False
    try:
        f = r.TFile.Open(fileName)
        evtTree = f.Get("Events")
        nEvt    = evtTree.GetEntriesFast()
        if(nEvt>1):
            evtTreeFlag = True
        runTree = f.Get("Runs")
        nRun    = evtTree.GetEntriesFast()
        if(nRun>0):
            runsTreeFlag = True
        f.Close()
    except:
        return 0

    if(runsTreeFlag and evtTreeFlag):
        return 1



parser = OptionParser()
parser.add_option('-d', '--dir',help="Directory with samples to analyze")
parser.add_option('-j', '--json',help="Output json file")
parser.add_option('-s', '--skipDirs',type='string',action='callback',callback=parseBlacklistDirs,help="Comma-separated list of keywords to skip")

(options,args) = parser.parse_args()
print(options.dir)
print(options.skipDirs)

if("2016" in options.dir):
    year = "2016"
elif("2017" in options.dir):
    year = "2017"
elif("2018" in options.dir):
    year = "2018"
else:
    print("Couldn't find year in directory name")
    sys.exit()


if os.path.exists(options.json):
    with open(options.json, "r") as jsonFile:
        outDict = json.load(jsonFile)
        outDict = collections.defaultdict(dict,outDict)
else:
    outDict = collections.defaultdict(dict)


sampleDirs = os.listdir(options.dir)
for sampleDir in sampleDirs:
    invalidCounter = 0
    if any(s in sampleDir for s in options.skipDirs):
        continue
    print(sampleDir)
    validFiles = []
    tempDir    = os.path.join(options.dir,sampleDir)
    tempFiles  = os.listdir(tempDir)
    for file in tempFiles:
        fileStatus = validateFile(os.path.join(tempDir,file))
        if fileStatus==1:
            validFiles.append(file)
        else:
            invalidCounter+=1
    if(invalidCounter!=0):
        print("Invalid files: {0}".format(invalidCounter))
    outDict[year][sampleDir] = validFiles

with open(options.json, 'w') as fp:
    json.dump(outDict, fp,indent=2)