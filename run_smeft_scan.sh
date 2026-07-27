#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# SMEFT scan pipeline for VHcc differential cross section
#
# Uses three separate physics model configurations:
#   SMEFT_POI=CHB  → workspace for 1D CHB scan (CHB=POI, CHW=nuisance)
#   SMEFT_POI=CHW  → workspace for 1D CHW scan (CHW=POI, CHB=nuisance)
#   SMEFT_POI=CHB,CHW → workspace for 2D scan (both are POIs)
#
# This way MultiDimFit only sees ONE POI for 1D scans,
# avoiding "defines more than one parameter of interest" warning
# and correctly profiling the non-POI SMEFT coefficient.
# ============================================================

BASE="/eos/user/h/haozhong/Combine/CMSSW_14_1_0_pre4/src/CombineHarvester/VHccCoHa_STXS_ptbinned_20260727"#VHccCoHa_STXS_ptbinned_20260712_SMEFT_veryGood_but_ratio_need_consider
OUTBASE="${BASE}/smeft_outputs"
MASS=125

PHYS_MODEL="${BASE}/physics_model_SMEFT.py"

# --- runtime knobs ---
ASIMOV="${ASIMOV:-1}"          # 1 => -t -1 (Asimov)
POINTS="${POINTS:-99}"        # scan points per dimension
C_MIN="${C_MIN:--2}"
C_MAX="${C_MAX:-2}"
DEBUG="${DEBUG:-0}"

# --- era dirs ---
DIR_22_PRE="${BASE}/output_Hbb_20260414/2022_preEE"
DIR_22_POST="${BASE}/output_Hbb_20260414/2022_postEE"
DIR_23_PRE="${BASE}/output_Hbb_20260414/2023_preBPix"
DIR_23_POST="${BASE}/output_Hbb_20260414/2023_postBPix"
DIR_24="${BASE}/output_Hbb_20260414/2024"

mkdir -p "${OUTBASE}"

echo "============================================================"
echo " SMEFT scan pipeline"
echo " BASE        : ${BASE}"
echo " OUTBASE     : ${OUTBASE}"
echo " PHYS_MODEL  : ${PHYS_MODEL}"
echo " ASIMOV      : ${ASIMOV}"
echo " C range     : [${C_MIN}, ${C_MAX}]"
echo " POINTS      : ${POINTS}  (1D: ${POINTS}; 2D: sqrt(${POINTS}) per dim)"
echo " DEBUG       : ${DEBUG}"
echo "============================================================"

need_file() { [[ -f "$1" ]] || { echo "[ERROR] Missing: $1" >&2; exit 1; }; }
need_file "${PHYS_MODEL}"

ASIMOV_OPTS=()
[[ "${ASIMOV}" == "1" ]] && ASIMOV_OPTS=(-t -1)

DBG_OPTS=()
if [[ "${DEBUG}" == "1" ]]; then
  DBG_OPTS=(--verbose 3 --X-rtd MINIMIZER_PrintLevel=3 --X-rtd MINIMIZER_debug=1)
fi

MIN_OPTS=(
 # --robustFit 1
 # --cminDefaultMinimizerStrategy 2
 # --cminPreScan
  --X-rtd MINIMIZER_MaxCalls=300000
  --X-rtd MINIMIZER_MaxIterations=300000
)

# ------------------------------------------------------------
# Card & workspace builders
# ------------------------------------------------------------
build_era_card() {
  local LABEL="$1" SRCDIR="$2" DEST="$3"
  mkdir -p "${DEST}"
  local OUT="${DEST}/vhqq_Zee_${LABEL}.txt"
  combineCards.py \
    SR_1="${SRCDIR}/vhqq_Zee_1_13p6TeV_${LABEL}.txt" \
    SR_2="${SRCDIR}/vhqq_Zee_2_13p6TeV_${LABEL}.txt" \
    SR_3="${SRCDIR}/vhqq_Zee_3_13p6TeV_${LABEL}.txt" \
    SR_4="${SRCDIR}/vhqq_Zee_4_13p6TeV_${LABEL}.txt" \
    SR_5="${SRCDIR}/vhqq_Zee_5_13p6TeV_${LABEL}.txt" \
    SR_6="${SRCDIR}/vhqq_Zee_6_13p6TeV_${LABEL}.txt" \
    CR_1="${SRCDIR}/vhqq_Zee_7_13p6TeV_${LABEL}.txt" \
    > "${OUT}"
  echo "${OUT}"
}

