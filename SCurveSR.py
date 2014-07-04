#!/usr/bin/env python

# **********************************************************
#
#  Author: Annapaola de Cosa
#          decosa@cern.ch
#          March/2014
#
#  test.py
#  Usage: test.py -r runNum -i iter -k key 
#  Description: Script to run Threshold Minimization
#               Procedure with SCurveCustomRange
#
#  Iteration 0: python test.py -r 'runVcThrVcal' -i 0 -d dac 
# **********************************************************



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
parser.add_option('-d', '--dac', dest='dac', type='int', help='Starting dac Number')
parser.add_option('-s', '--savePlots', dest='savePlots', default='False', help='Set this flag to True to save fits to graphs as pdf')
(opt, args) = parser.parse_args()
sys.argv.append('-b')


if opt.run is None:
    parser.error('Please define the run number')
elif opt.iter is None:
    parser.error('Please define the iteration number')



print sys.argv[0]

#runDir = os.environ['POS_OUTPUT_DIRS']
path = '%s/Run_%s/Run_%d/'%(runDir, runfolder(opt.run), opt.run)
print "Current directory is ", os.getcwd()
print "Directory to analyze is ", path

filename = '2DEfficiency'
if(opt.iter != 0): filename = 'SCurve'
files = []

##First iteration creates the map VcThr-Vcal
if(opt.iter==0):
    cmdrm = ('rm '+ runpath + 'mapRocVcalVcThr.txt')
    print cmdrm
    os.system(cmdrm)
    files = [ path + file for file in os.listdir(path) if file.startswith(filename) and file.endswith("root")]
    if len(files)<1:
        sys.exit('Could not find ', filename, ' file')
    else: 
        browseROCChain(files, fitVcalVcThr, opt.savePlots)
        #initThresholdMinimizationSCurve(path, opt.iter)

elif(opt.iter==100):
    print 'Creating newROCList'
    createROCList(path)
## Iterations with SCurveSR
else:
    cmdrm = ('rm '+os.getcwd()+ '/failed_'+str(opt.iter)+'.txt' )
    print cmdrm
    os.system(cmdrm)
    cmdrm = ('rm '+os.getcwd()+ '/delta_'+str(opt.iter)+'.txt' )
    print cmdrm
    os.system(cmdrm)
    print path
    
    RunSCurveSmartRangeAnalysis(opt.run)
    print os.listdir(path) 
    files = [ path + file for file in os.listdir(path) if file.startswith(filename) and file.endswith("root")]
    if len(files)<1:
        sys.exit('Could not find ', filename, ' file')
    else: 
        browseROCChain(files, checkROCthr, path, opt.iter)
        createNewDACsettings(path, opt.iter)


    


