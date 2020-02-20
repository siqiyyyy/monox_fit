#!/bin/bash
set -e
# INDIR=../input/2020-02-05_vbf_noeletrig
INDIR=../input/vbf/2020-02-13_sync_vbf_v2
TAG='default'
OUTDIR="../vbf/$(basename $INDIR)/${TAG}/root"
mkdir -p ${OUTDIR}

for YEAR in 2017 2018; do
    WSFILE=${OUTDIR}/ws_vbf_${YEAR}.root
    ./make_ws.py ${INDIR}/legacy_limit_${YEAR}.root --out ${WSFILE} --category vbf
    ./runModel.py ${WSFILE} --categories vbf --out ${OUTDIR}/combined_model_vbf_${YEAR}.root
done;

ln -s $(readlink -e ../vbf/templates/Makefile) ${OUTDIR}/../Makefile

pushd ${OUTDIR}/..
make cards
popd
