#!/usr/bin/env python

import os, sys, re
from pathlib import Path
from templates import *
import json

def split_jobs(files, nFiles):
  for i in range(0, len(files), nFiles):
    yield files[i:i + nFiles]

def removeValidFiles(allFiles,sample,year,CR):
  nonProcessedFiles = []
  if CR:
    #inputJson = "validCRskims.json"
    inputJson = "validSingleEskims.json"
  else:
    inputJson = "validSkims.json"
  with open(inputJson, "r") as jsonFile:
    validDict = json.load(jsonFile)

  try:
    validFiles = validDict[year][sample]
    for file in allFiles:
      fileName  = file.split("/")[-1]
      fileName  = fileName.replace(".root","_pp.root")
      if fileName in validFiles:
        continue
      else:
        nonProcessedFiles.append(file)
    return nonProcessedFiles
    
  except:#if sample not in valid skims dict, process all files
    return allFiles





def create_jobs(config, queue='',year="2016",jobs_dir="",out_dir="",nFiles=10,CR=False):
    for sample, sample_cfg in config.items():
      
      sampleJobs_dir = os.path.join(jobs_dir,sample)
      sampleOut_dir = os.path.join(out_dir, sample)
      #Create dir to store jobs and dir to store output
      Path(os.path.join(sampleJobs_dir, 'input')).mkdir(parents=True, exist_ok=True)
      Path(os.path.join(sampleJobs_dir, 'output')).mkdir(parents=True, exist_ok=True)
      Path(sampleOut_dir).mkdir(parents=True, exist_ok=True)

      #Create condor file and sh file
      exeScript = pp_template
      open(os.path.join(sampleJobs_dir, 'input', 'run_{}.sh'.format(sample)), 'w').write(exeScript)

      condor_script = re.sub('EXEC',os.path.join(sampleJobs_dir, 'input', 'run_{}.sh'.format(sample)), pp_condor)
      condor_script = re.sub('ARGFILE',os.path.join(sampleJobs_dir, 'input', 'args_{}.txt'.format(sample)), condor_script)
      condor_script = re.sub('OUTPUT',os.path.join(sampleJobs_dir, 'output'), condor_script)
      condor_script = re.sub('QUEUE',queue, condor_script)
      open(os.path.join(sampleJobs_dir, 'input', 'condor_{}.condor'.format(sample)), 'w').write(condor_script)


      dataset = sample_cfg["dataset"]
      if dataset.split('/')[-1] == "USER":
        instance = 'prod/phys03'
      else:
        instance = 'prod/global'
      das_query=[]
      for singleDataset in dataset.split(','):
        query = "dasgoclient -query='file dataset={singleDataset} instance={instance}'".format(**locals())
        das_query.append(query)
      import subprocess
      allFiles = []
      for query in das_query:
        files = subprocess.check_output(das_query, shell=True).split()
        for file in files:
          allFiles.append(file.decode("utf-8"))

      allFiles = removeValidFiles(allFiles,sample,year,CR)
      if(len(allFiles)==0):
        print("All files in {0} processed".format(sample))
        continue
      job_list = split_jobs(allFiles, nFiles)

      #Create file with arguments to the python script
      argsFile = open(os.path.join(sampleJobs_dir, 'input', 'args_{}.txt'.format(sample)), 'w')
      for n, l  in enumerate(list(job_list)):
        inputPath = os.path.join(sampleJobs_dir, 'input', 'input_{}.txt'.format(n))
        #outputPath = os.path.join(sampleOut_dir,'{0}_{1}.root'.format(sample,n))
        open(inputPath, 'w').writelines("{}\n".format(root_file) for root_file in l)
        if(CR):
            argsFile.write("-i {0} -o {1} --CR\n".format(inputPath,sampleOut_dir))
        else:
            argsFile.write("-i {0} -o {1}\n".format(inputPath,sampleOut_dir))

      #Submit
      print("condor_submit {0}".format(os.path.join(sampleJobs_dir, 'input', 'condor_{}.condor'.format(sample))))


def main():

  import json
  
  from argparse import ArgumentParser
  parser = ArgumentParser(description="Do -h to see usage")

  parser.add_argument('-c', '--config', help='Job config file in JSON format')
  parser.add_argument('-o', '--outdir',help='Output directory')
  parser.add_argument('-j', '--jobdir',help='Jobs directory')
  parser.add_argument('-n', '--nFiles',help='number of files per job')
  parser.add_argument('-y', '--year',help='2016, 2017 or 2018')
  parser.add_argument("-q", "--queue", dest="queue", action='store', default='longlunch', help="Default is 'longlunch' (This parameter is optional)", metavar="QUEUE")
  parser.add_argument('--CR', action="store_true",dest="isCR",default=False)

  args = parser.parse_args()

  print(args)

  with open(args.config, 'r') as config_file:
    config = json.load(config_file)
    create_jobs(config,queue=args.queue,out_dir=args.outdir,jobs_dir=args.jobdir,nFiles=int(args.nFiles),year=args.year,CR=args.isCR)
          

      

if __name__ == "__main__":
  main()

