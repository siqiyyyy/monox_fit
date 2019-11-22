from ROOT import *
from collections import defaultdict
import math, os
from math import sqrt, pow
from array import array
from tdrStyle import *
import os
setTDRStyle()


def dataValidation(region1,region2,category,ws_file, fitdiag_file, outdir):

    if region1 is "combined" and region2 is "gjets":
        name = "Z(ll)+jets / #gamma+jets"
    if region1 is "combined" and region2 is "combinedW":
        name = "Z(ll)+jets / W(l#nu)+jets"
    if region1 is "dielectron" and region2 is "gjets":
        name = "Z(ee)/#gamma"
    if region1 is "dimuon" and region2 is "gjets":
        name = "Z(mm)/#gamma"
    if region1 is "combinedW" and region2 is "gjets":
        name = "W(l#nu)+jets / #gamma+jets"
    if region1 is "singleelectron" and region2 is "gjets":
        name = "W(en)/#gamma"
    if region1 is "singlemuon" and region2 is "gjets":
        name = "W(mn)/#gamma"
    if region1 is "dielectron" and region2 is "singleelectron":
        name = "Z(ee)/W(en)"
    if region1 is "dimuon" and region2 is "singlemuon":
        name = "Z(mm)/W(mn)"


    if region1 is "dimuon" and region2 is "dielectron":
        name = "Z(mm)/Z(ee)"
    if region1 is "singlemuon" and region2 is "singleelectron":
        name = "W(mn)/W(en)"

    datalab = {"singlemuon":"Wmn", "dimuon":"Zmm", "gjets":"gjets", "signal":"signal", "singleelectron":"Wen", "dielectron":"Zee"}
  
    f_data = TFile(ws_file,"READ")
    f_data.cd("category_"+category)

    if region1 is "combined":
        h_data_1 = gDirectory.Get("Zmm_data")
        h_data_1_b = gDirectory.Get("Zee_data")
        h_data_1.Add(h_data_1_b)
    elif region1 is "combinedW":
        h_data_1 = gDirectory.Get("Wmn_data")
        h_data_1_b = gDirectory.Get("Wen_data")
        h_data_1.Add(h_data_1_b)

    else:
        h_data_1 = gDirectory.Get(datalab[region1]+"_data")
    h_data_1.Sumw2()
    if not "monov" in category:
        h_data_1.Rebin(2)

    if region2 is "combinedW":    
        h_data_2 = gDirectory.Get("Wmn_data")
        h_data_2_b = gDirectory.Get("Wen_data")
        h_data_2.Add(h_data_2_b)
    else:
        h_data_2 = gDirectory.Get(datalab[region2]+"_data")

    h_data_2.Sumw2()
    if not "monov" in category:
        h_data_2.Rebin(2)

    h_data_1.Divide(h_data_2)

    f_mlfit = TFile(fitdiag_file,'READ')

    channel = {"singlemuon":category+"_singlemu", "dimuon":category+"_dimuon", "gjets":category+"_photon", "signal":category+"_signal", "singleelectron":category+"_singleel", "dielectron":category+"_dielec"}

    h_prefit = {}

    if region1 is "combined":    
        h_prefit[region1] = f_mlfit.Get("shapes_prefit/"+category+"_dimuon/total_background")
        print f_mlfit, "shapes_prefit/"+category+"_dielec/total_background"
        h_mc_2 = f_mlfit.Get("shapes_prefit/"+category+"_dielec/total_background")
        h_prefit[region1].Add(h_mc_2)
    elif region1 is "combinedW":    
        h_prefit[region1] = f_mlfit.Get("shapes_prefit/"+category+"_singlemu/total_background")
        h_mc_2 = f_mlfit.Get("shapes_prefit/"+category+"_singleel/total_background")
        h_prefit[region1].Add(h_mc_2)
    else:
        h_prefit[region1] = f_mlfit.Get("shapes_prefit/"+channel[region1]+"/total_background")
    h_prefit[region1].Sumw2()
    if not "monov" in category:
        h_prefit[region1].Rebin(2)

    if region2 is "combinedW":    
        h_prefit[region2] = f_mlfit.Get("shapes_prefit/"+category+"_singlemu/total_background")
        h_mc2_2 = f_mlfit.Get("shapes_prefit/"+category+"_singleel/total_background")
        h_prefit[region2].Add(h_mc2_2)
    else:
        h_prefit[region2] = f_mlfit.Get("shapes_prefit/"+channel[region2]+"/total_background")

    h_prefit[region2].Sumw2()
    if not "monov" in category:
        h_prefit[region2].Rebin(2)
    
    h_prefit[region1].Divide(h_prefit[region2])
    
    if region2 is "gjets":
        uncFile     = TFile('../makeWorkspace/sys/theory_unc_ZG.root')
        uncertainties = [
            uncFile.ZG_QCDScale_met,
            uncFile.ZG_QCDShape_met,
            uncFile.ZG_QCDProcess_met,
            uncFile.ZG_NNLOEWK_met,
            uncFile.ZG_Sudakov1_met,
            uncFile.ZG_Sudakov2_met,
            uncFile.ZG_NNLOMiss1_met,
            uncFile.ZG_NNLOMiss2_met,
            uncFile.ZG_MIX_met,
            uncFile.ZG_PDF_met
            ]
        #uncertainties += ["SFreco"]
        
    else:
        uncFile     = TFile('../makeWorkspace/sys/theory_unc_ZW.root')
        uncertainties = [
            uncFile.ZW_QCDScale_met,
            uncFile.ZW_QCDShape_met,
            uncFile.ZW_QCDProcess_met,
            uncFile.ZW_NNLOEWK_met,
            uncFile.ZW_Sudakov1_met,
            uncFile.ZW_Sudakov2_met,
            uncFile.ZW_NNLOMiss1_met,
            uncFile.ZW_NNLOMiss2_met,
            uncFile.ZW_MIX_met,
            uncFile.ZW_PDF_met
            ]
        uncertainties += ["SFreco"]

    #print uncertainties

    for iBin in range(h_prefit[region1].GetNbinsX()):
        if iBin == 0:
            continue
        
        #sumw2 = math.pow((h_prefit[region1].GetBinError(iBin)),2)
        sumw2 = pow((h_prefit[region1].GetBinError(iBin)),2)
        print region1, region2, "staterror", sqrt(sumw2)
        
        for uncert in uncertainties:
            #print uncert
            if region2 is not "gjets" and type(uncert) == str :#uncert.startswith("SF"):
                if "reco" in uncert:
                    value = 0.01
                else:
                    value = 0.02

                if region2.startswith("single"):
                    sumw2 += pow((h_prefit[region1].GetBinContent(iBin) * (value) ),2)
                else:
                    sumw2 += pow((h_prefit[region1].GetBinContent(iBin) * (value*2) ),2)

            else:
                findbin =  uncert.FindBin(h_prefit[region1].GetBinCenter(iBin))
                sumw2 += pow((h_prefit[region1].GetBinContent(iBin) * (uncert.GetBinContent(findbin))),2)
            
        print region1, region2, iBin, "total", sqrt(sumw2)

        h_prefit[region1].SetBinError(iBin,sqrt(sumw2))
        #h_prefit[region1].SetBinError(iBin,math.sqrt(sumw2))


    c = TCanvas("c","c",600,650)
    SetOwnership(c,False)
    #c.SetTopMargin(0.08)

    c.SetBottomMargin(0.3)
    c.SetRightMargin(0.06)

    c.SetLeftMargin(0.15)

    c.cd()

    h_clone = h_prefit[region1].Clone()
    h_clone.SetFillColor(kGray) #SetFillColor(ROOT.kYellow)                                                                                   
    h_clone.SetLineColor(kGray) #SetLineColor(1)                                                                                                        
    h_clone.SetLineWidth(1)
    h_clone.SetMarkerSize(0)
    h_clone.GetXaxis().SetTitle("")
    h_clone.GetXaxis().SetLabelSize(0)
    h_clone.GetYaxis().SetTitle(name)
    #h_clone.GetYaxis().CenterTitle()
    h_clone.GetYaxis().SetTitleSize(0.05)
    h_clone.GetYaxis().SetLabelSize(0.04)
    h_clone.GetYaxis().SetTitleOffset(1.50)
    h_clone.SetMinimum(0)

    h_clone.SetMaximum(h_clone.GetMaximum()*2)

    h_clone.Draw("e2")

    h_prefit[region1].SetLineColor(2)
    h_prefit[region1].Draw("samehist")
    h_data_1.SetLineColor(1)
    h_data_1.SetMarkerColor(1)
    h_data_1.SetMarkerStyle(20)
    h_data_1.Draw("same")


    #legend = TLegend(0.35, 0.79, 0.95, .92);

    legend = TLegend(0.35, 0.77, 0.95, 0.90);

    legend.SetFillStyle(0);
    legend.AddEntry(h_data_1, name+" Data", "elp")

    if region2 is 'gjets' and region1 is 'combinedW':
        legend.AddEntry(h_prefit[region1], name+" MC      ", "l")
    elif region2 is 'gjets' and region1 is 'combined':
        legend.AddEntry(h_prefit[region1], name+" MC        ", "l")
    else:
        legend.AddEntry(h_prefit[region1], name+" MC", "l")

    legend.SetShadowColor(0);
    legend.SetFillColor(0);
    legend.SetLineColor(0);
    legend.SetLineStyle(0);
    legend.SetBorderSize(0);
    legend.Draw("same")

    latex2 = TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.6*c.GetTopMargin())
    latex2.SetTextFont(42)
    latex2.SetTextAlign(31) # align right                                                                                                                                                                                             
    latex2.DrawLatex(0.94, 0.95,"35.9 fb^{-1} (13 TeV)")
    latex2.SetTextSize(0.6*c.GetTopMargin())
    latex2.SetTextFont(62)
    latex2.SetTextAlign(11) # align right                                                                                                                                                                                                  
    latex2.DrawLatex(0.200, 0.85, "CMS")
    latex2.SetTextSize(0.6*c.GetTopMargin())
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    offset = 0.005
    #latex2.DrawLatex(0.20, 0.80, "Preliminary")          

    categoryLabel = TLatex();
    categoryLabel.SetNDC();
    #categoryLabel.SetTextSize(0.5*c.GetTopMargin());
    categoryLabel.SetTextSize(0.042);
    categoryLabel.SetTextFont(42);
    categoryLabel.SetTextAlign(11);
    categoryLabel.DrawLatex(0.200,0.80,category);
    categoryLabel.Draw("same");


    pad = TPad("pad", "pad", 0.0, 0.0, 1.0, 0.9)
    SetOwnership(pad,False)
    
    pad.SetTopMargin(0.7)
    pad.SetRightMargin(0.06)
    pad.SetLeftMargin(0.15)
    pad.SetFillColor(0)
    pad.SetGridy(0)
    
    pad.SetFillStyle(0)
    pad.Draw()
    pad.cd(0)
    
    dummy2 = h_data_1.Clone("dummy")
    dummy2.Sumw2()
    dummy2.Divide(h_prefit[region1])
    #for i in range(1,dummy2.GetNbinsX()):
    #    print dummy2.GetBinContent(i)
    #    dummy2.SetBinContent(i,1.0)

    ratiosys = dummy2.Clone("ratiosys")
    for hbin in range(0,ratiosys.GetNbinsX()+1):
        print "RATIOSYS", ratiosys.GetBinError(hbin+1), h_clone.GetBinError(hbin+1), h_data_1.GetBinError(hbin+1)
        ratiosys.SetBinContent(hbin+1,1.0)
        if h_clone.GetBinContent(hbin+1)>0:
            ratiosys.SetBinError(hbin+1,h_clone.GetBinError(hbin+1)/h_clone.GetBinContent(hbin+1))

    dummy2.GetYaxis().SetTitle("Data / Pred.")
    dummy2.GetXaxis().SetTitle("Hadronic recoil p_{T} [GeV]")
    dummy2.GetXaxis().SetTitleOffset(1.15)
    dummy2.GetXaxis().SetTitleSize(0.05)
    dummy2.GetXaxis().SetLabelSize(0.04)

    #dummy2.SetLineColor(0)
    #dummy2.SetMarkerColor(0)
    #dummy2.SetLineWidth(0)
    #dummy2.SetMarkerSize(0)
    dummy2.GetYaxis().SetLabelSize(0.04)
    dummy2.GetYaxis().SetNdivisions(5);
    #dummy2.GetXaxis().SetNdivisions(510)
    dummy2.GetYaxis().CenterTitle()
    dummy2.GetYaxis().SetTitleSize(0.04)
