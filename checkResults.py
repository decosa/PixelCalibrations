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
import optparse 


usage = 'usage: %prog -i iteration'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--iter', dest='iter', type='int', help='Iteration')
(opt, args) = parser.parse_args()
sys.argv.append('-b')


if opt.iter is None:
    parser.error('Please define the iteration number')



print sys.argv[0]


cmd_0 = 'grep \" 0\" delta_%d.txt | wc -l'%(opt.iter)
cmd_m4 = 'grep \" -4\" delta_%d.txt | wc -l'%(opt.iter)
cmd_2 = 'grep \" 2\" delta_%d.txt | wc -l '%(opt.iter)
print cmd_0
os.system(cmd_0)
print cmd_m4
os.system(cmd_m4)
print cmd_2
os.system(cmd_2)

 

    


