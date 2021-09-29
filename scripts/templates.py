pp_template='''#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
tar xzf tarball.tgz
cd CMSSW_10_6_14/src/PhysicsTools/NanoAODTools/scripts
eval `scramv1 runtime -sh`
python condor_pp.py $*
'''

pp_condor = """universe              = vanilla
executable            = EXEC
output                = OUTPUT/output_$(Process).out
error                 = OUTPUT/output_$(Process).err
log                   = OUTPUT/output_$(Process).log
+JobFlavour           = "QUEUE"
Arguments = "$(args)"
transfer_input_files = tarball.tgz
use_x509userproxy = true
Queue args from ARGFILE
queue
"""