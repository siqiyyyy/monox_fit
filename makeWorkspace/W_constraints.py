import ROOT
from counting_experiment import *
from parameters import flat_uncertainties

# Tell RooFit to be quiet
ROOT.RooMsgService.instance().setSilentMode(True)

def do_stat_unc(histogram, proc,cid, region, CR, outfile):
  """Add stat. unc. variations to the workspace"""

  # Store formatting inputs for repeated use
  replacement = {
    "PROC" : proc,
    "CONSTRAINT" : cid,
    "REGION" : region
  }

  # Add one variation per bin
  for b in range(1, histogram.GetNbinsX()+1):
    err = histogram.GetBinError(b)
    content = histogram.GetBinContent(b)

    # Safety
    if (content<=0) or (err/content < 0.001) :
      continue

    # Careful: The bin count "b" in this loop starts at 1
    # In the combine model, we want it to start from 0!
    replacement["BIN"] = b-1
    up = histogram.Clone("{PROC}_weights_{CONSTRAINT}_{CONSTRAINT}_stat_error_{REGION}_bin{BIN}_Up".format(**replacement))
    up.SetBinContent(b, content + err)
    down = histogram.Clone("{PROC}_weights_{CONSTRAINT}_{CONSTRAINT}_stat_error_{REGION}_bin{BIN}_Down".format(**replacement))
    down.SetBinContent(b, content - err)
    outfile.WriteTObject(up)
    outfile.WriteTObject(down)

    print "Adding an error -- ", up.GetName(),err
    CR.add_nuisance_shape("{CONSTRAINT}_stat_error_{REGION}_bin{BIN}".format(**replacement),outfile)


def add_variation(histogram, unc_file, unc_name, new_name, outfile):
  variation = histogram.Clone(new_name)
  factor = unc_file.Get(unc_name)
  variation.Multiply(factor)
  outfile.WriteTObject(variation)

