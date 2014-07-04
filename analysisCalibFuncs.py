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
#import io
import time
import subprocess
import ROOT
from array import array
import string
from browseCalibFiles import *

dacdir      = os.environ['PIXELCONFIGURATIONBASE'] +'/dac/'
detconfigdir      = os.environ['PIXELCONFIGURATIONBASE'] +'/detconfig/'
confpath    = os.environ['PIXELCONFIGURATIONBASE'] +"/configurations.txt"
runpath     = os.environ['HOME'] + '/run/'
runDir    = os.environ['POS_OUTPUT_DIRS']
pixelAnalysisExe   = os.environ['BUILD_HOME'] + '/pixel/PixelAnalysisTools/test/bin/linux/i386_slc5/PixelAnalysis.exe'
config             = runDir + '/SCurveAnalysis_bpix_one.xml'



def RunSCurveSmartRangeAnalysis(run):
    path = '%s/Run_%s/Run_%d/'%(runDir, runfolder(run), run)
    filename = 'SCurve'
    filelist = [ path + file for file in os.listdir(path) if file.startswith(filename) and file.endswith(".dmp")]
    newfiles = [f.replace('SCurveSmartRange', 'SCurve') for f in filelist]
    for i in xrange(len(filelist)):
        cmdcp = "cp %s %s"%(filelist[i], newfiles[i])
        os.system(cmdcp) 
    
    print "\n=======> Running SCurve Analysis <=======\n"
    cmd = '%s %s %d'%(pixelAnalysisExe, config, run)
    print cmd
    #with io.open("scurve.log", 'wb') as writer:
    writer =open("scurve.log", 'w') 
    process = subprocess.call(cmd, shell = True, stdout=writer)
    cmdrm = ('rm '+ runpath + 'mapRocOffset.txt')
    print cmdrm
    os.system(cmdrm)
    

def fitVcalVcThr( savePlots):
    failingRocs = 0 
    if not os.path.isfile(runpath + 'mapRocVcalVcThr.txt'):
        print "Saving New  Vcal VcThr map in ",runpath + 'mapRocVcalVcThr.txt'
        ofile = open(runpath + 'mapRocVcalVcThr.txt', 'w')
        ofile.write('='*80)    
        ofile.write('\nROC name                              a      b     chi2/NDF   LowestThreshold \n')
        ofile.write('='*80)
        ofile.write('\nVcThr = a + b*Vcal \n')
        ofile.write('='*80)
    else:
        ofile = open(runpath + 'mapRocVcalVcThr.txt', 'a')

    for roc in ROOT.gDirectory.GetListOfKeys(): # ROCs, e.g.:  BmI_SEC4_LYR1_LDR5F_MOD1_ROC0
        cName =  roc.GetName()
        h = roc.ReadObj().GetPrimitive(cName)
        step = h.GetYaxis().GetBinWidth(1)
        ### Fit range for intime WBC 
        VcalMin = 50
        VcalMax = 140    

        ### Fit range for next WBC 
        #VcalMin = 35
        #VcalMax = 110    


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
            minVcThr.append( h_VcThr.GetBinCenter( h_VcThr.FindLastBinAbove(0.9) ) )
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
    if(failingRocs > 0): print "There were ", failingRocs, " failing ROCs in module: ", cName


### The following functions look into the SCurve results and check for each ROCs
###if there are failing onces. For the moment a Threshold is defined failing only if the mean threshold is
###less than 35. Creates a file named failed_N.txt where failing ROCs are listed. N is the number
###of iteration 


def checkROCthr(path, iteration):
    filename = "failed_%d.txt"%(iteration)
    if not os.path.isfile(filename):
        ofile = open(filename,'w')
        print "File ", filename, " does not exist. Creating a new one "
        ofile.write('='*60)    
        ofile.write('\nFalingROC name                              ThrMean      ThrRMS     \n')
        ofile.write('='*60)    
    else:
      ofile = open(filename, 'a')

    for roc in ROOT.gDirectory.GetListOfKeys(): # ROCs, e.g.:  BmI_SEC4_LYR1_LDR5F_MOD1_ROC0
        name =  roc.GetName()
        rocname =  name.strip("_Threshold1D")
        if(name.endswith("Threshold1D")):
            h = roc.ReadObj()
            #print "ROC Name: ", name
            #print "ROC Mean: %.2f"%(h.GetMean())
            nPixelsOutRange = h.Integral(0, h.FindBin(30)) + h.Integral( h.FindBin(120), h.GetNbinsX()+2) 
            
            if(h.GetMean()<35 or nPixelsOutRange >2):
                ofile.write('\n%s  %.2f  %.2f'%(rocname, h.GetMean(), h.GetRMS()) )
            else: continue

            if(h.GetMean()<35):
                print "ROC failing because of mean Thr <35: ", rocname
            elif(nPixelsOutRange >2):
                print "ROC failing because pixel Thr out of range: ", rocname
                print "Number of bad pixels: " , nPixelsOutRange

