
### Asimov limit
mkdir -p limit
pushd limit
for YEAR in 2017 2018; do
    combine -M AsymptoticLimits -t -1 -n _vbf_${YEAR} ../cards/card_vbf_${YEAR}.root | tee log_asimov_${YEAR}.txt
    combine -M AsymptoticLimits -t -1 -n _vbf_nophoton_${YEAR} --setParameters mask_vbf_photon=1 ../cards/card_vbf_${YEAR}.root | tee log_asimov_nophoton_${YEAR}.txt
done
popd