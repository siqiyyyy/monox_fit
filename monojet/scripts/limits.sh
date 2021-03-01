#!/bin/bash

### Asimov limit
mkdir -p limit
pushd limit
for YEAR in 2017; do
    combine -M AsymptoticLimits -t -1 -n _monojet_${YEAR} ../cards/card_monojet_${YEAR}.root  --setParameters 'LUMISCALE=1' > log_${YEAR}.txt &
done
popd