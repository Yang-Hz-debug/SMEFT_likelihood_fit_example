import CombineHarvester.CombineTools.ch as ch
def AddCommonSystematics(cb, year=None, decorrelate_btag=False):
#def AddCommonSystematics(cb, year=None):
  period = None
  if year in ["2016","2017","2018"]:
    period = 'Run2'
  else:
    period = 'Run3'

  signal = cb.cp().signals().process_set()

  if period=='Run3':
    cb.cp().AddSyst(cb,'lumi_13p6TeV','lnN', ch.SystMap()(1.010))
  elif period=='Run2':
    cb.cp().AddSyst(cb,'lumi_13TeV','lnN', ch.SystMap()(1.010))

  # Theory uncertainties: signal
  cb.cp().AddSyst(cb,
                  'pdf_Higgs_qqbar', 'lnN', ch.SystMap('process')
                  (['ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf'], 1.016)
                  (['WH_hbb','WH_hcc'], 1.019))

  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'pdf_Higgs_gg', 'lnN', ch.SystMap()(1.024))
  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'QCDscale_ggZH', 'lnN',ch.SystMap()((1.251,0.811)))

  # cb.cp().AddSyst(cb,'QCDscale_VH', 'lnN', ch.SystMap('process')
  #                 (['ZH_bb','ZH_hcc'], (1.038,0.969))
  #                 (['WH_hbb','WH_hcc'], (1.005,0.993)))
  # cb.cp().AddSyst(cb,'QCDscale_VH', 'lnN', ch.SystMap('process')
  #                 (['ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf'], (1.038,0.969))
  #                 (['WH_hbb','WH_hcc'], (1.005,0.993)))

