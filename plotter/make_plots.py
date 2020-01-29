#!/bin/env python

from plot_PreFitPostFit import plotPreFitPostFit
from plot_datavalidation import dataValidation
from plot_ratio import plot_ratio
import os


regions = ['singlemuon','dimuon','gjets','singleelectron','dielectron']
procs = ['zmm','zee','w_weights','photon','wen','wmn']

if False:
    ## MonoV
    ws_file="../monov/root/ws_nominal_tight_2017.root"
    fitdiag_file = '../monov/fitDiagnostics_nominal_monovtight.root'
    category='monovtight'

    outdir = './plots/monov/'
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, 41.3)
    for proc in procs:
        plot_ratio(proc, category,'../monov/root/combined_model_monov_nominal_tight_2017.root', outdir, 41.3)

    dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir, 41.3)
    dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir, 41.3)
    dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir, 41.3)


    # # ### Monojet
    ws_file="../monojet/root/ws_monojet_2017.root"
    fitdiag_file = '../monojet/fitDiagnostics.root'
    category='monojet'
    outdir = './plots/monojet/'
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, 41.3)
    for proc in procs:
        plot_ratio(proc, category, '../monojet/root/combined_model_monojet_2017.root', outdir, 41.3)
    dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir,41.3)
    dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir,41.3)
    dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir,41.3)


# # ### VBF
ws_file="../vbf/root/ws_vbf_2017.root"
fitdiag_file = '../vbf/diagnostics/fitDiagnostics_vbf_2017.root'
category='vbf'
outdir = './plots/vbf/'
# for region in regions:
#     plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, 41.3)
# for proc in procs:
#     plot_ratio(proc, category, '../vbf/root/combined_model_vbf_2017.root', outdir, 41.3)
# dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir,41.3)
# dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir,41.3)
dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir,41.3)