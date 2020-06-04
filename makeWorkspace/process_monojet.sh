#!/bin/bash
set -e

INDIR=../input/2020-05-20_monojet_photon_update_newhem_v2_metphi_dyn/
TAG='testqcd'
INDIR="$(readlink -e $INDIR)"

OUTDIR="../monojet/$(basename $INDIR)/${TAG}/root"
mkdir -p ${OUTDIR}
OUTDIR="$(readlink -e ${OUTDIR})"

# Save some information so we can trace inputs
INFOFILE=${OUTDIR}/INFO.txt
echo "Input directory: ${INDIR}" > ${INFOFILE}
echo "--- INPUT ---" > ${INFOFILE}

INFILE=${INDIR}/legacy_limit_monojet.root
WSFILE=${OUTDIR}/ws_monojet.root

# Save the check sum for the input
md5sum ${INFILE} >> ${INFOFILE}

./make_ws.py ${INFILE} \
             --out ${WSFILE} \
             --categories monojet_2017,monojet_2018

./runModel.py ${WSFILE} --categories monojet_2017,monojet_2018 \
                        --out ${OUTDIR}/combined_model_monojet.root

cp sys/monojet_qcd_ws.root ${OUTDIR}

# Save the check sums for the output
echo "--- OUTPUT ---" >> ${INFOFILE}
md5sum ${OUTDIR}/*root >> ${INFOFILE}

ln -fs $(readlink -e ../monojet/templates/Makefile) ${OUTDIR}/../Makefile

pushd ${OUTDIR}/..
make cards
popd

echo $(readlink -e ../monojet/$(basename $INDIR)/${TAG})
