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

def get_jes_variations(obj, f_jes, category):
  '''Get JES variations from JES source file, returns all the varied histograms stored in a dictionary.'''
  channel = re.sub("(loose|tight)","", category)
  # Save varied histograms for all JES variations and the histogram names in this dictionary
  varied_hists = {}
  for key in [x.GetName() for x in f_jes.GetListOfKeys()]:
    if not (channel in key):
      continue
    variation = key.replace(channel+"_","")
    varied_name = obj.GetName()+"_"+variation
    varied_obj = obj.Clone(varied_name)
    # Multiply by JES factor to get the varied yields
    varied_obj.Multiply(f_jes.Get(key))
    # Save the varied histogram into a dict
    varied_hists[varied_name] = varied_obj

  return varied_hists

def create_workspace(fin, f_jes, fout, category):
  '''Create workspace and write the relevant histograms in it for the given category, returns the workspace.'''
  fdir = fin.Get("category_"+category)
  foutdir = fout.mkdir("category_"+category)

  wsin_combine = ROOT.RooWorkspace("wspace_"+category,"wspace_"+category)
  wsin_combine._import = SafeWorkspaceImporter(wsin_combine)

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
    
    if not 'data' in name:
      # JES variations: Get them from the source file and save them to workspace
      jes_varied_hists = get_jes_variations(obj, f_jes, category)
      for varied_name, varied_obj in jes_varied_hists.items():
        write_obj(varied_obj, varied_name)

  # Write the workspace
  foutdir.cd()
  foutdir.WriteTObject(wsin_combine)
  foutdir.Write()
  fout.Write()

  return wsin_combine

def main():
  # Commandline arguments
  args = cli_args()

  # Create output path
  outdir = os.path.dirname(args.out)
  if not os.path.exists(outdir):
    os.makedirs(outdir)

  fin = ROOT.TFile(args.file,'READ')
  # JES shape files for each category
  f_jes_dict = {
    '(monoj|monov).*': ROOT.TFile("sys/monoj_monov_shape_jes_uncs_smooth.root"),
    'vbf.*': ROOT.TFile("sys/vbf_shape_jes_uncs_smooth.root")
  }
  fout = ROOT.TFile(args.out,'RECREATE')
  dummy = []
  for category in args.categories:
    # Determine the relevant JES source file
    f_jes = None
    for regex, f in f_jes_dict.items():
      if re.match(regex, category):
        f_jes = f
    if not f_jes:
      raise RuntimeError('Could not find a JES source file for category: {}'.format(category))
    
    wsin_combine = create_workspace(fin, f_jes, fout, category)
    dummy.append(wsin_combine)

  # For reasons unknown, if we do not return
  # the workspace from this function, it goes
  # out of scope and segfaults.
  # ????
  # To be resolved.
  return dummy

if __name__ == "__main__":
  a=main()
