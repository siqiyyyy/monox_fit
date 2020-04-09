TAG=2020-03-27_monojet_monov_overlap_v2
SUBTAG=v1
JDIR=$(readlink -e ../monojet/${TAG}/combined/)
VDIR=$(readlink -e ../monov/${TAG}/combined/)

WDIR=./${TAG}/${SUBTAG}/
mkdir -p $WDIR
pushd $WDIR

mkdir -p root
cp $JDIR/root/combined_model_monojet.root ./root
cp $JDIR/root/ws_monojet.root ./root
cp $VDIR/root/combined_model_monov_nominal_tight.root ./root
cp $VDIR/root/ws_monov_nominal_tight.root ./root

mkdir -p cards
for YEAR in 2017 2018 combined; do
    COMBINED="./cards/card_monojet_monov_nominal_tight_${YEAR}.txt"
    combineCards.py $JDIR/cards/card_monojet_${YEAR}.txt $VDIR/cards/card_nominal_monovtight_${YEAR}.txt > ${COMBINED}

    # Get rid of channel prefixes + fix white space
    sed -i 's/ch\(1\|2\)_/    /g' ${COMBINED}
    sed -i 's/^bin    /bin/g' ${COMBINED}

    # Fix input file names
    sed -i '/combined_model_/ s|[^ ]*\(combined_model_.*.root\)|root/\1|g' ${COMBINED}

    text2workspace.py ${COMBINED} --channel-masks



    ### DEBUG
    # individual channels
    INDIVIDUAL="./cards/card_monojet_${YEAR}.txt"
    combineCards.py ${COMBINED} --xc 'monov.*' > ${INDIVIDUAL}
    sed -i 's/ch\(1\|2\)_/    /g' ${INDIVIDUAL}
    sed -i 's/^bin    /bin/g' ${INDIVIDUAL}
    sed -i '/combined_model_/ s|[^ ]*\(combined_model_.*.root\)|root/\1|g' ${INDIVIDUAL}
    text2workspace.py ${INDIVIDUAL} --channel-masks
done
popd
ln -fs $(readlink -e scripts/Makefile) ${WDIR}/Makefile
