# VHcc Combine Harvest

Here one can find some scripts used to produce the datacards for VHcc analysis.  
We use CombineHarvester package for this job, therefore one has to first install `Combine` and `CombineHarvester` packages.

## Getting started

1. Setup your [Combine](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/) package:  
```
cmsrel CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v10.0.2
scramv1 b clean; scramv1 b # always make a clean build
```  
**Note** that the above tag was the recommended at the time of writing this (Nov 7, 2024). Check if a newer tag is recommended before proceeding.


2. Setup the [CombineHarvester](http://cms-analysis.github.io/CombineHarvester/) package:  
```
cmsrel CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
# IMPORTANT: Checkout the recommended tag on the link above
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
git checkout v3.0.0-pre1
scram b
```  
**Note**: same as for Combine, check out the latest recommended tag.  


3. Now, get *this* repository under your `CombineHarvester` directory:
```
cd CombineHarvester
git clone ssh://git@gitlab.cern.ch:7999/cms-analysis/hig/vhcc-run3/VHccCoHa.git
scram b
```

4. Get the input file with shapes from running the analysis code.

5. Run the script:
```
python3 scripts/vhcc_cards.py -c Zll -y 2022_preEE
```  

The datacards and root file with re-arranged shapes should appear under `output` directory.

6. Create Combine workspace from the datacards:
```
ulimit -s unlimited
combineTool.py -M T2W --cc combined.txt -o ws.root -i output/vhcc_Run3_2022_preEE/cmb/*.txt
```  

7. Run the limit:
```
combineTool.py -M AsymptoticLimits -d ws.root --there --run blind
```  
