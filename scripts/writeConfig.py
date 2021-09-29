#!/usr/bin/env python

import os, sys, re
from pathlib import Path
import subprocess
import json


query       = "dasgoclient -query='dataset=/*/*mrogulji*/USER instance=prod/phys03'"
datasets    = subprocess.check_output(query, shell=True).split()
config      = "{\n"

for dataset in datasets:
    dataset = dataset.decode("utf-8")
    MX = dataset.split("_")[3]
    MY = dataset.split("_")[5]
    datasetName = '  "MX{0}_MY{1}": {{'.format(MX,MY)
    datasetPath = '    "dataset": "{0}"'.format(dataset)
    config+=datasetName+"\n"+datasetPath+"\n  },\n"
print(config)
config+="}"

f = open("skim_signal_2016.json", "w")
f.write(config)
f.close()