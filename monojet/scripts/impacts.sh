#!/bin/bash

### Impacts
SIGNAL="0.5"
mkdir -p impacts
pushd impacts
for YEAR in 2017 2018; do
    mkdir ${YEAR}
    pushd ${YEAR}
    combineTool.py -M Impacts -d ../../cards/card_monojet_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4
    combineTool.py -M Impacts -d ../../cards/card_monojet_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4
    combineTool.py -M Impacts -d ../../cards/card_monojet_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4
    popd
    plotImpacts.py -i ${YEAR}/impacts.json -o impacts_monojet_${YEAR}
done
popd
