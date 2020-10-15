#!/bin/bash
mkdir -p diagnostics
pushd diagnostics

# Year by year
for YEAR in 2017 2018; do
    for TAGGER in nominal; do
        for WP in tight loose; do
            combine -M FitDiagnostics \
            --saveShapes \
            --saveWithUncertainties \
            --setParameters 'rgx{mask_.*_signal}'=1 \
            -n _${TAGGER}_monov${WP}_${YEAR} \
            ../cards/card_${TAGGER}_monov${WP}_${YEAR}.root

            python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_${TAGGER}_monov${WP}_${YEAR}.root  -g diffnuisances_${TAGGER}_monov${WP}_${YEAR}.root
        done
    done
done


# Years combined
for TAGGER in nominal; do
    for WP in loose; do
        combine -M FitDiagnostics \
                --saveShapes \
                --saveWithUncertainties \
                --setParameters 'rgx{mask_.*_signal}'=1 \
                -n _${TAGGER}_monov${WP}_combined \
                ../cards/card_${TAGGER}_monov${WP}_combined.root

        python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_${TAGGER}_monov${WP}_combined.root  -g diffnuisances_${TAGGER}_monov${WP}_combined.root
    done
done

# Channels combined
for TAGGER in nominal; do
    for YEAR in 2017 2018 combined; do
        combine -M FitDiagnostics \
                        --saveShapes \
                        --saveWithUncertainties \
                        --setParameters 'rgx{mask_.*_signal}'=1 \
                        -n _${TAGGER}_monov_${YEAR} \
                        ../cards/card_${TAGGER}_monov_${YEAR}.root

        python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics_${TAGGER}_monov_${YEAR}.root  -g diffnuisances_${TAGGER}_monov_${YEAR}.root
        done
done

popd
