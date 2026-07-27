import ROOT
from HiggsAnalysis.CombinedLimit.PhysicsModel import *
from HiggsAnalysis.CombinedLimit.SMHiggsBuilder import SMHiggsBuilder

## Naming conventions
CMS_to_LHCHCG_Dec = {
    "hww": "WW",
    "hzz": "ZZ",
    "hgg": "gamgam",
    "hbb": "bb",
    "hcc": "cc",
    "htt": "tautau",
    "hmm": "mumu",
    "hzg": "Zgam",
    "hgluglu": "gluglu",
    "hinv": "inv",
}
CMS_to_LHCHCG_DecSimple = {
    "hww": "WW",
    "hzz": "ZZ",
    "hgg": "gamgam",
    "hbb": "bb",
    "hcc": "bb",
    "htt": "tautau",
    "hmm": "mumu",
    "hzg": "gamgam",
    "hgluglu": "bb",
    "hinv": "inv",
}
CMS_to_LHCHCG_Prod = {
    "ggH": "ggF",
    "qqH": "VBF",
    "WH": "WH",
    "WPlusH": "WH",
    "WMinusH": "WH",
    "ZH": "qqZH",
    "ggZH": "ggZH",
    "ttH": "ttH",
    "tHq": "tHjb",
    "tHW": "WtH",
    "bbH": "bbH",
}

