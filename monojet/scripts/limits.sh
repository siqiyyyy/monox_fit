#!/bin/bash

#remove limit on stack size to prevent related segfault
ulimit -s unlimited

### Asimov limit
mkdir -p limit
pushd limit
for YEAR in 2017; do
    combine -M AsymptoticLimits -t -1 -n _monojet_${YEAR} ../cards/card_monojet_${YEAR}.root  --setParameters 'LUMISCALE=1' > log_${YEAR}.txt &
done
popd
