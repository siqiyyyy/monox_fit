#!/bin/bash
set -e

mkdir -p cards
# Fill templates
for YEAR in 2017 2018; do
    CARD=cards/card_monojet_${YEAR}.txt
    cp ../../templates/monojet_template.txt ${CARD}
    sed -i "s|@YEAR|${YEAR}|g" ${CARD}

    if [ $YEAR -eq 2017 ]; then
        sed -i "s|@LUMIXY|1.008|g" ${CARD}
        sed -i "s|@LUMILS|1.003|g" ${CARD}
        sed -i "s|@LUMIBBD|1.004|g" ${CARD}
        sed -i "s|@LUMIDB|1.005|g" ${CARD}
        sed -i "s|@LUMIBCC|1.003|g" ${CARD}
        sed -i "s|@LUMIGS|1.001|g" ${CARD}
        sed -i "s|@LUMI|1.020|g" ${CARD}
    elif [ $YEAR -eq 2018 ]; then
        sed -i "s|@LUMIXY|1.02|g" ${CARD}
        sed -i "s|@LUMILS|1.002|g" ${CARD}
        sed -i "s|@LUMIBBD|1.0|g" ${CARD}
        sed -i "s|@LUMIDB|1.0|g" ${CARD}
        sed -i "s|@LUMIBCC|1.02|g" ${CARD}
        sed -i "s|@LUMIGS|1.00|g" ${CARD}
        sed -i "s|@LUMI|1.015|g" ${CARD}
        sed -i "/prefiring/d" ${CARD}
    fi
    sed -i "s|combined_model.root|../root/combined_model_monojet.root|g" ${CARD}
    sed -i "s|monojet_qcd_ws.root|../root/monojet_qcd_ws.root|g" ${CARD}

    text2workspace.py ${CARD} --channel-masks
    python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${CARD} > cards/systematics_${YEAR}.html
done


COMBINED=cards/card_monojet_combined.txt
combineCards.py cards/card_monojet_201*.txt > ${COMBINED}
sed -i 's/ch\(1\|2\)_//g' ${COMBINED}
text2workspace.py ${COMBINED} --channel-masks