#!/bin/bash

### Impacts
SIGNAL="0.15"
mkdir -p impacts
pushd impacts
for YEAR in 2017 2018; do
    mkdir ${YEAR}
    pushd ${YEAR}
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4 --rMin=-1
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4 --rMin=-1
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4 --rMin=-1
    popd
    plotImpacts.py -i ${YEAR}/impacts.json -o impacts_${YEAR}

    mkdir ${YEAR}_nophoton
    pushd ${YEAR}_nophoton
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4 --setParameters mask_vbf_photon=1 --rMin=-1
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4  --setParameters mask_vbf_photon=1 --rMin=-1
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4  --setParameters mask_vbf_photon=1 --rMin=-1
    popd
    plotImpacts.py -i ${YEAR}_nophoton/impacts.json -o impacts_${YEAR}_nophoton
done