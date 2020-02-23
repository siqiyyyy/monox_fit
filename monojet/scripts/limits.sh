#!/bin/bash

### Asimov limit
mkdir -p limit
pushd limit
for YEAR in 2017 2018; do
    combine -M AsymptoticLimits -t -1 -n _monojet_${YEAR} ../cards/card_monojet_${YEAR}.root | tee log_${YEAR}.txt
done
popd