# Define how a control region(s) transfer is made by defining cmodel provide, the calling pattern must be unchanged!
# First define simple string which will be used for the datacard
model = "wjets"
def cmodel(cid,nam,_f,_fOut, out_ws, diag, year):

  # Some setup
  _fin    = _f.Get("category_%s"%cid)
  _wspace = _fin.Get("wspace_%s"%cid)

  # ############################ USER DEFINED ###########################################################
  # First define the nominal transfer factors (histograms of signal/control, usually MC
  # note there are many tools available inside include/diagonalize.h for you to make
  # special datasets/histograms representing these and systematic effects
  # but for now this is just kept simple
  processName  = "WJets" # Give a name of the process being modelled
  metname      = "met"    # Observable variable name
  targetmc     = _fin.Get("signal_wjets")      # define monimal (MC) of which process this config will model
  controlmc    = _fin.Get("Wmn_wjets")  # defines in / out acceptance
  controlmc_e  = _fin.Get("Wen_wjets")  # defines in / out acceptance

  # Create the transfer factors and save them (not here you can also create systematic variations of these
  # transfer factors (named with extention _sysname_Up/Down
  WScales = targetmc.Clone("wmn_weights_%s"%cid);
  WScales.Divide(controlmc)
  _fOut.WriteTObject(WScales)  # always write out to the directory

  WScales_e = targetmc.Clone("wen_weights_%s"%cid);
  WScales_e.Divide(controlmc_e)
  _fOut.WriteTObject(WScales_e)  # always write out to the directory

  #######################################################################################################

  _bins = []  # take bins from some histogram, can choose anything but this is easy
  for b in range(targetmc.GetNbinsX()+1):
    _bins.append(targetmc.GetBinLowEdge(b+1))

  # Here is the important bit which "Builds" the control region, make a list of control regions which
  # are constraining this process, each "Channel" is created with ...
  # 	(name,_wspace,out_ws,cid+'_'+model,TRANSFERFACTORS)
  # the second and third arguments can be left unchanged, the others instead must be set
  # TRANSFERFACTORS are what is created above, eg WScales

  CRs = [
   Channel("singlemuon",_wspace,out_ws,cid+'_'+model,WScales),
   Channel("singleelectron",_wspace,out_ws,cid+'_'+model,WScales_e)
  ]


  # ############################ USER DEFINED ###########################################################
  # Add systematics in the following, for normalisations use name, relative size (0.01 --> 1%)
  # for shapes use add_nuisance_shape with (name,_fOut)
  # note, the code will LOOK for something called NOMINAL_name_Up and NOMINAL_name_Down, where NOMINAL=WScales.GetName()
  # these must be created and writted to the same dirctory as the nominal (fDir)


  do_stat_unc(WScales, "wmn", cid, "singlemuonCR", CRs[0],_fOut)
  do_stat_unc(WScales_e, "wen", cid, "singleelectronCR", CRs[1],_fOut)


  if "monov" in cid:
    tag = "_monov"
  else:
    tag = ""

  fztoz_trig = r.TFile.Open("sys/all_trig_2017.root") # 250 - 1400 binning
  
  # Trigger single muon
  add_variation(WScales, fztoz_trig, "trig_sys_down"+tag, "wmn_weights_%s_mettrig_Down"%cid, _fOut)
  add_variation(WScales, fztoz_trig, "trig_sys_up"+tag, "wmn_weights_%s_mettrig_Up"%cid, _fOut)
  CRs[0].add_nuisance_shape("mettrig",_fOut)

  # Trigger single electron
  add_variation(WScales_e, fztoz_trig, "trig_sys_down"+tag, "wen_weights_%s_mettrig_Down"%cid, _fOut)
  add_variation(WScales_e, fztoz_trig, "trig_sys_up"+tag, "wen_weights_%s_mettrig_Up"%cid, _fOut)
  CRs[1].add_nuisance_shape("mettrig",_fOut)

  # PDF unc
  fwtowpdf = r.TFile.Open("sys/wtow_pdf_sys.root")

  # PDF single muon
  add_variation(WScales, fwtowpdf, "ratio_Down"+tag, "wmn_weights_%s_wtowpdf_Down"%cid, _fOut)
  add_variation(WScales, fwtowpdf, "ratio"+tag, "wmn_weights_%s_wtowpdf_Up"%cid, _fOut)
  CRs[0].add_nuisance_shape("wtowpdf",_fOut)

  # PDF single electron
  add_variation(WScales_e, fwtowpdf, "ratio_Down"+tag, "wen_weights_%s_wtowpdf_Down"%cid, _fOut)
  add_variation(WScales_e, fwtowpdf, "ratio"+tag, "wen_weights_%s_wtowpdf_Up"%cid, _fOut)
  CRs[1].add_nuisance_shape("wtowpdf",_fOut)

  ## Veto uncertainties
  fwtowveto = r.TFile.Open("sys/veto_sys.root") # 250 - 1400 binning

  ## Wmuon CR first
  add_variation(WScales, fwtowveto, "eleveto"+tag, "wmn_weights_%s_eveto_Up"%cid, _fOut)
  add_variation(WScales, fwtowveto, "eleveto_Down"+tag, "wmn_weights_%s_eveto_Down"%cid, _fOut)
  CRs[0].add_nuisance_shape("eveto",_fOut)

  add_variation(WScales, fwtowveto, "muveto"+tag, "wmn_weights_%s_muveto_Up"%cid, _fOut)
  add_variation(WScales, fwtowveto, "muveto_Down"+tag, "wmn_weights_%s_muveto_Down"%cid, _fOut)
  CRs[0].add_nuisance_shape("muveto",_fOut)

  add_variation(WScales, fwtowveto, "tauveto"+tag, "wmn_weights_%s_tauveto_Up"%cid, _fOut)
  add_variation(WScales, fwtowveto, "tauveto_Down"+tag, "wmn_weights_%s_tauveto_Down"%cid, _fOut)
  CRs[0].add_nuisance_shape("tauveto",_fOut)

  ## W electron CR first
  add_variation(WScales_e, fwtowveto, "eleveto"+tag, "wen_weights_%s_eveto_Up"%cid, _fOut)
  add_variation(WScales_e, fwtowveto, "eleveto_Down"+tag, "wen_weights_%s_eveto_Down"%cid, _fOut)
  CRs[1].add_nuisance_shape("eveto",_fOut)

  add_variation(WScales_e, fwtowveto, "muveto"+tag, "wen_weights_%s_muveto_Up"%cid, _fOut)
  add_variation(WScales_e, fwtowveto, "muveto_Down"+tag, "wen_weights_%s_muveto_Down"%cid, _fOut)
  CRs[1].add_nuisance_shape("muveto",_fOut)

  add_variation(WScales_e, fwtowveto, "tauveto"+tag, "wen_weights_%s_tauveto_Up"%cid, _fOut)
  add_variation(WScales_e, fwtowveto, "tauveto_Down"+tag, "wen_weights_%s_tauveto_Down"%cid, _fOut)
  CRs[1].add_nuisance_shape("tauveto",_fOut)



  #######################################################################################################

  cat = Category(model,cid,nam,_fin,_fOut,_wspace,out_ws,_bins,metname,targetmc.GetName(),CRs,diag)
  cat.setDependant("zjets","wjetssignal")  # Can use this to state that the "BASE" of this is already dependant on another process
  # EG if the W->lv in signal is dependant on the Z->vv and then the W->mv is depenant on W->lv, then
  # give the arguments model,channel name from the config which defines the Z->vv => W->lv map!
  # Return of course
  return cat

