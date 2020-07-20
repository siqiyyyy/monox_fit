#!/bin/bash

### Asimov limit
mkdir -p limit
pushd limit
for YEAR in combined 2017 2018; do
    combine -M AsymptoticLimits -t -1 -n _monojet_${YEAR} ../cards/card_monojet_${YEAR}.root > log_${YEAR}.txt &
done
popd