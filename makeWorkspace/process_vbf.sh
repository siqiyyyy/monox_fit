#!/bin/bash
set -e
# INDIR=../input/2020-02-05_vbf_noeletrig
TAG='ic'
INDIR=../input/vbf/2020-02-28_latest
INDIR="$(readlink -e $INDIR)"

OUTDIR="../vbf/$(basename $INDIR)/${TAG}/root"
mkdir -p ${OUTDIR}
OUTDIR="$(readlink -e ${OUTDIR})"

# Save some information so we can trace inputs
INFOFILE=${OUTDIR}/INFO.txt
echo "Input directory: ${INDIR}" > ${INFOFILE}
echo "--- INPUT ---" > ${INFOFILE}

for YEAR in 2017 2018; do
    WSFILE=${OUTDIR}/ws_vbf_${YEAR}.root
    INFILE=${INDIR}/legacy_limit_${YEAR}.root

    # Save the check sum for the input
    md5sum ${INFILE} >> ${INFOFILE}

    ./make_ws.py ${INFILE} --out ${WSFILE} --category vbf
    ./runModel.py ${WSFILE} --categories vbf --out ${OUTDIR}/combined_model_vbf_${YEAR}.root
done;

# Save the check sums for the output
echo "--- OUTPUT ---" >> ${INFOFILE}
md5sum ${OUTDIR}/*root >> ${INFOFILE}

ln -fs $(readlink -e ../vbf/templates/Makefile) ${OUTDIR}/../Makefile

pushd ${OUTDIR}/..
make cards
popd
