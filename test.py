#!/usr/bin/env python

# ************************************************
#
#  Author: Annapaola de Cosa
#          decosa@cern.ch
#          March/2014
#
#  VcThrVcalRel.py
#  Usage: VcThrVcalRel.py -r runNum
#  Description:
#
# *************************************************



import sys
import os, commands
import ROOT
from array import array
import optparse 
from browseCalibFiles import *
from analysisCalibFuncs import *
usage = 'usage: %prog -r runNum'
parser = optparse.OptionParser(usage)
parser.add_option('-r', '--run', dest='run', type='int', help='Number of the run to analyze')
parser.add_option('-i', '--iter', dest='iter', type='int', help='Iteration')
parser.add_option('-k', '--key', dest='key', type='int', help='Starting Key Number')
parser.add_option('-s', '--savePlots', dest='savePlots', default='False', help='Set this flag to True to save fits to graphs as pdf')
(opt, args) = parser.parse_args()
sys.argv.append('-b')


if opt.run is None:
    parser.error('Please define the run number')
elif opt.iter is None:
    parser.error('Please define the iteration number')
elif (opt.iter == 0 and opt.key is None):
    parser.error('Please indicate the key number from which starting the procedure')

print sys.argv[0]

runDir = os.environ['POS_OUTPUT_DIRS']
path = '%s/Run_%s/Run_%d/'%(runDir, runfolder(opt.run), opt.run)
print path

filename = '2DEfficiency'
if(opt.iter != 0): filename = 'SCurve'

files = [ path + file for file in os.listdir(path) if file.startswith(filename) and file.endswith("root")]
print files
if len(files)<1:
    sys.exit('Could not find ', filename, ' file')
else: 

    if(opt.iter==0):
        browseROCChain(files, fitVcalVcThr, opt.savePlots)
        initThresholdMinimizationSCurve(opt.key, opt.iter)
    else:
        browseROCChain(files, checkROCthr, path, opt.iter)
        createNewDACsettings(path, opt.iter)

    
    #initDacSettings()


    #   ofile = open('testSCurve.txt', 'w')
    #   browseFolder(files, "Summaries", readHistoInfo, "RmsThreshold")
    
    #   browseFolder(files, "Summaries", dummy, ofile, "RmsThreshold")
    
    
    #    browsePixChain(files, getSCurveResults, ofile)
    # 
    


