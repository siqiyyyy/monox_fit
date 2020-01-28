#!/bin/bash

INDIR=../input/2019-12-04_fix_hinv_xs_monov
OUTDIR='../monov/root'
YEAR='2017'
mkdir -p ${OUTDIR}

### Start by making workspaces split by working point and tagger type
for TAGGER in nominal MD; do
    for WP in tight loose; do
        WSFILE=${OUTDIR}/ws_${TAGGER}_${WP}_${YEAR}.root
        ./make_ws.py ${INDIR}/merged_legacy_limit_${TAGGER}_monov_${YEAR}.root --out ${WSFILE} --category monov${WP};
        ./runModel.py ${WSFILE} --categories monov${WP} --out ${OUTDIR}/combined_model_monov_${TAGGER}_${WP}_${YEAR}.root
    done;
done

./make_ws.py ${INDIR}/merged_legacy_limit_monov_tau21_${YEAR}.root --out ${OUTDIR}/ws_tau21_${YEAR}.root --category monov
./runModel.py ${OUTDIR}/ws_tau21_${YEAR}.root --categories monov --out ${OUTDIR}/combined_model_monov_tau21_${YEAR}.root

# hadd -f ${OUTDIR}/ws_nominal_monov.root ${OUTDIR}/ws_*nominal*2017.root
# hadd -f ${OUTDIR}/ws_MD_monov.root ${OUTDIR}/ws_*MD*2017.root


# ./runModel.py ${OUTDIR}/ws_nominal_monov.root --categories monovtight,monovloose --out ${OUTDIR}/combined_model_monov_nominal.root
# ./runModel.py ${OUTDIR}/ws_MD_monov.root --categories monovtight,monovloose --out ${OUTDIR}/combined_model_monov_MD.root

