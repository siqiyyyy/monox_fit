This is the fitting code for the mono-x analysis. It is adapted to run on TH1D histograms.
First you need to run make_ws.py script. This inputs the histograms Andreas prepares and outputs a file called mono-x.root which has a workspace that includes all the histograms. Then you you need to run the runModel.py script. This inputs the mono-x.root and outputs combined_model.root. It is designed to run all categories simulatenously, but you can suppress or enable at will by modifying: "categories = ["monojet","monov"]" in the beginning of the script. The links between the control and signal regions are set in W_constraints.py and Z_constraints.py files. This is where you would input all uncertainties.

The output file, combined_model.root is what you will need to run limits.
