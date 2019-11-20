This is the fitting code for the mono-x analysis. It is adapted to run on TH1D histograms.


## Step 1: Converting inputs into a workspace
This script reads the histograms from the bucoffea legacy limit scripts and converts them into a RooWorkspace. Output is saved into `mono-x.root`. Usage:

```bash
./make_ws.py /path/to/input.root --category your_category
```

use `./make_ws.py --help` for help.

## Step 2: Creating the full model from the workspace

The actual model is then created using the `runModel.py` script. This script reads the workspace from `mono-x.root`.It is designed to run all categories simulatenously, but you can suppress or enable at will by modifying: `categories = ["monojet","monov"]` in the beginning of the script. The links between the control and signal regions are set in W_constraints.py and Z_constraints.py files. This is where you would input all uncertainties. The output file, `combined_model.root` is what you will need to run limits.
