#!/usr/bin/env python

# **************************************************************************************
#
#  Author: Annapaola de Cosa
#          decosa@cern.ch
#          November 2014
#
#  Note: Function to check PixelAlive results originally developed by Martina Malberti
#        and adapted for usage outside Threshold minimization procedure with PixelAlive
#
#  Description: Script to run last step of SCurve  Threshold Minimization
#               with PixelAliveAllEnabled
#
#  Usage: python PixelAlive.py -r 'PixelAliveRunNumber' -i iter --makeNewDac True
#         Iteration number must start from 1
#
# **************************************************************************************



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
#parser.add_option('-d', '--dac', dest='dac', type='int', help='Starting dac Number')
parser.add_option('-s', '--savePlots', dest='savePlots', default='False', help='Set this flag to True to save fits to graphs as pdf')
parser.add_option("-m","--modality",dest="mod",type="string",default="increase",help="Modality of dac setting: \"minimize\" for minimizing thresholds and \"increase\" to only increase thresholds of failing rocs. Default is \"increase\"")
parser.add_option("-o","--outputFile",dest="output",type="string",default="failedAlive",help="Name of the output file containing the list of failing rocs. Default is failed.txt")
parser.add_option("-d","--deltaFile",dest="delta",type="string",default="deltaAlive",help="Name of the output file containing the deltaVcThr. Default is delta.txt")
parser.add_option("-e","--exclude",dest="exclude",type="string",default="",help="List of the ROCs you want to exclude from the iterative procedure")
parser.add_option("","--skipFPix",dest="skipFPix",default=False,action="store_true",help="Skip FPix")
parser.add_option("","--skipBPix",dest="skipBPix",default=False,action="store_true",help="Skip BPix")
parser.add_option("","--makeNewDac",dest="makeNewDac",type="int",default=0,help="If 1, new dac is created. Default is 0.")
parser.add_option("","--maxDeadPixels",dest="maxDeadPixels",type="int",default=10,help="Maximum number of dead pixels per ROC. Default is 10.")


(opt, args) = parser.parse_args()
sys.argv.append('-b')


if opt.run is None:
    parser.error('Please define the run number')
elif opt.iter is None:
    parser.error('Please define the iteration number')
elif opt.iter is 0:
    parser.error('First iteration must be 1 and not 0')



print sys.argv[0]

#runDir = os.environ['POS_OUTPUT_DIRS']
path = '%s/Run_%s/Run_%d/'%(runDir, runfolder(opt.run), opt.run)
print "Current directory is ", os.getcwd()
print "Directory to analyze is ", path


filename = "PixelAlive"
files = []

## Iterations with PixelAlive
cmdrm = ('rm '+os.getcwd()+ '/'+opt.output+'_'+str(opt.iter)+'.txt' )
print cmdrm
os.system(cmdrm)
cmdrm = ('rm '+os.getcwd()+ '/'+opt.delta+'_'+str(opt.iter)+'.txt' )
print cmdrm
os.system(cmdrm)
print path

# --- Analyze PixelAlive run
#RunPixelAliveAnalysis(opt.run)


# --- Check the efficiency of all ROCS and make a list of failed rocs (i.e. rocs with more than maxDeadPixels pixels)
#print os.listdir(path) 
files = [ path + file for file in os.listdir(path) if file.startswith(filename) and file.endswith("root")]
if len(files)<1:
    sys.exit('Could not find ', filename, ' file')
else: 
    CheckEfficiency(files, opt.output, opt.iter, opt.maxDeadPixels,opt.skipFPix, opt.skipBPix, opt.exclude)
    # --- Prepare new dac settings (change VcThr)
    createNewDACsettings(path, opt.iter, opt.delta, opt.output, opt.mod, opt.makeNewDac)


if(opt.makeNewDac==0): print "N.B: new dac settings were not saved -> set makeNewDac to ture if you want to save them"

    


    