build_combo_card() {
  local LABEL="$1" DEST="$2"; shift 2
  local ERA_DIRS=("$@")
  mkdir -p "${DEST}"
  local OUT="${DEST}/vhqq_Zee_${LABEL}.txt"
  local cmd=(combineCards.py)
  for era in "${ERA_DIRS[@]}"; do
    local tag="y$(basename "${era}")"
    local era_name=$(basename "${era}")
    for i in {1..7}; do
      cmd+=("${tag}_cat${i}=${era}/vhqq_Zee_${i}_13p6TeV_${era_name}.txt")
    done
  done
  "${cmd[@]}" > "${OUT}"
  echo "${OUT}"
}

# Build a workspace for a specific SMEFT_POI configuration
build_workspace() {
  local LABEL="$1" CARD="$2" DEST="$3" POI_CONFIG="$4"
  mkdir -p "${DEST}"
  cp -f "${PHYS_MODEL}" "${DEST}/physics_model_SMEFT.py"
  export PYTHONPATH="${DEST}"
  export SMEFT_POI="${POI_CONFIG}"
  echo ">>> Building workspace for SMEFT_POI=${SMEFT_POI}" >&2
  text2workspace.py "${CARD}" \
    -m "${MASS}" \
    -P physics_model_SMEFT:smeftModel \
    -o "${DEST}/ws_${LABEL}_${POI_CONFIG//,/_}.root"
}

# ------------------------------------------------------------
# 1D scan of a single POI
# ------------------------------------------------------------
run_scan_1d() {
  local LABEL="$1" WS="$2" SCANDIR="$3" POI="$4"
  mkdir -p "${SCANDIR}"
  cd "${SCANDIR}"

  # The non-POI Wilson coefficient is already FIXED to 0 in the workspace
  # (see physics_model_SMEFT.py). So we only set the scanned POI.
  local SET_PARAMS="${POI}=0"
  local SET_RANGES="${POI}=${C_MIN},${C_MAX}"

  echo ">>> [${LABEL}] 1D scan ${POI} (other SMEFT param FIXED to 0 in workspace)" >&2
  combine -M MultiDimFit "${WS}" \
    -m "${MASS}" "${ASIMOV_OPTS[@]}" \
    --setParameters "${SET_PARAMS}" \
    --setParameterRanges "${SET_RANGES}" \
    "${MIN_OPTS[@]}" "${DBG_OPTS[@]}" \
    --algo=grid --points "${POINTS}" \
    -P "${POI}" \
    --fastScan \
    --alignEdges=on \
    --saveNLL \
    -n "_scan_${POI}"
}

# ------------------------------------------------------------
# 2D scan: both CHB and CHW are POIs
# ------------------------------------------------------------
run_scan_2d() {
  local LABEL="$1" WS="$2" SCANDIR="$3"
  mkdir -p "${SCANDIR}"
  cd "${SCANDIR}"

  # Use an ODD number of points per dimension so that 0 is exactly on the grid
  # when using --alignEdges. With an even number, 0 falls between points.
  local N_PER_DIM
  N_PER_DIM=$(python3 -c "import math; n=int(math.sqrt(${POINTS})); n=(n//2)*2+1; print(max(n,5))" 2>/dev/null || echo 9)
  local POINTS_2D=$((N_PER_DIM * N_PER_DIM))

  local SET_PARAMS="CHB=0,CHW=0"
  local SET_RANGES="CHB=${C_MIN},${C_MAX}:CHW=${C_MIN},${C_MAX}"

  echo ">>> [${LABEL}] 2D scan CHB vs CHW (grid ${N_PER_DIM}x${N_PER_DIM} = ${POINTS_2D} points)" >&2
  combine -M MultiDimFit "${WS}" \
    -m "${MASS}" "${ASIMOV_OPTS[@]}" \
    --setParameters "${SET_PARAMS}" \
    --setParameterRanges "${SET_RANGES}" \
    "${MIN_OPTS[@]}" "${DBG_OPTS[@]}" \
    --algo=grid --points "${POINTS_2D}" \
    -P "CHB" -P "CHW" \
    --fastScan \
    --alignEdges=on \
    --saveNLL \
    -n "_scan_2D"
}

