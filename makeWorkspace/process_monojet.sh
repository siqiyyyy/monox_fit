#!/bin/bash
set -e

INDIR=/uscms_data/d3/aandreas/legacy_limit/monox_fit/input/2020-02-21_19Feb20_skim_monojet_monov_gjets_ele
TAG='default'
INDIR="$(readlink -e $INDIR)"

OUTDIR="../monojet/$(basename $INDIR)/${TAG}/root"
mkdir -p ${OUTDIR}
OUTDIR="$(readlink -e ${OUTDIR})"

# Save some information so we can trace inputs
INFOFILE=${OUTDIR}/INFO.txt
echo "Input directory: ${INDIR}" > ${INFOFILE}
echo "--- INPUT ---" > ${INFOFILE}

for YEAR in 2017 2018; do
    WSFILE=${OUTDIR}/ws_monojet_${YEAR}.root
    INFILE=${INDIR}/legacy_limit_${YEAR}.root

    # Save the check sum for the input
    md5sum ${INFILE} >> ${INFOFILE}

    ./make_ws.py ${INFILE} --out ${WSFILE} --category monojet
    ./runModel.py ${WSFILE} --categories monojet --out ${OUTDIR}/combined_model_monojet_${YEAR}.root
done;

# Save the check sums for the output
echo "--- OUTPUT ---" >> ${INFOFILE}
md5sum ${OUTDIR}/*root >> ${INFOFILE}

ln -fs $(readlink -e ../monojet/templates/Makefile) ${OUTDIR}/../Makefile

pushd ${OUTDIR}/..
make cards
popd

echo $(readlink -e ../monojet/$(basename $INDIR)/${TAG})
