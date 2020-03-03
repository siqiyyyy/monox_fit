import ROOT
from counting_experiment import *
# Define how a control region(s) transfer is made by defining *cmodel*, the calling pattern must be unchanged!
# First define simple string which will be used for the datacard 
model = "qcd_zjets"

def cmodel(cid,nam,_f,_fOut, out_ws, diag, year):
  
  # Some setup
  _fin = _f.Get("category_%s"%cid)
  _wspace = _fin.Get("wspace_%s"%cid)

  # ############################ USER DEFINED ###########################################################
  # First define the nominal transfer factors (histograms of signal/control, usually MC 
  # note there are many tools available inside include/diagonalize.h for you to make 
  # special datasets/histograms representing these and systematic effects 
  # example below for creating shape systematic for photon which is just every bin up/down 30% 

  metname    = 'mjj'          # Observable variable name 
  gvptname   = "genBosonPt"    # Weights are in generator pT

  target             = _fin.Get("signal_qcdzjets")      # define monimal (MC) of which process this config will model
  controlmc          = _fin.Get("Zmm_qcdzll")           # defines Zmm MC of which process will be controlled by
  controlmc_e        = _fin.Get("Zee_qcdzll")           # defines Zmm MC of which process will be controlled by
  controlmc_w        = _fin.Get("signal_qcdwjets")
  controlmc_ewk      = _fin.Get('signal_ewkzjets')
  controlmc_photon   = _fin.Get("gjets_qcdgjets")       # defines Gjets MC of which process will be controlled by                                                                              

  # Create the transfer factors and save them (not here you can also create systematic variations of these 
  # transfer factors (named with extention _sysname_Up/Down
  ZmmScales = target.Clone(); ZmmScales.SetName("qcd_zmm_weights_%s"%cid)
  ZmmScales.Divide(controlmc)
  _fOut.WriteTObject(ZmmScales)  # always write out to the directory 

  ZeeScales = target.Clone(); ZeeScales.SetName("qcd_zee_weights_%s"%cid)
  ZeeScales.Divide(controlmc_e)
  _fOut.WriteTObject(ZeeScales)  # always write out to the directory 

  WZScales = target.Clone(); WZScales.SetName("qcd_w_weights_%s"%cid)
  WZScales.Divide(controlmc_w)
  _fOut.WriteTObject(WZScales)  # always write out to the directory 

  EQScales = target.Clone(); EQScales.SetName("ewkqcd_weights_%s"%cid)
  EQScales.Divide(controlmc_ewk)
  _fOut.WriteTObject(EQScales)  # always write out to the directory 

  PhotonScales = target.Clone(); PhotonScales.SetName("qcd_photon_weights_%s"%cid)
  PhotonScales.Divide(controlmc_photon)
  _fOut.WriteTObject(PhotonScales) # always write out to the directory 

  my_function(_wspace,_fin,_fOut,cid,diag)

  #######################################################################################################

  _bins = []  # take bins from some histogram, can choose anything but this is easy 
  for b in range(target.GetNbinsX()+1):
    _bins.append(target.GetBinLowEdge(b+1))

  # Here is the important bit which "Builds" the control region, make a list of control regions which 
  # are constraining this process, each "Channel" is created with ...
  #   (name,_wspace,out_ws,cid+'_'+model,TRANSFERFACTORS) 
  # the second and third arguments can be left unchanged, the others instead must be set
  # TRANSFERFACTORS are what is created above, eg WScales

  CRs = [
    Channel("qcd_dimuon",_wspace,out_ws,cid+'_'+model,ZmmScales)
    ,Channel("qcd_dielectron",_wspace,out_ws,cid+'_'+model,ZeeScales)
    ,Channel("qcd_wjetssignal",_wspace,out_ws,cid+'_'+model,WZScales)
    ,Channel("qcd_photon",_wspace,out_ws,cid+'_'+model,PhotonScales)
    ,Channel("ewkqcd_signal",_wspace,out_ws,cid+'_'+model,EQScales)
  ]
  for c in CRs[:3]:
    c.add_nuisance('CMS_trigger{YEAR}_met'.replace(YEAR=year),0.02)  
    c.add_nuisance('CMS_scale{YEAR}_j_vbf'.replace(YEAR=year),0.01)

  # ############################ USER DEFINED ###########################################################
  # Add systematics in the following, for normalisations use name, relative size (0.01 --> 1%)
  # for shapes use add_nuisance_shape with (name,_fOut)
  # note, the code will LOOK for something called NOMINAL_name_Up and NOMINAL_name_Down, where NOMINAL=WScales.GetName()
  # these must be created and writted to the same dirctory as the nominal (fDir)

  # Bin by bin nuisances to cover statistical uncertainties ...

  for b in range(target.GetNbinsX()):
    err = ZmmScales.GetBinError(b+1)
    if not ZmmScales.GetBinContent(b+1)>0: continue 
    relerr = err/ZmmScales.GetBinContent(b+1)
    if relerr<0.01: continue
    byb_u = ZmmScales.Clone(); byb_u.SetName("qcd_zmm_weights_%s_%s_stat_error_%s_bin%d_Up"%(cid,cid,"qcd_dimuonCR",b))
    byb_u.SetBinContent(b+1,ZmmScales.GetBinContent(b+1)+err)
    byb_d = ZmmScales.Clone(); byb_d.SetName("qcd_zmm_weights_%s_%s_stat_error_%s_bin%d_Down"%(cid,cid,"qcd_dimuonCR",b))
    if (ZmmScales.GetBinContent(b+1)-err > 0):
      byb_d.SetBinContent(b+1,ZmmScales.GetBinContent(b+1)-err)
    else:
      byb_d.SetBinContent(b+1,1)
    _fOut.WriteTObject(byb_u)
    _fOut.WriteTObject(byb_d)
    print "Adding an error -- ", byb_u.GetName(),err
    CRs[0].add_nuisance_shape("%s_stat_error_%s_bin%d"%(cid,"qcd_dimuonCR",b),_fOut)

  for b in range(target.GetNbinsX()):
    err = ZeeScales.GetBinError(b+1)
    if not ZeeScales.GetBinContent(b+1)>0: continue 
    relerr = err/ZeeScales.GetBinContent(b+1)
    if relerr<0.01: continue
    byb_u = ZeeScales.Clone(); byb_u.SetName("qcd_zee_weights_%s_%s_stat_error_%s_bin%d_Up"%(cid,cid,"qcd_dielectronCR",b))
    byb_u.SetBinContent(b+1,ZeeScales.GetBinContent(b+1)+err)
    byb_d = ZeeScales.Clone(); byb_d.SetName("qcd_zee_weights_%s_%s_stat_error_%s_bin%d_Down"%(cid,cid,"qcd_dielectronCR",b))
    if (ZeeScales.GetBinContent(b+1)-err > 0):
      byb_d.SetBinContent(b+1,ZeeScales.GetBinContent(b+1)-err)
    else:
      byb_d.SetBinContent(b+1,1)
    _fOut.WriteTObject(byb_u)
    _fOut.WriteTObject(byb_d)
    print "Adding an error -- ", byb_u.GetName(),err
    CRs[1].add_nuisance_shape("%s_stat_error_%s_bin%d"%(cid,"qcd_dielectronCR",b),_fOut)

  for b in range(target.GetNbinsX()):
    err = WZScales.GetBinError(b+1)
    if not WZScales.GetBinContent(b+1)>0: continue 
    relerr = err/WZScales.GetBinContent(b+1)
    if relerr<0.01: continue
    byb_u = WZScales.Clone(); byb_u.SetName("qcd_w_weights_%s_%s_stat_error_%s_bin%d_Up"%(cid,cid,"qcd_wzCR",b))
    byb_u.SetBinContent(b+1,WZScales.GetBinContent(b+1)+err)
    byb_d = WZScales.Clone(); byb_d.SetName("qcd_w_weights_%s_%s_stat_error_%s_bin%d_Down"%(cid,cid,"qcd_wzCR",b))
    if (WZScales.GetBinContent(b+1)-err > 0):
      byb_d.SetBinContent(b+1,WZScales.GetBinContent(b+1)-err)
    else:
      byb_d.SetBinContent(b+1,1)
    _fOut.WriteTObject(byb_u)
    _fOut.WriteTObject(byb_d)
    print "Adding an error -- ", byb_u.GetName(),err
    CRs[2].add_nuisance_shape("%s_stat_error_%s_bin%d"%(cid,"qcd_wzCR",b),_fOut)

  # for b in range(target.GetNbinsX()):
  #   err = EQScales.GetBinError(b+1)
  #   if not EQScales.GetBinContent(b+1)>0: continue 
  #   relerr = err/EQScales.GetBinContent(b+1)
  #   if relerr<0.01: continue
  #   byb_u = EQScales.Clone(); byb_u.SetName("ewkqcd_weights_%s_%s_stat_error_%s_bin%d_Up"%(cid,cid,"ewkqcdzCR",b))
  #   byb_u.SetBinContent(b+1,EQScales.GetBinContent(b+1)+err)
  #   byb_d = EQScales.Clone(); byb_d.SetName("ewkqcd_weights_%s_%s_stat_error_%s_bin%d_Down"%(cid,cid,"ewkqcdzCR",b))
  #   if (EQScales.GetBinContent(b+1)-err > 0):
  #     byb_d.SetBinContent(b+1,EQScales.GetBinContent(b+1)-err)
  #   else:
  #     byb_d.SetBinContent(b+1,1)
  #   _fOut.WriteTObject(byb_u)
  #   _fOut.WriteTObject(byb_d)
  #   print "Adding an error -- ", byb_u.GetName(),err
  #   CRs[3].add_nuisance_shape("%s_stat_error_%s_bin%d"%(cid,"ewkqcdzCR",b),_fOut)

  for b in range(target.GetNbinsX()):
    err = PhotonScales.GetBinError(b+1)
    if not PhotonScales.GetBinContent(b+1)>0: continue 
    relerr = err/PhotonScales.GetBinContent(b+1)
    if relerr<0.01: continue
    byb_u = PhotonScales.Clone(); byb_u.SetName("qcd_photon_weights_%s_%s_stat_error_%s_bin%d_Up"%(cid,cid,"qcd_photonCR",b))
    byb_u.SetBinContent(b+1,PhotonScales.GetBinContent(b+1)+err)
    byb_d = PhotonScales.Clone(); byb_d.SetName("qcd_photon_weights_%s_%s_stat_error_%s_bin%d_Down"%(cid,cid,"qcd_photonCR",b))
    if (PhotonScales.GetBinContent(b+1)-err > 0):
      byb_d.SetBinContent(b+1,PhotonScales.GetBinContent(b+1)-err)
    else:
      byb_d.SetBinContent(b+1,1)
    _fOut.WriteTObject(byb_u)
    _fOut.WriteTObject(byb_d)
    print "Adding an error -- ", byb_u.GetName(),err
    CRs[3].add_nuisance_shape("%s_stat_error_%s_bin%d"%(cid,"qcd_photonCR",b),_fOut)

  #######################################################################################################
  
  
  CRs[2].add_nuisance_shape("ZnunuWJets_QCD_renscale_vbf",_fOut)
  CRs[2].add_nuisance_shape("ZnunuWJets_QCD_facscale_vbf",_fOut)
  CRs[2].add_nuisance_shape("ZnunuWJets_QCD_pdf_vbf",_fOut) 

  for b in range(target.GetNbinsX()):
    CRs[2].add_nuisance_shape("qcd_ewk_%s_bin%d"%(cid,b),_fOut)


  CRs[3].add_nuisance_shape("Photon_QCD_renscale_vbf",_fOut)
  CRs[3].add_nuisance_shape("Photon_QCD_facscale_vbf",_fOut)
  CRs[3].add_nuisance_shape("Photon_QCD_pdf_vbf",_fOut) 

  for b in range(target.GetNbinsX()):
    CRs[3].add_nuisance_shape("qcd_photon_ewk_%s_bin%d"%(cid,b),_fOut)


  #######################################################################################################

  cat = Category(model,cid,nam,_fin,_fOut,_wspace,out_ws,_bins,metname,target.GetName(),CRs,diag)
  # Return of course
  return cat

