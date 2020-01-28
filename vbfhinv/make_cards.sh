#!/bin/bash
YEAR=2017

mkdir -p cards
# Fill templates
for YEAR in 2017 2018; do
    CARD=cards/card_vbfhinv_${YEAR}.txt
    cp vbfhinv_template.txt ${CARD}
    sed -i "s|combined_model.root|../root/combined_model_vbfhinv_${YEAR}.root|g" ${CARD}
    text2workspace.py ${CARD} --channel-masks
done
