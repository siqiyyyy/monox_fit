#!/bin/bash

### Impacts
mkdir -p impacts
pushd impacts
for SIGNAL in "0.0" "0.5"; do 
    for YEAR in 2017 2018; do
        mkdir ${YEAR}_${SIGNAL}
        pushd ${YEAR}_${SIGNAL}
        combineTool.py -M Impacts -d ../../cards/card_monojet_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4
        combineTool.py -M Impacts -d ../../cards/card_monojet_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4
        combineTool.py -M Impacts -d ../../cards/card_monojet_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4
        popd
        plotImpacts.py -i ${YEAR}_${SIGNAL}/impacts.json -o impacts_monojet_${YEAR}_${SIGNAL}
    done
done
popd
