import ROOT
from counting_experiment import *

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

    replacement["BIN"] = b
    up = histogram.Clone("{PROC}_weights_{CONSTRAINT}_{CONSTRAINT}_stat_error_{REGION}_bin{BIN}_Up".format(**replacement))
    up.SetBinContent(b, content + err)
    down = histogram.Clone("{PROC}_weights_{CONSTRAINT}_{CONSTRAINT}_stat_error_{REGION}_bin{BIN}_Down".format(**replacement))
    down.SetBinContent(b, content - err)
    outfile.WriteTObject(up)
    outfile.WriteTObject(down)

    print "Adding an error -- ", up.GetName(),err
    CR.add_nuisance_shape("{CONSTRAINT}_stat_error_{REGION}_bin{BIN}".format(**replacement),outfile)


# Define how a control region(s) transfer is made by defining cmodel provide, the calling pattern must be unchanged!
# First define simple string which will be used for the datacard
model = "wjets"
def cmodel(cid,nam,_f,_fOut, out_ws, diag):

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

  fztoz_trig = r.TFile.Open("sys/all_trig.root") # 250 - 1400 binning

  ## Here now adding the trigger uncertainty
  wtow_trig_down = fztoz_trig.Get("trig_sys_down"+tag)
  ratio_wtowtrig_down = WScales.Clone(); ratio_wtowtrig_down.SetName("wmn_weights_%s_mettrig_Down"%cid);
  ratio_wtowtrig_down.Multiply(wtow_trig_down)
  _fOut.WriteTObject(ratio_wtowtrig_down)

  wtow_trig_up = fztoz_trig.Get("trig_sys_up"+tag)
  ratio_wtowtrig_up = WScales.Clone(); ratio_wtowtrig_up.SetName("wmn_weights_%s_mettrig_Up"%cid);
  ratio_wtowtrig_up.Multiply(wtow_trig_up)
  _fOut.WriteTObject(ratio_wtowtrig_up)

  CRs[0].add_nuisance_shape("mettrig",_fOut)

  ## Here now adding the trigger uncertainty
  ewtow_trig_down = fztoz_trig.Get("trig_sys_down"+tag)
  eratio_wtowtrig_down = WScales_e.Clone(); eratio_wtowtrig_down.SetName("wen_weights_%s_mettrig_Down"%cid);
  eratio_wtowtrig_down.Multiply(ewtow_trig_down)
  _fOut.WriteTObject(eratio_wtowtrig_down)

  ewtow_trig_up = fztoz_trig.Get("trig_sys_up"+tag)
  eratio_wtowtrig_up = WScales_e.Clone(); eratio_wtowtrig_up.SetName("wen_weights_%s_mettrig_Up"%cid);
  eratio_wtowtrig_up.Multiply(ewtow_trig_up)
  _fOut.WriteTObject(eratio_wtowtrig_up)

  CRs[1].add_nuisance_shape("mettrig",_fOut)

  fwtowpdf = r.TFile.Open("sys/wtow_pdf_sys.root") # 250 - 1400 binning

  wtow_pdf_down   = fwtowpdf.Get("ratio_Down"+tag)
  ratio_wtowpdf_down = targetmc.Clone();  ratio_wtowpdf_down.SetName("wmn_weights_%s_wtowpdf_Down"%cid);
  ratio_wtowpdf_down.Divide(controlmc)
  ratio_wtowpdf_down.Multiply(wtow_pdf_down)
  _fOut.WriteTObject(ratio_wtowpdf_down)

  wtow_pdf_up   = fwtowpdf.Get("ratio"+tag)
  ratio_wtowpdf_up = targetmc.Clone();  ratio_wtowpdf_up.SetName("wmn_weights_%s_wtowpdf_Up"%cid);
  ratio_wtowpdf_up.Divide(controlmc)
  ratio_wtowpdf_up.Multiply(wtow_pdf_up)
  _fOut.WriteTObject(ratio_wtowpdf_up)

  ewtow_pdf_down   = fwtowpdf.Get("ratio_Down"+tag)
  eratio_wtowpdf_down = targetmc.Clone();  eratio_wtowpdf_down.SetName("wen_weights_%s_wtowpdf_Down"%cid);
  eratio_wtowpdf_down.Divide(controlmc_e)
  eratio_wtowpdf_down.Multiply(ewtow_pdf_down)
  _fOut.WriteTObject(eratio_wtowpdf_down)

  ewtow_pdf_up   = fwtowpdf.Get("ratio"+tag)
  eratio_wtowpdf_up = targetmc.Clone();  eratio_wtowpdf_up.SetName("wen_weights_%s_wtowpdf_Up"%cid);
  eratio_wtowpdf_up.Divide(controlmc_e)
  eratio_wtowpdf_up.Multiply(ewtow_pdf_up)
  _fOut.WriteTObject(eratio_wtowpdf_up)

  CRs[0].add_nuisance_shape("wtowpdf",_fOut)
  CRs[1].add_nuisance_shape("wtowpdf",_fOut)

  ## Veto uncertainties
  fwtowveto = r.TFile.Open("sys/veto_sys.root") # 250 - 1400 binning

  ## Wmuon CR first
  veto_el_up       = fwtowveto.Get("eleveto"+tag)
  ratio_veto_el_up = WScales.Clone(); ratio_veto_el_up.SetName("wmn_weights_%s_eveto_Up"%cid)
  ratio_veto_el_up.Multiply(veto_el_up)
  _fOut.WriteTObject(ratio_veto_el_up)

  veto_el_down       = fwtowveto.Get("eleveto_Down"+tag)
  ratio_veto_el_down = WScales.Clone(); ratio_veto_el_down.SetName("wmn_weights_%s_eveto_Down"%cid)
  ratio_veto_el_down.Multiply(veto_el_down)
  _fOut.WriteTObject(ratio_veto_el_down)

  veto_mu_up       = fwtowveto.Get("muveto"+tag)
  ratio_veto_mu_up = WScales.Clone(); ratio_veto_mu_up.SetName("wmn_weights_%s_muveto_Up"%cid)
  ratio_veto_mu_up.Multiply(veto_mu_up)
  _fOut.WriteTObject(ratio_veto_mu_up)

  veto_mu_down       = fwtowveto.Get("muveto_Down"+tag)
  ratio_veto_mu_down = WScales.Clone(); ratio_veto_mu_down.SetName("wmn_weights_%s_muveto_Down"%cid)
  ratio_veto_mu_down.Multiply(veto_mu_down)
  _fOut.WriteTObject(ratio_veto_mu_down)

  veto_tau_up       = fwtowveto.Get("tauveto"+tag)
  ratio_veto_tau_up = WScales.Clone(); ratio_veto_tau_up.SetName("wmn_weights_%s_tauveto_Up"%cid)
  ratio_veto_tau_up.Multiply(veto_tau_up)
  _fOut.WriteTObject(ratio_veto_tau_up)

  veto_tau_down       = fwtowveto.Get("tauveto_Down"+tag)
  ratio_veto_tau_down = WScales.Clone(); ratio_veto_tau_down.SetName("wmn_weights_%s_tauveto_Down"%cid)
  ratio_veto_tau_down.Multiply(veto_tau_down)
  _fOut.WriteTObject(ratio_veto_tau_down)

  CRs[0].add_nuisance_shape("eveto",_fOut)
  CRs[0].add_nuisance_shape("muveto",_fOut)
  CRs[0].add_nuisance_shape("tauveto",_fOut)

  ## W electron CR first
  eveto_el_up       = fwtowveto.Get("eleveto"+tag)
  eratio_veto_el_up = WScales_e.Clone(); eratio_veto_el_up.SetName("wen_weights_%s_eveto_Up"%cid)
  eratio_veto_el_up.Multiply(eveto_el_up)
  _fOut.WriteTObject(eratio_veto_el_up)

  eveto_el_down       = fwtowveto.Get("eleveto_Down"+tag)
  eratio_veto_el_down = WScales_e.Clone(); eratio_veto_el_down.SetName("wen_weights_%s_eveto_Down"%cid)
  eratio_veto_el_down.Multiply(eveto_el_down)
  _fOut.WriteTObject(eratio_veto_el_down)

  eveto_mu_up       = fwtowveto.Get("muveto"+tag)
  eratio_veto_mu_up = WScales_e.Clone(); eratio_veto_mu_up.SetName("wen_weights_%s_muveto_Up"%cid)
  eratio_veto_mu_up.Multiply(eveto_mu_up)
  _fOut.WriteTObject(eratio_veto_mu_up)

  eveto_mu_down       = fwtowveto.Get("muveto_Down"+tag)
  eratio_veto_mu_down = WScales_e.Clone(); eratio_veto_mu_down.SetName("wen_weights_%s_muveto_Down"%cid)
  eratio_veto_mu_down.Multiply(eveto_mu_down)
  _fOut.WriteTObject(eratio_veto_mu_down)

  eveto_tau_up       = fwtowveto.Get("tauveto"+tag)
  eratio_veto_tau_up = WScales_e.Clone(); eratio_veto_tau_up.SetName("wen_weights_%s_tauveto_Up"%cid)
  eratio_veto_tau_up.Multiply(eveto_tau_up)
  _fOut.WriteTObject(eratio_veto_tau_up)

  eveto_tau_down       = fwtowveto.Get("tauveto_Down"+tag)
  eratio_veto_tau_down = WScales_e.Clone(); eratio_veto_tau_down.SetName("wen_weights_%s_tauveto_Down"%cid)
  eratio_veto_tau_down.Multiply(eveto_tau_down)
  _fOut.WriteTObject(eratio_veto_tau_down)

  CRs[1].add_nuisance_shape("eveto",_fOut)
  CRs[1].add_nuisance_shape("muveto",_fOut)
  CRs[1].add_nuisance_shape("tauveto",_fOut)



  #######################################################################################################

  cat = Category(model,cid,nam,_fin,_fOut,_wspace,out_ws,_bins,metname,targetmc.GetName(),CRs,diag)
  cat.setDependant("zjets","wjetssignal")  # Can use this to state that the "BASE" of this is already dependant on another process
  # EG if the W->lv in signal is dependant on the Z->vv and then the W->mv is depenant on W->lv, then
  # give the arguments model,channel name from the config which defines the Z->vv => W->lv map!
  # Return of course
  return cat

