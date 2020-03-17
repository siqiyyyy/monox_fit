#!/bin/bash
mkdir -p diagnostics
pushd diagnostics
# Individual years
for YEAR in 2017 2018; do
    combine -M FitDiagnostics \
            --saveShapes \
            --saveWithUncertainties \
            --robustFit 1 \
            --setParameters mask_monojet_${YEAR}_signal=1 \
            -n _monojet_${YEAR} \
            ../cards/card_monojet_${YEAR}.root

    python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
           fitDiagnostics_monojet_${YEAR}.root \
           -g diffnuisances_monojet_${YEAR}.root
done

# Combined
combine -M FitDiagnostics \
        --saveShapes \
        --saveWithUncertainties \
        --robustFit 1 \
        --setParameters mask_monojet_2017_signal=1,mask_monojet_2018_signal=1 \
        -n _monojet_combined \
        ../cards/card_monojet_combined.root

python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
        fitDiagnostics_monojet_combined.root \
        -g diffnuisances_monojet_combined.root
popd


