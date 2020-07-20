import ROOT
from counting_experiment import *
from parameters import flat_uncertainties
import re
# Tell RooFit to be quiet
ROOT.RooMsgService.instance().setSilentMode(True)

def do_stat_unc(histogram, proc,cid, region, CR, outfile, functype="lognorm"):
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
    CR.add_nuisance_shape("{CONSTRAINT}_stat_error_{REGION}_bin{BIN}".format(**replacement),outfile, functype=functype)


def add_variation(histogram, unc_file, unc_name, new_name, outfile, invert=False):
  variation = histogram.Clone(new_name)
  factor = unc_file.Get(unc_name)

  if not factor:
    raise IOError("Could not retrieve histogram '%s' from file '%s'."%(unc_name, unc_file))

  if factor.GetNbinsX() == 1:
    if invert:
      variation.Scale(1 / factor.GetBinContent(1))
    else:
      variation.Scale(factor.GetBinContent(1))
  else:
    if invert:
      variation.Divide(factor)
    else:
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

  filler = {"YEAR":year}
  if "monov" in cid:
    tag = "_monov"
    filler["CHANNEL"] = "monov"
  else:
    tag = ""
    filler["CHANNEL"] = "monojet"
  fztoz_trig = r.TFile.Open("sys/all_trig_2017.root") # 250 - 1400 binning

  # We want to correlate experimental uncertainties between the loose and tight regions.
  cid_corr = re.sub("(loose|tight)","",cid)

  # Trigger single muon
  add_variation(WScales, fztoz_trig, "trig_sys_down"+tag, "wmn_weights_%s_mettrig_%s_Down"%(cid,year), _fOut)
  add_variation(WScales, fztoz_trig, "trig_sys_up"+tag, "wmn_weights_%s_mettrig_%s_Up"%(cid,year), _fOut)
  CRs[0].add_nuisance_shape("mettrig_%s"%year,_fOut)

  # Trigger single electron
  add_variation(WScales_e, fztoz_trig, "trig_sys_down"+tag, "wen_weights_%s_mettrig_%s_Down"%(cid,year), _fOut)
  add_variation(WScales_e, fztoz_trig, "trig_sys_up"+tag, "wen_weights_%s_mettrig_%s_Up"%(cid,year), _fOut)
  CRs[1].add_nuisance_shape("mettrig_%s"%year,_fOut)

  ## Veto uncertainties
  ftauveto = r.TFile.Open("sys/tau_veto_unc.root")
  fmuveto = r.TFile.Open("sys/muon_veto_unc.root")
  felveto = r.TFile.Open("sys/ele_veto_unc.root")

  ## Wmuon CR
  add_variation(WScales, felveto, "ele_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wmn_weights_%s_eveto_id_%s_Up"%(cid,year), _fOut)
  add_variation(WScales, felveto, "ele_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wmn_weights_%s_eveto_id_%s_Down"%(cid,year), _fOut)
  CRs[0].add_nuisance_shape("eveto_id_%s"%year,_fOut)

  add_variation(WScales, felveto, "ele_reco_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wmn_weights_%s_eveto_reco_%s_Up"%(cid,year), _fOut)
  add_variation(WScales, felveto, "ele_reco_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wmn_weights_%s_eveto_reco_%s_Down"%(cid,year), _fOut)
  CRs[0].add_nuisance_shape("eveto_reco_%s"%year,_fOut)

  add_variation(WScales, fmuveto, "muon_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wmn_weights_%s_muveto_id_%s_Up"%(cid,year), _fOut)
  add_variation(WScales, fmuveto, "muon_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wmn_weights_%s_muveto_id_%s_Down"%(cid,year), _fOut)
  CRs[0].add_nuisance_shape("muveto_id_%s"%year,_fOut)

  add_variation(WScales, fmuveto, "muon_iso_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wmn_weights_%s_muveto_iso_%s_Up"%(cid,year), _fOut)
  add_variation(WScales, fmuveto, "muon_iso_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wmn_weights_%s_muveto_iso_%s_Down"%(cid,year), _fOut)
  CRs[0].add_nuisance_shape("muveto_iso_%s"%year,_fOut)

  add_variation(WScales, ftauveto, "tau_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wmn_weights_%s_tauveto_%s_Up"%(cid,year), _fOut)
  add_variation(WScales, ftauveto, "tau_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wmn_weights_%s_tauveto_%s_Down"%(cid,year), _fOut)
  CRs[0].add_nuisance_shape("tauveto_%s"%year,_fOut)

  ## W electron CR
  add_variation(WScales_e, felveto, "ele_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wen_weights_%s_eveto_id_%s_Up"%(cid,year), _fOut)
  add_variation(WScales_e, felveto, "ele_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wen_weights_%s_eveto_id_%s_Down"%(cid,year), _fOut)
  CRs[1].add_nuisance_shape("eveto_id_%s"%year,_fOut)

  add_variation(WScales_e, felveto, "ele_reco_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wen_weights_%s_eveto_reco_%s_Up"%(cid,year), _fOut)
  add_variation(WScales_e, felveto, "ele_reco_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wen_weights_%s_eveto_reco_%s_Down"%(cid,year), _fOut)
  CRs[1].add_nuisance_shape("eveto_reco_%s"%year,_fOut)

  add_variation(WScales_e, fmuveto, "muon_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wen_weights_%s_muveto_id_%s_Up"%(cid,year), _fOut)
  add_variation(WScales_e, fmuveto, "muon_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wen_weights_%s_muveto_id_%s_Down"%(cid,year), _fOut)
  CRs[1].add_nuisance_shape("muveto_id_%s"%year,_fOut)

  add_variation(WScales_e, fmuveto, "muon_iso_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "wen_weights_%s_muveto_iso_%s_Up"%(cid,year), _fOut)
  add_variation(WScales_e, fmuveto, "muon_iso_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "wen_weights_%s_muveto_iso_%s_Down"%(cid,year), _fOut)
  CRs[1].add_nuisance_shape("muveto_iso_%s"%year,_fOut)

  add_variation(WScales_e, ftauveto, "tau_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler),"wen_weights_%s_tauveto_%s_Up"%(cid,year), _fOut)
  add_variation(WScales_e, ftauveto, "tau_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler),"wen_weights_%s_tauveto_%s_Down"%(cid,year), _fOut)
  CRs[1].add_nuisance_shape("tauveto_%s"%year,_fOut)


  # Prefiring uncertainty
  # The shape in the input file is just one histogram to be used for up/down
  # -> need to invert for one variation
  # Note that the "invert" argument is the other way round for electrons and muons
  # To take into account the anticorrelation between them
  if year == 2017:
    fpref = r.TFile.Open("sys/pref_unc.root")
    add_variation(WScales, fpref, "{CHANNEL}_pref_unc_w_over_m".format(**filler), "wmn_weights_%s_prefiring_Up"%cid, _fOut)
    add_variation(WScales, fpref, "{CHANNEL}_pref_unc_w_over_m".format(**filler), "wmn_weights_%s_prefiring_Down"%cid, _fOut, invert=True)
    CRs[0].add_nuisance_shape("prefiring",_fOut)

    add_variation(WScales_e, fpref, "{CHANNEL}_pref_unc_w_over_e".format(**filler), "wen_weights_%s_prefiring_Up"%cid, _fOut, invert=True)
    add_variation(WScales_e, fpref, "{CHANNEL}_pref_unc_w_over_e".format(**filler), "wen_weights_%s_prefiring_Down"%cid, _fOut)
    CRs[1].add_nuisance_shape("prefiring",_fOut)


    # JES uncertainties
  fjes = r.TFile.Open("sys/monojet_tf_uncs.root")

  # Get the list of available JES/JER variations directly from the file
  jet_variations = set()
  for x in list(fjes.GetListOfKeys()):
    var = re.sub("(.*qcd_|(Up|Down))","",x.GetName())
    if '201' in var and not (str(year) in var):
      continue
    jet_variations.add(var)

  for var in jet_variations:
    add_variation(WScales, fjes, 'wlnu_over_wmunu{YEAR}_qcd_{VARIATION}Up'.format(YEAR=year-2000, VARIATION=var), "wmn_weights_%s_%s_Up"%(cid, var), _fOut)
    add_variation(WScales, fjes, 'wlnu_over_wmunu{YEAR}_qcd_{VARIATION}Down'.format(YEAR=year-2000, VARIATION=var), "wmn_weights_%s_%s_Down"%(cid, var), _fOut)
    CRs[0].add_nuisance_shape(var,_fOut)

    add_variation(WScales_e, fjes, 'wlnu_over_wenu{YEAR}_qcd_{VARIATION}Up'.format(YEAR=year-2000, VARIATION=var), "wen_weights_%s_%s_Up"%(cid, var), _fOut)
    add_variation(WScales_e, fjes, 'wlnu_over_wenu{YEAR}_qcd_{VARIATION}Down'.format(YEAR=year-2000, VARIATION=var), "wen_weights_%s_%s_Down"%(cid, var), _fOut)
    CRs[1].add_nuisance_shape(var,_fOut)

  # PDF uncertainties
    fpdf = ROOT.TFile("sys/tf_pdf_unc.root")

  for direction in 'up', 'down':
    add_variation(
      WScales,
      fpdf,
      "{CHANNEL}_w_over_wmn_pdf_{DIR}".format(DIR=direction,**filler),
      "wmn_weights_{CID}_w_over_w_pdf_{DIR}".format(DIR=direction.capitalize(), **filler),
      _fOut
    )
    add_variation(
      WScales_e,
      fpdf,
      "{CHANNEL}_w_over_wen_pdf_{DIR}".format(DIR=direction,**filler),
      "wen_weights_{CID}_w_over_w_pdf_{DIR}".format(DIR=direction.capitalize(), **filler),
      _fOut
    )

  CRs[0].add_nuisance_shape("w_over_w_pdf",_fOut)
  CRs[1].add_nuisance_shape("w_over_w_pdf",_fOut)

  #######################################################################################################

  cat = Category(model,cid,nam,_fin,_fOut,_wspace,out_ws,_bins,metname,targetmc.GetName(),CRs,diag)
  cat.setDependant("zjets","wjetssignal")  # Can use this to state that the "BASE" of this is already dependant on another process
  # EG if the W->lv in signal is dependant on the Z->vv and then the W->mv is depenant on W->lv, then
  # give the arguments model,channel name from the config which defines the Z->vv => W->lv map!
  # Return of course
  return cat

