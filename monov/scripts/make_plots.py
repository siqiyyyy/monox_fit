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


## MonoV
for year in [2017,2018]:
    category='monovtight'
    filler = {
        "year" : year,
        "category" : "monovtight"
    }
    ws_file="root/ws_monov_nominal_tight_{year}.root".format(**filler)
    fitdiag_file = 'diagnostics/fitDiagnostics_nominal_{category}_{year}.root'.format(**filler)
    diffnuis_file = 'diagnostics/diffnuisances_nominal_{category}_{year}.root'.format(**filler)
    model_file = "root/combined_model_monov_nominal_tight_{year}.root".format(**filler)

    outdir = './plots/{year}/'.format(**filler)
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
    for proc in procs:
        plot_ratio(proc, category, model_file, outdir, lumi[year], year)

    dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir, lumi[year], year)

    plot_nuis(diffnuis_file, outdir)