#!/bin/bash
set -e

mkdir -p cards

for YEAR in 2017 2018; do
    ### INDIVIDUAL CARDS FOR DEEPAK8 WPS
    for WP in loose tight; do
        for TAGGER in nominal MD; do
            CARD=cards/card_${TAGGER}_monov${WP}_${YEAR}.txt
            cp ../../templates/card_template.txt ${CARD}
            sed -i "s/@WP/${WP}/g" ${CARD}
            sed -i "s|@YEAR|${YEAR}|g" ${CARD}

            if [ $YEAR -eq 2017 ]; then
                sed -i "s|@LUMI|1.025|g" ${CARD}
            elif [ $YEAR -eq 2018 ]; then
                sed -i "s|@LUMI|1.023|g" ${CARD}
            fi
            sed -i "s|combined_model.root|../root/combined_model_monov_${TAGGER}_${WP}.root|g" ${CARD}
            text2workspace.py ${CARD} --channel-masks
            python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${CARD} > cards/systematics_${TAGGER}_monov${WP}_${YEAR}.html
        done
    done

    pushd cards
    ### COMBINED TAGGER CARDS
    for TAGGER in nominal MD; do
        COMBINED=card_${TAGGER}_monov_${YEAR}.txt
        combineCards.py  card_${TAGGER}_monovloose_${YEAR}.txt \
                        card_${TAGGER}_monovtight_${YEAR}.txt \
                        > ${COMBINED}
        sed -i 's/ch\(1\|2\)_//g' ${COMBINED}
        text2workspace.py ${COMBINED} --channel-masks
        python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${COMBINED} > systematics_${TAGGER}_monov_${YEAR}.html
    done

    ### TAU21 CARDS
    CARD=card_tau21_monov_${YEAR}.txt
    cp ../../../templates/card_template.txt ${CARD}
    sed -i "s/@WP//g" ${CARD}
    sed -i "s|@YEAR|${YEAR}|g" ${CARD}
    sed -i "s|combined_model.root|../root/combined_model_monov_tau21.root|g" ${CARD}
    if [ $YEAR -eq 2017 ]; then
        sed -i "s|@LUMI|1.025|g" ${CARD}
    elif [ $YEAR -eq 2018 ]; then
        sed -i "s|@LUMI|1.023|g" ${CARD}
    fi
    text2workspace.py ${CARD} --channel-masks
    python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${CARD} > systematics_tau21_monov_${YEAR}.html

    popd
done


pushd cards
# Combine across years
for TAGGER in nominal MD; do
    COMBINED=card_${TAGGER}_monov_combined.txt
    combineCards.py card_${TAGGER}_monov_201*.txt > ${COMBINED}
    sed -i 's/ch\(1\|2\)_//g' ${COMBINED}
    text2workspace.py ${COMBINED} --channel-masks
    python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${COMBINED} > systematics_${TAGGER}_monov_combined.html

    for WP in loose tight; do
        COMBINED=card_${TAGGER}_monov${WP}_combined.txt
        combineCards.py card_${TAGGER}_monov${WP}_201*.txt > ${COMBINED}
        sed -i 's/ch\(1\|2\)_//g' ${COMBINED}
        text2workspace.py ${COMBINED} --channel-masks
        python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${COMBINED} > systematics_${TAGGER}_monov${WP}_combined.html
    done

    COMBINED=card_tau21_monov_combined.txt
    combineCards.py card_tau21_monov_201*.txt > ${COMBINED}
    sed -i 's/ch\(1\|2\)_//g' ${COMBINED}
    text2workspace.py ${COMBINED} --channel-masks
    python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${COMBINED} > systematics_tau21_monov_combined.html
done
popd