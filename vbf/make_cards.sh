#!/bin/bash
set -e
YEAR=2017

mkdir -p cards
# Fill templates
for YEAR in 2017 2018; do
    CARD=cards/card_vbf_${YEAR}.txt
    cp vbf_template_pretty_withphotons.txt ${CARD}
    sed -i "s|@YEAR|${YEAR}|g" ${CARD}

    if [ $YEAR -eq 2017 ]; then
        sed -i "s|@LUMI|1.025|g" ${CARD}
    elif [ $YEAR -eq 2018 ]; then
        sed -i "s|@LUMI|1.023|g" ${CARD}
    fi
    sed -i "s|combined_model.root|../root/combined_model_vbf_${YEAR}.root|g" ${CARD}
    text2workspace.py ${CARD} --channel-masks
done
