#!/usr/bin/env python

# *************************************************************************************
#                                
#  Author: Annapaola de Cosa
#          decosa@cern.ch
#          March/2014
#
#  analysisCalibFuncs.py
#  Description: Collection of utility functions for the analysis
#  of calibration-result files.   
#  
#  - fitVcalVcThr(path, savePlots): loop over the objects within the folder
#    and pick up the canvanses saved for each ROC, perform a fit to the Vcal(VcThr)
#    distribution and write down to an output file (ofile) the values of the Parameters
#    a and b and the chi2/NDF - Fit function => Vcal = a + b*VcThr
#    -- path: position of the output file. No need to specify the name of the file,
#       if it does not exist it will be created in the run folder, if it does already
#       it will be just updated (new info appended to the file).
#    -- savePlots: savePlots to plots folder, default is False
#
#  - checkROCthr(path): pick up the threshold histogram ("Threshold1D") for each ROC
#    and check whether the mean is less than 35, in this case flag the ROC as failing
#    and add it to the list of failing ROCs in the output file
#    -- path: position of the output file. No need to specify the name of the file,
#       if it does not exist it will be created in the run folder, if it does already
#       it will be just updated (new info appended to the file).
#
#  - readHistoInfo(name): pick up the histogram corresponding to
#    the specified name and print Mean and RMS of the distribution
#    -- name: name of the histo
# **************************************************************************************



import sys
import os, commands
import ROOT
from array import array



#dacdir      = os.environ['PIXELCONFIGURATIONBASE']+'/dac'
confpath    = "Run_1000/configurations.txt"

def fitVcalVcThr(path,  savePlots):
    failingRocs = 0 
    if not os.path.isfile(path + 'mapRocVcalVcThr.txt'):
        ofile = open(path + 'mapRocVcalVcThr.txt', 'w')
        ofile.write('='*60)    
        ofile.write('\nROC name                              a      b     chi2/NDF \n')
        ofile.write('='*60)
        ofile.write('\nVcThr = a + b*Vcal \n')
        ofile.write('='*60)
    else: ofile = open(path + 'mapRocVcalVcThr.txt', 'a')
 
    for roc in ROOT.gDirectory.GetListOfKeys(): # ROCs, e.g.:  BmI_SEC4_LYR1_LDR5F_MOD1_ROC0
        cName =  roc.GetName()
        h = roc.ReadObj().GetPrimitive(cName)
        step = h.GetYaxis().GetBinWidth(1)
        ### Fit range 
        VcalMin = 35
        VcalMax = 110    
        # define the two arrays VcThrs and Vcals,
        # the former storing the values of VcThr to consider 
        # and the latter the corresponding Vcal values
        
        Vcals = range(VcalMin, VcalMax, int(step))
        VcThrs  = [] 
        
        for Vcal in Vcals:
            bin = h.GetYaxis().FindBin(Vcal)
            h_VcThr= h.ProjectionX("VcThr", bin, bin)
            firstBin = h_VcThr.FindFirstBinAbove(0.4)
            VcThrs.append(h_VcThr.GetBinCenter(firstBin))
        
        VcThrArray = array('f', VcThrs)
        VcalArray = array('f', Vcals)
        VcThrVcal_graph = ROOT.TGraph( len(VcalArray), VcalArray, VcThrArray)
        VcThrVcal_graph.Fit("pol1", "Q")
        VcThrVcal_graph.SetTitle(cName)
        VcThrVcal_graph.GetXaxis().SetTitle("Vcal")
        VcThrVcal_graph.GetYaxis().SetTitle("VcThr")
        fitRes = VcThrVcal_graph.GetFunction("pol1")
        
        ofile.write('\n%s   %.2f   %.2f   %.2f'%(cName, fitRes.GetParameter(0), fitRes.GetParameter(1), fitRes.GetChisquare()/fitRes.GetNDF(),))                      
        if(fitRes.GetChisquare()/fitRes.GetNDF() > 10.): failingRocs = failingRocs + 1
        if(savePlots == 'True'):
            if(not os.path.isdir("plots")): os.system('mkdir plots')
            c = ROOT.TCanvas(cName+'_fit')
            c.cd()
            VcThrVcal_graph.Draw("A*")
            c.Print("plots/" + cName+".pdf")
    if(failingRocs > 0): print failingRocs, "failing ROCs in module: ", cName


def checkROCthr(path):
    filename = path + 'FailingROCs.txt'    
    if not os.path.isfile(filename):
        ofile = open(filename, 'w')
        print "File ", filename, " does not exist. Creating a new one "
        ofile.write('='*60)    
        ofile.write('FalingROC name                              ThrMean      ThrRMS     \n')
        ofile.write('='*60)    
    else:
      ofile = open(filename, 'a')

    for roc in ROOT.gDirectory.GetListOfKeys(): # ROCs, e.g.:  BmI_SEC4_LYR1_LDR5F_MOD1_ROC0
        name =  roc.GetName()
        if(name.endswith("Threshold1D")):
            h = roc.ReadObj()
            #print "ROC Name: ", name.strip("_Threshold1D")
            #print "ROC Mean: %.2f"%(h.GetMean())
            if(h.GetMean()<35): 
                ofile.write('\n%s  %.2f  %.2f'%(name.replace("_Threshold1D", ""), h.GetMean(), h.GetRMS()) )
                print "ROC Name: ", name

def readHistoInfo(name):
    a =    ROOT.gDirectory.Get(name)
    print a.GetTitle()
    print "RMS   Mean"
    print  '%.2f  %.2f'%(a.GetRMS(), a.GetMean())
    return a



def createNewDACsettings(path):
    filename = path + 'PixelConfigurationKey.txt'    
    key, dac = 0, 0

    # Open the file and look for the key 
    try: 
        f = open(filename, 'r')
    except IOError:
        print "Cannot open file ", filename
    else:
        lines = f.readlines()
        key = lines[1].split()[-1]
        print key 
        # Open the configuration file and look for the key 
        try: 
           cfg = open(confpath)
            
        except IOError:
            print "Cannot open ", confpath

        else:
            while True:
                l = cfg.readline()
                if(l.startswith("key")):
                    if(l.split()[1] == str(key) ):
                        pos = cfg.tell()
                        print pos
                        break
                    
            cfg.seek(pos)
            while True:
                l = cfg.readline()
                if(l.startswith("dac")):
                    dac = l.split()[1]
                if(l.startswith("calib")):
                    calib = l.split()[1]

                    break
            print "dummy"
            print "key ",key
            print "dac ",dac
            print "calib ",calib
                    
#            cfg.seek(pos)

   

        
        

