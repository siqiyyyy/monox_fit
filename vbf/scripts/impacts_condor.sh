#!/bin/bash -e
do_impacts(){
    YEAR=${1}
    SIGNAL=${2}
    SUBTAG=${3}
    mkdir -p ${SUBTAG}${YEAR}_${SIGNAL}
    pushd ${SUBTAG}${YEAR}_${SIGNAL}
    COMMON_OPTS="--parallel=4 --rMin=-5 --rMax=5 --autoRange 5 --squareDistPoiStep"

    if [ "${SUBTAG}" = "nophoton" ]; then
        COMMON_OPTS="${COMMON_OPTS} --setParameters mask_vbf_${YEAR}_photon=1"
    fi
    combineTool.py -M Impacts \
                   -d ../../cards/card_vbf_${YEAR}.root \
                   -m 125 \
                   --doInitialFit \
                   --robustFit 1 \
                   --cminDefaultMinimizerStrategy 0 \
                   ${COMMON_OPTS} || exit 1

    # Submit the hard work to condor
    TAG=task_${YEAR}_${SIGNAL}_${RANDOM}
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root \
                   -m 125 \
                   --robustFit 1 \
                   --doFits \
                   --job-mode condor \
                   --task-name ${TAG} \
                   --cminDefaultMinimizerStrategy 0 \
                    ${COMMON_OPTS} || exit 1

    # Wait for condor jobs to return
    date
    if [ ! -e ${TAG}*.log ]; then
        exit 1
    fi
    for i in $(seq 1 1 10); do
        condor_wait -debug -status ${TAG}*.log && break;
        sleep $((i*120))
    done
    date
    sleep 60

    combineTool.py -M Impacts \
                   -d ../../cards/card_vbf_${YEAR}.root \
                   -m 125 \
                   -o impacts.json \
                   --robustFit 1 \
                   --cminDefaultMinimizerStrategy 0 \
                    ${COMMON_OPTS}
    popd
    plotImpacts.py -i ${SUBTAG}${YEAR}_${SIGNAL}/impacts.json -o impacts_vbf_${SUBTAG}${YEAR}_${SIGNAL} --blind
}

export -f do_impacts
### Impacts
mkdir -p impacts
pushd impacts
for SUBTAG in ""; do
    for SIGNAL in "0.0"; do
        for YEAR in combined; do
            nohup bash -c "do_impacts $YEAR $SIGNAL ${SUBTAG}" >  impacts_${SUBTAG}${YEAR}_${SIGNAL}.log &
        done
    done
done
popd
