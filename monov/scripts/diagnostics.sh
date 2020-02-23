#!/bin/bash
mkdir -p diagnostics
pushd diagnostics

for YEAR in 2017 2018; do
    for TAGGER in nominal MD; do
        for WP in tight loose; do
            combine -M FitDiagnostics --saveShapes --saveWithUncertainties --setParameters mask_monov_signal=1 -n _${TAGGER}_monov${WP}_${YEAR} ../cards/card_${TAGGER}_monov${WP}_${YEAR}.root
            python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_${TAGGER}_monov${WP}_${YEAR}.root  -g diffnuisances_${TAGGER}_monov${WP}_${YEAR}.root
        done
    done
done
popd


