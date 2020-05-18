
do_impacts(){
    YEAR=${1}
    SIGNAL=${2}
    SUBTAG=${3}
    mkdir -p ${SUBTAG}${YEAR}_${SIGNAL}
    pushd ${SUBTAG}${YEAR}_${SIGNAL}
    COMMON_OPTS="-t -1 --expectSignal=${SIGNAL} --parallel=4 --rMin=-1 --autoRange 5 --squareDistPoiStep"

    if [ "${SUBTAG}" = "nophoton" ]; then
        COMMON_OPTS="${COMMON_OPTS} --setParameters mask_vbf_${YEAR}_photon=1"
    fi
    combineTool.py -M Impacts \
                   -d ../../cards/card_vbf_${YEAR}.root \
                   -m 125 \
                   --doInitialFit \
                   --robustFit 1 \
                   ${COMMON_OPTS}

    # Submit the hard work to condor
    TAG=task_${YEAR}_${SIGNAL}_${RANDOM}
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root \
                   -m 125 \
                   --robustFit 1 \
                   --doFits \
                   --job-mode condor \
                   --task-name ${TAG} \
                    ${COMMON_OPTS}

    # Wait for condor jobs to return
    date
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
                    ${COMMON_OPTS}
    popd
    plotImpacts.py -i ${SUBTAG}${YEAR}_${SIGNAL}/impacts.json -o impacts_vbf_${SUBTAG}${YEAR}_${SIGNAL}
}

export -f do_impacts
### Impacts
mkdir -p impacts
pushd impacts
for SUBTAG in "nophoton"; do
    for SIGNAL in "0.0"; do
        for YEAR in 2017; do
            nohup bash -c "do_impacts $YEAR $SIGNAL ${SUBTAG}" >  impacts_${SUBTAG}${YEAR}_${SIGNAL}.log &
        done
    done
done
popd
