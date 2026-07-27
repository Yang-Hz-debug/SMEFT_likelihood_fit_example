import CombineHarvester.CombineTools.ch as ch

def AddCommonSystematics(cb, year=None):
  period = None
  if year in ["2016","2017","2018"]:
    period = 'Run2'
  else:
    period = 'Run3'

  signal = cb.cp().signals().process_set()

  # -------------------------------------------------------------------
  # Luminosity uncertainty: decomposed for Run3, single for Run2
  if period=='Run3':
    # Extract base year (e.g., "2022_preEE" -> "2022")
    base_year = year.split('_')[0] if '_' in year else year
    lumi_vals = {
        '2022': 1.014,  # 1.4%
        '2023': 1.013,  # 1.3%
        '2024': 1.016   # 1.6%
    }
    if base_year in lumi_vals:
        # lumi_1: correlated across all years
        cb.cp().AddSyst(cb, 'lumi_1', 'lnN', ch.SystMap()(lumi_vals[base_year]))
        # lumi_2: partially correlated (2023,2024)
        if base_year in ['2023','2024']:
            cb.cp().AddSyst(cb, 'lumi_2', 'lnN', ch.SystMap()(lumi_vals[base_year]))
        # lumi_3: uncorrelated (2024 only)
        if base_year == '2024':
            cb.cp().AddSyst(cb, 'lumi_3', 'lnN', ch.SystMap()(lumi_vals[base_year]))
  elif period=='Run2':
    cb.cp().AddSyst(cb,'lumi_13TeV','lnN', ch.SystMap()(1.010))

  # -------------------------------------------------------------------
  # Theory uncertainties: signal (unchanged)
  cb.cp().AddSyst(cb,
                  'pdf_Higgs_qqbar', 'lnN', ch.SystMap('process')
                  (['ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf','ZH_hbb_inclusive','ZH_hcc'], 1.016)
                  (['WH_hbb','WH_hcc'], 1.019))

  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'pdf_Higgs_gg', 'lnN', ch.SystMap()(1.024))
  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'QCDscale_ggZH', 'lnN',ch.SystMap()((1.251,0.811)))

  cb.cp().AddSyst(cb,'QCDscale_VH', 'lnN', ch.SystMap('process')
                  (['ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf','ZH_hbb_inclusive','ZH_hcc'], (1.038,0.969))
                  (['WH_hbb','WH_hcc'], (1.005,0.993)))

  cb.cp().process(['ZH_hcc','WH_hcc','ggZH_hcc']).AddSyst(cb,'BR_hcc', 'lnN', ch.SystMap()((1.05,0.97)))
  cb.cp().process(['ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf','ZH_hbb_inclusive','WH_hbb','ggZH_hbb']).AddSyst(cb,'BR_hbb', 'lnN', ch.SystMap()(1.005))

  #NLO EWK pt(V) correction to the VH and ggZH processes
  cb.cp().AddSyst(cb,
                  'CMS_vhbb_boost_EWK', 'lnN', ch.SystMap('channel','process')
                  (['Zee','Zmm'],['ZH_hcc','ggZH_hcc','ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf','ZH_hbb_inclusive','ggZH_hbb'], 1.02)
                  (['Znn'],['ZH_hcc','WH_hcc','ggZH_hcc','ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf','ZH_hbb_inclusive','WH_hbb','ggZH_hbb'],1.02)
                  (['Wen','Wmn'],['WH_hcc','ZH_hcc','WH_hbb','ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf','ZH_hbb_inclusive'],1.02))

  # Measured cross section uncertainties ############TODO:if have rate param, consider not use these
#   cb.cp().process(['ST']).AddSyst(cb,'CMS_vhqq_ST', 'lnN', ch.SystMap()(1.15))
#   cb.cp().process(['WW', 'VZbb', 'VZcc', 'VZlx']).AddSyst(cb,'CMS_vhqq_WW', 'lnN', ch.SystMap()(1.05))

  # Theoretical PDF uncertainties
  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'CMS_LHE_pdf_ggZH', 'lnN', ch.SystMap()(1.023))
  cb.cp().process(['ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf','ZH_hbb_inclusive','ZH_hcc']).AddSyst(cb,'CMS_LHE_pdf_ZH', 'lnN', ch.SystMap()(1.018))
  cb.cp().process(['WH_hbb','WH_hcc']).AddSyst(cb,'CMS_LHE_pdf_WH', 'lnN', ch.SystMap()(1.018))
  ############TODO:if have rate param, consider not use these
