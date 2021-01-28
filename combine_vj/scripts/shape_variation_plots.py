#!/bin/env python

#########################################################################################
# Can plot the shape variations for histograms in root/combined_model_xxx.root
# Usage: go to the root directory, type" python [path to this script] [file1] [file2] ...
# Output plots are orgnized per file and per subdir in each file
#########################################################################################

import uproot,re
import os,sys
import matplotlib
# speed up plotting for non-graphic environment
matplotlib.use('Agg')
from matplotlib import pyplot as plt

outdir = "nuisance_debug_plots"

# given all histogram names in current directory, figure out what are the nominal weight 
# names and what are the systematic variation names
def parse_ratio_weights(names):
    weights_mapping = {}
    for name in names:
        if "Up" in name or "Down" in name or name.endswith("_"):
            continue
        if not weights_mapping.has_key(name):
            weights_mapping[name] = []
    for name in names:
        for ratio_name in weights_mapping.keys():
            m = re.match(ratio_name + "_(.*)_Up", name)
            if m:
                weight_name = m.groups()[0]
                if not weight_name in weights_mapping[ratio_name]:
                    weights_mapping[ratio_name].append(weight_name)
    return weights_mapping

# run this function for each input file
def debug_file(filename):
    rootfile = uproot.open(filename)
    if not rootfile:
        print("Error: cannot open file: "+filename)
        exit()
    per_file_outdir = os.path.join(outdir, filename.replace(".root",""))
    if not os.path.exists(per_file_outdir):
        os.makedirs(per_file_outdir)
    for sub_dirname in rootfile.keys():
        if not "constraints_category" in sub_dirname:
            continue
        sub_dir = rootfile[sub_dirname]
        per_dir_outdir = os.path.join(per_file_outdir, sub_dirname)
        if not os.path.exists(per_dir_outdir):
            os.makedirs(per_dir_outdir)
        hist_names = []
        for key in sub_dir.keys():
            hist_name = str(key).split(";")[0]
            hist_names.append(hist_name)
        ratio_weights = parse_ratio_weights(hist_names)
        fig, ax = plt.subplots(1,1)
        for ratio_name, weight_names in ratio_weights.items():
            for weight_name in weight_names:
                h_nom = sub_dir[ratio_name]
                h_up  = sub_dir[ratio_name+"_"+weight_name+"_Up"]
                h_dn  = sub_dir[ratio_name+"_"+weight_name+"_Down"]
                h_nom_values, edges = h_nom.numpy 
                h_up_values = h_up.values
                h_dn_values = h_dn.values
                centers = 0.5 * (edges[1:] + edges[:-1])
                widths = (edges[1:] - edges[:-1])
                ax.plot([edges[0],edges[-1]],[0,0],color='gray')
                ax.bar(edges[:-1], h_up_values/h_nom_values-1, bottom=0, width=widths, color="red", label="up")
                ax.bar(edges[:-1], h_dn_values/h_nom_values-1, bottom=0, width=widths, color="blue", label="down")
                ax.legend()
                ax.set_xlabel("recoil")
                ax.set_ylabel("variation")
                ax.set_title(ratio_name + " " + weight_name)
                plot_file_name = ratio_name + "_" + weight_name + ".png"
                fig.savefig(os.path.join(per_dir_outdir, plot_file_name))
                print("created plot: "+os.path.join(per_dir_outdir, plot_file_name))
                ax.clear()
    return 0

def main():
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    if not len(sys.argv)>1:
        print("usage: python [path to this script] [file1] [file2] ...")
    file_list = sys.argv[1:]
    for filename in file_list:
        debug_file(filename)

if __name__ == "__main__":
    main()
