
mkdir -p limit
pushd limit

for YEAR in 2017 2018 combined; do
    combine -M AsymptoticLimits -t -1 -n monojet_monov_nominal_${YEAR} ../cards/card_monojet_monov_nominal_${YEAR}.root --setParameters LUMISCALE=1 --freezeParameters LUMISCALE | tee log_${YEAR}.txt &
done
popd