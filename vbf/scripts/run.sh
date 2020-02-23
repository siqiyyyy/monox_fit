#!/bin/bash

### Fit diagnostics
mkdir -p diagnostics
pushd diagnostics
for YEAR in 2017 2018; do
    combine -M FitDiagnostics --saveShapes --saveWithUncertainties --setParameters mask_vbf_signal=1 -n _vbf_${YEAR} ../cards/card_vbf_${YEAR}.root
    python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_vbf_${YEAR}.root  -g diffnuisances.root
done
popd


### Asimov limit
mkdir -p limit
pushd limit
for YEAR in 2017 2018; do
    combine -M AsymptoticLimits -t -1 -n _vbf_${YEAR} ../cards/card_vbf_${YEAR}.root | tee log_asimov_${YEAR}.txt
    combine -M AsymptoticLimits -t -1 -n _vbf_nophoton_${YEAR} --setParameters mask_vbf_photon=1 ../cards/card_vbf_${YEAR}.root | tee log_asimov_nophoton_${YEAR}.txt
done
popd

### Impacts
SIGNAL="0.15"
mkdir -p impacts
pushd impacts
for YEAR in 2017 2018; do
    mkdir ${YEAR}
    pushd ${YEAR}
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4
    popd
    plotImpacts.py -i ${YEAR}/impacts.json -o impacts_{YEAR}.pdf

    mkdir ${YEAR}_nophoton
    pushd ${YEAR}_nophoton
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4 --setParameters mask_vbf_photon=1
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4  --setParameters mask_vbf_photon=1
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4  --setParameters mask_vbf_photon=1
    popd
    plotImpacts.py -i ${YEAR}_nophoton/impacts.json -o impacts_{YEAR}_nophoton.pdf
done
popd