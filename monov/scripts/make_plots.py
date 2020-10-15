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


def monov_plot_channels_separately():
    ### Years fit separately
    for year in [2017,2018]:
        for wp in 'loose', 'tight':
            model_file = "root/combined_model_monov_nominal_{WP}.root".format(WP=wp)
            ws_file="root/ws_monov_nominal_{WP}.root".format(WP=wp)
            category='monov{WP}_{YEAR}'.format(WP=wp, YEAR=year)
            filler = {
                "WP" : wp,
                "year" : year,
                "category" : category
            }
            fitdiag_file = 'diagnostics/fitDiagnostics_nominal_{category}.root'.format(**filler)
            diffnuis_file = 'diagnostics/diffnuisances_nominal_{category}.root'.format(**filler)

            outdir = './plots/{WP}_{year}/'.format(**filler)
            for region in regions:
                plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
            for proc in procs:
                plot_ratio(proc, category, model_file, outdir, lumi[year], year)

            # Flavor integrated
            dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
            dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
            dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir,lumi[year],year)
            # Split by flavor
            dataValidation("dimuon",        "singlemuon",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
            dataValidation("dielectron",    "singleelectron",category, ws_file, fitdiag_file, outdir,lumi[year],year)
            dataValidation("singleelectron","gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
            dataValidation("singlemuon",    "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
            dataValidation("dielectron",    "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
            dataValidation("dimuon",        "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
            # plot_nuis(diffnuis_file, outdir)


def monov_plot_agreement_channels_combined_years_combined():
    ### Channels combined, years combined
    fitdiag_file = 'diagnostics/fitDiagnostics_nominal_monov_combined.root'
    for wp in 'loose', 'tight':
        ### Years fit together
        filler = {
            "category" : "monov{WP}".format(WP=wp),
            "WP" : wp,
        }
        ws_file="root/ws_monov_nominal_{WP}.root".format(**filler)
        model_file = "root/combined_model_monov_nominal_{WP}.root".format(**filler)

        for year in [2017,2018]:
            outdir = './plots/combined_combined_{YEAR}/'.format(YEAR=year)
            category = 'monov{WP}_{YEAR}'.format(WP=wp,YEAR=year)
            for region in regions:
                plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
            for proc in procs:
                plot_ratio(proc, category, model_file, outdir, lumi[year], year)
        outdir = './plots/combined/'

def monov_plot_nuisance_channels_combined():
    #### Channels combined
    # Nuisances
    for year in [2017,2018,"combined"]:
        filler = {
                "year" : year,
            }
        outdir = './plots/combined_{year}/'.format(**filler)
        diffnuis_file = 'diagnostics/diffnuisances_nominal_monov_{year}.root'.format(**filler)
        plot_nuis(diffnuis_file, outdir)

def monov_plot_agreement_channels_combined_years_separately():
    # Years separately: prefit / postfit
    for year in 2017, 2018:
        filler = {
                "year" : year,
            }
        fitdiag_file = 'diagnostics/fitDiagnostics_nominal_monov_{year}.root'.format(**filler)
        outdir = './plots/combined_{year}/'.format(**filler)
        for wp in 'loose', 'tight':
            model_file = "root/combined_model_monov_nominal_{WP}.root".format(WP=wp)
            ws_file="root/ws_monov_nominal_{WP}.root".format(WP=wp)
            category='monov{WP}_{YEAR}'.format(WP=wp, YEAR=year)
            filler = {
                "wp" : "WP",
                "year" : year,
                "category" : category
            }

            for region in regions:
                plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
            for proc in procs:
                plot_ratio(proc, category, model_file, outdir, lumi[year], year)

monov_plot_nuisance_channels_combined()
monov_plot_channels_separately()
monov_plot_agreement_channels_combined_years_separately()
monov_plot_agreement_channels_combined_years_combined()

