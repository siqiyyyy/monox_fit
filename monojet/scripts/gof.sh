COMMON_OPTS="--setParameters 'rgx{mask_.*signal}'=1"

mkdir -p gof
pushd gof

for YEAR in 2017 2018 combined; do
    mkdir -p $YEAR;
    pushd $YEAR;
    combine -M GoodnessOfFit ../../cards/card_monojet_${YEAR}.root ${COMMON_OPTS} --algo=saturated -t 100 -s -1 -n toys_${YEAR} -m 125.0 > log_toys_${YEAR}.txt &
    combine -M GoodnessOfFit ../../cards/card_monojet_${YEAR}.root ${COMMON_OPTS} --algo=saturated -n _obs_${YEAR} -m 125.0  > log_obs_${YEAR}.txt &
    popd;
done
popd