#   cb.cp().process(['TT']).AddSyst(cb,'CMS_LHE_pdf_TT', 'lnN', ch.SystMap()(1.0265))
#   cb.cp().process(['ST']).AddSyst(cb,'CMS_LHE_pdf_ST', 'lnN', ch.SystMap()(1.0288))
 # cb.cp().process(['VJetbx','VJetcx','VJetll', 'WJetbx','WJetcx','WJetll', 'ZJetbx','ZJetcx','ZJetll']).AddSyst(cb,'CMS_LHE_pdf_VJet', 'lnN', ch.SystMap()(1.027))

  # PCA shape variations (unchanged)
  import ROOT
  import os
  pca_systs = set()
  for file_suffix in ['2L', '1L', '0L']:
      pca_file = f'./vhqq_shapes_{year}_{file_suffix}.root'
      if os.path.exists(pca_file):
          f = ROOT.TFile.Open(pca_file)
          if f:
              for dir_key in f.GetListOfKeys():
                  d = dir_key.ReadObj()
                  if d.InheritsFrom('TDirectory'):
                      for hist_key in d.GetListOfKeys():
                          hname = hist_key.GetName()
                          if 'PCA' in hname and 'Up' in hname:
                              sys_name = hname.split('_', 1)[1].replace('Up', '')
                              pca_systs.add(sys_name)
              f.Close()

  for sys_name in pca_systs:
      if 'dy_hf_2e' in sys_name:
          cb.cp().channel(['Zee']).process(['VJetbx','VJetcx']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'dy_hf_2m' in sys_name:
          cb.cp().channel(['Zmm']).process(['VJetbx','VJetcx']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'dy_lf_2e' in sys_name:
          cb.cp().channel(['Zee']).process(['VJetll']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'dy_lf_2m' in sys_name:
          cb.cp().channel(['Zmm']).process(['VJetll']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'w_hf_1e' in sys_name:
          cb.cp().channel(['Wen']).process(['WJetbx','WJetcx']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'w_hf_1m' in sys_name:
          cb.cp().channel(['Wmn']).process(['WJetbx','WJetcx']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'w_lf_1e' in sys_name:
          cb.cp().channel(['Wen']).process(['WJetll']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'w_lf_1m' in sys_name:
          cb.cp().channel(['Wmn']).process(['WJetll']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'z_hf_0l' in sys_name:
          cb.cp().channel(['Znn']).process(['ZJetbx','ZJetcx']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'z_lf_0l' in sys_name:
          cb.cp().channel(['Znn']).process(['ZJetll']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'w_hf_0l' in sys_name:
          cb.cp().channel(['Znn']).process(['WJetbx','WJetcx']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))
      if 'w_lf_0l' in sys_name:
          cb.cp().channel(['Znn']).process(['WJetll']).AddSyst(cb, sys_name, 'shape', ch.SystMap()(1.0))

  # -------------------------------------------------------------------
  # Jet energy scale / resolution (temporary total uncertainty, to be replaced by reduced set)
  cb.cp().AddSyst(cb,'AK4PFPuppi_JER','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'AK4PFPuppi_JES_Total','shape',ch.SystMap()(1.0))
  # cb.cp().AddSyst(cb,'AK8PFPuppi_JER','shape',ch.SystMap()(1.0))
  # cb.cp().AddSyst(cb,'AK8PFPuppi_JES_Total','shape',ch.SystMap()(1.0))

  # Pileup (correlated across years)
  cb.cp().AddSyst(cb,'pileup','shape',ch.SystMap()(1.0))

#   # -------------------------------------------------------------------
#   # b-tagging uncertainties
#   # correlated across eras
#   cb.cp().AddSyst(cb,'sf_btag_cferr1','shape',ch.SystMap()(1.0))
#   cb.cp().AddSyst(cb,'sf_btag_cferr2','shape',ch.SystMap()(1.0))
#   cb.cp().AddSyst(cb,'sf_btag_hf','shape',ch.SystMap()(1.0))
#   cb.cp().AddSyst(cb,'sf_btag_lf','shape',ch.SystMap()(1.0))

#   # decorrelated across eras -> add year suffix
#   cb.cp().AddSyst(cb, f'sf_btag_hfstats1_{year}', 'shape', ch.SystMap()(1.0))
#   cb.cp().AddSyst(cb, f'sf_btag_hfstats2_{year}', 'shape', ch.SystMap()(1.0))
#   cb.cp().AddSyst(cb, f'sf_btag_lfstats1_{year}', 'shape', ch.SystMap()(1.0))
#   cb.cp().AddSyst(cb, f'sf_btag_lfstats2_{year}', 'shape', ch.SystMap()(1.0))
  if year != '2024':
                # ----------------------------------------
                # B-Tagging uncertainties (custom names)
                # ----------------------------------------
                # cferr1/2 and hf/lf → usually correlated
                # hfstats*/lfstats* → usually decorrelated
                correlated_systs = [
                  #  "sf_btag_cferr1", "sf_btag_cferr2",
                    "sf_btag_hf", "sf_btag_lf"
                ]
                stats_systs = [
                    "sf_btag_hfstats1", "sf_btag_hfstats2",
                    "sf_btag_lfstats1", "sf_btag_lfstats2"
                ]
                ## Add correlated ones with a suffix to make it explicit
                for s in correlated_systs:
                    cb.cp().AddSyst(cb, f"{s}_Correlated", "shape", ch.SystMap()(1.0))
                ## Add uncorrelated (decorrelated) stats terms
                for s in stats_systs:
                    # if decorrelate_btag:
                        # Add with explicit year/period suffix
                        cb.cp().AddSyst(cb, f"{s}_Uncorrelated_{year}", "shape", ch.SystMap()(1.0))
                    # else:
                    #     # Still call them correlated if not decorrelating
                    #     cb.cp().AddSyst(cb, f"{s}_Correlated", "shape", ch.SystMap()(1.0))
                ### RATEPARAMS (aka SCALE FACTORS) for TT, Z+Jets and W+jets processes
                cb.cp().AddSyst(cb,'weight_vjet','shape',ch.SystMap()(1.0))
  # -------------------------------------------------------------------
  # Jet ID (2% per jet, uncorrelated across years)
  cb.cp().AddSyst(cb, f'JetID_{year}', 'lnN', ch.SystMap()(1.02))

  # Lepton uncertainties (correlated across years)
  cb.cp().AddSyst(cb,'sf_ele_diele_trigger','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_ele_id','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_ele_reco','shape',ch.SystMap()(1.0))
  # cb.cp().AddSyst(cb,'sf_mu_id','shape',ch.SystMap()(1.0))
  # cb.cp().AddSyst(cb,'sf_mu_iso','shape',ch.SystMap()(1.0))
  # MC Statistics — 新增 TODO: Auto MC stats
  #cb.cp().AddSyst(cb, f'MCstat_{base_year}', 'lnN', ch.SystMap()(1.0))

  # Parton shower uncertainties
  cb.cp().AddSyst(cb,'sf_partonshower_fsr','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_partonshower_isr','shape',ch.SystMap()(1.0))



  # Rate parameters (free-floating normalizations)
  cb.cp().channel(['Zee','Zmm']).process(['TT']).AddSyst(cb,
      'SF_TT_2L_Zee_BB'+year, 'rateParam', ch.SystMap('bin_id')
      ([1,2,3,4,5,6,7], 1.0))

  cb.cp().channel(['Zee','Zmm']).process(['VJetbx']).AddSyst(cb,
      'SF_VJet_bx_2L_Zee_BB'+year, 'rateParam', ch.SystMap('bin_id')
      ([1,2,3,4,5,6,7], 1.0))

#   cb.cp().channel(['Zee','Zmm']).process(['VJetcx']).AddSyst(cb,
#       'SF_VJet_cx_2L_Zee_BB'+year, 'rateParam', ch.SystMap('bin_id')
#       ([1,2,3,4,5,6,7], 1.0))

#   cb.cp().channel(['Zee','Zmm']).process(['VJetll']).AddSyst(cb,
#       'SF_VJet_ll_2L_Zee_BB'+year, 'rateParam', ch.SystMap('bin_id')
#       ([1,2,3,4,5,6,7], 1.0))

  for syst in cb.cp().syst_type(["rateParam"]).syst_name_set():
    cb.GetParameter(syst).set_range(0,5)

  # Year-specific Wj_bj normalization
  if year == '2016':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2016', 'lnN', ch.SystMap()(1.50))
  elif year == '2017':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2017', 'lnN', ch.SystMap()(1.50))
  elif year == '2018':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2018', 'lnN', ch.SystMap()(1.50))

  # Lepton efficiency uncertainties (automatically year-dependent)
  if period=='Run2':
    cb.cp().channel(['Wmn']).AddSyst(cb,'CMS_vhbb_eff_m_Wln_13TeV_'+year,'lnN',ch.SystMap()(1.02))
    cb.cp().channel(['Wen']).AddSyst(cb,'CMS_vhbb_eff_e_Wln_13TeV_'+year,'lnN',ch.SystMap()(1.02))
    cb.cp().channel(['Zmm']).AddSyst(cb,'CMS_vhbb_eff_m_Zll_13TeV_'+year,'lnN',ch.SystMap()(1.04))
    cb.cp().channel(['Zee']).AddSyst(cb,'CMS_vhbb_eff_e_Zll_13TeV_'+year,'lnN',ch.SystMap()(1.04))
  elif period=='Run3':
    cb.cp().channel(['Wmn']).AddSyst(cb,'CMS_vhbb_eff_m_Wln_13p6TeV_'+year,'lnN',ch.SystMap()(1.02))
    cb.cp().channel(['Wen']).AddSyst(cb,'CMS_vhbb_eff_e_Wln_13p6TeV_'+year,'lnN',ch.SystMap()(1.02))
    cb.cp().channel(['Zmm']).AddSyst(cb,'CMS_vhbb_eff_m_Zll_13p6TeV_'+year,'lnN',ch.SystMap()(1.04))
    cb.cp().channel(['Zee']).AddSyst(cb,'CMS_vhbb_eff_e_Zll_13p6TeV_'+year,'lnN',ch.SystMap()(1.04))