# ------------------------------------------------------------
# Plot results
# ------------------------------------------------------------
plot_all() {
  local LABEL="$1" SCANDIR="$2"
  python3 "${BASE}/make_smeft_results.py" \
    --scandir "${SCANDIR}" \
    --mass "${MASS}" \
    --out-json "${SCANDIR}/smeft_results_${LABEL}.json" \
    --plot-dir "${SCANDIR}"
}

# ------------------------------------------------------------
# Main runner: builds 3 workspaces (CHB, CHW, 2D) and runs scans
# ------------------------------------------------------------
run_smeft_era() {
  local LABEL="$1" DIR="$2"

  # Build combined card (shared by all 3 workspaces)
  local CARDDIR="${OUTBASE}/${LABEL}/cards"
  local CARD
  CARD="$(build_era_card "${LABEL}" "${DIR}" "${CARDDIR}")"

  # --- 1D scan CHB ---
  local WSDIR_CHB="${OUTBASE}/${LABEL}/workspace_CHB"
  local SCANDIR_CHB="${OUTBASE}/${LABEL}/scans_CHB"
  mkdir -p "${WSDIR_CHB}" "${SCANDIR_CHB}"
  build_workspace "${LABEL}" "${CARD}" "${WSDIR_CHB}" "CHB"
  run_scan_1d "${LABEL}" "${WSDIR_CHB}/ws_${LABEL}_CHB.root" "${SCANDIR_CHB}" "CHB"

  # --- 1D scan CHW ---
  local WSDIR_CHW="${OUTBASE}/${LABEL}/workspace_CHW"
  local SCANDIR_CHW="${OUTBASE}/${LABEL}/scans_CHW"
  mkdir -p "${WSDIR_CHW}" "${SCANDIR_CHW}"
  build_workspace "${LABEL}" "${CARD}" "${WSDIR_CHW}" "CHW"
  run_scan_1d "${LABEL}" "${WSDIR_CHW}/ws_${LABEL}_CHW.root" "${SCANDIR_CHW}" "CHW"

  # --- 2D scan ---
  local WSDIR_2D="${OUTBASE}/${LABEL}/workspace_2D"
  local SCANDIR_2D="${OUTBASE}/${LABEL}/scans_2D"
  mkdir -p "${WSDIR_2D}" "${SCANDIR_2D}"
  build_workspace "${LABEL}" "${CARD}" "${WSDIR_2D}" "CHB,CHW"
  run_scan_2d "${LABEL}" "${WSDIR_2D}/ws_${LABEL}_CHB_CHW.root" "${SCANDIR_2D}"

  # --- Combine scan outputs into a single directory for plotting ---
  local ALLSCANS="${OUTBASE}/${LABEL}/scans"
  mkdir -p "${ALLSCANS}"
  # Symlink (or copy) all scan results into one place
  for f in "${SCANDIR_CHB}"/*.root; do
    bn=$(basename "$f" | sed 's/_CHB//')
    if [[ "$f" == *"higgsCombine_scan_CHB"* ]]; then
      ln -sf "$f" "${ALLSCANS}/$(basename "$f")" 2>/dev/null || cp "$f" "${ALLSCANS}/"
    fi
  done
  for f in "${SCANDIR_CHW}"/*.root; do
    if [[ "$f" == *"higgsCombine_scan_CHW"* ]]; then
      ln -sf "$f" "${ALLSCANS}/$(basename "$f")" 2>/dev/null || cp "$f" "${ALLSCANS}/"
    fi
  done
  for f in "${SCANDIR_2D}"/*.root; do
    if [[ "$f" == *"higgsCombine_scan_2D"* ]]; then
      ln -sf "$f" "${ALLSCANS}/$(basename "$f")" 2>/dev/null || cp "$f" "${ALLSCANS}/"
    fi
  done

  plot_all "${LABEL}" "${ALLSCANS}"
}

run_smeft_combo() {
  local LABEL="$1"; shift
  local DIRS=("$@")

  # Build combined card
  local CARDDIR="${OUTBASE}/${LABEL}/cards"
  local CARD
  CARD="$(build_combo_card "${LABEL}" "${CARDDIR}" "${DIRS[@]}")"

  # 1D CHB
  local WSDIR_CHB="${OUTBASE}/${LABEL}/workspace_CHB"
  local SCANDIR_CHB="${OUTBASE}/${LABEL}/scans_CHB"
  mkdir -p "${WSDIR_CHB}" "${SCANDIR_CHB}"
  build_workspace "${LABEL}" "${CARD}" "${WSDIR_CHB}" "CHB"
  run_scan_1d "${LABEL}" "${WSDIR_CHB}/ws_${LABEL}_CHB.root" "${SCANDIR_CHB}" "CHB"

  # 1D CHW
  local WSDIR_CHW="${OUTBASE}/${LABEL}/workspace_CHW"
  local SCANDIR_CHW="${OUTBASE}/${LABEL}/scans_CHW"
  mkdir -p "${WSDIR_CHW}" "${SCANDIR_CHW}"
  build_workspace "${LABEL}" "${CARD}" "${WSDIR_CHW}" "CHW"
  run_scan_1d "${LABEL}" "${WSDIR_CHW}/ws_${LABEL}_CHW.root" "${SCANDIR_CHW}" "CHW"

  # 2D
  local WSDIR_2D="${OUTBASE}/${LABEL}/workspace_2D"
  local SCANDIR_2D="${OUTBASE}/${LABEL}/scans_2D"
  mkdir -p "${WSDIR_2D}" "${SCANDIR_2D}"
  build_workspace "${LABEL}" "${CARD}" "${WSDIR_2D}" "CHB,CHW"
  run_scan_2d "${LABEL}" "${WSDIR_2D}/ws_${LABEL}_CHB_CHW.root" "${SCANDIR_2D}"

  # Combine outputs
  local ALLSCANS="${OUTBASE}/${LABEL}/scans"
  mkdir -p "${ALLSCANS}"
  for f in "${SCANDIR_CHB}"/*.root; do
    if [[ "$f" == *"higgsCombine_scan_CHB"* ]]; then
      ln -sf "$f" "${ALLSCANS}/" 2>/dev/null || cp "$f" "${ALLSCANS}/"
    fi
  done
  for f in "${SCANDIR_CHW}"/*.root; do
    if [[ "$f" == *"higgsCombine_scan_CHW"* ]]; then
      ln -sf "$f" "${ALLSCANS}/" 2>/dev/null || cp "$f" "${ALLSCANS}/"
    fi
  done
  for f in "${SCANDIR_2D}"/*.root; do
    if [[ "$f" == *"higgsCombine_scan_2D"* ]]; then
      ln -sf "$f" "${ALLSCANS}/" 2>/dev/null || cp "$f" "${ALLSCANS}/"
    fi
  done

  plot_all "${LABEL}" "${ALLSCANS}"
}

# ======================== RUN ========================
run_smeft_era "2024" "${DIR_24}"

# Uncomment for full Run3 combination:
# run_smeft_combo "Run3_full" "${DIR_22_POST}" "${DIR_22_PRE}" "${DIR_23_PRE}" "${DIR_23_POST}" "${DIR_24}"

echo "============================================================"
echo " SMEFT scan DONE – outputs in ${OUTBASE}"
echo "============================================================"