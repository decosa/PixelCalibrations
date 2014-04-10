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
#  - fitVcalVcThr(ofile, savePlots): loop over the objects within the folder
#    and pick up the canvanses saved for each ROC, perform a fit to the Vcal(VcThr)
#    distribution and write down to an output file (ofile) the values of the Parameters
#    a and b and the chi2/NDF - Fit function => Vcal = a + b*VcThr
#    -- ofile: output file
#    -- savePlots: savePlots to plots folder, default is False
#    
#  - readHistoInfo(name): pick up the histogram corresponding to
#    the specified name and print Mean and RMS of the distribution
#    -- name: name of the histo
# **************************************************************************************



import sys
import os, commands
import ROOT
from array import array


def fitVcalVcThr(path,  savePlots):

    if not os.path.isfile(path + 'mapRocVcalVcThr.txt'):
        ofile = open(path + 'mapRocVcalVcThr.txt', 'w')
        ofile.write('='*60)    
        ofile.write('\nROC name                              a      b     chi2/NDF \n')
        ofile.write('='*60)
        ofile.write('\nVcal = a + b*VcThr \n')
        ofile.write('='*60)
    else: ofile = open(path + 'mapRocVcalVcThr.txt', 'a')
 
    for roc in ROOT.gDirectory.GetListOfKeys(): # ROCs, e.g.:  BmI_SEC4_LYR1_LDR5F_MOD1_ROC0
        cName =  roc.GetName()
        h = roc.ReadObj().GetPrimitive(cName)
        step = h.GetBinWidth(1)
        ### Fit range 
        VcThrMin = 40
        VcThrMax = 120    
        # define the two arrays VcThrs and Vcals,
        # the former storing the values of VcThr to consider 
        # and the latter the corresponding Vcal values
        
        VcThrs = range(VcThrMin, VcThrMax, int(step))
        Vcals  = [] 
        
    
        for VcThr in VcThrs:
            bin = h.GetXaxis().FindBin(VcThr)
            h_Vcal = h.ProjectionY("Vcal", bin, bin)
            firstBin = h_Vcal.FindFirstBinAbove(0.5)
            Vcals.append(h_Vcal.GetBinCenter(firstBin))
        
        VcThrArray = array('f', VcThrs)
        VcalArray = array('f', Vcals)
        VcThrVcal_graph = ROOT.TGraph( len(VcThrArray), VcThrArray, VcalArray)
        
        VcThrVcal_graph.Fit("pol1", "Q")
        VcThrVcal_graph.SetTitle(cName)
        VcThrVcal_graph.GetXaxis().SetTitle("VcThr")
        VcThrVcal_graph.GetYaxis().SetTitle("Vcal")
        
        fitRes = VcThrVcal_graph.GetFunction("pol1")
        
        ofile.write('\n%s   %.2f   %.2f   %.2f'%(cName, fitRes.GetParameter(0), fitRes.GetParameter(1), fitRes.GetChisquare()/fitRes.GetNDF(),))                      
    
        if(savePlots == 'True'):
            if(not os.path.isdir("plots")): os.system('mkdir plots')
            c = ROOT.TCanvas(cName+'_fit')
            c.cd()
            VcThrVcal_graph.Draw("A*")
            c.Print("plots/" + cName+".pdf")



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