class lambda_cb(LHCHCGBaseModel):
    "assume the SM coupling but leave the Higgs mass to float -> specialties compared to Kappas: no kappa_c but ratio lambda_cb as POI resolved=True is not implemented yet"

    def __init__(
        self,
        resolved=False,
        BRU=False,
        addInvisible=False,
        addUndet=False,
        addWidth=False,
        addLambdaCB=True,
        custodial=False,
    ):
        LHCHCGBaseModel.__init__(self)  # not using 'super(x,self).__init__' since I don't understand it
        self.doBRU = BRU
        self.resolved = resolved
        self.addInvisible = addInvisible
        self.addUndet = addUndet
        self.addLambdaCB = addLambdaCB
        self.addWidth = addWidth
        self.custodial = custodial

    def setPhysicsOptions(self, physOptions):
        self.setPhysicsOptionsBase(physOptions)
        for po in physOptions:
            if po.startswith("BRU="):
                self.doBRU = po.replace("BRU=", "") in [
                    "yes",
                    "1",
                    "Yes",
                    "True",
                    "true",
                ]
        print("BR uncertainties in partial widths: %s " % self.doBRU)

    def doParametersOfInterest(self):
        """Create POI out of signal strength and MH"""
        if not self.custodial:
            self.modelBuilder.doVar("kappa_W[1,0.0,2.0]")
            self.modelBuilder.doVar("kappa_Z[1,-2.0,2.0]")
            self.kappa_W = "kappa_W"
            self.kappa_Z = "kappa_Z"
        else:
            self.modelBuilder.doVar("kappa_V[1,0.0,2.0]")
            self.kappa_W = "kappa_V"
            self.kappa_Z = "kappa_V"
        kappa_b = "kappa_b"
        if self.addWidth:
            kappa_b = "c7_Gscal_tot"
            self.modelBuilder.doVar("c7_Gscal_tot[1,0.5,2.0]")
        else:
            self.modelBuilder.doVar("kappa_b[1,-10.0,10.0]")
        self.modelBuilder.doVar("kappa_tau[1,0.0,3.0]")
        self.modelBuilder.doVar("kappa_mu[1,0.0,5.0]")
        # self.modelBuilder.factory_("expr::kappa_mu_expr(\"@0*@1+(1-@0)*@2\", CMS_use_kmu[0], kappa_mu, kappa_tau)")
        self.modelBuilder.doVar("kappa_t[1,0.0,4.0]")
        if not self.resolved:
            self.modelBuilder.doVar("kappa_g[1,0.0,2.0]")
            self.modelBuilder.doVar("kappa_gam[1,0.0,2.5]")
        self.modelBuilder.doVar("BRinv[0,0,1]")
        self.modelBuilder.doVar("BRundet[0,0,1]")
        if not self.addInvisible:
            self.modelBuilder.out.var("BRinv").setConstant(True)
        if not self.addUndet:
            self.modelBuilder.out.var("BRundet").setConstant(True)
        pois = self.kappa_W + "," + self.kappa_Z + ",kappa_tau,kappa_t," + kappa_b
        if not self.resolved:
            pois += ",kappa_g,kappa_gam"
        if self.addInvisible:
            pois += ",BRinv"
        if self.addUndet:
            pois += ",BRundet"
        if self.addLambdaCB:
            self.modelBuilder.doVar("lambda_cb[1,-15.0,15.0]")
            pois += ",lambda_cb"
        if self.promote_hzg and not self.resolved:
            self.modelBuilder.doVar("kappa_Zgam[1.0,0.0,5.0]")
            pois += ",kappa_Zgam"
        self.doMH()
        self.modelBuilder.doSet("POI", pois)
        self.SMH = SMHiggsBuilder(self.modelBuilder)
        self.setup()

    def setup(self):
        self.dobbH()
        # SM BR
        for d in SM_HIGG_DECAYS + ["hss"]:
            self.SMH.makeBR(d)
        # BR uncertainties
        if self.doBRU:
            self.SMH.makePartialWidthUncertainties()
        else:
            for d in SM_HIGG_DECAYS:
                self.modelBuilder.factory_("HiggsDecayWidth_UncertaintyScaling_%s[1.0]" % d)
        # get VBF, tHq, tHW, ggZH cross section
        self.SMH.makeScaling("qqH", CW=self.kappa_W, CZ=self.kappa_Z)
        self.SMH.makeScaling("tHq", CW=self.kappa_W, Ctop="kappa_t")
        self.SMH.makeScaling("tHW", CW=self.kappa_W, Ctop="kappa_t")
        # resolve loops
        if self.resolved:
            if self.addKappaC:
                self.SMH.makeScaling("ggH", Cb="kappa_b", Ctop="kappa_t", Cc="kappa_c")
            else:
                self.SMH.makeScaling("ggH", Cb="kappa_b", Ctop="kappa_t", Cc="kappa_t")
            self.SMH.makeScaling("hgluglu", Cb="kappa_b", Ctop="kappa_t")
            self.SMH.makeScaling("hgg", Cb="kappa_b", Ctop="kappa_t", CW=self.kappa_W, Ctau="kappa_tau")
            self.SMH.makeScaling("hzg", Cb="kappa_b", Ctop="kappa_t", CW=self.kappa_W, Ctau="kappa_tau")
        else:
            self.modelBuilder.factory_('expr::Scaling_hgluglu("@0*@0", kappa_g)')
            self.modelBuilder.factory_('expr::Scaling_hgg("@0*@0", kappa_gam)')
            if self.promote_hzg:
                self.modelBuilder.factory_('expr::Scaling_hzg("@0*@0", kappa_Zgam)')
            else:
                self.modelBuilder.factory_('expr::Scaling_hzg("@0*@0", kappa_gam)')
            self.modelBuilder.factory_('expr::Scaling_ggH_7TeV("@0*@0", kappa_g)')
            self.modelBuilder.factory_('expr::Scaling_ggH_8TeV("@0*@0", kappa_g)')
            self.modelBuilder.factory_('expr::Scaling_ggH_13TeV("@0*@0", kappa_g)')
            self.modelBuilder.factory_('expr::Scaling_ggH_14TeV("@0*@0", kappa_g)')

        ## partial witdhs, normalized to the SM one
        kappa_mu_expr = "kappa_mu" if self.promote_hmm else "kappa_tau"
        self.modelBuilder.factory_('expr::c7_Gscal_Z("@0*@0*@1*@2", ' + self.kappa_Z + ", SM_BR_hzz, HiggsDecayWidth_UncertaintyScaling_hzz)")
        self.modelBuilder.factory_('expr::c7_Gscal_W("@0*@0*@1*@2", ' + self.kappa_W + ", SM_BR_hww, HiggsDecayWidth_UncertaintyScaling_hww)")
        if self.addLambdaCB:
            self.modelBuilder.factory_('expr::c7_Gscal_top("@0*@1*@0*@1 * @2*@3", kappa_b, lambda_cb, SM_BR_hcc, HiggsDecayWidth_UncertaintyScaling_hcc)')
        else:
            self.modelBuilder.factory_('expr::c7_Gscal_top("@0*@0 * @1*@2", kappa_t, SM_BR_hcc, HiggsDecayWidth_UncertaintyScaling_hcc)')
        self.modelBuilder.factory_('expr::c7_Gscal_gluon("  @0  * @1 * @2", Scaling_hgluglu, SM_BR_hgluglu, HiggsDecayWidth_UncertaintyScaling_hgluglu)')
        self.modelBuilder.factory_(
            'expr::c7_Gscal_gamma("@0*@1*@4 + @2*@3*@5",  Scaling_hgg, SM_BR_hgg, Scaling_hzg, SM_BR_hzg, HiggsDecayWidth_UncertaintyScaling_hgg, HiggsDecayWidth_UncertaintyScaling_hzg)'
        )
        self.modelBuilder.factory_(
            'expr::c7_Gscal_tau("@0*@0*@1*@4+@2*@2*@3*@5", kappa_tau, SM_BR_htt, %s, SM_BR_hmm, HiggsDecayWidth_UncertaintyScaling_htt, HiggsDecayWidth_UncertaintyScaling_hmm)'
            % kappa_mu_expr
        )
        # fix to have all BRs add up to unity
        self.modelBuilder.factory_("sum::c7_SMBRs(%s)" % (",".join("SM_BR_" + X for X in "hzz hww htt hmm hcc hbb hss hgluglu hgg hzg".split())))
        self.modelBuilder.out.function("c7_SMBRs").Print("")

        if self.addWidth:
            self.modelBuilder.factory_(
                'expr::c7_Gscal_bottom("@1*@8*(1-@0-@9)-(@2+@3+@4+@5+@6+@7)", BRinv, c7_Gscal_tot, c7_Gscal_W, c7_Gscal_Z, c7_Gscal_top, c7_Gscal_tau, c7_Gscal_gluon, c7_Gscal_gamma, c7_SMBRs, BRundet)'
            )
            self.modelBuilder.factory_('expr::kappa_b("sqrt(@0/(@1*@3+@2))", c7_Gscal_bottom, SM_BR_hbb, SM_BR_hss, HiggsDecayWidth_UncertaintyScaling_hbb)')

        else:
            self.modelBuilder.factory_('expr::c7_Gscal_bottom("@0*@0 * (@1*@3+@2)", kappa_b, SM_BR_hbb, SM_BR_hss, HiggsDecayWidth_UncertaintyScaling_hbb)')

        ## total witdh, normalized to the SM one
        if not self.addWidth:
            self.modelBuilder.factory_(
                'expr::c7_Gscal_tot("(@1+@2+@3+@4+@5+@6+@7)/@8/(1-@0-@9)", BRinv, c7_Gscal_Z, c7_Gscal_W, c7_Gscal_tau, c7_Gscal_top, c7_Gscal_bottom, c7_Gscal_gluon, c7_Gscal_gamma, c7_SMBRs, BRundet)'
            )

        self.SMH.makeScaling("ggZH", CZ=self.kappa_Z, Ctop="kappa_t", Cb="kappa_b")

        ## BRs, normalized to the SM ones: they scale as (partial/partial_SM) / (total/total_SM)
        self.modelBuilder.factory_('expr::c7_BRscal_hww("@0*@0*@2/@1", ' + self.kappa_W + ", c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hww)")
        self.modelBuilder.factory_('expr::c7_BRscal_hzz("@0*@0*@2/@1", ' + self.kappa_Z + ", c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hzz)")
        self.modelBuilder.factory_('expr::c7_BRscal_htt("@0*@0*@2/@1", kappa_tau, c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_htt)')
        self.modelBuilder.factory_('expr::c7_BRscal_hmm("@0*@0*@2/@1", %s, c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hmm)' % kappa_mu_expr)
        self.modelBuilder.factory_('expr::c7_BRscal_hbb("@0*@0*@2/@1", kappa_b, c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hbb)')
        if self.addLambdaCB:
            self.modelBuilder.factory_('expr::c7_BRscal_hcc("@0*@1*@0*@1*@3/@2", kappa_b, lambda_cb, c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hcc)')
        else:
            self.modelBuilder.factory_('expr::c7_BRscal_hcc("@0*@0*@2/@1", kappa_t, c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hcc)')
        self.modelBuilder.factory_('expr::c7_BRscal_hgg("@0*@2/@1", Scaling_hgg, c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hgg)')
        self.modelBuilder.factory_('expr::c7_BRscal_hzg("@0*@2/@1", Scaling_hzg, c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hzg)')
        self.modelBuilder.factory_('expr::c7_BRscal_hgluglu("@0*@2/@1", Scaling_hgluglu, c7_Gscal_tot, HiggsDecayWidth_UncertaintyScaling_hgluglu)')

        self.modelBuilder.factory_('expr::c7_BRscal_hinv("@0", BRinv)')

    def getHiggsSignalYieldScale(self, production, decay, energy):
        name = f"c7_XSBRscal_{production}_{decay}_{energy}"
        if not self.modelBuilder.out.function(name):
            if production in ["ggH", "qqH", "ggZH", "tHq", "tHW"]:
                XSscal = ("x[0]", f"Scaling_{production}_{energy}")
            elif production == "WH":
                XSscal = ("x[0]*x[0]", self.kappa_W)
            elif production == "ZH":
                XSscal = ("x[0]*x[0]", self.kappa_Z)
            elif production == "ttH":
                XSscal = ("x[0]*x[0]", "kappa_t")
            elif production == "bbH":
                XSscal = ("x[0]*x[0]", "kappa_b")
            else:
                raise RuntimeError("Production %s not supported" % production)
            BRscal = decay
            if not self.modelBuilder.out.function("c7_BRscal_" + BRscal):
                raise RuntimeError("Decay mode %s not supported" % decay)
            if decay == "hss":
                BRscal = "hbb"
            if production == "ggH" and (decay in self.add_bbH) and energy in ["7TeV", "8TeV", "13TeV", "14TeV"]:
                b2g = f"CMS_R_bbH_ggH_{decay}_{energy}[{0.01:g}]"
                b2gs = "CMS_bbH_scaler_%s" % energy
                self.modelBuilder.factory_(f'expr::{name}("({XSscal[0]} + x[1]*x[1]*x[2]*x[3])*x[4]", {XSscal[1]}, kappa_b, {b2g}, {b2gs}, c7_BRscal_{BRscal})')
            else:
                self.modelBuilder.factory_(f'expr::{name}("{XSscal[0]}*x[1]", {XSscal[1]}, c7_BRscal_{BRscal})')
            print("[LHC-HCG Lambda_cb]", name, production, decay, energy, ": ", end=" ")
            self.modelBuilder.out.function(name).Print("")
        return name

RCB = lambda_cb(resolved=False, BRU=False, addInvisible=False, addUndet=False, addWidth=False, addLambdaCB=True)