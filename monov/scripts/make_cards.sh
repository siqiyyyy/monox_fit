#!/bin/bash
set -e

mkdir -p cards

for YEAR in 2017 2018; do
    ### INDIVIDUAL CARDS FOR DEEPAK8 WPS
    for WP in loose tight; do
        for TAGGER in nominal MD; do
            CARD=cards/card_${TAGGER}_monov${WP}_${YEAR}.txt
            cp ../../templates/card_template.txt ${CARD}
            sed -i "s/monov/monov${WP}/g" ${CARD}
            sed -i "s|@YEAR|${YEAR}|g" ${CARD}

            if [ $YEAR -eq 2017 ]; then
                sed -i "s|@LUMI|1.025|g" ${CARD}
            elif [ $YEAR -eq 2018 ]; then
                sed -i "s|@LUMI|1.023|g" ${CARD}
            fi
            sed -i "s|combined_model.root|../root/combined_model_monov_${TAGGER}_${WP}_${YEAR}.root|g" ${CARD}
            text2workspace.py ${CARD} --channel-masks
        done
    done

    ### COMBINED TAGGER CARDS
    for TAGGER in nominal MD; do
            COMBINED=./cards/card_${TAGGER}_monov_${YEAR}.txt
            combineCards.py  ./cards/card_${TAGGER}_monovloose_${YEAR}.txt \
                            ./cards/card_${TAGGER}_monovtight_${YEAR}.txt \
                            > ${COMBINED}
            sed -i 's/ch\(1\|2\)_//g' ${COMBINED}
            text2workspace.py ${COMBINED} --channel-masks
    done

    ### TAU21 CARDS
    CARD=cards/card_tau21_monov_${YEAR}.txt
    cp ../../templates/card_template.txt ${CARD}
    sed -i "s|combined_model.root|../root/combined_model_monov_tau21_${YEAR}.root|g" ${CARD}
    sed -i "s|@YEAR|${YEAR}|g" ${CARD}
    if [ $YEAR -eq 2017 ]; then
        sed -i "s|@LUMI|1.025|g" ${CARD}
    elif [ $YEAR -eq 2018 ]; then
        sed -i "s|@LUMI|1.023|g" ${CARD}
    fi
    text2workspace.py ${CARD} --channel-masks

done