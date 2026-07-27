# # import os
# # from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel


# # class SMEFTModel(PhysicsModel):
# #     """
# #     SMEFT model for differential VH cross section.

# #     Signal yield per pT(H) bin = SM * f, where
# #       f = (1 + a_i*CHB + b_i*CHB^2 + c_i*CHW + d_i*CHW^2)

# #     Coefficients have ~2% theoretical uncertainty, floating parameters.

# #     Configuration via SMEFT_POI env var:
# #       SMEFT_POI=CHB    -> 1D: CHB is POI, CHW fixed to 0
# #       SMEFT_POI=CHW    -> 1D: CHW is POI, CHB fixed to 0
# #       SMEFT_POI=CHB,CHW -> 2D: both POIs (default)

# #     NOTE: RooFormula treats "inf" as infinity, so we avoid using raw
# #     formula strings containing "pTH_450_inf". Instead we build per-bin
# #     formulas using product/sum factory commands.
# #     """
# #     def __init__(self):
# #         super(SMEFTModel, self).__init__()
# #         self.smeft_poi = os.environ.get('SMEFT_POI', 'CHB,CHW')
# #         self.scale_map = {}

# #     def doParametersOfInterest(self):
# #         # --- Wilson coefficients ---
# #         if self.smeft_poi == 'CHB':
# #             self.modelBuilder.doVar("CHB[0,-10,10]")
# #             self.modelBuilder.doVar("CHW[0]")          # fixed to 0
# #             print("[SMEFTModel] 1D CHB mode: CHW fixed to 0", flush=True)
# #         elif self.smeft_poi == 'CHW':
# #             self.modelBuilder.doVar("CHB[0]")          # fixed to 0
# #             self.modelBuilder.doVar("CHW[0,-10,10]")
# #             print("[SMEFTModel] 1D CHW mode: CHB fixed to 0", flush=True)
# #         else:
# #             self.modelBuilder.doVar("CHB[0,-10,10]")
# #             self.modelBuilder.doVar("CHW[0,-10,10]")
# #             print("[SMEFTModel] 2D mode: both POIs", flush=True)

# #         # --- bin coefficients (2% uncertainty, floating) ---
# #         #   Binning keys use "pTH_XXX" but we replace underscores for 
# #         #   variable names to avoid RooFormula issues with "inf" etc.
# #         unc_frac = 0.02
# #         coeffs_in = {
# #             "pTH_0_60":    (0.10, 0.01, 0.2,  0.02),
# #             "pTH_60_120":  (0.15, 0.015, 0.3,  0.03),
# #             "pTH_120_200": (0.20, 0.02,  0.4,  0.04),
# #             "pTH_200_300": (0.25, 0.025, 0.5,  0.05),
# #             "pTH_300_450": (0.30, 0.03,  0.6,  0.06),
# #             "pTH_450_inf": (0.35, 0.035, 0.7,  0.07),
# #         }
# #         # We build the coeffs dict and store the safe key mapping
# #         self.coeffs = {}
# #         for k, v in coeffs_in.items():
# #             # safe key: replace hyphens and special chars
# #             safe = k.replace("_inf", "_infinity")
# #             self.coeffs[k] = (safe, v)

# #         for k, (safe_key, (a, b, c, d)) in self.coeffs.items():
# #             def make(name, val):
# #                 unc = max(unc_frac * abs(val), 0.001)
# #                 lo = val - 1*abs(unc)
# #                 hi = val + 1*abs(unc)
# #                 self.modelBuilder.doVar(f"{name}[{val:.6f},{lo:.6f},{hi:.6f}]")

# #             make(f"k_a_CHB_{safe_key}", a)
# #             make(f"k_b_CHB2_{safe_key}", b)
# #             make(f"k_c_CHW_{safe_key}", c)
# #             make(f"k_d_CHW2_{safe_key}", d)

# #         # --- build per-bin yield-scale formulas ---
# #         #   getYieldScale must return a name already in the workspace.
# #         #   We use product and sum factory commands which don't have
# #         #   the "inf" parsing issue of RooFormula strings.
# #         for k, (safe_key, (a, b, c, d)) in self.coeffs.items():
# #             try:
# #                 # Build: scale = 1 + term_CHB + term_CHB2 + term_CHW + term_CHW2
# #                 # Using product and sum to avoid RooFormula string issues
# #                 ka = f"k_a_CHB_{safe_key}"
# #                 kb = f"k_b_CHB2_{safe_key}"
# #                 kc = f"k_c_CHW_{safe_key}"
# #                 kd = f"k_d_CHW2_{safe_key}"

