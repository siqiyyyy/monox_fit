#!/usr/bin/env python

import ROOT
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from HiggsAnalysis.CombinedLimit.ModelTools import *
import os
import argparse
pjoin = os.path.join

def cli_args():
    parser = argparse.ArgumentParser(prog='Convert input histograms into RooWorkspace.')
    parser.add_argument('file', type=str, help='Input file to use.')
    parser.add_argument('--out', type=str, help='Path to save output under.', default='mono-x.root')
    parser.add_argument('--category', type=str, default=None, help='Analysis category')
    args = parser.parse_args()

    args.file = os.path.abspath(args.file)
    args.out = os.path.abspath(args.out)
    if not os.path.exists(args.file):
      raise IOError("Input file not found: " + args.file)
    if not args.file.endswith('.root'):
      raise IOError("Input file is not a ROOT file: " + args.file)
    if not args.category:
      raise IOError("Please specify the --category option.")
    return args

def main():
  # Commandline arguments
  args = cli_args()

  # Create output path
  outdir = os.path.dirname(args.out)
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  
  fin = ROOT.TFile(args.file,'READ')
  fdir = fin.Get("category_"+args.category)

  fout = ROOT.TFile(args.out,'RECREATE')
  foutdir = fout.mkdir("category_"+args.category)

  wsin_combine = ROOT.RooWorkspace("wspace_"+args.category,"wspace_"+args.category)
  wsin_combine._import = SafeWorkspaceImporter(wsin_combine)#getattr(wsin_combine,"import")
  
  varl = ROOT.RooRealVar("met","met",0,100000);

  # Keys in the fdir 
  keys_local = fdir.GetListOfKeys()
  for key in keys_local: 
    obj = key.ReadObj()
    print obj.GetName(), obj.GetTitle(), type(obj)
    if type(obj)!=type(ROOT.TH1D()): 
      continue
    title = obj.GetTitle()
    name = obj.GetName()
    if not obj.Integral() > 0: 
      obj.SetBinContent(1,0.0001) # otherwise Combine will complain!
    print "Creating Data Hist for ", name 
    dhist = ROOT.RooDataHist("%s"%(name),"DataSet - %s, %s"%(args.category,name),ROOT.RooArgList(varl),obj)
    wsin_combine._import(dhist)


  foutdir.cd()
  foutdir.WriteTObject(wsin_combine)
  foutdir.Write()
  fout.Write()


  # For reasons unknown, if we do not return 
  # the workspace from this function, it goes
  # out of scope and segfaults.
  # ????
  # To be resolved.
  return wsin_combine

if __name__ == "__main__":
  a=main()