import CombineHarvester.CombineTools.ch as ch

def AddCommonSystematics(cb):
  
  signal = cb.cp().signals().process_set()
  # rateParams

  # Theory uncertainties: signal
  cb.cp().AddSyst(cb,
                  'pdf_Higgs_qqbar', 'lnN', ch.SystMap('process')
                  (['ZH_hbb','ZH_hcc'],1.016)
                  (['WH_hbb','WH_hcc'],1.019))
  
  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'pdf_Higgs_gg', 'lnN', ch.SystMap()(1.024))
  
  cb.cp().process(['ggZH_hbb','ggZH_hcc']).AddSyst(cb,'QCDscale_ggZH', 'lnN',ch.SystMap()((1.251,0.811)))
  
  cb.cp().AddSyst(cb,'QCDscale_VH', 'lnN', ch.SystMap('process') 
                  (['ZH_hbb','ZH_hcc'], (1.038,0.969)) 
                  (['WH_hbb','WH_hcc'], (1.005,0.993)))


  cb.cp().AddSyst(cb,'lumi_13TeV','lnN', ch.SystMap()(1.010))
