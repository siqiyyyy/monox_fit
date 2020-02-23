#!/bin/env python
import os
import sys
sys.path.append(os.path.abspath("../../../plotter"))
from plot_PreFitPostFit import plotPreFitPostFit
from plot_datavalidation import dataValidation
from plot_ratio import plot_ratio
from plot_diffnuis import plot_nuis
lumi ={
    2017 : 41.5,
    2018: 59.7
}
regions = ['singlemuon','dimuon','gjets','singleelectron','dielectron']
procs = ['zmm','zee','w_weights','photon','wen','wmn']

### Monojet
for year in [2017,2018]:
    ws_file = "root/ws_monojet_{year}.root".format(year=year)
    fitdiag_file = 'diagnostics/fitDiagnostics_monojet_{year}.root'.format(year=year)
    diffnuis_file = 'diagnostics/diffnuisances_monojet_{year}.root'.format(year=year)
    category='monojet'
    outdir = './plots/{year}/'.format(year=year)
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
    for proc in procs:
        plot_ratio(proc, category, 'root/combined_model_monojet_{year}.root'.format(year=year), outdir, lumi[year],year)
    dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir,lumi[year],year)

    plot_nuis(diffnuis_file, outdir)
    