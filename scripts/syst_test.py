import CombineHarvester.CombineTools.ch as ch

def AddCommonSystematics(cb, year=None):
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
                  (['ZH_hbb','ZH_hcc'], 1.016)
                  (['WH_hbb','WH_hcc'], 1.019))

  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'pdf_Higgs_gg', 'lnN', ch.SystMap()(1.024))
  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'QCDscale_ggZH', 'lnN',ch.SystMap()((1.251,0.811)))

  cb.cp().AddSyst(cb,'QCDscale_VH', 'lnN', ch.SystMap('process')
                  (['ZH_hbb','ZH_hcc'], (1.038,0.969))
                  (['WH_hbb','WH_hcc'], (1.005,0.993)))


  cb.cp().process(['ZH_hcc','WH_hcc','ggZH_hcc']).AddSyst(cb,'BR_hcc', 'lnN', ch.SystMap()((1.05,0.97)))
  cb.cp().process(['ZH_hbb','WH_hbb','ggZH_hbb']).AddSyst(cb,'BR_hbb', 'lnN', ch.SystMap()(1.005))
  # Hbb branching ratio as measured by CMS:
  #cb.cp().process(['ZH_hbb','WH_hbb','ggZH_hbb']).AddSyst(cb,'BR_hbb', 'lnN', ch.SystMap()(1.20))

  #NLO EWK pt(V) correction to the VH and ggZH processes
  cb.cp().AddSyst(cb,
                  'CMS_vhcc_boost_EWK', 'lnN', ch.SystMap('channel','process')
                  (['Zee','Zmm'],['ZH_hcc','ggZH_hcc','ZH_hbb','ggZH_hbb'], 1.02)
                  (['Znn'],['ZH_hcc','WH_hcc','ggZH_hcc','ZH_hbb','WH_hbb','ggZH_hbb'],1.02)
                  (['Wen','Wmn'],['WH_hcc','ZH_hcc','WH_hbb','ZH_hbb'],1.02))

  # Measured cross section uncertainties because we don't have SF:
  #cb.cp().process(['VVother','VZcc']).AddSyst(cb,'CMS_vhcc_VV', 'lnN', ch.SystMap()(1.05))
  cb.cp().process(['s_Top']).AddSyst(cb,'CMS_vhcc_ST', 'lnN', ch.SystMap()(1.15))

  # Uncertainty on di-boson NNLO reweighting
  #cb.cp().process(['VVother','VZcc']).AddSyst(cb, 'CMS_VV_NNLOWeights_13TeV', 'shape', ch.SystMap()(1.0))

  # Theoretical PDF uncertainties
  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'CMS_LHE_pdf_ggZH', 'lnN', ch.SystMap()(1.023))
  cb.cp().process(['ZH_hbb','ZH_hcc']).AddSyst(cb,'CMS_LHE_pdf_ZH', 'lnN', ch.SystMap()(1.018))
  cb.cp().process(['WH_hbb','WH_hcc']).AddSyst(cb,'CMS_LHE_pdf_WH', 'lnN', ch.SystMap()(1.018))
  cb.cp().process(['TT']).AddSyst(cb,'CMS_LHE_pdf_TT', 'lnN', ch.SystMap()(1.0265))
  cb.cp().process(['s_Top']).AddSyst(cb,'CMS_LHE_pdf_ST', 'lnN', ch.SystMap()(1.0288))
  cb.cp().process(['Zj_ll']).AddSyst(cb,'CMS_LHE_pdf_Zj_ll', 'lnN', ch.SystMap()(1.027))
  cb.cp().process(['Zj_bj']).AddSyst(cb,'CMS_LHE_pdf_Zj_bj', 'lnN', ch.SystMap()(1.027))
  cb.cp().process(['Zj_cj']).AddSyst(cb,'CMS_LHE_pdf_Zj_cj', 'lnN', ch.SystMap()(1.027))
  cb.cp().process(['Wj_ll']).AddSyst(cb,'CMS_LHE_pdf_Wj_ll', 'lnN', ch.SystMap()(1.027))
  cb.cp().process(['Wj_bj']).AddSyst(cb,'CMS_LHE_pdf_Wj_bj', 'lnN', ch.SystMap()(1.027))
  cb.cp().process(['Wj_cj']).AddSyst(cb,'CMS_LHE_pdf_Wj_cj', 'lnN', ch.SystMap()(1.027))
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

  # 'JER_AK4PFPuppiDown', 'JER_AK4PFPuppiUp', 'JES_Total_AK4PFPuppiDown', 'JES_Total_AK4PFPuppiUp', 'nominal', 'pileupDown', 'pileupUp', 'sf_ele_idDown', 'sf_ele_idUp', 'sf_ele_recoDown', 'sf_ele_recoUp', 'sf_mu_idDown', 'sf_mu_idUp', 'sf_mu_isoDown', 'sf_mu_isoUp'
  cb.cp().AddSyst(cb,'AK4PFPuppi_JER','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'AK4PFPuppi_JES_Total','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'pileup','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_ele_id','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_ele_reco','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_mu_id','shape',ch.SystMap()(1.0))
  cb.cp().AddSyst(cb,'sf_mu_iso','shape',ch.SystMap()(1.0))

  ### RATEPARAMS (aka SCALE FACTORS) for TT, Z+Jets and W+jets processes

  # TT proc in 2L channel
  cb.cp().channel(['Zee','Zmm']).process(['TT']).AddSyst(cb,
                                                         'SF_TT_2L_loZPT_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([1,3,5,7,9],  1.0))
  cb.cp().channel(['Zee','Zmm']).process(['TT']).AddSyst(cb,
                                                         'SF_TT_2L_hiZPT_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([2,4,6,8,10],  1.0))
  cb.cp().channel(['Zee','Zmm']).process(['TT']).AddSyst(cb,
                                                         'SF_TT_2L_Hbb_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([11,12,13],  1.0))
  # Zj_ll in 2L
  cb.cp().channel(['Zee','Zmm']).process(['Zj_ll']).AddSyst(cb,
                                                            'SF_Zj_ll_2L_loZPT_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([1,3,5,7,9],  1.0))
  cb.cp().channel(['Zee','Zmm']).process(['Zj_ll']).AddSyst(cb,
                                                            'SF_Zj_ll_2L_hiZPT_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([2,4,6,8,10],  1.0))
    cb.cp().channel(['Zee','Zmm']).process(['Zj_ll']).AddSyst(cb,
                                                            'SF_Zj_ll_2L_Hbb_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([11,12,13],  1.0))
  # Zj_bj in 2L
  cb.cp().channel(['Zee','Zmm']).process(['Zj_bj']).AddSyst(cb,
                                                            'SF_Zj_bj_2L_loZPT_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([1,3,5,7,9],1.0))
  cb.cp().channel(['Zee','Zmm']).process(['Zj_bj']).AddSyst(cb,
                                                            'SF_Zj_bj_2L_hiZPT_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([2,4,6,8,10],1.0))
  cb.cp().channel(['Zee','Zmm']).process(['Zj_bj']).AddSyst(cb,
                                                            'SF_Zj_bj_2L_Hbb_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([11,12,13],  1.0))
  # Zj_cj in 2L
  cb.cp().channel(['Zee','Zmm']).process(['Zj_cj']).AddSyst(cb,
                                                            'SF_Zj_cj_2L_loZPT_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([1,3,5,7,9],1.0))
  cb.cp().channel(['Zee','Zmm']).process(['Zj_cj']).AddSyst(cb,
                                                            'SF_Zj_cj_2L_hiZPT_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([2,4,6,8,10],1.0))
  cb.cp().channel(['Zee','Zmm']).process(['Zj_cj']).AddSyst(cb,
                                                            'SF_Zj_cj_2L_Hbb_'+year, 'rateParam', ch.SystMap('bin_id')
                                                            ([11,12,13],  1.0))

  # TT in 1L channel
  cb.cp().channel(['Wen','Wmn']).process(['TT']).AddSyst(cb,
                                                         'SF_TT_1L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([1,2,3,4,5,6,7,8],  1.0))
  # Wj_ll in 1L AND 0L
  cb.cp().channel(['Wen','Wmn','Znn']).process(['Wj_ll']).AddSyst(cb,
                                                         'SF_Wj_ll_1L0L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([1,2,3,4,5,6,7,8],  1.0))
  # Wj_bj in 1L AND 0L
  cb.cp().channel(['Wen','Wmn','Znn']).process(['Wj_bj']).AddSyst(cb,
                                                         'SF_Wj_bj_1L0L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([1,2,3,4,5,6,7,8],  1.0))
  # Wj_cj in 1L AND 0L
  cb.cp().channel(['Wen','Wmn','Znn']).process(['Wj_cj']).AddSyst(cb,
                                                         'SF_Wj_cj_1L0L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                         ([1,2,3,4,5,6,7,8],  1.0))
  
  
  # TT in 0L channel
  cb.cp().channel(['Znn']).process(['TT']).AddSyst(cb,
                                                   'SF_TT_0L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                    ([1,2,3,4,5,6,7,8],  1.0))
  # Zj_ll in 0L
  cb.cp().channel(['Znn']).process(['Zj_ll']).AddSyst(cb,
                                                    'SF_Zj_ll_0L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                    ([1,2,3,4,5,6,7,8],  1.0))
  # Zj_bj in 0L
  cb.cp().channel(['Znn']).process(['Zj_bj']).AddSyst(cb,
                                                    'SF_Zj_bj_0L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                    ([1,2,3,4,5,6,7,8],  1.0))
  # Zj_cj in 0L
  cb.cp().channel(['Znn']).process(['Zj_cj']).AddSyst(cb,
                                                    'SF_Zj_cj_0L_'+year, 'rateParam', ch.SystMap('bin_id')
                                                    ([1,2,3,4,5,6,7,8],  1.0))
  
  for syst in cb.cp().syst_type(["rateParam"]).syst_name_set():
    cb.GetParameter(syst).set_range(0.0,5.0)

  # Uncertainties specific to data-taking period:
  if year == '2016':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2016', 'lnN', ch.SystMap()(1.50))
  elif year == '2017':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2017', 'lnN', ch.SystMap()(1.50))
  elif year == '2018':
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_2018', 'lnN', ch.SystMap()(1.50))

  elif year in ['2022_preEE','2022_postEE','2023_preBPix','2023_postBPix']:
    cb.cp().process(['Wj_bj']).AddSyst(cb,'Norm_Wj_bj_'+year, 'lnN', ch.SystMap()(1.50))


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
    cb.cp().channel(['Zee']).AddSyst(cb,'CMS_vhcc_eff_e_Zll_13p6TeV_'+year,'lnN',ch.SystMap()(1.04))
