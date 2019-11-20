This is the fitting code for the mono-x analysis. It is adapted to run on TH1D histograms.


## Step 1: Converting inputs into a workspace
This script reads the histograms from the bucoffea legacy limit scripts and converts them into a RooWorkspace. Output is saved into `mono-x.root`. Usage:

```bash
./make_ws.py /path/to/input.root --category your_category --out workspace.root
```

use `./make_ws.py --help` for help.

## Step 2: Creating the full model from the workspace

The actual model is then created using the `runModel.py` script. This script reads the workspace from `workspace.root`. Usage:

```bash
./runModel.py /path/to/workspace.root --categories category1,category2 --out combined_model.root
```

The links between the control and signal regions are set in W_constraints.py and Z_constraints.py files, which can be modified to define the uncertainties. The `combined_model.root` file contains the full model necessary to run the limits.
