#!/bin/bash

TAGGER="nominal"
WP="tight"

### Impacts

# Separately by year
mkdir -p impacts
pushd impacts
for SIGNAL in "0.0"; do
    for YEAR in 2017 2018; do
        mkdir -p ${YEAR}_${TAGGER}_${SIGNAL}
        pushd ${YEAR}_${TAGGER}_${SIGNAL}
        combineTool.py -M Impacts -d ../../cards/card_${TAGGER}_monov${WP}_${YEAR}.root --rMin -1 -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4
        combineTool.py -M Impacts -d ../../cards/card_${TAGGER}_monov${WP}_${YEAR}.root --rMin -1 -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4
        combineTool.py -M Impacts -d ../../cards/card_${TAGGER}_monov${WP}_${YEAR}.root --rMin -1 -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4
        popd
        plotImpacts.py -i ${YEAR}_${TAGGER}_${SIGNAL}/impacts.json -o impacts_${TAGGER}_monov${WP}_${YEAR}_${SIGNAL}
    done
done


# Combined
for SIGNAL in "0.0"; do
    mkdir -p combined_${TAGGER}_${SIGNAL}
    pushd combined_${TAGGER}_${SIGNAL}
    combineTool.py -M Impacts -d ../../cards/card_${TAGGER}_monov${WP}_combined.root --rMin -1 -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4
    combineTool.py -M Impacts -d ../../cards/card_${TAGGER}_monov${WP}_combined.root --rMin -1 -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4
    combineTool.py -M Impacts -d ../../cards/card_${TAGGER}_monov${WP}_combined.root --rMin -1 -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4
    popd
    plotImpacts.py -i combined_${TAGGER}_${SIGNAL}/impacts.json -o impacts_${TAGGER}_monov${WP}_combined_${SIGNAL}
done
popd