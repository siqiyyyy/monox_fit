#!/usr/bin/env python

import argparse
import os
import re
from math import sqrt

import ROOT
from HiggsAnalysis.CombinedLimit.ModelTools import *

ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
pjoin = os.path.join

def cli_args():
    parser = argparse.ArgumentParser(prog='Convert input histograms into RooWorkspace.')
    parser.add_argument('file', type=str, help='Input file to use.')
    parser.add_argument('--out', type=str, help='Path to save output under.', default='mono-x.root')
    parser.add_argument('--categories', type=str, default=None, help='Analysis category')
    args = parser.parse_args()

    args.file = os.path.abspath(args.file)
    args.out = os.path.abspath(args.out)
    if not os.path.exists(args.file):
      raise IOError("Input file not found: " + args.file)
    if not args.file.endswith('.root'):
      raise IOError("Input file is not a ROOT file: " + args.file)
    if not args.categories:
      raise IOError("Please specify the --categories option.")

    args.categories = args.categories.split(',')

    return args

def main():
  # Commandline arguments
  args = cli_args()

  # Create output path
  outdir = os.path.dirname(args.out)
  if not os.path.exists(outdir):
    os.makedirs(outdir)

  fin = ROOT.TFile(args.file,'READ')
  f_jes = ROOT.TFile("sys/shape_jes_uncs_smooth.root")
  f_diboson = ROOT.TFile("sys/shape_diboson_unc.root")
  fout = ROOT.TFile(args.out,'RECREATE')
  dummy = []
  for category in args.categories:
    fdir = fin.Get("category_"+category)

    foutdir = fout.mkdir("category_"+category)

    wsin_combine = ROOT.RooWorkspace("wspace_"+category,"wspace_"+category)
    wsin_combine._import = SafeWorkspaceImporter(wsin_combine)#getattr(wsin_combine,"import")

    variable_name = "mjj" if ("vbf" in category) else "met"
    varl = ROOT.RooRealVar(variable_name, variable_name, 0,100000);
    # Helper function
    def write_obj(obj, name):
      '''Converts histogram to RooDataHist and writes to workspace + ROOT file'''
      print "Creating Data Hist for ", name
      dhist = ROOT.RooDataHist(
                            name,
                            "DataSet - %s, %s"%(category,name),
                            ROOT.RooArgList(varl),
                            obj
                            )
      wsin_combine._import(dhist)

      # Write the individual histograms
      # for easy transfer factor calculation
      # later on
      obj.SetDirectory(0)
      foutdir.cd()
      foutdir.WriteTObject(obj)

    # Loop over all keys in the input file
    # pick out the histograms, and add to
    # the work space.
    keys_local = fdir.GetListOfKeys()
    for key in keys_local:
      obj = key.ReadObj()
      if type(obj) not in [ROOT.TH1D, ROOT.TH1F]:
        continue
      title = obj.GetTitle()
      name = obj.GetName()

      # Ensure non-zero integral for combine
      if not obj.Integral() > 0:
        obj.SetBinContent(1,0.0001)

      # Add overflow to last bin
      overflow        = obj.GetBinContent(obj.GetNbinsX()+1)
      overflow_err    = obj.GetBinError(obj.GetNbinsX()+1)
      lastbin         = obj.GetBinContent(obj.GetNbinsX())
      lastbin_err     = obj.GetBinError(obj.GetNbinsX())
      new_lastbin     = overflow + lastbin
      new_lastbin_err = sqrt(overflow_err**2 + lastbin_err**2)

      obj.SetBinContent(obj.GetNbinsX(), new_lastbin)
      obj.SetBinError(obj.GetNbinsX(), new_lastbin_err)
      obj.SetBinContent(obj.GetNbinsX()+1, 0)
      obj.SetBinError(obj.GetNbinsX()+1, 0)

      write_obj(obj, name)
      
      # Systematic variations
      if not 'data' in name:
        category = re.sub("(loose|tight)","", category)
        channel = re.sub("_201\d", "", category)
        # JES / JER variations
        for jeskey in [x.GetName() for x in f_jes.GetListOfKeys()]:
          if not (category in jeskey):
            continue
          variation = jeskey.replace(category+"_","")
          name = obj.GetName()+"_"+variation
          varied_obj = obj.Clone(name)
          varied_obj.Multiply(f_jes.Get(jeskey))
          write_obj(varied_obj, name)

        # Diboson variations
        vvprocs = ['wz','ww','zz','zgamma','wgamma']

        process = "_".join(key.GetName().split("_")[1:])
        if process in vvprocs:
          for vvkey in [x.GetName() for x in f_diboson.GetListOfKeys()]:
            if not process in vvkey:
              continue
            if not channel in vvkey:
              continue
            variation = vvkey.replace(channel + "_" + process + "_", "")

            name = obj.GetName()+"_"+variation
            print("TEST ", key, variation, name)
            varied_obj = obj.Clone(name)
            varied_obj.Multiply(f_diboson.Get(vvkey))
            write_obj(varied_obj, name)

    dummy.append(wsin_combine)

    # Write the workspace
    foutdir.cd()
    foutdir.WriteTObject(wsin_combine)
    foutdir.Write()
    fout.Write()


  # For reasons unknown, if we do not return
  # the workspace from this function, it goes
  # out of scope and segfaults.
  # ????
  # To be resolved.
  return dummy

if __name__ == "__main__":
  a=main()
