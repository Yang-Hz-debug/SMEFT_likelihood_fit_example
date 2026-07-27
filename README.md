# Part 2: SMEFT Combine Directory – Fitting & Results Extraction

**Directory:**  
`/eos/user/h/haozhong/Combine/CMSSW_14_1_0_pre4/src/CombineHarvester/VHccCoHa_STXS_ptbinned_20260727` 

## Scripts Overview

| File | Description |
| :--- | :--- |
| **`xxx_auto.py`** | Extracts ratio values from the LHE-level output folders (the ratio `.txt` files are produced via the [`gridpick_CERN_CMS`](https://github.com/Yang-Hz-debug/gridpick_CERN_CMS) repository) and performs the fitting procedure. |
| **`Get_ration_vs_HWorHB_fitResult.py`** | Extracts the fit results and reformats them into a coefficient-style output. **Important:** Only copy the coefficients that are actually used in `physics_model_SMEFT.py` – do not copy unused ones. |
| **`physics_model_SMEFT.py`** | Defines the baseline model variations for the Wilson coefficients `CHW` and `CHB`. <br> • Currently, the coefficient uncertainties are treated as **Gaussian errors**. <br> • **Future improvements:** This error treatment requires further validation (e.g., through impact studies) and will be updated to correctly assign error values. |
| **`make_smeft_results.py`** | Plotting script to visualise the fitted SMEFT results. |
| **`run_smeft_scan.sh`** | **Main execution script.** <br> • It uses the same card configuration as `run_full_diffxsec_pipeline_28_12_1.sh` (which was previously used for signal-strength POI scans). <br> • **No new modifications** to the card are required – the existing card is fully compatible. |

---

## Workflow Summary

1. **Generate ratios** using the `gridpick_CERN_CMS` tool (outside this directory).
2. Run `xxx_auto.py` to extract these ratios and perform the fit.
3. Run `Get_ration_vs_HWorHB_fitResult.py` to extract and format the fit coefficients (filtering only those used in `physics_model_SMEFT.py`).
4. (Optional) Use `make_smeft_results.py` to produce plots.
5. Execute the main scan via `run_smeft_scan.sh`.

---

## Notes & Future Improvements

- The current Gaussian error assumption for coefficients is provisional. **Next steps** include:
  - Performing impact studies to validate the error treatment.
  - Updating the code to correctly propagate and assign uncertainties.
- The pipeline is designed to reuse existing Combine cards, ensuring consistency with previous signal-strength analyses.
