#!/bin/bash
mkdir -p diagnostics
pushd diagnostics

# Year by year
for YEAR in 2017 2018; do
    for TAGGER in nominal MD; do
        for WP in tight loose; do
            combine -M FitDiagnostics \
            --saveShapes \
            --saveWithUncertainties \
            --setParameters mask_monov${WP}_${YEAR}_signal=1 \
            -n _${TAGGER}_monov${WP}_${YEAR} \
            ../cards/card_${TAGGER}_monov${WP}_${YEAR}.root

            python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_${TAGGER}_monov${WP}_${YEAR}.root  -g diffnuisances_${TAGGER}_monov${WP}_${YEAR}.root
        done
    done
done


# Combined tight
for TAGGER in nominal MD; do
    combine -M FitDiagnostics \
            --saveShapes \
            --saveWithUncertainties \
            --setParameters mask_monovtight_2017_signal=1,mask_monovloose_2017_signal=1,mask_monovtight_2018_signal=1,mask_monovloose_2018_signal=1 \
            -n _${TAGGER}_monovtight_combined \
            ../cards/card_${TAGGER}_monovtight_combined.root

            python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_${TAGGER}_monovtight_combined.root  -g diffnuisances_${TAGGER}_monovtight_combined.root
done
popd