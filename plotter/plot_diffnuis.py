#!/usr/bin/env python
import ROOT as r
import os
import math

r.gROOT.SetBatch(r.kTRUE)

def get_nbins(canvas):
    nbins = 0
    for item in canvas.GetListOfPrimitives():
        try:
            print item
            nbins = item.GetNbinsX()
        except:
            continue
    return nbins

def plot_nuis(fname, outdir):
    if not os.path.exists(fname):
        raise IOError("Input file does not exist: " + fname)
    r.gStyle.SetOptStat(0)

    f = r.TFile(fname)

    c = f.Get("nuisances")



    c.SetBottomMargin(0.3)
    c.SetRightMargin(0.02)
    c.SetLeftMargin(0.02)
    c.SetTopMargin(0.05)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    name = os.path.basename(fname).replace('.root','').replace('diffnuisances_','')

    # Derive the splitting
    nbins = get_nbins(c)     # total bins
    perplot = 30             # optimal bins per plot
    rest = nbins % perplot   # bins in the last plot
    nplots = int(math.ceil(float(nbins) / perplot))

    # If there are too few in the last plot, just
    # redistribute to the earlier plots
    if rest < 0.2 * perplot:
        nplots = nplots - 1
        perplot = perplot + int(math.ceil(float(rest))/nplots)

    nplots = nbins / perplot

    for i in range(nplots+1):
        for item in c.GetListOfPrimitives():
            try:
                item.GetXaxis().SetRangeUser(i*perplot, (i+1)*perplot)
                item.GetXaxis().SetLabelSize(0.04)
                item.LabelsOption("v")
                item.SetTitle("Nuisances {name} {i}".format(name=name, i=i))
            except:
                pass

            try:
                item.SetBBoxX1(600)
                item.SetBBoxY1(1)
                item.SetBBoxY2(75)
            except AttributeError:
                pass
        c.Draw()
        c.SetCanvasSize(1200,600)
        for extension in ['png','pdf']:
            c.SaveAs(os.path.join(outdir,"diffnuis_{name}_{i}.{ext}".format(name=name, i=i, ext=extension)))
    