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
parser.add_option('-s', '--savePlots', dest='savePlots', default='False', help='Set this flag to True to save fits to graphs as pdf')
(opt, args) = parser.parse_args()
sys.argv.append('-b')


if opt.run is None:
    parser.error('Please define the run number')


print sys.argv[0]

runDir = os.environ['POS_OUTPUT_DIRS']


path = '%s/Run_%s/Run_%d/'%(runDir, runfolder(opt.run), opt.run)
print path

filename = 'SCurve'
filename = '2DEfficiency'
files = [ path+ file for file in os.listdir(path) if file.startswith(filename)]
print files
if len(files)<1:
    sys.exit('Could not find ', filename, ' file')
else: 

    #    if os.path.isfile(path + 'mapRocVcalVcThr.txt'):
 #   ofile = open(path + 'mapRocVcalVcThr.txt', 'a')


#    mapRocVcalVcThr = open('mapRocVcalVcThr.txt', 'w')
#    mapRocVcalVcThr.write('\nROC name                              a      b     chi2/NDF \n')
#    mapRocVcalVcThr.write('='*60)
#    mapRocVcalVcThr.write('\nVcal = a + b*VcThr \n')
#    mapRocVcalVcThr.write('='*60)

#   ofile = open('testSCurve.txt', 'w')
#   browseFolder(files, "Summaries", readHistoInfo, "RmsThreshold")

#   browseFolder(files, "Summaries", dummy, ofile, "RmsThreshold")

 
#    browsePixChain(files, getSCurveResults, ofile)
#    browseROCChain(files, fitVcalVcThr, path, opt.savePlots)
    browseROCChain(files, checkROCthr, path)



#    mapRocVcalVcThr.write('\n')
#    mapRocVcalVcThr.close()