# #                 self.modelBuilder.factory_(f"prod::term_a_{safe_key}({ka},CHB)")
# #                 self.modelBuilder.factory_(f"prod::term_b_{safe_key}({kb},CHB,CHB)")
# #                 self.modelBuilder.factory_(f"prod::term_c_{safe_key}({kc},CHW)")
# #                 self.modelBuilder.factory_(f"prod::term_d_{safe_key}({kd},CHW,CHW)")
# #                 self.modelBuilder.factory_(
# #                     f"sum::scale_{safe_key}(1,term_a_{safe_key},term_b_{safe_key},term_c_{safe_key},term_d_{safe_key})"
# #                 )
# #                 self.scale_map[k] = f"scale_{safe_key}"
# #                 print(f"  [OK] scale_{safe_key}", flush=True)
# #             except Exception as e:
# #                 print(f"  [WARN] failed for {k}: {e}", flush=True)
# #                 # fallback constant
# #                 self.modelBuilder.doVar(f"scale_{safe_key}[1]")
# #                 self.scale_map[k] = f"scale_{safe_key}"

# #         # --- POI set ---
# #         if self.smeft_poi == 'CHB':
# #             self.modelBuilder.doSet("POI", "CHB")
# #         elif self.smeft_poi == 'CHW':
# #             self.modelBuilder.doSet("POI", "CHW")
# #         else:
# #             self.smeft_poi = 'CHB,CHW'
# #             self.modelBuilder.doSet("POI", "CHB,CHW")

# #     def getYieldScale(self, bin, process):
# #         # Map ZH signals to the per-bin formula
# #         if process.startswith("ZH_hbb_pTH_"):
# #             bin_suffix = process[len("ZH_hbb_"):]  # e.g. "pTH_0_60"
# #             if bin_suffix in self.scale_map:
# #                 return self.scale_map[bin_suffix]
# #         return 1


# # # register
# # smeftModel = SMEFTModel()


# import os
# from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel


# class SMEFTModel(PhysicsModel):
#     """
#     SMEFT model for differential VH cross section.

#     Signal yield per pT(H) bin i = SM * f_i, where
#       f_i = (1 + a_i*CHB + b_i*CHB^2 + c_i*CHW + d_i*CHW^2)

#     Coefficients have ~2% theoretical uncertainty, floating parameters.

#     Configuration via SMEFT_POI env var:
#       SMEFT_POI=CHB    -> 1D: CHB is POI, CHW fixed to 0
#       SMEFT_POI=CHW    -> 1D: CHW is POI, CHB fixed to 0
#       SMEFT_POI=CHB,CHW -> 2D: both POIs (default)

#     NOTE: RooFormula treats "inf" as infinity, so we avoid using raw
#     formula strings containing "pTH_450_inf". Instead we build per-bin
#     formulas using product/sum factory commands.
#     """
#     def __init__(self):
#         super(SMEFTModel, self).__init__()
#         self.smeft_poi = os.environ.get('SMEFT_POI', 'CHB,CHW')
#         self.scale_map = {}

#     def doParametersOfInterest(self):
#         # --- Wilson coefficients ---
#         if self.smeft_poi == 'CHB':
#             self.modelBuilder.doVar("CHB[0,-10,10]")
#             self.modelBuilder.doVar("CHW[0]")          # fixed to 0
#             print("[SMEFTModel] 1D CHB mode: CHW fixed to 0", flush=True)
#         elif self.smeft_poi == 'CHW':
#             self.modelBuilder.doVar("CHB[0]")          # fixed to 0
#             self.modelBuilder.doVar("CHW[0,-10,10]")
#             print("[SMEFTModel] 1D CHW mode: CHB fixed to 0", flush=True)
#         else:
#             self.modelBuilder.doVar("CHB[0,-10,10]")
#             self.modelBuilder.doVar("CHW[0,-10,10]")
#             print("[SMEFTModel] 2D mode: both POIs", flush=True)

