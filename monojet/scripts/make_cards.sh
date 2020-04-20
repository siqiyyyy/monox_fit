#!/bin/bash
set -e

mkdir -p cards
# Fill templates
for YEAR in 2017 2018; do
    CARD=cards/card_monojet_${YEAR}.txt
    cp ../../templates/monojet_template.txt ${CARD}
    sed -i "s|@YEAR|${YEAR}|g" ${CARD}

    if [ $YEAR -eq 2017 ]; then
        sed -i "s|@LUMI|1.025|g" ${CARD}
    elif [ $YEAR -eq 2018 ]; then
        sed -i "s|@LUMI|1.023|g" ${CARD}
        sed -i "/prefiring/d" ${CARD}
    fi
    sed -i "s|combined_model.root|../root/combined_model_monojet.root|g" ${CARD}

    text2workspace.py ${CARD} --channel-masks
    python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${CARD} > cards/systematics_${YEAR}.html
done


COMBINED=cards/card_monojet_combined.txt
combineCards.py cards/card_monojet_201*.txt > ${COMBINED}
sed -i 's/ch\(1\|2\)_//g' ${COMBINED}
text2workspace.py ${COMBINED} --channel-masks