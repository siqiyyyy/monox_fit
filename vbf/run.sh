#!/bin/bash

### Fit diagnostics
mkdir -p diagnostics
pushd diagnostics
for YEAR in 2018; do
    combine -M FitDiagnostics --saveShapes --saveWithUncertainties --setParameters mask_vbf_signal=1 -n _vbf_${YEAR} ../cards/card_vbf_${YEAR}.root
    python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_vbf_${YEAR}.root  -g diffnuisances.root
done
popd


### Asimov limit
mkdir -p limit
pushd limit
for YEAR in 2018; do
    combine -M AsymptoticLimits -t -1 -n _vbf_${YEAR} ../cards/card_vbf_${YEAR}.root
done
popd

# ### Impacts
# mkdir -p impacts
# for YEAR in 2017 2018; do
#     combineTool.py -M Impacts -d ../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=1 --parallel=4  --setParameters mask_vbf_signal=1
#     combineTool.py -M Impacts -d ../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=1 --parallel=4  --setParameters mask_vbf_signal=1
#     combineTool.py -M Impacts -d ../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=1  --parallel=4 --setParameters mask_vbf_signal=1
# done
# popd