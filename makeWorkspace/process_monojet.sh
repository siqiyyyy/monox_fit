#!/bin/bash
set -e

INDIR=../input/2020-02-21_19Feb20_skim_monojet_monov
TAG='test'
OUTDIR="../monojet/$(basename $INDIR)/${TAG}/root"
mkdir -p ${OUTDIR}

for YEAR in 2017 2018; do
    WSFILE=${OUTDIR}/ws_monojet_${YEAR}.root
    ./make_ws.py ${INDIR}/legacy_limit_${YEAR}.root --out ${WSFILE} --category monojet
    ./runModel.py ${WSFILE} --categories monojet --out ${OUTDIR}/combined_model_monojet_${YEAR}.root
done;

ln -fs $(readlink -e ../monojet/templates/Makefile) ${OUTDIR}/../Makefile

pushd ${OUTDIR}/..
make cards
popd