def readHistoInfo(name):
    a =    ROOT.gDirectory.Get(name)
    print a.GetTitle()
    print "RMS   Mean"
    print  '%.2f  %.2f'%(a.GetRMS(), a.GetMean())
    return a


def findDetConfigFromPath(path):
    
    filename = path + 'PixelConfigurationKey.txt'    
    key, detconfig = 0, 0
    # Open the PIxelConfigurationKey file and look for the key 
    try: 
        f = open(filename, 'r')
    except IOError:
        print "Cannot open file ", filename
    else:
        lines = f.readlines()
        key = lines[1].split()[-1]
        #print key 
        detconfig = findDetConfigFromKey(key)
    return detconfig


### Create new dac settings staring from the key and so the dac number used for
###the current Calibration. It checks if there are failing ROCs, and for those
###increases the threshold of 2 units. It would be possible to add a check on the previous
###iterations, but let s keep this for a second moment. 

def findDacFromPath(path):
    
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
        #print key 
        dac = findDacFromKey(key)
    return dac

def listFromFile(filepath):
    f =open(filepath)
    flist = f.readlines()[1:]
    flist = [l.replace(" \n", "") for l in flist] 
    return flist

def createROCList(path):
    detconfig = findDetConfigFromPath(path)
    if(detconfig!=0):
        detconfiglist =listFromFile(detconfigdir + str(detconfig) + "/detectconfig.dat")
        #print detconfigfile
        #detconfiglist = detconfigfile.readlines()[1:]
        #detconfiglist = [l.replace(" \n", "") for l in detconfiglist] 
        #print detconfiglist
        return detconfiglist
        
def createNewDACsettings(path, iteration):
    detconfiglist = createROCList(path)
    minimizedROCs = []
    if(iteration>1): minimizedROCs = listFromFile("failed_%d.txt"%(iteration-1))
    minimizedROCs = [l.split()[0] for l in minimizedROCs if (l.startswith("BPix") or l.startswith("FPix"))]
    print "ROCs already fixed ", minimizedROCs
    dac = findDacFromPath(path)
    if(dac!=0):
        subdirs = [ int(x) for x in os.walk(dacdir).next()[1] ] 
        subdirs.sort()
        print 'Last dac dir: ', subdirs[-1]    
        lastsettings = subdirs[-1]
        newsettings = subdirs[-1]+1       
        newdir =  os.getcwd() +  '/ThresholdMinimization/dac/' + str(newsettings)
        os.makedirs(newdir)
        os.makedirs(dacdir + str(newsettings))
        cmd_cpdac = 'cp -r ' + dacdir + str(dac) + '/* ' + dacdir + str(newsettings)
        #        cmd_cpdac = 'cp -r ' + dacdir + dac + '/* ' + newdir
        print cmd_cpdac
        os.system(cmd_cpdac)
        failingRocs = getFailingRocs(path, iteration)
        #        failingRocs = ["BPix_BmI_SEC4_LYR1_LDR5F_MOD1_ROC0"]
        orgdacpath = dacdir + dac
        files = [ file for file in os.listdir(orgdacpath) if file.startswith("ROC_DAC")]
        # just for testing
        deltafilenew = open("delta_%d.txt"%(iteration),'a')
        
        for f in files:
            newdacfile = open(newdir + '/'+f, 'w')
            openfile = open(orgdacpath + '/'+ f, 'r') 
            delta = 0
            
            for line in openfile.readlines():
                if (line.startswith("ROC")):
                    #if line.split()[1].startswith("BPix_BmI_SEC4"): print line
                    rocname = line.split()[1]
                    if(rocname in detconfiglist):
                        if(rocname in minimizedROCs):
                            delta = 0 
                        elif(rocname in failingRocs):
                            delta = -4 # decrease VcThr of 4 units making the threshold higher   
                        else:
                            delta = +2 # lower the threshold

                        deltafilenew.write('%s %d\n'%(rocname,delta))
                        
                    else: delta =0
                    
                        
                elif (line.startswith('VcThr') ): 
                    newVcThr = int(line.split()[1]) + delta
                    #print "old dac: ", line.split()[1]
                    #print "new dac: ", newVcThr
                    #print "old line: ",line
                    line = string.replace(line, str(line.split()[1]), str(newVcThr))
                    #print "new line: ",line
                                        
                newdacfile.write(line)
                


        cmd_cpnewdac = 'cp -r ' + newdir + " " + dacdir 
        print cmd_cpnewdac
        os.system(cmd_cpnewdac)
        
        # --- Make the new dac the default
        cmd = 'PixelConfigDBCmd.exe --insertVersionAlias dac %d Default'%newsettings
        print cmd
        print "New DAC settings dir: dac/%d"%newsettings
        #        print "N.B: NEW DAC not set as default, do it by hand"
        os.system(cmd)