#    dummy2.GetYaxis().SetLabelSize(0.04)
    dummy2.GetYaxis().SetTitleOffset(1.5)
    dummy2.SetMaximum(1.6)                                                                        
    dummy2.SetMinimum(0.4) 

    dummy2.Draw()

    ratiosys.SetFillColor(kGray) #SetFillColor(ROOT.kYellow)
    ratiosys.SetLineColor(kGray) #SetLineColor(1)
    ratiosys.SetLineWidth(1)
    ratiosys.SetMarkerSize(0)
    ratiosys.Draw("e2same")

    dummy2.Draw("same")
    
    f1 = TF1("f1","1",-5000,5000);
    f1.SetLineColor(1);
    f1.SetLineStyle(2);
    f1.SetLineWidth(1);
    f1.Draw("same")

    pad.RedrawAxis("G sameaxis")
    gPad.RedrawAxis()

    #ratiosys.SetFillColor(kGray) #SetFillColor(ROOT.kYellow)
    #ratiosys.SetLineColor(kGray) #SetLineColor(1)
    #ratiosys.SetLineWidth(1)
    #ratiosys.SetMarkerSize(0)
    #ratiosys.Draw("e2same")
    #g_ratio_pre.Draw("epsame")

        

    outdir = "./output/"
    import os
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    c.SaveAs(outdir+region1+"_"+region2+"_cat_"+category+"_ratio.pdf")
    c.SaveAs(outdir+region1+"_"+region2+"_cat_"+category+"_ratio.png")
    c.SaveAs(outdir+region1+"_"+region2+"_cat_"+category+"_ratio.C")

