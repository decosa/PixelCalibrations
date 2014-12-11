#!/usr/bin/env python

# ************************************************************************************************************
#
#  Authors: Annapaola de Cosa
#           decosa@cern.ch
#           Martina Malberti
#           malberti@cern.ch
#           March/2014
#  
#  Description:
#  Here a set of tools aimed to browse calibration files are collected.
#
#
#  - browseROCChain(files,  func, *args): opens all the files from the list
#    and browse the directories up to the last one containing info on the ROCs 
#    saved as canvanses or histos, 
#    e.g  BPix/BPix_BmI/BPix_BmI_SEC4/BPix_BmI_SEC4_LYR1/BPix_BmI_SEC4_LYR1_LDR5F/BPix_BmI_SEC4_LYR1_LDR5F_MOD1
#    -- files:   list of files to open and browse 
#    -- func:    function to execute
#    -- *args:   arguments to pass to the function
#
#  - browseFEDChannels(files,  func, *args): opens all the files of the list
#    and accesses the FED directory and all the channel folders stored inside. 
#    e.g FED26/FED26_Channel1
#    -- files:   list of files to open and browse 
#    -- func:    function to execute
#    -- *args:   arguments to pass to the function
#
#  - browseFolder(files, dirName,  func, *args): opens all the files
#    of the list and accesses the directory called dirName, and 
#    executes the function func.
#    -- files:   list of files to open and browse 
#    -- dirName: name of the directory to access
#    -- func:    function to execute
#    -- *args:   arguments to pass to the function
#
#  - runfolder(run): select the right folder for the given run.
#    Runs are categorized in folders such as Run_0, Run_1000, Run_2000 etc
#    -- run: run number
# ***************************************************************************************************************



import sys
import os, commands
import ROOT

def runfolder(run):
    f = int(run/1000)*1000
    return f 


def browseROCChain(files,  func, *args):
    for file in files:
        try:
            f = ROOT.TFile.Open(file)
        except IOError:
            print "Cannot open ", file
        else:
            print "Opening file ",  file
            f.cd()
            
            ### Browse the file up to the last directory

            for r in ROOT.gDirectory.GetListOfKeys(): # BPIX or FPIX
                if(r.ReadObj().GetName()=="BPix" or r.ReadObj().GetName()=="FPix"):
                    if r.IsFolder():
                        r.ReadObj().cd()

                        for shell in ROOT.gDirectory.GetListOfKeys(): # BmI, BmO, BpI, BpO folders
                            if shell.IsFolder():
                                shell.ReadObj().cd()
                            
                            for disk in ROOT.gDirectory.GetListOfKeys(): # Disk folders, e.g: BmI_D1
                                if disk.IsFolder():
                                    disk.ReadObj().cd()
                                    
                                    for bld in ROOT.gDirectory.GetListOfKeys(): # Blade folders, e.g.: BmI_D1_BLD1
                                        if bld.IsFolder():
                                            bld.ReadObj().cd()

                                            for pnl in ROOT.gDirectory.GetListOfKeys(): # Panel folders, e.g.:  BmI_D1_BLD1_PNL1
                                                if pnl.IsFolder():
                                                    pnl.ReadObj().cd()
                                                    
                                                    for plq in ROOT.gDirectory.GetListOfKeys(): # Plaquette folders, e.g.:  BmI_D1_BLD1_PNL1_PLQ1
                                                        if plq.IsFolder():
                                                            plq.ReadObj().cd()
                                                            
                                                            func(*args)

                                                            

        



def browseFEDChannels(files,  func, *args):
    for file in files:
        try:
            f = ROOT.TFile.Open(file)
        except IOError:
            print "Cannot open ", file
        else:
            print "Opening file ",  file
            f.cd()
            
            ### Browse the file up to the last directory

            for fedDir in ROOT.gDirectory.GetListOfKeys(): # access FED folder
                if(fedDir.ReadObj().GetName().startswith("FED")):
                    if fedDir.IsFolder():
                        fedDir.ReadObj().cd()

                        for ch in ROOT.gDirectory.GetListOfKeys(): # FED channels
                            if ch.IsFolder():
                                ch.ReadObj().cd()
                                func(*args)

                                                      

def browseFolder(files, treeName,  func, *args):
    for file in files:
        f = ROOT.TFile.Open(file)
        try:
            f = ROOT.TFile.Open(file)
        except IOError:
            print "Cannot open ", file
        else:
            print "Opening file ", file
            f.cd()
            
            obj = f.Get(treeName)
            try:
                obj.cd()
            except TypeError:
                print "This is not a directory."
            else:
                list = ROOT.gDirectory.GetListOfKeys()
                func(*args)
