mkdir -p limit
pushd limit

#remove limit on stack size to prevent related segfault
ulimit -s unlimited

for file in ../cards/*.root; do

    TAG=$(basename $file | sed 's/card_//g;s/.root//g');
    combine -M AsymptoticLimits $file -t -1 -n $TAG | tee log_$TAG.txt & 
done
popd

# mkdir -p diagnostics
# pushd diagnostics
# for file in ../cards/*.root; do
#     TAG=$(basename $file | sed 's/card_//g;s/.root//g');
#     combine -M FitDiagnostics  $file -t -1 -n $TAG --saveShapes --saveWithUncertainties --setParameters mask_monovloose_signal=1,mask_monovtight_signal=1 | tee log_fitDiag_$TAG.txt
# done
# popd
