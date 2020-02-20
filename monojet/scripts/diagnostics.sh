#!/bin/bash
mkdir -p diagnostics
pushd diagnostics
for YEAR in 2017 2018; do
    combine -M FitDiagnostics --saveShapes --saveWithUncertainties --setParameters mask_monojet_signal=1 -n _monojet_${YEAR} ../cards/card_monojet_${YEAR}.root
    python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_monojet_${YEAR}.root  -g diffnuisances_monojet_${YEAR}.root
done
popd


