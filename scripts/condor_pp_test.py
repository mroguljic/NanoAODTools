#!/usr/bin/env python
import os, sys, math, subprocess, fnmatch, tempfile
from optparse import OptionParser

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 

#this takes care of converting the input files from CRAB
#from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *#UncertaintiesFactorized import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *

parser = OptionParser()

parser.add_option('-i', '--input', metavar='IFILE', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='OFILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('--CR', action="store_true",dest="isCR",default=False)




(options, args) = parser.parse_args()
if(".txt" in options.input):
  files = open(options.input,"r").read().splitlines()
else:
  files = [options.input]

if("UL201" in files[0] or "UL1" in files[0]):
    ULflag = True
else:
    ULflag = False

if("2016" in files[0]):
    year = "2016"
elif("2017" in files[0]):
    year = "2017"
elif("2018" in files[0]):
    year = "2018"    
else:
    print("Couldn't read year from inputfile")


if(ULflag):
    year = "UL"+year

if("JetHT" in files[0] or "SingleMuon" in files[0]):
    isMC = False
    period = "B"
else:
    isMC = True
    period = False
new_list = []
tempfolder = tempfile.mkdtemp()
for f in files:
    file_name = f.split('/')[-1]
    full_path = file_name
    #print('xrdcp '+full_path+' '+tempfolder+'/'+file_name)
    #subprocess.call('xrdcp '+full_path+' '+tempfolder+'/'+file_name,shell=True)
    #new_list.append(file_name)
    new_list.append(full_path)

print(new_list)

print("MC {0}, year {1}, period {2}".format(isMC,year,period))

correctorAK8 = createJMECorrector(isMC=isMC,
                               dataYear=year,
                               runPeriod=period,
                               jetType="AK8PFPuppi")

correctorAK4 = createJMECorrector(isMC=isMC,
                               dataYear=year,
                               runPeriod=period,
                               jetType="AK4PFchs")

if(options.isCR):
    mymodules = [correctorAK8(),correctorAK4()]
    print("AK8 and AK4 correctors")
else:
    mymodules = [correctorAK8()]
    print("AK8 corrector")

cutstring1 = '(FatJet_pt[0]>300)&&(abs(FatJet_eta[0])<2.5) && (FatJet_pt[1]>300) && (abs(FatJet_eta[1])<2.5)'#hadronic selection
cutstring2 = '(FatJet_pt[0]>400)&&(abs(FatJet_eta[0])<2.5) && (FatJet_msoftdrop[0]>30)'#sf measurement
cutstring3 = 'nFatJet>0 && (nElectron>0 || nMuon>0)'#semileptonic cr
#semileptonic cut didn't include FatJet_pt cut

if(options.isCR):
  cutstring = cutstring3
else:
  cutstring = '('+cutstring1+') || ('+cutstring2+')'



p=PostProcessor("./",new_list,cutstring,
                modules=mymodules,
                provenance=True,
                postfix="_pp",
                outputbranchsel='keep_and_drop_out.txt')

p.run()

print("Modules check = "+str(mymodules))
# rm_cmd = "rm *root"#removing input and postprocessed file from worker node
# print(rm_cmd)
# os.system(rm_cmd)

print "DONE"



