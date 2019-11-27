#!/bin/bash

INDIR=../input/
OUTDIR='../monojet/root'
YEAR='2017'
mkdir -p ${OUTDIR}

### Start by making workspaces split by working point and tagger type

for YEAR in 2017 2018; do
    WSFILE=${OUTDIR}/ws_monojet_${YEAR}.root
    ./make_ws.py ${INDIR}/legacy_limit_${YEAR}.root --out ${WSFILE} --category monojet
    ./runModel.py ${WSFILE} --categories monojet --out ${OUTDIR}/combined_model_monojet_${YEAR}.root
done;


# hadd -f ${OUTDIR}/ws_nominal_monov.root ${OUTDIR}/ws_*nominal*2017.root
# hadd -f ${OUTDIR}/ws_MD_monov.root ${OUTDIR}/ws_*MD*2017.root


# ./runModel.py ${OUTDIR}/ws_nominal_monov.root --categories monovtight,monovloose --out ${OUTDIR}/combined_model_monov_nominal.root
# ./runModel.py ${OUTDIR}/ws_MD_monov.root --categories monovtight,monovloose --out ${OUTDIR}/combined_model_monov_MD.root

