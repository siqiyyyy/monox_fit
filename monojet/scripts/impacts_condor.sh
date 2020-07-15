#!/bin/bash

do_impacts(){
    YEAR=${1}
    SIGNAL=${2}
    mkdir -p ${YEAR}_${SIGNAL}
    pushd ${YEAR}_${SIGNAL}
    COMMON_OPTS="-t -1 --expectSignal=${SIGNAL} --parallel=4 --rMin=-1 --autoRange 5 --squareDistPoiStep"
    combineTool.py -M Impacts \
                   -d ../../cards/card_monojet_${YEAR}.root \
                   -m 125 \
                   --doInitialFit \
                   --robustFit 1 \
                   ${COMMON_OPTS}

    # Submit the hard work to condor
    TAG=task_${YEAR}_${SIGNAL}_${RANDOM}
    combineTool.py -M Impacts -d ../../cards/card_monojet_${YEAR}.root \
                   -m 125 \
                   --robustFit 1 \
                   --doFits \
                   --job-mode condor \
                   --task-name ${TAG} \
                   --sub-opts '+MaxRuntime=3600' \
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
                   -d ../../cards/card_monojet_${YEAR}.root \
                   -m 125 \
                   -o impacts.json \
                    ${COMMON_OPTS}
    popd
    plotImpacts.py -i ${YEAR}_${SIGNAL}/impacts.json -o impacts_monojet_${YEAR}_${SIGNAL}
}
export -f do_impacts
### Impacts
mkdir -p impacts
pushd impacts
for SIGNAL in "0.0"; do
    for YEAR in combined; do
        nohup bash -c "do_impacts $YEAR $SIGNAL" >  impacts_${YEAR}_${SIGNAL}.log &
    done
done
popd