### Initialize DAC settings, set VcThr for each ROC at the value found 
### by the VcThrVcal mapping function and increase it by 2 units.
#def initThresholdMinimizationSCurve(key, iteration):
def initThresholdMinimizationSCurve(path, iteration):
    dac = findDacFromPath(path)
    if(dac!=0):
        subdirs = [ int(x) for x in os.walk(dacdir).next()[1] ] 
        subdirs.sort()
        print 'Last dac dir: ', subdirs[-1]    
        lastsettings = subdirs[-1]
        newsettings = subdirs[-1]+1       
        newdir =  os.getcwd() +  '/ThresholdMinimization/dac/' + str(newsettings) 
        print newdir
        os.makedirs(newdir)
        os.makedirs(dacdir + str(newsettings))
        cmd_cpdac = 'cp -r ' + dacdir + str(dac) + '/* ' + dacdir + str(newsettings)
        print cmd_cpdac
        os.system(cmd_cpdac)
        orgdacpath = dacdir + str(dac)
        
        files = [ file for file in os.listdir(orgdacpath) if file.startswith("ROC_DAC")]
        initDACs =  initDacSettings()
        delta = -2
        for f in files:
            newdacfile = open(newdir + '/'+f, 'w')
            openfile = open(orgdacpath + '/'+ f, 'r') 
            newVcThr = 0
            for line in openfile.readlines():
                #                if(line.split()[1].startswith("BPix_BmI_SEC4")): print 'ROC name:', line.split()[1]

                if (line.startswith("ROC")):
                    if(line.split()[1] in initDACs.keys()): 
                        newVcThr = int(initDACs[line.split()[1]]) + delta 

                elif (line.startswith('VcThr')): 
                    if (newVcThr !=0):line = string.replace(line, str(line.split()[1]), str(newVcThr))
                    newVcThr = 0      
         
                newdacfile.write(line)
        
        cmd_cpnewdac = 'cp ' + newdir + "/*.dat " + dacdir + str(newsettings)
        print cmd_cpnewdac
        os.system(cmd_cpnewdac)
        
        # --- Make the new dac the default
        cmd = 'PixelConfigDBCmd.exe --insertVersionAlias dac %d Default'%newsettings
        print cmd
        
        print "New DAC settings dir: dac/%d"%newsettings
        # print "N.B: NEW DAC not set as default, do it by hand"
        os.system(cmd)
        
### Read the file produced by the function creating the map between Vcal and VcThr 
### and get the minimum VcThr allowed for that ROC. Returns a dictionary storing ROC vs VcThr DAC

def  initDacSettings():
    filename = runpath + 'mapRocVcalVcThr.txt'    
    try:
        ofile = open(filename, 'r')
    except IOError:
        print "Cannot open ", filename
    
    else:
        rocDACs = {l.split()[0]:l.split()[4] for l in ofile.readlines() if l.split()[0].startswith("BPix")}
        ofile.close()
        return rocDACs


def findDacFromKey(key):

    dac = []

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


def findDetConfigFromKey(key):

    detconfig = []

    with open(os.environ['PIXELCONFIGURATIONBASE']+'/configurations.txt','r') as f:
        chunks = f.read().split('\n\n')
    for c in chunks:
        config = c.split('\n')
        if 'key %s'%key in config:
            detconfig = [item.split()[1] for item in config if item.startswith('detconfig')]
    if len(detconfig)<1:
        sys.exit("Error: detconfig not found")
    print "Used key %s with detconfig %s"%(key,detconfig[0])
    return detconfig[0]

        
### Analyse the file produced by CheckROCThr and get a list of failing ROCs        
def getFailingRocs(path, iteration):
    if(iteration != 0):
        try:
            ofile = open("failed_%d.txt"%(iteration),'r')
        except IOError:
            print "Cannot open ", "failed_%d.txt"%(iteration)
            
        else:
            lines = ofile.readlines() 

            print "==========================================="
            print "Failing ROCs: ", len(lines) - 3
            print "==========================================="
          

            rocs = [l.split()[0] for l in lines]
            failrocs = [l.split()[0] for l in lines if (l.startswith("BPix") or l.startswith("FPix"))]
            #            print failrocs
            ofile.close()
            return failrocs
    else:   return []