#  cb.cp().process(['ZH_hcc','WH_hcc','ggZH_hcc']).AddSyst(cb,'BR_hcc', 'lnN', ch.SystMap()((1.05,0.97)))
  cb.cp().process(['ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf','WH_hbb','ggZH_hbb']).AddSyst(cb,'BR_hbb', 'lnN', ch.SystMap()(1.005))
  # Hbb branching ratio as measured by CMS:
  #cb.cp().process(['ZH_hbb','WH_hbb','ggZH_hbb']).AddSyst(cb,'BR_hbb', 'lnN', ch.SystMap()(1.20))

  #NLO EWK pt(V) correction to the VH and ggZH processes
  cb.cp().AddSyst(cb,
                  'CMS_vhbb_boost_EWK', 'lnN', ch.SystMap('channel','process')
                  (['Zee','Zmm'],['ZH_hbb_pTH_0_60','ZH_hbb_pTH_60_120','ZH_hbb_pTH_120_200','ZH_hbb_pTH_200_300','ZH_hbb_pTH_300_450','ZH_hbb_pTH_450_inf'], 1.02)#
                  (['Znn'],['ZH_hcc','WH_hcc','ggZH_hcc','ZH_bb','WH_hbb','ggZH_hbb'],1.02)
                  (['Wen','Wmn'],['WH_hcc','ZH_hcc','WH_hbb','ZH_bb'],1.02))

  # Measured cross section uncertainties because we don't have SF: !!!!!!!!!!!!!but we have rate Param for TT and  VZ bb
  cb.cp().process(['ST']).AddSyst(cb,'CMS_vhqq_ST', 'lnN', ch.SystMap()(1.15))
  # cb.cp().process(['WW', 'VZbb', 'VZcc', 'VZlx']).AddSyst(cb,'CMS_vhqq_WW', 'lnN', ch.SystMap()(1.05))##########
  cb.cp().process(['WW', 'VZcc', 'VZlx']).AddSyst(cb,'CMS_vhqq_WW', 'lnN', ch.SystMap()(1.05))

  # Uncertainty on di-boson NNLO reweighting ??
  #cb.cp().process(['VVother','VZcc']).AddSyst(cb, 'CMS_VV_NNLOWeights_13TeV', 'shape', ch.SystMap()(1.0))

  # Theoretical PDF uncertainties
  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'CMS_LHE_pdf_ggZH', 'lnN', ch.SystMap()(1.023))
  cb.cp().process(['ZH_bb','ZH_hcc']).AddSyst(cb,'CMS_LHE_pdf_ZH', 'lnN', ch.SystMap()(1.018))
  cb.cp().process(['WH_hbb','WH_hcc']).AddSyst(cb,'CMS_LHE_pdf_WH', 'lnN', ch.SystMap()(1.018))
  cb.cp().process(['TT']).AddSyst(cb,'CMS_LHE_pdf_TT', 'lnN', ch.SystMap()(1.0265))
  cb.cp().process(['ST']).AddSyst(cb,'CMS_LHE_pdf_ST', 'lnN', ch.SystMap()(1.0288))
  cb.cp().process(['VJetbx','VJetcx','VJetll']).AddSyst(cb,'CMS_LHE_pdf_VJet', 'lnN', ch.SystMap()(1.027))
  # cb.cp().process(['Zj_ll']).AddSyst(cb,'CMS_LHE_pdf_Zj_ll', 'lnN', ch.SystMap()(1.027))
  # cb.cp().process(['Zj_bj']).AddSyst(cb,'CMS_LHE_pdf_Zj_bj', 'lnN', ch.SystMap()(1.027))
  # cb.cp().process(['Zj_cj']).AddSyst(cb,'CMS_LHE_pdf_Zj_cj', 'lnN', ch.SystMap()(1.027))
  cb.cp().process(['VJet']).AddSyst(cb,'CMS_LHE_pdf_VJet', 'lnN', ch.SystMap()(1.027))
  # cb.cp().process(['Wj_ll']).AddSyst(cb,'CMS_LHE_pdf_Wj_ll', 'lnN', ch.SystMap()(1.027))
  # cb.cp().process(['Wj_bj']).AddSyst(cb,'CMS_LHE_pdf_Wj_bj', 'lnN', ch.SystMap()(1.027))
  # cb.cp().process(['Wj_cj']).AddSyst(cb,'CMS_LHE_pdf_Wj_cj', 'lnN', ch.SystMap()(1.027))
  #cb.cp().process(['VZcc']).AddSyst(cb,'CMS_LHE_pdf_VZcc', 'lnN', ch.SystMap()(1.015))
  #cb.cp().process(['VVother']).AddSyst(cb,'CMS_LHE_pdf_VVother', 'lnN', ch.SystMap()(1.0135))


  # Theoretical Renormalization and Factorization scale uncertainties
  ### Shapes are not implemented yet. Need input from coffea
  ### cb.cp().process(['ZH_hbb','ZH_hcc']).AddSyst(cb,'CMS_LHE_weights_scale_muR_ZH','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['WH_hbb','WH_hcc']).AddSyst(cb,'CMS_LHE_weights_scale_muR_WH','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'CMS_LHE_weights_scale_muR_ggZH','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['ZH_hbb','ZH_hcc']).AddSyst(cb,'CMS_LHE_weights_scale_muF_ZH','shape',ch.SystMap()(1.0))
  ### b.cp().process(['WH_hbb','WH_hcc']).AddSyst(cb,'CMS_LHE_weights_scale_muF_WH','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'CMS_LHE_weights_scale_muF_ggZH','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Zj_ll']).AddSyst(cb,'CMS_LHE_weights_scale_muR_Zj_ll','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Zj_ll']).AddSyst(cb,'CMS_LHE_weights_scale_muF_Zj_ll','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Zj_bj']).AddSyst(cb,'CMS_LHE_weights_scale_muR_Zj_bj','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Zj_bj']).AddSyst(cb,'CMS_LHE_weights_scale_muF_Zj_bj','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Zj_cj']).AddSyst(cb,'CMS_LHE_weights_scale_muR_Zj_cj','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Zj_cj']).AddSyst(cb,'CMS_LHE_weights_scale_muF_Zj_cj','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Wj_ll']).AddSyst(cb,'CMS_LHE_weights_scale_muR_Wj_ll','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Wj_ll']).AddSyst(cb,'CMS_LHE_weights_scale_muF_Wj_ll','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Wj_bj']).AddSyst(cb,'CMS_LHE_weights_scale_muR_Wj_bj','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Wj_bj']).AddSyst(cb,'CMS_LHE_weights_scale_muF_Wj_bj','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Wj_cj']).AddSyst(cb,'CMS_LHE_weights_scale_muR_Wj_cj','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['Wj_cj']).AddSyst(cb,'CMS_LHE_weights_scale_muF_Wj_cj','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['TT']).AddSyst(cb,'CMS_LHE_weights_scale_muR_TT','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['TT']).AddSyst(cb,'CMS_LHE_weights_scale_muF_TT','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['s_Top']).AddSyst(cb,'CMS_LHE_weights_scale_muR_ST','shape',ch.SystMap()(1.0))
  ### cb.cp().process(['s_Top']).AddSyst(cb,'CMS_LHE_weights_scale_muF_ST','shape',ch.SystMap()(1.0))
  ### #cb.cp().process(['VVother']).AddSyst(cb,'CMS_LHE_weights_scale_muR_VVother','shape',ch.SystMap()(1.0))
  ### #cb.cp().process(['VZcc']).AddSyst(cb,'CMS_LHE_weights_scale_muR_VZcc','shape',ch.SystMap()(1.0))
  ### #cb.cp().process(['VVother']).AddSyst(cb,'CMS_LHE_weights_scale_muF_VVother','shape',ch.SystMap()(1.0))
  ### #cb.cp().process(['VZcc']).AddSyst(cb,'CMS_LHE_weights_scale_muF_VZcc','shape',ch.SystMap()(1.0))
    
  #cb.cp().process(['VJetbx','VJetcx','VJetll']).AddSyst(cb,'nlo_reweight_vjet','shape',ch.SystMap()(1.0))

  cb.cp().AddSyst(cb,'AK4PFPuppi_JER','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'AK4PFPuppi_JES_Total','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'pileup','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_ele_id','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_ele_reco','shape',ch.SystMap()(1.0))
  # cb.cp().AddSyst(cb,'sf_mu_id','shape',ch.SystMap()(1.0))
  # cb.cp().AddSyst(cb,'sf_mu_iso','shape',ch.SystMap()(1.0))
  # cb.cp().AddSyst(cb, 'sf_mu_dimu_trigger', 'shape', ch.SystMap()(1.0))
  
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

  # TT proc in 2L channel
  cb.cp().channel(['Zee','Zmm']).process(['TT']).AddSyst(cb,
                                                         'SF_TT_2L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([1,2,3,4,5,6,7,8],  1.0))
  
  # VJet in 2L
  cb.cp().channel(['Zee','Zmm']).process(['VJetbx']).AddSyst(cb,
                                                            'SF_VJet_bx_2L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([1,2,3,4,5,6,7,8],  1.0))
  #cb.cp().channel(['Zee','Zmm']).process(['VJetcx']).AddSyst(cb,
  #                                                          'SF_VJet_cx_2L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
  # cb.cp().channel(['Zee','Zmm']).process(['VJetll']).AddSyst(cb,
  #                                                           'SF_VJet_ll_2L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                        ([1,2,3,4,5,6,7,8],  1.0))
#
#
  ## TT in 1L channel
  #cb.cp().channel(['Wen','Wmn']).process(['TT']).AddSyst(cb,
  #                                                       'SF_TT_1L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
#
  ## VJet in 2L
  #cb.cp().channel(['Wen','Wmn']).process(['VJetbx']).AddSyst(cb,
  #                                                          'SF_VJet_bx_1L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
  #cb.cp().channel(['Wen','Wmn']).process(['VJetcx']).AddSyst(cb,
  #                                                          'SF_VJet_cx_1L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
  #cb.cp().channel(['Wen','Wmn']).process(['VJetll']).AddSyst(cb,
  #                                                          'SF_VJet_ll_1L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
  #
# #  # TT in 0L channel
  #cb.cp().channel(['Znn']).process(['TT']).AddSyst(cb,
  #                                                 'SF_TT_0L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
# #  # Zj_ll in 0L
  #cb.cp().channel(['Znn']).process(['VJetbx']).AddSyst(cb,
  #                                                          'SF_VJet_bx_0L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
  #cb.cp().channel(['Znn']).process(['VJetcx']).AddSyst(cb,
  #                                                          'SF_VJet_cx_0L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
  #cb.cp().channel(['Znn']).process(['VJetll']).AddSyst(cb,
  #                                                          'SF_VJet_ll_0L_'+year, 'rateParam', ch.SystMap('bin_id')
  #                                                       ([1,2,3,4,5,6,7,8],  1.0))
  
  for syst in cb.cp().syst_type(["rateParam"]).syst_name_set():
    cb.GetParameter(syst).set_range(0.0,5.0)

  # Uncertainties specific to data-taking period:
  if year == '2016':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2016', 'lnN', ch.SystMap()(1.50))
  elif year == '2017':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2017', 'lnN', ch.SystMap()(1.50))
  elif year == '2018':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2018', 'lnN', ch.SystMap()(1.50))

  # what does this for???
  # elif year in ['2022_preEE','2022_postEE','2023_preBPix','2023_postBPix','2024']:
  #   cb.cp().process(['VJetbx']).AddSyst(cb,'Norm_Vj_bj_'+year, 'lnN', ch.SystMap()(1.50))


  #========= Lepton efficiencies
  if period=='Run2':
    cb.cp().channel(['Wmn']).AddSyst(cb,'CMS_vhcc_eff_m_Wln_13TeV_'+year,'lnN',ch.SystMap()(1.02))
    cb.cp().channel(['Wen']).AddSyst(cb,'CMS_vhcc_eff_e_Wln_13TeV_'+year,'lnN',ch.SystMap()(1.02))
    cb.cp().channel(['Zmm']).AddSyst(cb,'CMS_vhcc_eff_m_Zll_13TeV_'+year,'lnN',ch.SystMap()(1.04))
    cb.cp().channel(['Zee']).AddSyst(cb,'CMS_vhcc_eff_e_Zll_13TeV_'+year,'lnN',ch.SystMap()(1.04))

  elif period=='Run3':
    cb.cp().channel(['Wmn']).AddSyst(cb,'CMS_vhcc_eff_m_Wln_13p6TeV_'+year,'lnN',ch.SystMap()(1.02))
    cb.cp().channel(['Wen']).AddSyst(cb,'CMS_vhcc_eff_e_Wln_13p6TeV_'+year,'lnN',ch.SystMap()(1.02))
    cb.cp().channel(['Zmm']).AddSyst(cb,'CMS_vhcc_eff_m_Zll_13p6TeV_'+year,'lnN',ch.SystMap()(1.04))
    cb.cp().channel(['Zee']).AddSyst(cb,'CMS_vhbb_eff_e_Zll_13p6TeV_'+year,'lnN',ch.SystMap()(1.04))