#         # --- bin coefficients (2% uncertainty, floating) ---
#         unc_frac = 0.05
#         # coeffs_in = {
#         #     "pTH_0_60":    (0.10, 0.01, 0.2,  0.02),
#         #     "pTH_60_120":  (0.15, 0.015, 0.3,  0.03),
#         #     "pTH_120_200": (0.20, 0.02,  0.4,  0.04),
#         #     "pTH_200_300": (0.25, 0.025, 0.5,  0.05),
#         #     "pTH_300_450": (0.30, 0.03,  0.6,  0.06),
#         #     "pTH_450_inf": (0.35, 0.035, 0.7,  0.07),
#         # }
#         coeffs_in = {
#             "pTH_0_60":    (0.065305, 0.017151, 0.636715, 0.156014),
#             "pTH_60_120":    (0.074252, 0.024416, 0.743476, 0.221406),
#             "pTH_120_200":    (0.072536, 0.047706, 0.854893, 0.402098),
#             "pTH_200_300":    (0.055479, 0.092100, 0.888280, 0.774872),
#             "pTH_300_450":    (0.130734, 0.157467, 1.062200, 1.583314),
#             "pTH_450_inf":    (0.125439, 0.432533, 1.250515, 3.588667),
#         }
        
#         self.coeffs = {}
#         for k, v in coeffs_in.items():
#             safe = k.replace("_inf", "_infinity")
#             self.coeffs[k] = (safe, v)

#         # Create all variables and constraints
#         for k, (safe_key, (a, b, c, d)) in self.coeffs.items():
#             def make(name, val):
#                 unc = max(unc_frac * abs(val), 0.001)
#                 lo = val - 1*abs(unc)
#                 hi = val + 1*abs(unc)
#                 self.modelBuilder.doVar(f"{name}[{val:.6f},{lo:.6f},{hi:.6f}]")

#             make(f"k_a_CHB_{safe_key}", a)
#             make(f"k_b_CHB2_{safe_key}", b)
#             make(f"k_c_CHW_{safe_key}", c)
#             make(f"k_d_CHW2_{safe_key}", d)
            
#             # Add Gaussian constraints - MUST end with _Pdf for combine to recognize them
#             unc_a = max(unc_frac * abs(a), 0.001)
#             unc_b = max(unc_frac * abs(b), 0.001)
#             unc_c = max(unc_frac * abs(c), 0.001)
#             unc_d = max(unc_frac * abs(d), 0.001)
            
#             self.modelBuilder.factory_(
#                 f"Gaussian::gauss_a_{safe_key}_Pdf(k_a_CHB_{safe_key}, {a:.6f}, {unc_a:.6f})"
#             )
#             self.modelBuilder.factory_(
#                 f"Gaussian::gauss_b_{safe_key}_Pdf(k_b_CHB2_{safe_key}, {b:.6f}, {unc_b:.6f})"
#             )
#             self.modelBuilder.factory_(
#                 f"Gaussian::gauss_c_{safe_key}_Pdf(k_c_CHW_{safe_key}, {c:.6f}, {unc_c:.6f})"
#             )
#             self.modelBuilder.factory_(
#                 f"Gaussian::gauss_d_{safe_key}_Pdf(k_d_CHW2_{safe_key}, {d:.6f}, {unc_d:.6f})"
#             )
            
#             print(f"  [OK] Gaussian constraints for {safe_key}", flush=True)

#         # --- build per-bin yield-scale formulas ---
#         for k, (safe_key, (a, b, c, d)) in self.coeffs.items():
#             try:
#                 ka = f"k_a_CHB_{safe_key}"
#                 kb = f"k_b_CHB2_{safe_key}"
#                 kc = f"k_c_CHW_{safe_key}"
#                 kd = f"k_d_CHW2_{safe_key}"