# My Function. Just to put all of the complicated part into one function
def my_function(_wspace,_fin,_fOut,nam,diag):

  metname    = "mjj"   # Observable variable name 
  gvptname   = "genBosonPt"    # Weights are in generator pT

  target             = _fin.Get("signal_qcdzjets")      # define monimal (MC) of which process this config will model
  controlmc          = _fin.Get("Zmm_qcdzll")           # defines Zmm MC of which process will be controlled by
  controlmc_w        = _fin.Get("signal_qcdwjets")
  controlmc_photon   = _fin.Get("gjets_qcdgjets")

  #################################################################################################################


  #################################################################################################################                                                                   
  WSpectrum      = controlmc_w.Clone(); WSpectrum.SetName("qcd_w_spectrum_%s_"%nam)
  ZvvSpectrum    = target.Clone(); ZvvSpectrum.SetName("qcd_zvv_spectrum_%s_"%nam)
  PhotonSpectrum = controlmc_photon.Clone(); PhotonSpectrum.SetName("qcd_gjets_spectrum_%s_"%nam)

  _fOut.WriteTObject( WSpectrum )
  _fOut.WriteTObject( PhotonSpectrum )
  #_fOut.WriteTObject( ZvvSpectrum ) No need to rewrite

  #################################################################################################################

  Wsig = controlmc_w.Clone(); Wsig.SetName("qcd_w_weights_denom_%s"%nam)
  Zvv_w = target.Clone(); Zvv_w.SetName("qcd_w_weights_nom_%s"%nam)

  vbf_sys = r.TFile.Open("sys/vbf_z_w_gjets_theory_unc_ratio_unc.root")

  uncertainty_zoverw_ewk_up   = vbf_sys.Get("uncertainty_ratio_z_qcd_mjj_unc_w_ewkcorr_overz_common_up_"+str(year))
  uncertainty_zoverw_ewk_down = vbf_sys.Get("uncertainty_ratio_z_qcd_mjj_unc_w_ewkcorr_overz_common_down_"+str(year))
  uncertainty_zoverw_mur_up   = vbf_sys.Get("uncertainty_ratio_z_qcd_mjj_unc_zoverw_nlo_mur_up_"+str(year))
  uncertainty_zoverw_mur_down = vbf_sys.Get("uncertainty_ratio_z_qcd_mjj_unc_zoverw_nlo_mur_down_"+str(year))
  uncertainty_zoverw_muf_up   = vbf_sys.Get("uncertainty_ratio_z_qcd_mjj_unc_zoverw_nlo_muf_up_"+str(year))
  uncertainty_zoverw_muf_down = vbf_sys.Get("uncertainty_ratio_z_qcd_mjj_unc_zoverw_nlo_muf_down_"+str(year))
  uncertainty_zoverw_pdf_up   = vbf_sys.Get("uncertainty_ratio_z_qcd_mjj_unc_zoverw_nlo_pdf_up_"+str(year))
  uncertainty_zoverw_pdf_down = vbf_sys.Get("uncertainty_ratio_z_qcd_mjj_unc_zoverw_nlo_pdf_down_"+str(year))

  uncertainty_zoverg_ewk_up   = vbf_sys.Get("uncertainty_ratio_gjets_qcd_mjj_unc_w_ewkcorr_overz_common_up_"+str(year))
  uncertainty_zoverg_ewk_down = vbf_sys.Get("uncertainty_ratio_gjets_qcd_mjj_unc_w_ewkcorr_overz_common_down_"+str(year))
  uncertainty_zoverg_mur_up   = vbf_sys.Get("uncertainty_ratio_gjets_qcd_mjj_unc_goverz_nlo_mur_up_"+str(year))
  uncertainty_zoverg_mur_down = vbf_sys.Get("uncertainty_ratio_gjets_qcd_mjj_unc_goverz_nlo_mur_down_"+str(year))
  uncertainty_zoverg_muf_up   = vbf_sys.Get("uncertainty_ratio_gjets_qcd_mjj_unc_goverz_nlo_muf_up_"+str(year))
  uncertainty_zoverg_muf_down = vbf_sys.Get("uncertainty_ratio_gjets_qcd_mjj_unc_goverz_nlo_muf_down_"+str(year))
  uncertainty_zoverg_pdf_up   = vbf_sys.Get("uncertainty_ratio_gjets_qcd_mjj_unc_goverz_nlo_pdf_up_"+str(year))
  uncertainty_zoverg_pdf_down = vbf_sys.Get("uncertainty_ratio_gjets_qcd_mjj_unc_goverz_nlo_pdf_down_"+str(year))

  wratio_ren_scale_up = Zvv_w.Clone();  wratio_ren_scale_up.SetName("qcd_w_weights_%s_ZnunuWJets_QCD_renscale_vbf_Up"%nam);
  wratio_ren_scale_up.Divide(Wsig)
  for b in range(uncertainty_zoverw_mur_up.GetNbinsX()): uncertainty_zoverw_mur_up.SetBinContent(b+1,uncertainty_zoverw_mur_up.GetBinContent(b+1)+1)
  wratio_ren_scale_up.Multiply(uncertainty_zoverw_mur_up)
  _fOut.WriteTObject(wratio_ren_scale_up)
  
  wratio_ren_scale_down = Zvv_w.Clone();  wratio_ren_scale_down.SetName("qcd_w_weights_%s_ZnunuWJets_QCD_renscale_vbf_Down"%nam);
  wratio_ren_scale_down.Divide(Wsig)
  for b in range(uncertainty_zoverw_mur_down.GetNbinsX()): uncertainty_zoverw_mur_down.SetBinContent(b+1,uncertainty_zoverw_mur_down.GetBinContent(b+1)+1)
  wratio_ren_scale_down.Multiply(uncertainty_zoverw_mur_down)
  _fOut.WriteTObject(wratio_ren_scale_down)

  wratio_fac_scale_up = Zvv_w.Clone(); wratio_fac_scale_up.SetName("qcd_w_weights_%s_ZnunuWJets_QCD_facscale_vbf_Up"%nam);
  wratio_fac_scale_up.Divide(Wsig)
  for b in range(uncertainty_zoverw_muf_up.GetNbinsX()): uncertainty_zoverw_muf_up.SetBinContent(b+1,uncertainty_zoverw_muf_up.GetBinContent(b+1)+1)
  wratio_fac_scale_up.Multiply(uncertainty_zoverw_muf_up)
  _fOut.WriteTObject(wratio_fac_scale_up)
  
  wratio_fac_scale_down = Zvv_w.Clone();  wratio_fac_scale_down.SetName("qcd_w_weights_%s_ZnunuWJets_QCD_facscale_vbf_Down"%nam);
  wratio_fac_scale_down.Divide(Wsig)
  for b in range(uncertainty_zoverw_muf_down.GetNbinsX()): uncertainty_zoverw_muf_down.SetBinContent(b+1,uncertainty_zoverw_muf_down.GetBinContent(b+1)+1)
  wratio_fac_scale_down.Multiply(uncertainty_zoverw_muf_down)
  _fOut.WriteTObject(wratio_fac_scale_down)

  wratio_pdf_up = Zvv_w.Clone();  wratio_pdf_up.SetName("qcd_w_weights_%s_ZnunuWJets_QCD_pdf_vbf_Up"%nam);
  wratio_pdf_up.Divide(Wsig)
  for b in range(uncertainty_zoverw_pdf_up.GetNbinsX()): uncertainty_zoverw_pdf_up.SetBinContent(b+1,uncertainty_zoverw_pdf_up.GetBinContent(b+1)+1)
  wratio_pdf_up.Multiply(uncertainty_zoverw_pdf_up)
  _fOut.WriteTObject(wratio_pdf_up)
  
  wratio_pdf_down = Zvv_w.Clone();  wratio_pdf_down.SetName("qcd_w_weights_%s_ZnunuWJets_QCD_pdf_vbf_Down"%nam);
  wratio_pdf_down.Divide(Wsig)
  for b in range(uncertainty_zoverw_pdf_down.GetNbinsX()): uncertainty_zoverw_pdf_down.SetBinContent(b+1,uncertainty_zoverw_pdf_down.GetBinContent(b+1)+1)
  wratio_pdf_down.Multiply(uncertainty_zoverw_pdf_down)
  _fOut.WriteTObject(wratio_pdf_down)

  wratio_ewk_up = Zvv_w.Clone();  wratio_ewk_up.SetName("qcd_w_weights_%s_ewk_Up"%nam);
  wratio_ewk_up.Divide(Wsig)
  for b in range(uncertainty_zoverw_ewk_up.GetNbinsX()): uncertainty_zoverw_ewk_up.SetBinContent(b+1,uncertainty_zoverw_ewk_up.GetBinContent(b+1)+1)
  wratio_ewk_up.Multiply(uncertainty_zoverw_ewk_up)
  # We are now going to uncorrelate the bins
  #_fOut.WriteTObject(ratio_ewk_up)
  
  wratio_ewk_down = Zvv_w.Clone();  wratio_ewk_down.SetName("qcd_w_weights_%s_ewk_Down"%nam);
  wratio_ewk_down.Divide(Wsig)
  for b in range(uncertainty_zoverw_ewk_down.GetNbinsX()): uncertainty_zoverw_ewk_down.SetBinContent(b+1,uncertainty_zoverw_ewk_down.GetBinContent(b+1)+1)
  wratio_ewk_down.Multiply(uncertainty_zoverw_ewk_down)
  # We are now going to uncorrelate the bins
  #_fOut.WriteTObject(ratio_ewk_down)

  ############### GET SOMETHING CENTRAL PLEASE ############################
  #Wsig = controlmc_w.Clone(); Wsig.SetName("w_weights_denom_%s"%nam)
  #Zvv_w = target.Clone(); Zvv_w.SetName("w_weights_nom_%s"%nam)

  Zvv_w.Divide(Wsig)

  #Now lets uncorrelate the bins:
  for b in range(target.GetNbinsX()):
    #print "HELLO trying to fill up / down"
    ewk_up_w = Zvv_w.Clone(); ewk_up_w.SetName("qcd_w_weights_%s_qcd_ewk_%s_bin%d_Up"%(nam,nam,b))
    ewk_down_w = Zvv_w.Clone(); ewk_down_w.SetName("qcd_w_weights_%s_qcd_ewk_%s_bin%d_Down"%(nam,nam,b))
    for i in range(target.GetNbinsX()):
      if i==b:
        ewk_up_w.SetBinContent(i+1,wratio_ewk_up.GetBinContent(i+1))
        ewk_down_w.SetBinContent(i+1,wratio_ewk_down.GetBinContent(i+1))
        break

    #print "HELLO filled up / down ",ewk_up.GetBinContent(b+1), ewk_down.GetBinContent(b+1)

    _fOut.WriteTObject(ewk_up_w)
    _fOut.WriteTObject(ewk_down_w)




