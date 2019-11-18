from ROOT import *
from collections import defaultdict
import math
from array import array
from tdrStyle import *
setTDRStyle()

from pretty import plot_ratio

f_mlfit   = {}
h_bkg_pre = {}
h_bkg_pos = {}
h_data    = {}

channel   = {"monojet_singlemu":"ch3", "monojet_dimuon":"ch2", "monojet_signal":"ch1", "monojet_singleel":"ch5", "monojet_dielec":"ch5", "monojet_photon":"ch4"}
#processes = {"qcd":"QCD", "zll":"qcd_zjets", "gjets":"Znunu", "top":"Top", "diboson":"Dibosons", "wjets":"qcd_wjets", "zjets":"qcd_znunu", "ggh":"ggH_hinv", "wh":"WH_hinv", "zh":"ZH_hinv", "vbf":"qqH_hinv"}
processes = {"zll":"qcd_zll", "gjets":"gjets", "wjets":"qcd_wjets", "zjets":"qcd_znunu", "ggh":"ggH_hinv", "wh":"WH_hinv", "zh":"ZH_hinv", "vbf":"qqH_hinv"}

infolder = "../../v3/monojet/fitDiagnostics.root"
f_mlfit[0] = TFile(infolder,"READ")
f_mlfit[1] = TFile("hig-17-023/HiggsInvisibleCombination/fitDiagnostics.root","READ")

c = {}

folder = '/afs/cern.ch/user/z/zdemirag/www/monojet_fullrun2/v3/'
status = "prefit"

for zeynep, raffaele in channel.iteritems():
  #for proc_zeynep, proc_raffaele in processes.iteritems():
    
    print "Checking channel", zeynep
    '''
    print "shapes_"+status+"/"+zeynep+"/"+proc_zeynep
    #h_data[0] = f_mlfit[0].Get("shapes_"+status+"/"+zeynep+"/data")
    h_data[0] = f_mlfit[0].Get("shapes_"+status+"/"+zeynep+"/"+proc_zeynep)
    print "shapes_"+status+"/"+raffaele+"/"+proc_raffaele
    #h_data[1] = f_mlfit[1].Get("shapes_"+status+"/"+raffaele+"/data")
    h_data[1] = f_mlfit[1].Get("shapes_"+status+"/"+raffaele+"/"+proc_raffaele)

    cdata = TCanvas()
    cdata.SetLogy()

    h_data[0].GetYaxis().SetTitle('Events/GeV')
    h_data[0].GetYaxis().CenterTitle()
    h_data[0].GetYaxis().SetTitleOffset(1.4)
    h_data[0].GetYaxis().SetTitleSize(0.04)
    h_data[0].GetXaxis().SetTitle('Recoil')

    h_data[0].SetMarkerStyle(20)
    h_data[0].Draw("AP")
    h_data[1].SetMarkerColor(2)
    h_data[1].SetLineColor(2)
    h_data[1].SetMarkerStyle(20)
    h_data[1].Draw("sameP")

    legend = TLegend(.60,.65,.82,.92)
    legend.SetShadowColor(0);
    legend.SetFillColor(0);
    legend.SetLineColor(0);
    legend.AddEntry(h_data[0],"MIT",'p')
    legend.AddEntry(h_data[1],"UCSD",'p')
    legend.Draw("same")

    cdata.SaveAs(folder+"/"+zeynep+"_data_"+status+".pdf")
    cdata.SaveAs(folder+"/"+zeynep+"_data_"+status+".png")
    '''
    for p_s, p_r in processes.iteritems():
                
        print "Comparing process", "shapes_prefit/"+zeynep+"/"+p_s , "vs shapes_prefit/"+raffaele+"/"+p_r
    
        h_bkg_pre[0] = f_mlfit[0].Get("shapes_"+status+"/"+zeynep+"/"+p_s)        
        h_bkg_pre[1] = f_mlfit[1].Get("shapes_"+status+"/"+raffaele+"/"+p_r) 
        
        if h_bkg_pre[0] and h_bkg_pre[1]:

            c = TCanvas("c","c",600,700)
            c.SetLogy()
            c.SetBottomMargin(0.3)
            c.SetRightMargin(0.06)

            h_bkg_pre[0].Sumw2()
            h_bkg_pre[1].Sumw2()

            plot_zeynep = h_bkg_pre[0].Clone()

            h_bkg_pre[0].SetLineWidth(2)
            h_bkg_pre[0].Draw("hist")
            h_bkg_pre[0].GetYaxis().SetTitle('Events/GeV')
            h_bkg_pre[0].GetYaxis().CenterTitle()
            h_bkg_pre[0].GetYaxis().SetTitleOffset(1.4)
            h_bkg_pre[0].GetYaxis().SetTitleSize(0.04)
            h_bkg_pre[0].GetXaxis().SetLabelSize(0)
            h_bkg_pre[0].GetXaxis().SetTitle('')
            h_bkg_pre[1].SetLineColor(2)
            h_bkg_pre[1].SetLineWidth(2)
            h_bkg_pre[1].Draw("histsame")

            legend = TLegend(.60,.65,.82,.92)
            legend.SetShadowColor(0);
            legend.SetFillColor(0);
            legend.SetLineColor(0);
            legend.AddEntry(h_bkg_pre[0],"2017 Analysis")
            legend.AddEntry(h_bkg_pre[1],"2016 Analysis")
            legend.Draw("same")

            Pad = TPad("pad", "pad", 0.0, 0.0, 1.0, 0.9)
            Pad.SetTopMargin(0.7)
            Pad.SetRightMargin(0.06)
            Pad.SetFillColor(0)
            Pad.SetGridy(1)
            Pad.SetFillStyle(0)
            Pad.Draw()
            Pad.cd(0)

            ratio = plot_ratio(False,plot_zeynep,h_bkg_pre[1],"Recoil",'2017/2016',0,2,5)
            ratio.Draw("HIST")

            c.SaveAs(folder+"/"+zeynep+"_"+p_s+"_"+status+".pdf")
            c.SaveAs(folder+"/"+zeynep+"_"+p_s+"_"+status+".png")
            
            del h_bkg_pre[0], h_bkg_pre[1]
