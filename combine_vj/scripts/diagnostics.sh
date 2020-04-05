# text2workspace.py card_combined.txt --channel-masks

mkdir -p diagnostics
pushd diagnostics

for YEAR in 2017 2018 combined; do
        combine -M FitDiagnostics \
                --saveShapes \
                --saveWithUncertainties \
                --robustFit 1 \
                --setParameters mask_monojet_2017_signal=1,mask_monovtight_2017_signal=1,mask_monojet_2018_signal=1,mask_monovtight_2018_signal=1 \
                -n _monojet_monov_${YEAR} \
                ../cards/card_monojet_monov_nominal_tight_${YEAR}.root \
                | tee diag_${YEAR}.log

        python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
                fitDiagnostics_monojet_monov_${YEAR}.root \
                -g diffnuisances_monojet_monov_combined_${YEAR}.root
done
popd