### Photons  #################################################################################################################

  Photon = controlmc_photon.Clone(); Photon.SetName("qcd_photon_weights_denom_%s"%nam)
  Zvv_g = target.Clone(); Zvv_g.SetName("qcd_photon_weights_nom_%s"%nam)

  ###temporarily using W uncertainties on the Zs.

  gratio_ren_scale_up = Zvv_g.Clone();  gratio_ren_scale_up.SetName("qcd_photon_weights_%s_Photon_QCD_renscale_vbf_Up"%nam);
  gratio_ren_scale_up.Divide(Photon)
  for b in range(uncertainty_zoverg_mur_up.GetNbinsX()): uncertainty_zoverg_mur_up.SetBinContent(b+1,uncertainty_zoverg_mur_up.GetBinContent(b+1)+1)
  gratio_ren_scale_up.Multiply(uncertainty_zoverg_mur_up)
  _fOut.WriteTObject(gratio_ren_scale_up)
  
  gratio_ren_scale_down = Zvv_g.Clone();  gratio_ren_scale_down.SetName("qcd_photon_weights_%s_Photon_QCD_renscale_vbf_Down"%nam);
  gratio_ren_scale_down.Divide(Photon)
  for b in range(uncertainty_zoverg_mur_down.GetNbinsX()): uncertainty_zoverg_mur_down.SetBinContent(b+1,uncertainty_zoverg_mur_down.GetBinContent(b+1)+1)
  gratio_ren_scale_down.Multiply(uncertainty_zoverg_mur_down)
  _fOut.WriteTObject(gratio_ren_scale_down)

  gratio_fac_scale_up = Zvv_g.Clone(); gratio_fac_scale_up.SetName("qcd_photon_weights_%s_Photon_QCD_facscale_vbf_Up"%nam);
  gratio_fac_scale_up.Divide(Photon)
  for b in range(uncertainty_zoverg_muf_up.GetNbinsX()): uncertainty_zoverg_muf_up.SetBinContent(b+1,uncertainty_zoverg_muf_up.GetBinContent(b+1)+1)
  gratio_fac_scale_up.Multiply(uncertainty_zoverg_muf_up)
  _fOut.WriteTObject(gratio_fac_scale_up)
  
  gratio_fac_scale_down = Zvv_g.Clone();  gratio_fac_scale_down.SetName("qcd_photon_weights_%s_Photon_QCD_facscale_vbf_Down"%nam);
  gratio_fac_scale_down.Divide(Photon)
  for b in range(uncertainty_zoverg_muf_down.GetNbinsX()): uncertainty_zoverg_muf_down.SetBinContent(b+1,uncertainty_zoverg_muf_down.GetBinContent(b+1)+1)
  gratio_fac_scale_down.Multiply(uncertainty_zoverg_muf_down)
  _fOut.WriteTObject(gratio_fac_scale_down)

  gratio_pdf_up = Zvv_g.Clone();  gratio_pdf_up.SetName("qcd_photon_weights_%s_Photon_QCD_pdf_vbf_Up"%nam);
  gratio_pdf_up.Divide(Photon)
  for b in range(uncertainty_zoverg_pdf_up.GetNbinsX()): uncertainty_zoverg_pdf_up.SetBinContent(b+1,uncertainty_zoverg_pdf_up.GetBinContent(b+1)+1)
  gratio_pdf_up.Multiply(uncertainty_zoverg_pdf_up)
  _fOut.WriteTObject(gratio_pdf_up)
  
  gratio_pdf_down = Zvv_g.Clone();  gratio_pdf_down.SetName("qcd_photon_weights_%s_Photon_QCD_pdf_vbf_Down"%nam);
  gratio_pdf_down.Divide(Photon)
  for b in range(uncertainty_zoverg_pdf_down.GetNbinsX()): uncertainty_zoverg_pdf_down.SetBinContent(b+1,uncertainty_zoverg_pdf_down.GetBinContent(b+1)+1)
  gratio_pdf_down.Multiply(uncertainty_zoverg_pdf_down)
  _fOut.WriteTObject(gratio_pdf_down)

  gratio_ewk_up = Zvv_g.Clone();  gratio_ewk_up.SetName("qcd_photon_weights_%s_ewk_Up"%nam);
  gratio_ewk_up.Divide(Photon)
  for b in range(uncertainty_zoverg_ewk_up.GetNbinsX()): uncertainty_zoverg_ewk_up.SetBinContent(b+1,uncertainty_zoverg_ewk_up.GetBinContent(b+1)+1)
  gratio_ewk_up.Multiply(uncertainty_zoverg_ewk_up)
  # We are now going to uncorrelate the bins
  #_fOut.WriteTObject(ratio_ewk_up)
  
  gratio_ewk_down = Zvv_g.Clone();  gratio_ewk_down.SetName("qcd_photon_weights_%s_ewk_Down"%nam);
  gratio_ewk_down.Divide(Photon)
  for b in range(uncertainty_zoverg_ewk_down.GetNbinsX()): uncertainty_zoverg_ewk_down.SetBinContent(b+1,uncertainty_zoverg_ewk_down.GetBinContent(b+1)+1)
  gratio_ewk_down.Multiply(uncertainty_zoverg_ewk_down)
  # We are now going to uncorrelate the bins
  #_fOut.WriteTObject(ratio_ewk_down)

  Zvv_g.Divide(Photon)

  #Now lets uncorrelate the bins:
  for b in range(target.GetNbinsX()):
    #print "HELLO trying to fill up / down"
    ewk_up_g = Zvv_g.Clone(); ewk_up_g.SetName("qcd_photon_weights_%s_qcd_photon_ewk_%s_bin%d_Up"%(nam,nam,b))
    ewk_down_g = Zvv_g.Clone(); ewk_down_g.SetName("qcd_photon_weights_%s_qcd_photon_ewk_%s_bin%d_Down"%(nam,nam,b))
    for i in range(target.GetNbinsX()):
      if i==b:
        ewk_up_g.SetBinContent(i+1,gratio_ewk_up.GetBinContent(i+1))
        ewk_down_g.SetBinContent(i+1,gratio_ewk_down.GetBinContent(i+1))
        break

    #print "HELLO filled up / down ",ewk_up.GetBinContent(b+1), ewk_down.GetBinContent(b+1)

    _fOut.WriteTObject(ewk_up_g)
    _fOut.WriteTObject(ewk_down_g)