#dataValidation("dielectron","gjets","monojet")
#dataValidation("dimuon"    ,"gjets","monojet")
# ws_file="../monojet/root/ws_monojet_2017.root"
# fitdiag_file = '../monojet/higgsCombineTest.FitDiagnostics.mH120.root'
# dataValidation("combined"  ,  "gjets",  "monojet", ws_file, fitdiag_file)
# dataValidation("combinedW", "gjets"    ,"monojet", ws_file, fitdiag_file)
# dataValidation("combined" , "combinedW","monojet", ws_file, fitdiag_file)



#dataValidation("singlemuon","singleelectron","monojet")
#dataValidation("dimuon","dielectron","monojet")

#dataValidation("singleelectron","gjets","monojet")
#dataValidation("singlemuon","gjets","monojet")

#dataValidation("dielectron","gjets","monojet")
#dataValidation("dimuon","gjets","monojet")
#dataValidation("dielectron","singleelectron","monojet")
#dataValidation("dimuon","singlemuon","monojet")


#dataValidation("dielectron","gjets","monov")
#dataValidation("dimuon"    ,"gjets","monov")
#dataValidation("combined"  ,"gjets","monov")

#dataValidation("combinedW","gjets"    ,"monov")
#dataValidation("combined" ,"combinedW","monov")

#dataValidation("singlemuon","singleelectron","monov")
#dataValidation("dimuon","dielectron","monov")

#dataValidation("singleelectron","gjets","monov")
#dataValidation("singlemuon","gjets","monov")

#dataValidation("dielectron","gjets","monov")
#dataValidation("dimuon","gjets","monov")
#dataValidation("dielectron","singleelectron","monov")
#dataValidation("dimuon","singlemuon","monov")

