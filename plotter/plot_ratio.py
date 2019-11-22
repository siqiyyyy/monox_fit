from ROOT import *
from array import array
from tdrStyle import *
setTDRStyle()
import os
import math

def plot_ratio(process,category, model_file, outdir, lumi):

    highest = {}
    highest2 = {}
    lowest = {}

    print model_file
    f = TFile(model_file,'READ')
        
    if (process=='zmm'):
        dirname = "Z_constraints_category_"+category
        base    = "zmm_weights_"+category
        label = "R_{Z(#mu#mu)}"
        addsys  = math.sqrt(0.04*0.04 + 0.02*0.02)

    if (process=='zee'):
        dirname = "Z_constraints_category_"+category
        base    = "zee_weights_"+category
        label   = "R_{Z(ee)}"
        addsys  = math.sqrt(0.04*0.04 + 0.02*0.02 + 0.01*0.01)

    if (process=='photon'):
        dirname = "Z_constraints_category_"+category 
        base    = "photon_weights_"+category
        label   = "R_{#gamma}"
        addsys  = 0.01

    if (process=='w_weights'):
        dirname = "Z_constraints_category_"+category 
        base    = "w_weights_"+category
        label   = "R_{Z/W}"
        addsys  = 0.01

    if (process=='wen'):
        dirname = "W_constraints_category_"+category 
        base    = "wen_weights_"+category
        label   = "R_{W(e#nu)}"
        #addsys  = math.sqrt(0.02*0.02 + 0.02*0.02 + 0.01*0.01 + 0.02*0.02)
        addsys  = 0.02
        
    if (process=='wmn'):
        dirname = "W_constraints_category_"+category 
        base    = "wmn_weights_"+category
        label   = "R_{W(#mu#nu)}"
        #addsys  = math.sqrt(0.03*0.03)
        #addsys  = math.sqrt(0.03*0.03 + 0.01*0.01)
        addsys  = 0.02
        

    ratio = f.Get(dirname+"/"+base)
    up_final = ratio.Clone("ratio")
    up_ewk = ratio.Clone("ratio")
    down_final = ratio.Clone("ratio")

    for b in range(ratio.GetNbinsX()+1):
        up_final.SetBinContent(b,0.0)
        up_ewk.SetBinContent(b,0.0)
        down_final.SetBinContent(b,0.0)
        highest[b] = 0
        highest2[b] = 0
        lowest [b] = 100.0

    f.cd(dirname)
    for key in gDirectory.GetListOfKeys():
        if (key.GetClassName(),"TH1"):
            if process in key.GetName():
                #print key.GetName()
                if ('Up' in key.GetName()):
                    #print key.GetName()
                    up = f.Get(dirname+"/"+key.GetName())
                    for b in range(ratio.GetNbinsX()+1):
                        diff = up.GetBinContent(b) - ratio.GetBinContent(b)
                        highest[b] =  math.sqrt(highest[b]**2 + diff**2)
                        #bin =  ratio.GetXaxis().FindBin(1000)
                        #if b >= bin and 'scale' in key.GetName():
                        #    print key.GetName(), bin
                        #    highest[b] = math.sqrt(highest[b]**2 + (ratio.GetBinContent(b)*0.1)**2)
                        up_final.SetBinContent(b,highest[b])
                        #print diff, highest[b]

                        if ('ewk' in key.GetName() or 'sudakov' in key.GetName() or 'nnlo' in key.GetName() or 'stat' in key.GetName()):
                            diff2 = up.GetBinContent(b) - ratio.GetBinContent(b)
                            highest2[b] =  math.sqrt(highest2[b]**2 + diff2**2)
                            up_ewk.SetBinContent(b,highest2[b])

                if ('Down' in key.GetName()):
                    down = f.Get(dirname+"/"+key.GetName())
                    for b in range(ratio.GetNbinsX()+1):
                        if down.GetBinContent(b) < lowest[b]:
                            lowest[b] = down.GetBinContent(b)
                        else:
                            lowest[b] = lowest[b]
                        down_final.SetBinContent(b,lowest[b])
              
    gStyle.SetOptStat(0)

    c = TCanvas("c","c",600,600)  
    c.SetTopMargin(0.06)
    c.cd()
    c.SetRightMargin(0.04)
    c.SetTopMargin(0.07)
    c.SetLeftMargin(0.12)


    uncertband    = ratio.Clone("ratio")
    uncertband2   = ratio.Clone("ratio2")
    uncertband3   = ratio.Clone("ratio3")
    for b in range(ratio.GetNbinsX()+1):
        #err1 = abs(down_final.GetBinContent(b) -  ratio.GetBinContent(b))
        err1 = abs(up_final.GetBinContent(b) -  ratio.GetBinContent(b))
        #uncertband.SetBinError(b,max(err1,err2))
        #uncertband.SetBinError(b,err1)
        #print up_final.GetBinContent(b), addsys
        #uncertband.SetBinError(b,up_final.GetBinContent(b) + addsys*uncertband.GetBinContent(b))
        uncertband.SetBinError(b,up_final.GetBinContent(b))
        uncertband2.SetBinError(b,up_ewk.GetBinContent(b))
        uncertband3.SetBinError(b,up_final.GetBinContent(b) + addsys*uncertband.GetBinContent(b))

        #HACK
        #if b == ratio.GetNbinsX():
        #    uncertband.SetBinError(b,up_final.GetBinContent(b-1) + addsys)
        #    uncertband2.SetBinError(b,up_ewk.GetBinContent(b-1))

        #print "Uncert",b,ratio.GetBinContent(b),down_final.GetBinContent(b),up_final.GetBinContent(b), max(err1,err2)

    #uncertband.SetFillStyle(3144);
    #uncertband.SetFillColor(33);

    #uncertband.SetFillStyle(0);
    #uncertband2.SetFillColor(ROOT.kOrange+1);
    uncertband2.SetFillColor(33);
    uncertband3.SetFillColor(ROOT.kBlue+1);
    #uncertband2.SetFillColor(ROOT.kGray);
    
    if process == "photon" or process == "w_weights":
        #uncertband.SetFillColor(ROOT.kGreen+1);
        uncertband.SetFillColor(ROOT.kAzure+1);
        #uncertband.SetFillColor(ROOT.kMagenta+3);
    else:
        #uncertband.SetFillColor(ROOT.kOrange+1);
        uncertband.SetFillColor(33);
        #uncertband.SetFillColor(ROOT.kGray);

    uncertband3.GetYaxis().SetTitle(label)
    uncertband3.GetYaxis().CenterTitle()
    uncertband3.GetYaxis().SetTitleSize(0.4*c.GetLeftMargin())
    uncertband3.GetXaxis().SetTitle("U [GeV]")
    uncertband3.GetXaxis().SetTitleSize(0.4*c.GetBottomMargin())
    uncertband3.SetMaximum(2.0*ratio.GetMaximum())
    uncertband3.SetMinimum(0.5*ratio.GetMinimum())
    uncertband3.GetYaxis().SetTitleOffset(1.15)

    ratio.SetMarkerStyle(20)
    ratio.SetLineColor(1)
    ratio.SetLineWidth(2)

    uncertband3.Draw("e2")    
    uncertband.Draw("e2same")    
    uncertband2.Draw("e2same")    
    ratio.Draw("same")

    legend = TLegend(.45,.75,.82,.92)
    legend.AddEntry(ratio,"Transfer Factor (Stat Uncert)" , "p")
    if process == "photon" or process == "w_weights":
        legend.AddEntry(uncertband2 ,"Stat + Syst. (EWK)" , "f")
        legend.AddEntry(uncertband  ,"Stat + Syst. (EWK+QCD)" , "f")
        legend.AddEntry(uncertband3 ,"Stat + Syst. (EWK+QCD+Exp)" , "f")
    else:
        uncertband3.SetFillColor(33)
        legend.AddEntry(uncertband3 ,"Stat + Syst. (Exp)" , "f")
        
        
    legend.SetShadowColor(0);
    legend.SetFillColor(0);
    legend.SetLineColor(0);

    legend.Draw("same")

    latex2 = TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.035)
    latex2.SetTextAlign(31) # align right
    latex2.DrawLatex(0.87, 0.95, "{LUMI:.1f} fb^{{-1}} (13 TeV)".format(LUMI=lumi))

    latex3 = TLatex()
    latex3.SetNDC()
    latex3.SetTextSize(0.75*c.GetTopMargin())
    latex3.SetTextFont(62)
    latex3.SetTextAlign(11) # align right
    latex3.DrawLatex(0.22, 0.85, "CMS");
    latex3.SetTextSize(0.5*c.GetTopMargin())
    latex3.SetTextFont(52)
    latex3.SetTextAlign(11)
    latex3.DrawLatex(0.20, 0.8, "Preliminary");

    gPad.RedrawAxis()
    import os
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    c.SaveAs(outdir+"/rfactor_"+category+"_"+process+".pdf")
    c.SaveAs(outdir+"/rfactor_"+category+"_"+process+".png")
    c.SaveAs(outdir+"/rfactor_"+category+"_"+process+".C")
    f.Close()
    c.Close()
