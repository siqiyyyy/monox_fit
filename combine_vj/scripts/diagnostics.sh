# text2workspace.py card_combined.txt --channel-masks

mkdir -p diagnostics
pushd diagnostics

for YEAR in 2017 2018 combined; do
        combine -M FitDiagnostics \
                --saveShapes \
                --saveWithUncertainties \
                --robustFit 1 \
                --setParameters 'rgx{mask_.*_signal}'=1 \
                -n _monojet_monov_${YEAR} \
                ../cards/card_monojet_monov_nominal_${YEAR}.root \
                | tee diag_${YEAR}.log && \
        python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
                fitDiagnostics_monojet_monov_${YEAR}.root \
                -g diffnuisances_monojet_monov_combined_${YEAR}.root \
                --skipFitS | tee diffnuis_${YEAR}.log &

        combine -M FitDiagnostics \
                --saveShapes \
                --saveWithUncertainties \
                --robustFit 1 \
                --setParameters 'rgx{mask_.*_signal}'=0 \
                -n _unblind_monojet_monov_${YEAR} \
                ../cards/card_monojet_monov_nominal_${YEAR}.root \
                | tee diag_unblind_${YEAR}.log && \
        python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
                fitDiagnostics_unblind_monojet_monov_${YEAR}.root \
                -g diffnuisances_unblind__monojet_monov_combined_${YEAR}.root \
                --skipFitS | tee diffnuis_unblind_${YEAR}.log &
done
popd