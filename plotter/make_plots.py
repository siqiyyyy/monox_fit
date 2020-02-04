#!/bin/env python

from plot_PreFitPostFit import plotPreFitPostFit
from plot_datavalidation import dataValidation
from plot_ratio import plot_ratio
import os
import sys
lumi ={
    2017 : 41.5,
    2018: 59.7
}
regions = ['singlemuon','dimuon','gjets','singleelectron','dielectron']
procs = ['zmm','zee','w_weights','photon','wen','wmn']

categories = sys.argv[1:]
if 'monov' in categories:
    ## MonoV
    ws_file="../monov/root/ws_nominal_tight_2017.root"
    fitdiag_file = '../monov/fitDiagnostics_nominal_monovtight.root'
    category='monovtight'

    outdir = './plots/monov/'
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year])
    for proc in procs:
        plot_ratio(proc, category,'../monov/root/combined_model_monov_nominal_tight_2017.root', outdir, lumi[year])

    dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir, lumi[year])
    dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir, lumi[year])
    dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir, lumi[year])


if 'monojet' in categories:
    # # ### Monojet
    ws_file="../monojet/root/ws_monojet_2017.root"
    fitdiag_file = '../monojet/fitDiagnostics.root'
    category='monojet'
    outdir = './plots/monojet/'
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year])
    for proc in procs:
        plot_ratio(proc, category, '../monojet/root/combined_model_monojet_2017.root', outdir, lumi[year])
    dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year])
    dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year])
    dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir,lumi[year])


# # ### VBF
# for year in [2017, 2018]:
#     ws_file="../vbf/root/ws_vbf_{YEAR}.root".format(YEAR=year)
#     fitdiag_file = '../vbf/diagnostics/fitDiagnostics_vbf_{YEAR}.root'.format(YEAR=year)
#     category='vbf'
#     outdir = './plots/vbf/'
#     regions = ['singlemuon','dimuon','singleelectron','dielectron']

#     for region in regions:
#         plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
#     dataValidation("combined",  "combinedW", category, ws_file, fitdiag_file, outdir,lumi[year], year)


### VBF photon
if 'vbf' in categories:
    category='vbf'
    regions = ['singlemuon','dimuon','gjets','singleelectron','dielectron']
    outdir = './plots/vbf/'
    for year in [2017, 2018]:
        if year == 2017:
            ws_file="../vbf/tmp/mono-x.root"
            fitdiag_file = '/uscms_data/d3/aandreas/legacy_limit/monox_fit/vbf/tmp/fitDiagnostics.root'
        elif year == 2018:
            ws_file="../vbf/tmp/mono-x_2018.root"
            fitdiag_file = '../vbf/tmp/withphotons/fitDiagnostics_2018.root'

        for region in regions:
            plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)

        dataValidation("combined",  "combinedW", category, ws_file, fitdiag_file, outdir,lumi[year], year)
        dataValidation("combinedW",  "gjets", category, ws_file, fitdiag_file, outdir,lumi[year], year)
        dataValidation("combined",  "gjets", category, ws_file, fitdiag_file, outdir,lumi[year], year)

        procs = ['zmm','zee','w_weights','photon','wen','wmn']

        for proc in procs:
            plot_ratio(proc, category, '/uscms_data/d3/aandreas/legacy_limit/monox_fit/vbf/tmp/combined_model.root', outdir, lumi[year], year)
