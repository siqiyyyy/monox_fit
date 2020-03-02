#!/bin/env python
import sys
import os
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


category='vbf'
regions = ['singlemuon','dimuon','gjets','singleelectron','dielectron']
for year in [2017, 2018]:
    outdir = './plots/{year}/'.format(year=year)
    fitdiag_file = 'diagnostics/fitDiagnostics_vbf_{year}.root'.format(year=year)
    ws_file = './root/ws_vbf_{year}.root'.format(year=year)
    diffnuis_file = 'diagnostics/diffnuisances_vbf_{year}.root'.format(year=year)
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)

    dataValidation("combined",  "combinedW", category, ws_file, fitdiag_file, outdir,lumi[year], year)
    dataValidation("combinedW",  "gjets", category, ws_file, fitdiag_file, outdir,lumi[year], year)
    dataValidation("combined",  "gjets", category, ws_file, fitdiag_file, outdir,lumi[year], year)

    procs = ['zmm','zee','w_weights','photon','wen','wmn']

    for proc in procs:
        plot_ratio(proc, category, 'root/combined_model_vbf_{year}.root'.format(year=year), outdir, lumi[year], year)

    plot_nuis(diffnuis_file, outdir)
