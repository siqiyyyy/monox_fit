# Configuration for a simple monojet topology. Use this as a template for your own Run-2 mono-X analysis
# First provide ouput file name in out_file_name field 

out_file_name = 'mono-x.root'

bins = [250.0, 280.0, 310.0, 340.0, 370.0, 400.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0, 1400.0]

monojet_category = {
	    'name':"monojet"
            ,'in_file_name':"/eos/cms/store/group/phys_exotica/monojet/zdemirag/panda/monojet/v2/fitting/fittingForest_all.root"
            ,"cutstring":"(met>250)"
            ,"varstring":["met",250,1400]
            ,"weightname":"weight"
            ,"bins":bins[:]
            ,"additionalvars":[['met',100,250,1400]]
            ,"pdfmodel":0
            ,"samples":
	   	{  
		  # Signal Region
                   "Zvv_signal"           :['signal','zjets',1,0]
                  ,"Zll_signal"           :['signal','zll',1,0]
                  ,"Wlv_signal"           :['signal','wjets',1,0]
                  ,"ttbar_signal"         :['signal','top',1,0]
                  ,"ST_signal"            :['signal','top',1,0]
                  ,"QCD_signal"           :['signal','qcd',1,0]
                  ,"Pho_signal"           :['signal','gjets',1,0]
                  ,"Diboson_signal"       :['signal','diboson',1,0]
                  ,"Data_signal"          :['signal','data',0,0]
                  #,"Vector_MonoJ_NLO_Mphi-1750_Mchi2-10_gSM-0p25_gDM-1p0_Mchi1-1_ctau-10_signal"      :['signal','mj_1750_10_ct10',1,1]
                  #,"Vector_MonoJ_NLO_Mphi-1750_Mchi2-300_gSM-0p25_gDM-1p0_Mchi1-1_ctau-100_signal"    :['signal','mj_1750_300_ct100',1,1]
                  #,"Vector_MonoJ_NLO_Mphi-1750_Mchi2-300_gSM-0p25_gDM-1p0_Mchi1-1_ctau-100000_signal" :['signal','mj_1750_300_ct100000',1,1]
                  #,"Vector_MonoJ_NLO_Mphi-1750_Mchi2-500_gSM-0p25_gDM-1p0_Mchi1-1_ctau-100000_signal" :['signal','mj_1750_500_ct100000',1,1]

                  # Single muon-Control
                  ,"Wlv_singlemuon"        :['Wmn','wjets',1,1]
                  ,"Zll_singlemuon"        :['Wmn','zll',1,0]
                  ,"ttbar_singlemuon"      :['Wmn','top',1,0]
                  ,"ST_singlemuon"         :['Wmn','top',1,0]
                  ,"QCD_singlemuon"        :['Wmn','qcd',1,0]
                  ,"Diboson_singlemuon"    :['Wmn','diboson',1,0]
                  ,"Data_singlemuon"       :['Wmn','data',0,0]

                  # Single electron-Control
                  ,"Wlv_singleelectron"    :['Wen','wjets',1,1]
                  ,"Zll_singleelectron"    :['Wen','zll',1,0]
                  ,"ttbar_singleelectron"  :['Wen','top',1,0]
                  ,"ST_singleelectron"     :['Wen','top',1,0]
                  ,"QCD_singleelectron"    :['Wen','qcd',1,0]
                  ,"Diboson_singleelectron":['Wen','diboson',1,0]
                  ,"Data_singleelectron"   :['Wen','data',0,0]

                  # Double muon-Control	
                  ,"Zll_dimuon"            :['Zmm','zll',1,1]
                  ,"ttbar_dimuon"          :['Zmm','top',1,0]
                  ,"ST_dimuon"             :['Zmm','top',1,0]
                  ,"QCD_dimuon"            :['Zmm','qcd',1,0]
                  ,"Diboson_dimuon"        :['Zmm','diboson',1,0]
                  ,"Data_dimuon"           :['Zmm','data',0,0]

                  # Di electron-Control
                  ,"Zll_dielectron"        :['Zee','zll',1,1]
                  ,"ttbar_dielectron"      :['Zee','top',1,0]
                  ,"ST_dielectron"         :['Zee','top',1,0]
                  ,"QCD_dielectron"        :['Zee','qcd',1,0]
                  ,"Diboson_dielectron"    :['Zee','diboson',1,0]
                  ,"Data_dielectron"       :['Zee','data',0,0]

                  # Gamma + Jets
                  ,"Pho_photon"            :['gjets','gjets',1,1]
                  ,"QCD_photon"            :['gjets','qcd',1,0]
                  ,"Data_photon"           :['gjets','data',0,0]

   	},
}

categories = [monojet_category]
