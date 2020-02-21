#!/bin/bash
set -e

mkdir -p cards
for YEAR in 2017 2018; do
    for WP in loose tight; do
        for TAGGER in nominal MD; do
            CARD=cards/card_${TAGGER}_monov${WP}_${YEAR}.txt
            cp ../../templates/card_template.txt ${CARD}
            sed -i "s/monov/monov${WP}/g" ${CARD}
            sed -i "s|combined_model.root|../root/combined_model_monov_${TAGGER}_${WP}_${YEAR}.root|g" ${CARD}
            text2workspace.py ${CARD} --channel-masks
        done
    done
# #
CARD=cards/card_tau21_monov_${YEAR}.txt
cp card_template.txt ${CARD}
sed -i "s|combined_model.root|../root/combined_model_monov_tau21_${YEAR}.root|g" ${CARD}
text2workspace.py ${CARD} --channel-masks

    for TAGGER in nominal MD; do
        COMBINED=./cards/card_${TAGGER}_monov_${YEAR}.txt
        combineCards.py  ./cards/card_${TAGGER}_monovloose_${YEAR}.txt \
                        ./cards/card_${TAGGER}_monovtight_${YEAR}.txt \
                        > ${COMBINED}
        sed -i 's/ch\(1\|2\)_//g' ${COMBINED}
        text2workspace.py ${COMBINED} --channel-masks
    done
done