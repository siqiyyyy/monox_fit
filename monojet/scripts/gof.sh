mkdir -p gof
pushd gof

function gof() {
    YEAR=$1
    MASK=$2
    TAG=$3
    NJOBS=${4}

    WDIR=${YEAR}_${TAG}
    mkdir -p ${WDIR};
    pushd ${WDIR};

    CARD="../../cards/card_monojet_${YEAR}.root"
    for IJOB in $(seq 1 1 ${NJOBS}); do
        combineTool.py \
            --task-name toys_${YEAR}_${TAG}_${IJOB} \
            --job-mode condor \
            -M GoodnessOfFit \
            ${CARD} \
            --setParameters ${MASK} \
            --algo=saturated \
            -t 25 \
            -s -1 \
            --toysFreq \
            --sub-opts '+MaxRuntime=3600' \
            -n _CRonly_toys_${YEAR}_${IJOB} \
            -m 125.0 &
        sleep 10
    done
    combine -M GoodnessOfFit \
              ${CARD} \
              --setParameters ${MASK} \
              --algo=saturated \
              -n _CRonly_obs_${YEAR} \
              -m 125.0  > log_obs_${YEAR}.txt &
    popd;
}

NJOBS=50

for YEAR in 2017; do
    gof "${YEAR}" "rgx{mask_.*_signal}=1,LUMISCALE=1" "nominal" 50 &
    gof "${YEAR}" "rgx{mask_.*_signal}=0" "nominal_unblind" 50 &
    # gof "${YEAR}" "rgx{mask_.*_signal}=0,rgx{mask_.*photon}=1" "no_photon_unblind"    "${NJOBS}"
    # gof "${YEAR}" "rgx{mask_.*_signal}=0,rgx{mask_.*_dielec}=1,rgx{mask_.*_dimuon}=1" "no_z_unblind"    "${NJOBS}"
    # gof "${YEAR}" "rgx{mask_.*_signal}=0,rgx{mask_.*_singleel}=1,rgx{mask_.*_singlemu}=1" "no_w_unblind"    "${NJOBS}" &

    # gof "${YEAR}" "rgx{mask_.*_signal}=1,rgx{mask_.*tight.*}=1"                           "notight" "${NJOBS}" &
    # gof "${YEAR}" "rgx{mask_.*_signal}=1,rgx{mask_.*loose.*}=1"                           "noloose" "${NJOBS}" &
    # gof "${YEAR}" "rgx{mask_.*_signal}=1,rgx{mask_.*monojet.*}=1"                         "monov"   "${NJOBS}" &
    # gof "${YEAR}" "rgx{mask_.*_signal}=1,rgx{mask_.*loose.*}=1,rgx{mask_.*tight.*}=1"     "monojet" "${NJOBS}" &
    # gof "${YEAR}" "rgx{mask_.*_signal}=1,rgx{mask_.*monojet.*}=1,rgx{mask_.*tight.*}=1"   "loose"   "${NJOBS}" &
    # gof "${YEAR}" "rgx{mask_.*_signal}=1,rgx{mask_.*monojet.*}=1,rgx{mask_.*loose.*}=1"   "tight"   "${NJOBS}" &
done
# gof "2018" "rgx{mask_.*_signal}=1,rgx{mask_.*tight.*}=1"                         "notight" "${NJOBS}"
# gof "2018" "rgx{mask_.*_signal}=1,rgx{mask_.*loose.*}=1"                         "noloose" "${NJOBS}"
# gof "2018" "rgx{mask_.*_signal}=1,rgx{mask_.*loose.*}=1,rgx{mask_.*tight.*}=1"   "monojet" "${NJOBS}"
# gof "2018" "rgx{mask_.*_signal}=1,rgx{mask_.*monojet.*}=1"                       "monov"   "${NJOBS}"
# gof "2018" "rgx{mask_.*_signal}=1,rgx{mask_.*monojet.*}=1,rgx{mask_.*tight.*}=1" "loose"   "${NJOBS}"
# gof "2018" "rgx{mask_.*_signal}=1,rgx{mask_.*monojet.*}=1,rgx{mask_.*loose.*}=1" "tight"   "${NJOBS}"

# gof "combined" "rgx{mask_.*_signal}=1,rgx{mask_.*tight.*}=1" "notight" "${NJOBS}"
# gof "combined" "rgx{mask_.*_signal}=1,rgx{mask_.*loose.*}=1" "noloose" "${NJOBS}"
# gof "combined" "rgx{mask_.*_signal}=1,rgx{mask_.*loose.*}=1,rgx{mask_.*tight.*}=1" "monojet" "${NJOBS}"
# gof "combined" "rgx{mask_.*_signal}=1,rgx{mask_.*monojet.*}=1,rgx{mask_.*tight.*}=1" "loose" "${NJOBS}"
# gof "combined" "rgx{mask_.*_signal}=1,rgx{mask_.*monojet.*}=1,rgx{mask_.*loose.*}=1" "tight" "${NJOBS}"