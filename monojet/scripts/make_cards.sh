#!/bin/bash
set -e

mkdir -p cards
# Fill templates
for YEAR in 2017 2018; do
    CARD=cards/card_monojet_${YEAR}.txt
    cp ../../templates/monojet_template.txt ${CARD}
    sed -i "s|combined_model.root|../root/combined_model_monojet_${YEAR}.root|g" ${CARD}
    text2workspace.py ${CARD} --channel-masks
done
