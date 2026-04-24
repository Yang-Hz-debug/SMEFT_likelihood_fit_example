from HiggsAnalysis.CombinedLimit.PhysicsModel import PhysicsModel


class DiffXsecModel(PhysicsModel):
    """
    Differential cross section model for merged VH signal.

    Assumptions:
      - Signal processes are already merged in the datacards:
          ZH_hbb_pTH_0_60, ZH_hbb_pTH_60_120, ...
      - One POI r_pTH_* per pT(H) bin
      - Backgrounds are not scaled
    """

    def __init__(self):
        super(DiffXsecModel, self).__init__()

    def doParametersOfInterest(self):
        """
        Define one POI per pT(H) bin.
        """

        pt_bins = [
            "pTH_0_60",
            "pTH_60_120",
            "pTH_120_200",
            "pTH_200_300",
            "pTH_300_450",
            "pTH_450_inf",
        ]

        pois = []

        for b in pt_bins:
            poi = f"r_{b}"

            # Physical range: non-negative, loose upper bound
            self.modelBuilder.doVar(f"{poi}[1.0,-20.0,20.0]")
            pois.append(poi)

        self.modelBuilder.doSet("POI", ",".join(pois))

    def getYieldScale(self, bin, process):
        """
        Map merged VH signal → corresponding POI.
        Backgrounds return 1.
        """

        # Signal: merged VH per pT bin
        if process.startswith("ZH_hbb_pTH_"):
            # ZH_hbb_pTH_200_300 → r_pTH_200_300
            return "r_" + process.replace("ZH_hbb_", "")

        # Backgrounds untouched
        return 1


# ------------------------------------------------------------
# IMPORTANT: register the model for text2workspace
# ------------------------------------------------------------
diffXsecModel = DiffXsecModel()
