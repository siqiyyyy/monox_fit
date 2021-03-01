import ROOT
import os
import sys

ROOT.gROOT.SetBatch(True)

files = ["../monojet_jes_jer_tf_uncs_jer_smeared.root", "../monojet_jes_jer_tf_uncs_not_jer_smeared.root"]

for input_file_name in files:
    output_file_name = input_file_name.replace(".root","_symmetrized.root")
    input_file = ROOT.TFile.Open(input_file_name)
    output_file = ROOT.TFile.Open(output_file_name, "recreate")

    hist_names = [hist_name.GetName().split(";")[0] for hist_name in input_file.GetListOfKeys()]
    up_hist_names = [hist_name for hist_name in hist_names if "Up" in hist_name]
    count=0
    for up_hist_name in up_hist_names:
        count+=1
        down_hist_name = up_hist_name.replace("Up","Down")
        up = input_file.Get(up_hist_name)
        down = input_file.Get(down_hist_name)
    
        new_up = up.Clone()
        new_up.Reset()
        new_down = down.Clone()
        new_down.Reset()
        
        for i in range(1,new_up.GetNbinsX()+1):
            cont_up = up.GetBinContent(i)
            cont_down = down.GetBinContent(i)
        
            # Step 1: decide which direction is "Up"
            # bigger variation gets do win
            if cont_up > cont_down:
                direction = +1
            else:
                direction = -1
        
            # Step 2: New unc = average of old variations
            average_unc = 0.5*(abs(cont_up-1) + abs(cont_down-1))
            new_up.SetBinContent(i, 1 + direction * average_unc)
            new_down.SetBinContent(i, 1 - direction * average_unc)
        
        # Step 3: Write to new file
        # use same histogram names, so we dont have
        # to change our other code
        new_up.SetDirectory(output_file)
        new_up.Write(up.GetName())
        
        new_down.SetDirectory(output_file)
        new_down.Write(down.GetName())
    input_file.Close()
    output_file.Close()

# Validate
canv = ROOT.TCanvas("canv","canv", 800, 400)
canv.Divide(2)
for input_file_name in files:
    output_file_name = input_file_name.replace(".root","_symmetrized.root")
    input_file = ROOT.TFile.Open(input_file_name)
    output_file = ROOT.TFile.Open(output_file_name)

    old_list = [key.GetName() for key in input_file.GetListOfKeys()]
    new_list = [key.GetName() for key in output_file.GetListOfKeys()]
    assert len(old_list)==len(new_list)

    outdir_name = input_file_name.split("/")[-1].replace(".root","")
    if not os.path.exists(outdir_name):
        os.makedirs(outdir_name)

    hist_names = [hist_name.GetName().split(";")[0] for hist_name in input_file.GetListOfKeys()]
    up_hist_names = [hist_name for hist_name in hist_names if "Up" in hist_name]
    for up_hist_name in up_hist_names:
        down_hist_name = up_hist_name.replace("Up","Down")
        up = input_file.Get(up_hist_name)
        down = input_file.Get(down_hist_name)
        new_up = output_file.Get(up_hist_name)
        new_down = output_file.Get(down_hist_name)

        max_val = max(up.GetMaximum(), down.GetMaximum(), new_up.GetMaximum(), new_down.GetMaximum())
        min_val = min(up.GetMinimum(), down.GetMinimum(), new_up.GetMinimum(), new_down.GetMinimum())
        up.GetYaxis().SetRangeUser(min_val-0.1*abs(min_val-1),max_val+0.1*abs(max_val-1))
        up.SetLineColorAlpha(ROOT.kRed,0.5)
        down.SetLineColorAlpha(ROOT.kBlue,0.5)
        new_up.GetYaxis().SetRangeUser(min_val-0.1*abs(min_val-1),max_val+0.1*abs(max_val-1))
        new_up.SetLineColorAlpha(ROOT.kRed,1)
        new_down.SetLineColorAlpha(ROOT.kBlue,1)

        canv.cd(1)
        up.Draw("hist")
        down.Draw("same hist")
        canv.cd(2)
        new_up.Draw("hist")
        new_down.Draw("same hist")

        plot_name = os.path.join(outdir_name, up_hist_name.replace("Up","")+".png")
        canv.Print(plot_name)
    input_file.Close()
    output_file.Close()


