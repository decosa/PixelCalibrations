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
import string


dacdir      = os.environ['PIXELCONFIGURATIONBASE'] +'/dac/'
confpath    = os.environ['PIXELCONFIGURATIONBASE'] +"/configurations.txt"
runpath    = os.environ['HOME'] +"/run/"


def fitVcalVcThr( savePlots):
    failingRocs = 0 
    if not os.path.isfile(runpath + 'mapRocVcalVcThr.txt'):
        ofile = open(runpath + 'mapRocVcalVcThr.txt', 'w')
        ofile.write('='*80)    
        ofile.write('\nROC name                              a      b     chi2/NDF   LowestThreshold \n')
        ofile.write('='*80)
        ofile.write('\nVcThr = a + b*Vcal \n')
        ofile.write('='*80)
    else: ofile = open(runpath + 'mapRocVcalVcThr.txt', 'a')
 
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
        minVcThr = []        
        for Vcal in Vcals:
            bin = h.GetYaxis().FindBin(Vcal)
            h_VcThr= h.ProjectionX("VcThr", bin, bin)
            firstBin = h_VcThr.FindFirstBinAbove(0.4)
            minVcThr.append( h_VcThr.GetBinCenter( h_VcThr.FindLastBinAbove(0.1) ) )
            VcThrs.append(h_VcThr.GetBinCenter(firstBin))
        
        VcThrArray = array('f', VcThrs)
        VcalArray = array('f', Vcals)
        VcThrVcal_graph = ROOT.TGraph( len(VcalArray), VcalArray, VcThrArray)
        VcThrVcal_graph.Fit("pol1", "Q")
        VcThrVcal_graph.SetTitle(cName)
        VcThrVcal_graph.GetXaxis().SetTitle("Vcal")
        VcThrVcal_graph.GetYaxis().SetTitle("VcThr")
        fitRes = VcThrVcal_graph.GetFunction("pol1")
        
        ofile.write('\n%s   %.2f   %.2f   %.2f   %d '%(cName, fitRes.GetParameter(0), fitRes.GetParameter(1), fitRes.GetChisquare()/fitRes.GetNDF(), min(minVcThr)))                      
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

    iter = 0
    filename = path + 'PixelConfigurationKey.txt'    
    key, dac = 0, 0
    # Open the PIxelConfigurationKey file and look for the key 
    try: 
        f = open(filename, 'r')
    except IOError:
        print "Cannot open file ", filename
    else:
        lines = f.readlines()
        key = lines[1].split()[-1]
        print key 

        dac = findDacFromKey(key)
        print "key ",key
        print "dac ",dac
        subdirs = [ int(x) for x in os.walk(dacdir).next()[1] ] 
        subdirs.sort()
        print 'Last dac dir : ', subdirs[-1]    
        lastsettings = subdirs[-1]
        newsettings = subdirs[-1]+1       
        newdir =  path + 'dac/' + str(newsettings) 

        os.makedirs(newdir)
        cmd_cpdac = 'cp -r ' + dacdir + dac + '/*' + newdir
        print cmd_cpdac
        failingRocs = getFailingRocs(path)
        orgdacpath = dacdir + dac

    #        createNewDacFiles(dacdir + dac , newdir, failingRocs)


        files = [ file for file in os.listdir(orgdacpath) if file.startswith("ROC_DAC")]
        # just for testing
        failingRocs = ["BPix_BpI_SEC1_LYR3_LDR2F_MOD1_ROC0"]
        initDACs =  initDacSettings()
        for f in files:
            newdacfile = open(newdir + '/'+f, 'w')
            openfile = open(orgdacpath + '/'+ f, 'r') 
            delta = 2
            
        for line in openfile.readlines():
            if (line.startswith("ROC")):
                if(iter == 0 and line.split()[1] in initDACs.keys()): newVcThr = initDACs[line.split()[1]] - delta 
                elif(iter == 0 and line.split()[1] not in initDACs.keys()): newVcThr = -1   
                else: 
                    if line.split()[1] in failingRocs:  delta = -4
                    else: delta = 2


            elif (line.startswith('VcThr') and newVcThr!= -1): 
                if(iter!=0): newVcThr = int(line.split()[1]) + delta                    
                line = string.replace(line, str(line.split()[1]), str(newVcThr))

            newdacfile.write(line)
        
        cmd_cpnewdac = 'cp -r ' + newdir + " " + dacdir 
        print cmd_cpnewdac
        os.system(cmd_cpnewdac)

#        createNewDacFiles(dacdir + dac , newdir, failingRocs)
        # --- Make the new dac the default
        #        cmd = 'PixelConfigDBCmd.exe --insertVersionAlias dac %d Default'%newsettings
   

def findDacFromKey(key):
    #find dac settings corresponding to the key used for this run

    #aliases = open(os.environ['PIXELCONFIGURATIONBASE']+'aliases.txt','r')
    #a = [item for item in aliases if item.startswith('PixelAlive     %s'%key)]
    #if len(a)<1:
    #    sys.exit('ERROR: incorrect key! Please check ')
    #else:
    #    aliases.seek(0)
    #    dac = [item.split()[1] for item in aliases if item.startswith('dac') ]

    dac = []
    #f =  open(os.environ['PIXELCONFIGURATIONBASE']+'/configurations.txt','r')
    #if(f): chunks = f.read().split('\n\n')

    with open(os.environ['PIXELCONFIGURATIONBASE']+'/configurations.txt','r') as f:
        chunks = f.read().split('\n\n')
    for c in chunks:
        config = c.split('\n')
        if 'key %s'%key in config:
            dac = [item.split()[1] for item in config if item.startswith('dac')]
    if len(dac)<1:
        sys.exit("Error: dac not found")
    print "Used key %s with dac %s"%(key,dac[0])
    return dac[0]

        
        
def getFailingRocs(path):
    filename = path + 'FailingROCs.txt'    
    try:
        ofile = open(filename, 'r')
    except IOError:
        print "Cannot open ", filename
    
    else:
        lines = ofile.readlines()
        print "Failing ROCs: ", len(lines)
        failrocs = [l.split()[0] for l in lines if l.split()[0].startswith("BPix")]
        print failrocs
        ofile.close()
        return failrocs

        
def createNewDacFiles(orgdacpath, newdacpath, failingRocs):
    files = [ file for file in os.listdir(orgdacpath) if file.startswith("ROC_DAC")]
    failingRocs = ["BPix_BpI_SEC1_LYR3_LDR2F_MOD1_ROC0"]
    for f in files:
        delta = 2
        newdacfile = open(newdacpath + '/'+f, 'w')
        openfile = open(orgdacpath + '/'+ f, 'r') 
        for line in openfile.readlines():
            if (line.startswith("ROC")):
                if line.split()[1] in failingRocs: 
                    print "Failing Roc"
                    delta = -4
                else: delta = 2
            elif line.startswith('VcThr'): 
                newVcThr = int(line.split()[1]) + delta                    
                line = string.replace(line, str(line.split()[1]), str(newVcThr))

            newdacfile.write(line)


def  initDacSettings():
    #    leggere mappa
    #    prendere l'ultimo valore e settare la dac di quella roc a quel valore -2

    filename = runpath + 'mapRocVcalVcThr.txt'    
    try:
        ofile = open(filename, 'r')
    except IOError:
        print "Cannot open ", filename
    
    else:
        rocDAC = {l.split()[0]:l.split()[4] for l in ofile.readlines() if l.split()[0].startswith("BPix")}
        ofile.close()
        return rocDAC

