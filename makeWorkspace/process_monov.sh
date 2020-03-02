#!/bin/bash
set -e

INDIR=/uscms_data/d3/aandreas/legacy_limit/monox_fit/input/2020-02-21_19Feb20_skim_monojet_monov_gjets_ele
TAG='default'
INDIR="$(readlink -e $INDIR)"

OUTDIR="../monov/$(basename $INDIR)/${TAG}/root"
mkdir -p ${OUTDIR}
OUTDIR="$(readlink -e ${OUTDIR})"

# Save some information so we can trace inputs
INFOFILE=${OUTDIR}/INFO.txt
echo "Input directory: ${INDIR}" > ${INFOFILE}
echo "--- INPUT ---" > ${INFOFILE}

### Start by making workspaces split by working point and tagger type
for YEAR in 2017 2018; do
    for TAGGER in nominal MD; do
        for WP in tight loose; do
            WSFILE=${OUTDIR}/ws_monov_${TAGGER}_${WP}_${YEAR}.root
            INFILE=${INDIR}/merged_legacy_limit_${TAGGER}_monov_${YEAR}.root
            
             # Save the check sum for the input
            md5sum ${INFILE} >> ${INFOFILE}

            ./make_ws.py ${INFILE} --out ${WSFILE} --category monov${WP};
            ./runModel.py ${WSFILE} --categories monov${WP} --out ${OUTDIR}/combined_model_monov_${TAGGER}_${WP}_${YEAR}.root
        done;
    done

    # Tau 21 has just one WP
    INFILE=${INDIR}/merged_legacy_limit_monov_tau21_${YEAR}.root
     # Save the check sum for the input
    md5sum ${INFILE} >> ${INFOFILE}
    ./make_ws.py ${INFILE} --out ${OUTDIR}/ws_tau21_${YEAR}.root --category monov
    ./runModel.py ${OUTDIR}/ws_tau21_${YEAR}.root --categories monov --out ${OUTDIR}/combined_model_monov_tau21_${YEAR}.root
done


# Save the check sums for the output
echo "--- OUTPUT ---" >> ${INFOFILE}
md5sum ${OUTDIR}/*root >> ${INFOFILE}

ln -fs $(readlink -e ../monov/templates/Makefile) ${OUTDIR}/../Makefile

pushd ${OUTDIR}/..
make cards
popd
echo $(readlink -e ../monov/$(basename $INDIR)/${TAG})