#                 self.modelBuilder.factory_(f"prod::term_a_{safe_key}({ka},CHB)")
#                 self.modelBuilder.factory_(f"prod::term_b_{safe_key}({kb},CHB,CHB)")
#                 self.modelBuilder.factory_(f"prod::term_c_{safe_key}({kc},CHW)")
#                 self.modelBuilder.factory_(f"prod::term_d_{safe_key}({kd},CHW,CHW)")
#                 self.modelBuilder.factory_(
#                     f"sum::scale_{safe_key}(1,term_a_{safe_key},term_b_{safe_key},term_c_{safe_key},term_d_{safe_key})"
#                 )
#                 self.scale_map[k] = f"scale_{safe_key}"
#                 print(f"  [OK] scale_{safe_key}", flush=True)
#             except Exception as e:
#                 print(f"  [WARN] failed for {k}: {e}", flush=True)
#                 self.modelBuilder.doVar(f"scale_{safe_key}[1]")
#                 self.scale_map[k] = f"scale_{safe_key}"

#         # --- POI set ---
#         if self.smeft_poi == 'CHB':
#             self.modelBuilder.doSet("POI", "CHB")
#         elif self.smeft_poi == 'CHW':
#             self.modelBuilder.doSet("POI", "CHW")
#         else:
#             self.modelBuilder.doSet("POI", "CHB,CHW")
        
#         print("[SMEFTModel] Done adding parameters and constraints", flush=True)

#     def getYieldScale(self, bin, process):
#         if process.startswith("ZH_hbb_pTH_"):
#             bin_suffix = process[len("ZH_hbb_"):]
#             if bin_suffix in self.scale_map:
#                 return self.scale_map[bin_suffix]
#         return 1


# # register
# smeftModel = SMEFTModel()

import os
from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel


