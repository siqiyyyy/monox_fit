#!/bin/bash
mkdir -p diagnostics
pushd diagnostics

#remove limit on stack size to prevent related segfault
ulimit -s unlimited

# Individual years
for YEAR in 2017 2018 combined; do
    combine -M FitDiagnostics \
            --saveShapes \
            --saveWithUncertainties \
            --robustFit 1 \
            --setParameters 'rgx{mask_.*_signal}=1' \
            -n _monojet_${YEAR} \
            ../cards/card_monojet_${YEAR}.root \
            | tee diag_${YEAR}.log &&
    python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
           fitDiagnostics_monojet_${YEAR}.root \
           -g diffnuisances_monojet_${YEAR}.root \
           --skipFitS &

    combine -M FitDiagnostics \
            --saveShapes \
            --saveWithUncertainties \
            --robustFit 1 \
            -n _monojet_unblind_${YEAR} \
            ../cards/card_monojet_${YEAR}.root \
            | tee diag_unblind_${YEAR}.log &&
    python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
           fitDiagnostics_monojet_unblind_${YEAR}.root \
           -g diffnuisances_monojet_unblind_${YEAR}.root \
           --skipFitS &
done
popd


