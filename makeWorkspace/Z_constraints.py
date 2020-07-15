import ROOT
from counting_experiment import *
from W_constraints import do_stat_unc, add_variation
from parameters import flat_uncertainties
import re
ROOT.RooMsgService.instance().setSilentMode(True)

# Define how a control region(s) transfer is made by defining *cmodel*, the calling pattern must be unchanged!
# First define simple string which will be used for the datacard
model = "zjets"

def cmodel(cid,nam,_f,_fOut, out_ws, diag, year):
  filler = {
    "YEAR" : year,
    "CHANNEL" : "monojet" if "monojet" in cid else "monov"
  }
  # Some setup
  _fin = _f.Get("category_%s"%cid)
  _wspace = _fin.Get("wspace_%s"%cid)

  # ############################ USER DEFINED ###########################################################
  # First define the nominal transfer factors (histograms of signal/control, usually MC
  # note there are many tools available inside include/diagonalize.h for you to make
  # special datasets/histograms representing these and systematic effects
  # example below for creating shape systematic for photon which is just every bin up/down 30%

  metname    = "met"          # Observable variable name
  gvptname   = "genBosonPt"   # Weights are in generator pT

  target             = _fin.Get("signal_zjets")      # define monimal (MC) of which process this config will model
  controlmc          = _fin.Get("Zmm_zll")           # defines Zmm MC of which process will be controlled by
  controlmc_photon   = _fin.Get("gjets_gjets")       # defines Gjets MC of which process will be controlled by
  controlmc_e        = _fin.Get("Zee_zll")           # defines Zmm MC of which process will be controlled by
  controlmc_w        = _fin.Get("signal_wjets")

  # Create the transfer factors and save them (not here you can also create systematic variations of these
  # transfer factors (named with extention _sysname_Up/Down
  ZmmScales = target.Clone(); ZmmScales.SetName("zmm_weights_%s"%cid)
  ZmmScales.Divide(controlmc)
  _fOut.WriteTObject(ZmmScales)  # always write out to the directory

  ZeeScales = target.Clone(); ZeeScales.SetName("zee_weights_%s"%cid)
  ZeeScales.Divide(controlmc_e)
  _fOut.WriteTObject(ZeeScales)  # always write out to the directory

  WZScales = target.Clone(); WZScales.SetName("w_weights_%s"%cid)
  WZScales.Divide(controlmc_w)
  _fOut.WriteTObject(WZScales)  # always write out to the directory

  PhotonScales = target.Clone(); PhotonScales.SetName("photon_weights_%s"%cid)
  PhotonScales.Divide(controlmc_photon)
  _fOut.WriteTObject(PhotonScales)

  #######################################################################################################

  _bins = []  # take bins from some histogram, can choose anything but this is easy
  for b in range(target.GetNbinsX()+1):
    _bins.append(target.GetBinLowEdge(b+1))

  # Here is the important bit which "Builds" the control region, make a list of control regions which
  # are constraining this process, each "Channel" is created with ...
  # 	(name,_wspace,out_ws,cid+'_'+model,TRANSFERFACTORS)
  # the second and third arguments can be left unchanged, the others instead must be set
  # TRANSFERFACTORS are what is created above, eg WScales

  CRs = [
   Channel("photon",_wspace,out_ws,cid+'_'+model,PhotonScales)
  ,Channel("dimuon",_wspace,out_ws,cid+'_'+model,ZmmScales)
  ,Channel("dielectron",_wspace,out_ws,cid+'_'+model,ZeeScales)
  ,Channel("wjetssignal",_wspace,out_ws,cid+'_'+model,WZScales)
  ]
  my_function(_wspace,_fin,_fOut,cid,diag, filler)

  # ############################ USER DEFINED ###########################################################
  # Add systematics in the following, for normalisations use name, relative size (0.01 --> 1%)
  # for shapes use add_nuisance_shape with (name,_fOut)
  # note, the code will LOOK for something called NOMINAL_name_Up and NOMINAL_name_Down, where NOMINAL=WScales.GetName()
  # these must be created and writted to the same dirctory as the nominal (fDir)

  if "monov" in cid:
    tag = "_monov"
  else:
    tag = ""

  do_stat_unc(PhotonScales, "photon", cid, "photonCR", CRs[0],_fOut)
  do_stat_unc(ZmmScales, "zmm", cid, "dimuonCR", CRs[1],_fOut)
  do_stat_unc(ZeeScales, "zee", cid, "dielectronCR", CRs[2],_fOut)
  do_stat_unc(WZScales, "w", cid, "wzCR", CRs[3],_fOut)

  ## Here now adding the trigger uncertainty
  fztoz_trig = r.TFile.Open("sys/all_trig_2017.root") # 250 - 1400 binning

  # We want to correlate experimental uncertainties between the loose and tight regions.
  cid_corr = re.sub("(loose|tight)","",cid)

  add_variation(PhotonScales,fztoz_trig,"trig_sys_down"+tag,"photon_weights_%s_mettrig_%s_Down"%(cid,year), _fOut)
  add_variation(PhotonScales,fztoz_trig,"trig_sys_up"+tag,"photon_weights_%s_mettrig_%s_Up"%(cid,year), _fOut)
  CRs[0].add_nuisance_shape("mettrig_%s"%year,_fOut)

  # Take the square of the uncertainty because we are going from zero to two leptons
  add_variation(ZmmScales,fztoz_trig,"trig_sys_sqr_down"+tag,"zmm_weights_%s_mettrig_%s_Down"%(cid,year), _fOut)
  add_variation(ZmmScales,fztoz_trig,"trig_sys_sqr_up"+tag,"zmm_weights_%s_mettrig_%s_Up"%(cid,year), _fOut)
  CRs[1].add_nuisance_shape("mettrig_%s"%year,_fOut)

  ## Here now adding the trigger uncertainty
  add_variation(ZeeScales,fztoz_trig,"trig_sys_down"+tag,"zee_weights_%s_mettrig_%s_Down"%(cid,year), _fOut)
  add_variation(ZeeScales,fztoz_trig,"trig_sys_up"+tag,"zee_weights_%s_mettrig_%s_Up"%(cid,year), _fOut)
  CRs[2].add_nuisance_shape("mettrig_%s"%year,_fOut)

  #######################################################################################################

  CRs[0].add_nuisance_shape("qcd",_fOut)
  CRs[0].add_nuisance_shape("qcdshape",_fOut)
  CRs[0].add_nuisance_shape("qcdprocess",_fOut)
  CRs[0].add_nuisance_shape("ewk",_fOut)
  CRs[0].add_nuisance_shape("sudakovZ",_fOut)
  CRs[0].add_nuisance_shape("sudakovG",_fOut)
  CRs[0].add_nuisance_shape("nnlomissZ",_fOut)
  CRs[0].add_nuisance_shape("nnlomissG",_fOut)
  CRs[0].add_nuisance_shape("cross",_fOut)
  CRs[0].add_nuisance_shape("pdf",_fOut)

  CRs[3].add_nuisance_shape("wqcd",_fOut)
  CRs[3].add_nuisance_shape("wqcdshape",_fOut)
  CRs[3].add_nuisance_shape("wqcdprocess",_fOut)
  CRs[3].add_nuisance_shape("wewk",_fOut)
  CRs[3].add_nuisance_shape("sudakovZ",_fOut)
  CRs[3].add_nuisance_shape("sudakovW",_fOut)
  CRs[3].add_nuisance_shape("nnlomissZ",_fOut)
  CRs[3].add_nuisance_shape("nnlomissW",_fOut)
  CRs[3].add_nuisance_shape("wcross",_fOut)
  CRs[3].add_nuisance_shape("wpdf",_fOut)



  #######################################################################################################


  # Veto uncertainties
  ftauveto = r.TFile.Open("sys/tau_veto_unc.root")
  fmuveto = r.TFile.Open("sys/muon_veto_unc.root")
  felveto = r.TFile.Open("sys/ele_veto_unc.root")

  # The transfer factor here is Z(SR) / W(SR)
  # -> Invert the veto shapes relative to W_constraints, where the TF is W(SR) / W(CR)
  add_variation(WZScales, felveto, "ele_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "w_weights_%s_eveto_id_%s_Up"%(cid, year), _fOut,invert=True)
  add_variation(WZScales, felveto, "ele_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "w_weights_%s_eveto_id_%s_Down"%(cid, year), _fOut,invert=True)
  CRs[3].add_nuisance_shape("eveto_id_%s"%year,_fOut)

  add_variation(WZScales, felveto, "ele_reco_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "w_weights_%s_eveto_reco_%s_Up"%(cid, year), _fOut,invert=True)
  add_variation(WZScales, felveto, "ele_reco_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "w_weights_%s_eveto_reco_%s_Down"%(cid, year), _fOut,invert=True)
  CRs[3].add_nuisance_shape("eveto_reco_%s"%year,_fOut)

  add_variation(WZScales, ftauveto, "tau_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "w_weights_%s_tauveto_%s_Up"%(cid, year), _fOut,invert=True)
  add_variation(WZScales, ftauveto, "tau_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "w_weights_%s_tauveto_%s_Down"%(cid, year), _fOut,invert=True)
  CRs[3].add_nuisance_shape("tauveto_%s"%year,_fOut)

  add_variation(WZScales, fmuveto, "muon_id_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "w_weights_%s_muveto_id_%s_Up"%(cid, year), _fOut,invert=True)
  add_variation(WZScales, fmuveto, "muon_id_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "w_weights_%s_muveto_id_%s_Down"%(cid, year), _fOut,invert=True)
  CRs[3].add_nuisance_shape("muveto_id_%s"%year,_fOut)

  add_variation(WZScales, fmuveto, "muon_iso_veto_sys_{CHANNEL}_up_{YEAR}".format(**filler), "w_weights_%s_muveto_iso_%s_Up"%(cid, year), _fOut,invert=True)
  add_variation(WZScales, fmuveto, "muon_iso_veto_sys_{CHANNEL}_down_{YEAR}".format(**filler), "w_weights_%s_muveto_iso_%s_Down"%(cid, year), _fOut,invert=True)
  CRs[3].add_nuisance_shape("muveto_iso_%s"%year,_fOut)

  # Prefiring uncertainty
  # The shape in the input file is just one histogram to be used for up/down
  # -> need to invert for one variation
  # Note that the "invert" argument is the other way round for electrons and muons
  # To take into account the anticorrelation between them
  if year == 2017:
    fpref = r.TFile.Open("sys/pref_unc.root")

    add_variation(ZmmScales, fpref, "{CHANNEL}_pref_unc_z_over_mm".format(**filler), "zmm_weights_%s_prefiring_Up"%cid, _fOut)
    add_variation(ZmmScales, fpref, "{CHANNEL}_pref_unc_z_over_mm".format(**filler), "zmm_weights_%s_prefiring_Down"%cid, _fOut,invert=True)
    CRs[1].add_nuisance_shape("prefiring",_fOut)

    add_variation(ZeeScales, fpref, "{CHANNEL}_pref_unc_z_over_ee".format(**filler), "zee_weights_%s_prefiring_Up"%cid, _fOut,invert=True)
    add_variation(ZeeScales, fpref, "{CHANNEL}_pref_unc_z_over_ee".format(**filler), "zee_weights_%s_prefiring_Down"%cid, _fOut)
    CRs[2].add_nuisance_shape("prefiring",_fOut)


  fphotonid = r.TFile.Open("sys/photon_id_unc.root")
  add_variation(PhotonScales, fphotonid, "{CHANNEL}_{YEAR}_photon_id_up".format(**filler), "photon_weights_%s_CMS_eff%s_pho_Up"%(cid, year), _fOut)
  add_variation(PhotonScales, fphotonid, "{CHANNEL}_{YEAR}_photon_id_dn".format(**filler), "photon_weights_%s_CMS_eff%s_pho_Down"%(cid, year), _fOut)
  CRs[0].add_nuisance_shape("CMS_eff{YEAR}_pho".format(**filler),_fOut)
  add_variation(PhotonScales, fphotonid, "{CHANNEL}_{YEAR}_photon_id_extrap_up".format(**filler), "photon_weights_%s_CMS_eff%s_pho_extrap_Up"%(cid, year), _fOut)
  add_variation(PhotonScales, fphotonid, "{CHANNEL}_{YEAR}_photon_id_extrap_dn".format(**filler), "photon_weights_%s_CMS_eff%s_pho_extrap_Down"%(cid, year), _fOut)
  CRs[0].add_nuisance_shape("CMS_eff{YEAR}_pho_extrap".format(**filler),_fOut)


  # JES uncertainties
  fjes = r.TFile.Open("sys/monojet_tf_uncs.root")
  
  # Get the list of available JES/JER variations directly from the file
  jet_variations = set()
  for x in list(fjes.GetListOfKeys()):
    var = re.sub("(.*qcd_|(Up|Down))","",x.GetName())
    if '201' in var and not (str(year) in var):
      continue
    jet_variations.add(var)

  print "VARIATIONS"
  print jet_variations
  for var in jet_variations:
    add_variation(WZScales, fjes, 'znunu_over_wlnu{YEAR}_qcd_{VARIATION}Up'.format(YEAR=year-2000, VARIATION=var), "w_weights_%s_%s_Up"%(cid, var), _fOut)
    add_variation(WZScales, fjes, 'znunu_over_wlnu{YEAR}_qcd_{VARIATION}Down'.format(YEAR=year-2000, VARIATION=var), "w_weights_%s_%s_Down"%(cid, var), _fOut)
    CRs[3].add_nuisance_shape(var,_fOut)
    
    add_variation(ZmmScales, fjes, 'znunu_over_zmumu{YEAR}_qcd_{VARIATION}Up'.format(YEAR=year-2000, VARIATION=var), "zmm_weights_%s_%s_Up"%(cid, var), _fOut)
    add_variation(ZmmScales, fjes, 'znunu_over_zmumu{YEAR}_qcd_{VARIATION}Down'.format(YEAR=year-2000, VARIATION=var), "zmm_weights_%s_%s_Down"%(cid, var), _fOut)
    CRs[1].add_nuisance_shape(var,_fOut)

    add_variation(ZeeScales, fjes, 'znunu_over_zee{YEAR}_qcd_{VARIATION}Up'.format(YEAR=year-2000, VARIATION=var), "zee_weights_%s_%s_Up"%(cid, var), _fOut)
    add_variation(ZeeScales, fjes, 'znunu_over_zee{YEAR}_qcd_{VARIATION}Down'.format(YEAR=year-2000, VARIATION=var), "zee_weights_%s_%s_Down"%(cid, var), _fOut)
    CRs[2].add_nuisance_shape(var,_fOut)
    
    add_variation(PhotonScales, fjes, 'gjets_over_znunu{YEAR}_qcd_{VARIATION}Up'.format(YEAR=year-2000, VARIATION=var), "photon_weights_%s_%s_Up"%(cid, var), _fOut, invert=True)
    add_variation(PhotonScales, fjes, 'gjets_over_znunu{YEAR}_qcd_{VARIATION}Down'.format(YEAR=year-2000, VARIATION=var), "photon_weights_%s_%s_Down"%(cid, var), _fOut, invert=True)
    CRs[0].add_nuisance_shape(var,_fOut)



  cat = Category(model,cid,nam,_fin,_fOut,_wspace,out_ws,_bins,metname,target.GetName(),CRs,diag)
  # Return of course
  return cat

# My Function. Just to put all of the complicated part into one function
def my_function(_wspace,_fin,_fOut,nam,diag, filler):

  print "What is your cid?", nam

  if "monov" in nam:
    tag = "_monov"
  else:
    tag = ""

  metname    = "met"          # Observable variable name
  gvptname   = "genBosonPt"   # Weights are in generator pT

  target             = _fin.Get("signal_zjets")      # define monimal (MC) of which process this config will model
  controlmc          = _fin.Get("Zmm_zll")           # defines Zmm MC of which process will be controlled by
  controlmc_photon   = _fin.Get("gjets_gjets")       # defines Gjets MC of which process will be controlled by

  controlmc_w        = _fin.Get("signal_wjets")

  _gjet_mcname 	     = "gjets_gjets"
  GJet               = _fin.Get("gjets_gjets")

  PhotonSpectrum = controlmc_photon.Clone(); PhotonSpectrum.SetName("photon_spectrum_%s_"%nam)
  ZvvSpectrum 	 = target.Clone(); ZvvSpectrum.SetName("zvv_spectrum_%s_"%nam)

  _fOut.WriteTObject( PhotonSpectrum )
  _fOut.WriteTObject( ZvvSpectrum )

  #################################################################################################################

  Pho = controlmc_photon.Clone(); Pho.SetName("photon_weights_denom_%s"%nam)
  Zvv = target.Clone(); Zvv.SetName("photon_weights_nom_%s"%nam)

  fztog = r.TFile.Open("sys/gz_unc.root") # 250 - 1400 binning

  ## qcd scale
  ztog_qcd_up   = fztog.Get("ZG_QCDScale_met"+tag)
  ztog_qcd_down = fztog.Get("ZG_QCDScale_met_Down"+tag)

  ratio_qcd_up = Zvv.Clone();  ratio_qcd_up.SetName("photon_weights_%s_qcd_Up"%nam);
  ratio_qcd_up.Divide(Pho)
  ratio_qcd_up.Multiply(ztog_qcd_up)
  _fOut.WriteTObject(ratio_qcd_up)

  ratio_qcd_down = Zvv.Clone();  ratio_qcd_down.SetName("photon_weights_%s_qcd_Down"%nam);
  ratio_qcd_down.Divide(Pho)
  ratio_qcd_down.Multiply(ztog_qcd_down)
  _fOut.WriteTObject(ratio_qcd_down)

  ## qcd shape
  ztog_qcdshape_up   = fztog.Get("ZG_QCDShape_met"+tag)
  ztog_qcdshape_down = fztog.Get("ZG_QCDShape_met_Down"+tag)

  ratio_qcdshape_up = Zvv.Clone();  ratio_qcdshape_up.SetName("photon_weights_%s_qcdshape_Up"%nam);
  ratio_qcdshape_up.Divide(Pho)
  ratio_qcdshape_up.Multiply(ztog_qcdshape_up)
  _fOut.WriteTObject(ratio_qcdshape_up)

  ratio_qcdshape_down = Zvv.Clone();  ratio_qcdshape_down.SetName("photon_weights_%s_qcdshape_Down"%nam);
  ratio_qcdshape_down.Divide(Pho)
  ratio_qcdshape_down.Multiply(ztog_qcdshape_down)
  _fOut.WriteTObject(ratio_qcdshape_down)

  ## qcd process
  ztog_qcdprocess_up   = fztog.Get("ZG_QCDProcess_met"+tag)
  ztog_qcdprocess_down = fztog.Get("ZG_QCDProcess_met_Down"+tag)

  ratio_qcdprocess_up = Zvv.Clone();  ratio_qcdprocess_up.SetName("photon_weights_%s_qcdprocess_Up"%nam);
  ratio_qcdprocess_up.Divide(Pho)
  ratio_qcdprocess_up.Multiply(ztog_qcdprocess_up)
  _fOut.WriteTObject(ratio_qcdprocess_up)

  ratio_qcdprocess_down = Zvv.Clone();  ratio_qcdprocess_down.SetName("photon_weights_%s_qcdprocess_Down"%nam);
  ratio_qcdprocess_down.Divide(Pho)
  ratio_qcdprocess_down.Multiply(ztog_qcdprocess_down)
  _fOut.WriteTObject(ratio_qcdprocess_down)

  ## ewk
  ztog_ewk_up   = fztog.Get("ZG_NNLOEWK_met"+tag)
  ztog_ewk_down = fztog.Get("ZG_NNLOEWK_met_Down"+tag)

  ratio_ewk_up = Zvv.Clone();  ratio_ewk_up.SetName("photon_weights_%s_ewk_Up"%nam);
  ratio_ewk_up.Divide(Pho)
  ratio_ewk_up.Multiply(ztog_ewk_up)
  _fOut.WriteTObject(ratio_ewk_up)

  ratio_ewk_down = Zvv.Clone();  ratio_ewk_down.SetName("photon_weights_%s_ewk_Down"%nam);
  ratio_ewk_down.Divide(Pho)
  ratio_ewk_down.Multiply(ztog_ewk_down)
  _fOut.WriteTObject(ratio_ewk_down)

  ##Sudakov on the Z
  ztog_sudakov1_up   = fztog.Get("ZG_Sudakov1_met"+tag)
  ztog_sudakov1_down = fztog.Get("ZG_Sudakov1_met_Down"+tag)

  ratio_sudakov1_up = Zvv.Clone();  ratio_sudakov1_up.SetName("photon_weights_%s_sudakovZ_Up"%nam);
  ratio_sudakov1_up.Divide(Pho)
  ratio_sudakov1_up.Multiply(ztog_sudakov1_up)
  _fOut.WriteTObject(ratio_sudakov1_up)

  ratio_sudakov1_down = Zvv.Clone();  ratio_sudakov1_down.SetName("photon_weights_%s_sudakovZ_Down"%nam);
  ratio_sudakov1_down.Divide(Pho)
  ratio_sudakov1_down.Multiply(ztog_sudakov1_down)
  _fOut.WriteTObject(ratio_sudakov1_down)

  ##Sudakov on the G
  ztog_sudakov2_up   = fztog.Get("ZG_Sudakov2_met"+tag)
  ztog_sudakov2_down = fztog.Get("ZG_Sudakov2_met_Down"+tag)

  ratio_sudakov2_up = Zvv.Clone();  ratio_sudakov2_up.SetName("photon_weights_%s_sudakovG_Up"%nam);
  ratio_sudakov2_up.Divide(Pho)
  ratio_sudakov2_up.Multiply(ztog_sudakov2_up)
  _fOut.WriteTObject(ratio_sudakov2_up)

  ratio_sudakov2_down = Zvv.Clone();  ratio_sudakov2_down.SetName("photon_weights_%s_sudakovG_Down"%nam);
  ratio_sudakov2_down.Divide(Pho)
  ratio_sudakov2_down.Multiply(ztog_sudakov2_down)
  _fOut.WriteTObject(ratio_sudakov2_down)

  ##NNLO Miss on the Z
  ztog_nnlomiss1_up   = fztog.Get("ZG_NNLOMiss1_met"+tag)
  ztog_nnlomiss1_down = fztog.Get("ZG_NNLOMiss1_met_Down"+tag)

  ratio_nnlomiss1_up = Zvv.Clone();  ratio_nnlomiss1_up.SetName("photon_weights_%s_nnlomissZ_Up"%nam);
  ratio_nnlomiss1_up.Divide(Pho)
  ratio_nnlomiss1_up.Multiply(ztog_nnlomiss1_up)
  _fOut.WriteTObject(ratio_nnlomiss1_up)

  ratio_nnlomiss1_down = Zvv.Clone();  ratio_nnlomiss1_down.SetName("photon_weights_%s_nnlomissZ_Down"%nam);
  ratio_nnlomiss1_down.Divide(Pho)
  ratio_nnlomiss1_down.Multiply(ztog_nnlomiss1_down)
  _fOut.WriteTObject(ratio_nnlomiss1_down)

  ##NNLO Miss on the G
  ztog_nnlomiss2_up   = fztog.Get("ZG_NNLOMiss2_met"+tag)
  ztog_nnlomiss2_down = fztog.Get("ZG_NNLOMiss2_met_Down"+tag)

  ratio_nnlomiss2_up = Zvv.Clone();  ratio_nnlomiss2_up.SetName("photon_weights_%s_nnlomissG_Up"%nam);
  ratio_nnlomiss2_up.Divide(Pho)
  ratio_nnlomiss2_up.Multiply(ztog_nnlomiss2_up)
  _fOut.WriteTObject(ratio_nnlomiss2_up)

  ratio_nnlomiss2_down = Zvv.Clone();  ratio_nnlomiss2_down.SetName("photon_weights_%s_nnlomissG_Down"%nam);
  ratio_nnlomiss2_down.Divide(Pho)
  ratio_nnlomiss2_down.Multiply(ztog_nnlomiss2_down)
  _fOut.WriteTObject(ratio_nnlomiss2_down)

  ##PDF
  ztog_pdf_up   = fztog.Get("ZG_PDF_met"+tag)
  ztog_pdf_down = fztog.Get("ZG_PDF_met_Down"+tag)

  ratio_pdf_up = Zvv.Clone();  ratio_pdf_up.SetName("photon_weights_%s_pdf_Up"%nam);
  ratio_pdf_up.Divide(Pho)
  ratio_pdf_up.Multiply(ztog_pdf_up)
  _fOut.WriteTObject(ratio_pdf_up)

  ratio_pdf_down = Zvv.Clone();  ratio_pdf_down.SetName("photon_weights_%s_pdf_Down"%nam);
  ratio_pdf_down.Divide(Pho)
  ratio_pdf_down.Multiply(ztog_pdf_down)
  _fOut.WriteTObject(ratio_pdf_down)

  ## Cross
  ztog_cross_up   = fztog.Get("ZG_MIX_met"+tag)
  ztog_cross_down = fztog.Get("ZG_MIX_met_Down"+tag)

  ratio_cross_up = Zvv.Clone();  ratio_cross_up.SetName("photon_weights_%s_cross_Up"%nam);
  ratio_cross_up.Divide(Pho)
  ratio_cross_up.Multiply(ztog_cross_up)
  _fOut.WriteTObject(ratio_cross_up)

  ratio_cross_down = Zvv.Clone();  ratio_cross_down.SetName("photon_weights_%s_cross_Down"%nam);
  ratio_cross_down.Divide(Pho)
  ratio_cross_down.Multiply(ztog_cross_down)
  _fOut.WriteTObject(ratio_cross_down)

  Zvv.Divide(Pho); Zvv.SetName("photon_weights_%s"%nam)

  # PhotonScales = Zvv.Clone()
  # _fOut.WriteTObject(PhotonScales)

  #################################################################################################################
  #################################################################################################################
  ### Now lets do the same thing for W

  WSpectrum = controlmc_w.Clone(); WSpectrum.SetName("w_spectrum_%s_"%nam)
  ZvvSpectrum 	 = target.Clone(); ZvvSpectrum.SetName("zvv_spectrum_%s_"%nam)

  _fOut.WriteTObject( WSpectrum )

  #################################################################################################################

  Wsig = controlmc_w.Clone(); Wsig.SetName("w_weights_denom_%s"%nam)
  Zvv_w = target.Clone(); Zvv_w.SetName("w_weights_nom_%s"%nam)

  fztow = r.TFile.Open("sys/wz_unc.root") # 250 - 1400 binning new

  ## qcd scale
  ztow_qcd_up   = fztow.Get("ZW_QCDScale_met"+tag)
  ztow_qcd_down = fztow.Get("ZW_QCDScale_met_Down"+tag)

  wratio_qcd_up = Zvv_w.Clone();  wratio_qcd_up.SetName("w_weights_%s_wqcd_Up"%nam);
  wratio_qcd_up.Divide(Wsig)
  wratio_qcd_up.Multiply(ztow_qcd_up)
  _fOut.WriteTObject(wratio_qcd_up)

  wratio_qcd_down = Zvv_w.Clone();  wratio_qcd_down.SetName("w_weights_%s_wqcd_Down"%nam);
  wratio_qcd_down.Divide(Wsig)
  wratio_qcd_down.Multiply(ztow_qcd_down)
  _fOut.WriteTObject(wratio_qcd_down)

  ## qcd shape
  ztow_qcdshape_up   = fztow.Get("ZW_QCDShape_met"+tag)
  ztow_qcdshape_down = fztow.Get("ZW_QCDShape_met_Down"+tag)

  wratio_qcdshape_up = Zvv_w.Clone();  wratio_qcdshape_up.SetName("w_weights_%s_wqcdshape_Up"%nam);
  wratio_qcdshape_up.Divide(Wsig)
  wratio_qcdshape_up.Multiply(ztow_qcdshape_up)
  _fOut.WriteTObject(wratio_qcdshape_up)

  wratio_qcdshape_down = Zvv_w.Clone(); wratio_qcdshape_down.SetName("w_weights_%s_wqcdshape_Down"%nam);
  wratio_qcdshape_down.Divide(Wsig)
  wratio_qcdshape_down.Multiply(ztow_qcdshape_down)
  _fOut.WriteTObject(wratio_qcdshape_down)

  ## qcd process
  ztow_qcdprocess_up   = fztow.Get("ZW_QCDProcess_met"+tag)
  ztow_qcdprocess_down = fztow.Get("ZW_QCDProcess_met_Down"+tag)

  wratio_qcdprocess_up = Zvv_w.Clone();  wratio_qcdprocess_up.SetName("w_weights_%s_wqcdprocess_Up"%nam);
  wratio_qcdprocess_up.Divide(Wsig)
  wratio_qcdprocess_up.Multiply(ztow_qcdprocess_up)
  _fOut.WriteTObject(wratio_qcdprocess_up)

  wratio_qcdprocess_down = Zvv_w.Clone();  wratio_qcdprocess_down.SetName("w_weights_%s_wqcdprocess_Down"%nam);
  wratio_qcdprocess_down.Divide(Wsig)
  wratio_qcdprocess_down.Multiply(ztow_qcdprocess_down)
  _fOut.WriteTObject(wratio_qcdprocess_down)

  ## ewk
  ztow_ewk_up   = fztow.Get("ZW_NNLOEWK_met"+tag)
  ztow_ewk_down = fztow.Get("ZW_NNLOEWK_met_Down"+tag)

  wratio_ewk_up = Zvv_w.Clone();  wratio_ewk_up.SetName("w_weights_%s_wewk_Up"%nam);
  wratio_ewk_up.Divide(Wsig)
  wratio_ewk_up.Multiply(ztow_ewk_up)
  _fOut.WriteTObject(wratio_ewk_up)

  wratio_ewk_down = Zvv_w.Clone();  wratio_ewk_down.SetName("w_weights_%s_wewk_Down"%nam);
  wratio_ewk_down.Divide(Wsig)
  wratio_ewk_down.Multiply(ztow_ewk_down)
  _fOut.WriteTObject(wratio_ewk_down)

  ##Sudakov on the Z
  ztow_sudakov1_up   = fztow.Get("ZW_Sudakov1_met"+tag)
  ztow_sudakov1_down = fztow.Get("ZW_Sudakov1_met_Down"+tag)

  wratio_sudakov1_up = Zvv_w.Clone();  wratio_sudakov1_up.SetName("w_weights_%s_sudakovZ_Up"%nam);
  wratio_sudakov1_up.Divide(Wsig)
  wratio_sudakov1_up.Multiply(ztow_sudakov1_up)
  _fOut.WriteTObject(wratio_sudakov1_up)

  wratio_sudakov1_down = Zvv_w.Clone();  wratio_sudakov1_down.SetName("w_weights_%s_sudakovZ_Down"%nam);
  wratio_sudakov1_down.Divide(Wsig)
  wratio_sudakov1_down.Multiply(ztow_sudakov1_down)
  _fOut.WriteTObject(wratio_sudakov1_down)

  ##Sudakov on the W
  ztow_sudakov2_up   = fztow.Get("ZW_Sudakov2_met"+tag)
  ztow_sudakov2_down = fztow.Get("ZW_Sudakov2_met_Down"+tag)

  wratio_sudakov2_up = Zvv_w.Clone();  wratio_sudakov2_up.SetName("w_weights_%s_sudakovW_Up"%nam);
  wratio_sudakov2_up.Divide(Wsig)
  wratio_sudakov2_up.Multiply(ztow_sudakov2_up)
  _fOut.WriteTObject(wratio_sudakov2_up)

  wratio_sudakov2_down = Zvv_w.Clone();  wratio_sudakov2_down.SetName("w_weights_%s_sudakovW_Down"%nam);
  wratio_sudakov2_down.Divide(Wsig)
  wratio_sudakov2_down.Multiply(ztow_sudakov2_down)
  _fOut.WriteTObject(wratio_sudakov2_down)

  ##NNLO Miss on the Z
  ztow_nnlomiss1_up   = fztow.Get("ZW_NNLOMiss1_met"+tag)
  ztow_nnlomiss1_down = fztow.Get("ZW_NNLOMiss1_met_Down"+tag)

  wratio_nnlomiss1_up = Zvv_w.Clone();  wratio_nnlomiss1_up.SetName("w_weights_%s_nnlomissZ_Up"%nam);
  wratio_nnlomiss1_up.Divide(Wsig)
  wratio_nnlomiss1_up.Multiply(ztow_nnlomiss1_up)
  _fOut.WriteTObject(wratio_nnlomiss1_up)

  wratio_nnlomiss1_down = Zvv_w.Clone();  wratio_nnlomiss1_down.SetName("w_weights_%s_nnlomissZ_Down"%nam);
  wratio_nnlomiss1_down.Divide(Wsig)
  wratio_nnlomiss1_down.Multiply(ztow_nnlomiss1_down)
  _fOut.WriteTObject(wratio_nnlomiss1_down)

  ##NNLO Miss on the W
  ztow_nnlomiss2_up   = fztow.Get("ZW_NNLOMiss2_met"+tag)
  ztow_nnlomiss2_down = fztow.Get("ZW_NNLOMiss2_met_Down"+tag)

  wratio_nnlomiss2_up = Zvv_w.Clone();  wratio_nnlomiss2_up.SetName("w_weights_%s_nnlomissW_Up"%nam);
  wratio_nnlomiss2_up.Divide(Wsig)
  wratio_nnlomiss2_up.Multiply(ztow_nnlomiss2_up)
  _fOut.WriteTObject(wratio_nnlomiss2_up)

  wratio_nnlomiss2_down = Zvv_w.Clone();  wratio_nnlomiss2_down.SetName("w_weights_%s_nnlomissW_Down"%nam);
  wratio_nnlomiss2_down.Divide(Wsig)
  wratio_nnlomiss2_down.Multiply(ztow_nnlomiss2_down)
  _fOut.WriteTObject(wratio_nnlomiss2_down)

  ##PDF
  ztow_pdf_up   = fztow.Get("ZW_PDF_met"+tag)
  ztow_pdf_down = fztow.Get("ZW_PDF_met_Down"+tag)

  wratio_pdf_up = Zvv_w.Clone();  wratio_pdf_up.SetName("w_weights_%s_wpdf_Up"%nam);
  wratio_pdf_up.Divide(Wsig)
  wratio_pdf_up.Multiply(ztow_pdf_up)
  _fOut.WriteTObject(wratio_pdf_up)

  wratio_pdf_down = Zvv_w.Clone();  wratio_pdf_down.SetName("w_weights_%s_wpdf_Down"%nam);
  wratio_pdf_down.Divide(Wsig)
  wratio_pdf_down.Multiply(ztow_pdf_down)
  _fOut.WriteTObject(wratio_pdf_down)

  ## Cross
  ztow_cross_up   = fztow.Get("ZW_MIX_met"+tag)
  ztow_cross_down = fztow.Get("ZW_MIX_met_Down"+tag)

  wratio_cross_up = Zvv_w.Clone();  wratio_cross_up.SetName("w_weights_%s_wcross_Up"%nam);
  wratio_cross_up.Divide(Wsig)
  wratio_cross_up.Multiply(ztow_cross_up)
  _fOut.WriteTObject(wratio_cross_up)

  wratio_cross_down = Zvv_w.Clone();  wratio_cross_down.SetName("w_weights_%s_wcross_Down"%nam);
  wratio_cross_down.Divide(Wsig)
  wratio_cross_down.Multiply(ztow_cross_down)
  _fOut.WriteTObject(wratio_cross_down)


  ############### GET SOMETHING CENTRAL PLEASE ############################
  #Wsig = controlmc_w.Clone(); Wsig.SetName("w_weights_denom_%s"%nam)
  #Zvv_w = target.Clone(); Zvv_w.SetName("w_weights_nom_%s"%nam)

  Zvv_w.Divide(Wsig)