class SMEFTModel(PhysicsModel):
    """
    SMEFT model for differential VH cross section with cubic support.

    Signal yield per pT(H) bin i = SM * f_i, where:
      quadratic: f_i = 1 + a_i*CHB + b_i*CHB^2 + c_i*CHW + d_i*CHW^2
      cubic:     f_i = 1 + a_i*CHB + b_i*CHB^2 + e_i*CHB^3 + c_i*CHW + d_i*CHW^2 + f_i*CHW^3

    ADDED: normalization correction so that at CHB=CHW=0, yield = SM (not SMEFT_0p0)
    The correction factor = SM / SMEFT_0p0 from data.
    """
    def __init__(self):
        super(SMEFTModel, self).__init__()
        self.smeft_poi = os.environ.get('SMEFT_POI', 'CHB,CHW')
        # self.smeft_poly = os.environ.get('SMEFT_POLY', 'quadratic')
        self.smeft_poly = os.environ.get('SMEFT_POLY', 'cubic')
        self.use_cubic = (self.smeft_poly == 'cubic')
        self.scale_map = {}

    def doParametersOfInterest(self):
        # --- Wilson coefficients ---
        if self.smeft_poi == 'CHB':
            self.modelBuilder.doVar("CHB[0,-10,10]")
            self.modelBuilder.doVar("CHW[0]")
            print("[SMEFTModel] 1D CHB mode: CHW fixed to 0", flush=True)
        elif self.smeft_poi == 'CHW':
            self.modelBuilder.doVar("CHB[0]")
            self.modelBuilder.doVar("CHW[0,-10,10]")
            print("[SMEFTModel] 1D CHW mode: CHB fixed to 0", flush=True)
        else:
            self.modelBuilder.doVar("CHB[0,-10,10]")
            self.modelBuilder.doVar("CHW[0,-10,10]")
            print("[SMEFTModel] 2D mode: both POIs", flush=True)

        print(f"[SMEFTModel] Polynomial mode: {self.smeft_poly}", flush=True)

        # --- bin coefficients (5% uncertainty, floating) ---
        # Format: (a_CHB, b_CHB2, c_CHW, d_CHW2, e_CHB3, f_CHW3, norm_correction)
        # norm_correction = SM / SMEFT_0p0 (i.e., 1 / ratio_0p0_over_SM)
        unc_frac = 0.05
        # coeffs_in = {
        #     "pTH_0_60":    (0.065305, 0.017151, 0.636715, 0.156014, 0.0, 0.0, 0.954592),  # 1/1.047562
        #     "pTH_60_120":  (0.074252, 0.024416, 0.743476, 0.221406, 0.0, 0.0, 1.000161),  # 1/0.999839
        #     "pTH_120_200": (0.072536, 0.047706, 0.854893, 0.402098, 0.0, 0.0, 0.978266),  # 1/1.022219
        #     "pTH_200_300": (0.055479, 0.092100, 0.888280, 0.774872, 0.0, 0.0, 1.029970),  # 1/0.970901
        #     "pTH_300_450": (0.130734, 0.157467, 1.062200, 1.583314, 0.0, 0.0, 0.978985),  # 1/1.021463
        #     "pTH_450_inf": (0.125439, 0.432533, 1.250515, 3.588667, 0.0, 0.0, 1.107377),  # 1/0.903036
        # }
        coeffs_in = {
            "pTH_0_60":    (0.069751, 0.010800, 0.002032, 0.577464, 0.326195, -0.109114, 0.954592),
            "pTH_60_120":    (0.090765, 0.000824, 0.007550, 0.677527, 0.410827, -0.121450, 1.000161),
            "pTH_120_200":    (0.090910, 0.021456, 0.008400, 0.824115, 0.490501, -0.056681, 0.978266),
            "pTH_200_300":    (0.040838, 0.113017, -0.006693, 0.780191, 1.085324, -0.199052, 1.029970),
            "pTH_300_450":    (0.231797, 0.013082, 0.046204, 1.123344, 1.407696, 0.112601, 0.978985),
            "pTH_450_inf":    (0.145251, 0.404229, 0.009058, 1.379302, 3.218765, 0.237169, 1.107377),
        }
        # coeffs_in = {
        #     "pTH_0_60":    (0.069751, 0.010800, 0.002032, 0.577464, 0.326195, -0.109114,1),
        #     "pTH_60_120":    (0.090765, 0.000824, 0.007550, 0.677527, 0.410827, -0.121450,1),
        #     "pTH_120_200":    (0.090910, 0.021456, 0.008400, 0.824115, 0.490501, -0.056681,1),
        #     "pTH_200_300":    (0.040838, 0.113017, -0.006693, 0.780191, 1.085324, -0.199052, 1),
        #     "pTH_300_450":    (0.231797, 0.013082, 0.046204, 1.123344, 1.407696, 0.112601, 1),
        #     "pTH_450_inf":    (0.145251, 0.404229, 0.009058, 1.379302, 3.218765, 0.237169, 1),
        # }
        self.coeffs = {}
        for k, v in coeffs_in.items():
            safe = k.replace("_inf", "_infinity")
            self.coeffs[k] = (safe, v)

        # Create all variables, constraints and scale formulas
        for k, (safe_key, coeffs) in self.coeffs.items():
            a, b, c, d, e, f, norm_corr = coeffs
            
            def make_param(name, val):
                unc = max(unc_frac * abs(val), 0.001)
                lo = val - 5*abs(unc)
                hi = val + 5*abs(unc)
                self.modelBuilder.doVar(f"{name}[{val:.6f},{lo:.6f},{hi:.6f}]")
            
            # Create coefficient parameters
            make_param(f"k_a_CHB_{safe_key}", a)
            make_param(f"k_b_CHB2_{safe_key}", b)
            make_param(f"k_c_CHW_{safe_key}", c)
            make_param(f"k_d_CHW2_{safe_key}", d)
            
            # Add Gaussian constraints
            unc_a = max(unc_frac * abs(a), 0.001)
            unc_b = max(unc_frac * abs(b), 0.001)
            unc_c = max(unc_frac * abs(c), 0.001)
            unc_d = max(unc_frac * abs(d), 0.001)
            
            self.modelBuilder.factory_(
                f"Gaussian::gauss_a_{safe_key}_Pdf(k_a_CHB_{safe_key}, {a:.6f}, {unc_a:.6f})"
            )
            self.modelBuilder.factory_(
                f"Gaussian::gauss_b_{safe_key}_Pdf(k_b_CHB2_{safe_key}, {b:.6f}, {unc_b:.6f})"
            )
            self.modelBuilder.factory_(
                f"Gaussian::gauss_c_{safe_key}_Pdf(k_c_CHW_{safe_key}, {c:.6f}, {unc_c:.6f})"
            )
            self.modelBuilder.factory_(
                f"Gaussian::gauss_d_{safe_key}_Pdf(k_d_CHW2_{safe_key}, {d:.6f}, {unc_d:.6f})"
            )
            print(f"  [OK] Gaussian constraints for {safe_key} (quadratic)", flush=True)
            
            if self.use_cubic:
                make_param(f"k_e_CHB3_{safe_key}", e)
                make_param(f"k_f_CHW3_{safe_key}", f)
                unc_e = max(unc_frac * abs(e), 0.001)
                unc_f = max(unc_frac * abs(f), 0.001)
                self.modelBuilder.factory_(
                    f"Gaussian::gauss_e_{safe_key}_Pdf(k_e_CHB3_{safe_key}, {e:.6f}, {unc_e:.6f})"
                )
                self.modelBuilder.factory_(
                    f"Gaussian::gauss_f_{safe_key}_Pdf(k_f_CHW3_{safe_key}, {f:.6f}, {unc_f:.6f})"
                )
                print(f"  [OK] Gaussian constraints for {safe_key} (cubic)", flush=True)

            # Add normalization correction as a constant parameter
            self.modelBuilder.doVar(f"k_norm_{safe_key}[{norm_corr:.6f}]")
            print(f"  [INFO] Normalization correction for {safe_key}: {norm_corr:.6f} (SM/SMEFT_0p0)", flush=True)

        # --- build per-bin yield-scale formulas ---
        for k, (safe_key, coeffs) in self.coeffs.items():
            a, b, c, d, e, f, norm_corr = coeffs
            try:
                ka = f"k_a_CHB_{safe_key}"
                kb = f"k_b_CHB2_{safe_key}"
                kc = f"k_c_CHW_{safe_key}"
                kd = f"k_d_CHW2_{safe_key}"
                knorm = f"k_norm_{safe_key}"

                # Build the polynomial part (1 + terms)
                self.modelBuilder.factory_(f"prod::term_a_{safe_key}({ka},CHB)")
                self.modelBuilder.factory_(f"prod::term_b_{safe_key}({kb},CHB,CHB)")
                self.modelBuilder.factory_(f"prod::term_c_{safe_key}({kc},CHW)")
                self.modelBuilder.factory_(f"prod::term_d_{safe_key}({kd},CHW,CHW)")
                
                if self.use_cubic:
                    ke = f"k_e_CHB3_{safe_key}"
                    kf = f"k_f_CHW3_{safe_key}"
                    self.modelBuilder.factory_(f"prod::term_e_{safe_key}({ke},CHB,CHB,CHB)")
                    self.modelBuilder.factory_(f"prod::term_f_{safe_key}({kf},CHW,CHW,CHW)")
                    self.modelBuilder.factory_(
                        f"sum::poly_{safe_key}(1,term_a_{safe_key},term_b_{safe_key},term_c_{safe_key},term_d_{safe_key},term_e_{safe_key},term_f_{safe_key})"
                    )
                else:
                    self.modelBuilder.factory_(
                        f"sum::poly_{safe_key}(1,term_a_{safe_key},term_b_{safe_key},term_c_{safe_key},term_d_{safe_key})"
                    )
                
                # Apply normalization correction: scale = norm * poly
                self.modelBuilder.factory_(
                    f"prod::scale_{safe_key}({knorm},poly_{safe_key})"
                )
                
                self.scale_map[k] = f"scale_{safe_key}"
                print(f"  [OK] scale_{safe_key} = norm_{safe_key} * poly_{safe_key} ({self.smeft_poly})", flush=True)
            except Exception as e:
                print(f"  [WARN] failed for {k}: {e}", flush=True)
                self.modelBuilder.doVar(f"scale_{safe_key}[1]")
                self.scale_map[k] = f"scale_{safe_key}"

        # --- POI set ---
        if self.smeft_poi == 'CHB':
            self.modelBuilder.doSet("POI", "CHB")
        elif self.smeft_poi == 'CHW':
            self.modelBuilder.doSet("POI", "CHW")
        else:
            self.modelBuilder.doSet("POI", "CHB,CHW")
        
        print(f"[SMEFTModel] Done adding parameters and constraints (poly={self.smeft_poly})", flush=True)

    def getYieldScale(self, bin, process):
        if process.startswith("ZH_hbb_pTH_"):
            bin_suffix = process[len("ZH_hbb_"):]
            if bin_suffix in self.scale_map:
                return self.scale_map[bin_suffix]
        return 1


# register
smeftModel = SMEFTModel()