#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Diff-xsec pipeline (ASIMOV by default)
# - Uses global physics model at: ${BASE}/physics_model_diffXsec.py
# - Era cards: 6 SRs combined per era
# - Combo cards: raw SR cards across eras (unique channel labels)
# - Bestfit: robust, no interval hunting (log still may show POI warnings, but minimized)
# - 1D scans: grid, floatOtherPOIs=0, saveNLL
# ============================================================

BASE="/eos/user/h/haozhong/Combine/CMSSW_14_1_0_pre4/src/CombineHarvester/VHccCoHa"
OUTBASE="${BASE}/diffxsec_outputs_15_01_Gnn_SM_FR20_29jan"
MASS=125

PHYS_MODEL="${BASE}/physics_model_diffXsec.py"
SIGMA_JSON="${BASE}/sigma_SM_Zmm_Hbb.json"
MAKER="${BASE}/make_diffxsec_results.py"   # your rewritten script

# --- runtime knobs ---
ASIMOV="${ASIMOV:-1}"          # 1 => -t -1, 0 => observed
POINTS="${POINTS:-21}"
RMIN="${RMIN:--5}"
RMAX="${RMAX:-4}"
FREEZE_NUIS="${FREEZE_NUIS:-0}"  # 1 => freezeParameters all
DEBUG="${DEBUG:-0}"

# --- era dirs with SR cards ---
DIR_22_PRE="${BASE}/output_Hbb_20260414/2022_preEE"
DIR_22_POST="${BASE}/output_Hbb_20260414/2022_postEE"
DIR_23_PRE="${BASE}/output_Hbb_20260414/2023_preBPix"
DIR_23_POST="${BASE}/output_Hbb_20260414/2023_postBPix"
DIR_24="${BASE}/output_Hbb_20260414/2024"
POIS=( r_pTH_0_60 r_pTH_60_120 r_pTH_120_200 r_pTH_200_300 r_pTH_300_450 r_pTH_450_inf )

mkdir -p "${OUTBASE}"

echo "============================================================"
echo " Diff-xsec pipeline (ASIMOV)"
echo " BASE        : ${BASE}"
echo " OUTBASE     : ${OUTBASE}"
echo " PHYS_MODEL  : ${PHYS_MODEL}"
echo " ASIMOV      : ${ASIMOV}"
echo " R range     : [${RMIN}, ${RMAX}]"
echo " POINTS      : ${POINTS}"
echo " FREEZE_NUIS : ${FREEZE_NUIS}"
echo " DEBUG       : ${DEBUG}"
echo "============================================================"

need_file() { [[ -f "$1" ]] || { echo "[ERROR] Missing: $1" >&2; exit 1; }; }

need_file "${PHYS_MODEL}"
need_file "${SIGMA_JSON}"
need_file "${MAKER}"

ASIMOV_OPTS=()
[[ "${ASIMOV}" == "1" ]] && ASIMOV_OPTS=(-t -1)

FREEZE_OPTS=()
[[ "${FREEZE_NUIS}" == "1" ]] && FREEZE_OPTS=(--freezeParameters allConstrainedNuisances)
##FREEZE_OPTS=(--freezeParameters all)

DBG_OPTS=()
if [[ "${DEBUG}" == "1" ]]; then
  DBG_OPTS=(--verbose 3 --X-rtd MINIMIZER_PrintLevel=3 --X-rtd MINIMIZER_debug=1)
fi

SET_PARAMS=$(IFS=,; echo "${POIS[*]/%/=1}")
SET_RANGES=$(IFS=:; echo "${POIS[*]/%/=${RMIN},${RMAX}}")

MIN_OPTS=(
  --robustFit 1
  --cminDefaultMinimizerStrategy 0
  --cminPreScan
  --cminFallbackAlgo "Minuit2,0:0.1"
  --X-rtd MINIMIZER_MaxCalls=10000
  --X-rtd MINIMIZER_MaxIterations=10000
)

# ------------------------------------------------------------
# ERA card builder (6 SRs combined)
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
        # CR_2="${SRCDIR}/vhqq_Zee_8_13p6TeV_${LABEL}.txt" \
    # CR_3="${SRCDIR}/vhqq_Zee_9_13p6TeV_${LABEL}.txt" \
    # CR_4="${SRCDIR}/vhqq_Zee_10_13p6TeV_${LABEL}.txt" \
    # CR_5="${SRCDIR}/vhqq_Zee_11_13p6TeV_${LABEL}.txt" \
    # CR_6="${SRCDIR}/vhqq_Zee_12_13p6TeV_${LABEL}.txt" \
  # combineCards.py \
  #   SR_inclusive="${SRCDIR}/vhqq_Zee_13_13p6TeV_${LABEL}.txt" \
  #   CR_inclusive="${SRCDIR}/vhqq_Zee_14_13p6TeV_${LABEL}.txt" \
  #   > "${OUT}"
  echo "${OUT}"
}

# ------------------------------------------------------------
# Combo card builder from RAW SR cards across eras
# (unique labels per era+sr to avoid duplicates)
# ------------------------------------------------------------
# build_combo_card() {
#   local LABEL="$1" DEST="$2"; shift 2
#   local ERA_DIRS=("$@")
#   mkdir -p "${DEST}"
#   local OUT="${DEST}/vhqq_Zee_${LABEL}.txt"

#   local cmd=(combineCards.py)
#   for era in "${ERA_DIRS[@]}"; do
#     local tag
#     tag="y$(basename "${era}")"
#     for i in {1..6}; do
#       cmd+=("${tag}_cat${i}=${era}/vhqq_Zee_${i}_13p6TeV.txt")
#     done
#   done
#   "${cmd[@]}" > "${OUT}"
#   echo "${OUT}"
# }
build_combo_card() {
  local LABEL="$1" DEST="$2"; shift 2
  local ERA_DIRS=("$@")
  mkdir -p "${DEST}"
  local OUT="${DEST}/vhqq_Zee_${LABEL}.txt"

  local cmd=(combineCards.py)
  for era in "${ERA_DIRS[@]}"; do
    local tag
    tag="y$(basename "${era}")"
    for i in {1..7}; do  # 改为 1..14，因为您有12个卡片
      # 添加 _${era_name} 后缀，但需要提取 era 名称
      local era_name=$(basename "${era}")
      cmd+=("${tag}_cat${i}=${era}/vhqq_Zee_${i}_13p6TeV_${era_name}.txt")
    done
  done
  "${cmd[@]}" > "${OUT}" # 暂时注释掉合并card的那一行命令
  echo "${OUT}"
}

# ------------------------------------------------------------
# Workspace builder using global physics model
# (copy model into workspace dir + set PYTHONPATH there)
# ------------------------------------------------------------
build_workspace() {
  local LABEL="$1" CARD="$2" DEST="$3"
  mkdir -p "${DEST}"

  cp -f "${PHYS_MODEL}" "${DEST}/physics_model_diffXsec.py"
  export PYTHONPATH="${DEST}"

  text2workspace.py "${CARD}" \
    -m "${MASS}" \
    -P physics_model_diffXsec:diffXsecModel \
    -o "${DEST}/ws_${LABEL}.root"
}

# ------------------------------------------------------------
# Bestfit + scans
# ------------------------------------------------------------
run_scans() {
  local LABEL="$1" WS="$2" SCANDIR="$3"
  mkdir -p "${SCANDIR}"
  cd "${SCANDIR}"

  #echo ">>> [${LABEL}] Best fit" >&2
  #combine -M MultiDimFit "${WS}" \
  #  -m "${MASS}" "${ASIMOV_OPTS[@]}" \
  #  --setParameters "${SET_PARAMS}" \
  #  --setParameterRanges "${SET_RANGES}" \
  #  "${MIN_OPTS[@]}" "${FREEZE_OPTS[@]}" "${DBG_OPTS[@]}" \
  #  --algo=none \
  #  --saveWorkspace \
  #  --saveFitResult \
  #  -n "_bestfit"

  echo ">>> [${LABEL}] 1D scans" >&2
  for p in "${POIS[@]}"; do
    echo "    -> scan ${p}" >&2
    combine -M MultiDimFit "${WS}" \
      -m "${MASS}" "${ASIMOV_OPTS[@]}" \
      --setParameters "${SET_PARAMS}" \
      --setParameterRanges "${SET_RANGES}" \
      "${MIN_OPTS[@]}" "${FREEZE_OPTS[@]}" "${DBG_OPTS[@]}" \
      --algo=grid --points "${POINTS}" \
      -P "${p}" \
      --floatOtherPOIs=0 \
      --saveNLL \
      -n "_scan_${p}"
  done
}

plot_scans() {
  local LABEL="$1" SCANDIR="$2"
  cd "${SCANDIR}"
  command -v plot1DScan.py >/dev/null 2>&1 || return 0

  echo ">>> [${LABEL}] plot1DScan.py" >&2
  for p in "${POIS[@]}"; do
    local f="higgsCombine_scan_${p}.MultiDimFit.mH${MASS}.root"
    [[ -f "${f}" ]] || continue
    plot1DScan.py "${f}" --POI "${p}" --main-label "${LABEL}" --output "scan_${LABEL}_${p}"
  done
}

make_results() {
  local LABEL="$1" SCANDIR="$2"
  python3 "${MAKER}" \
    --scandir "${SCANDIR}" \
    --sigma-sm "${SIGMA_JSON}" \
    --mass "${MASS}" \
    --out-csv "${SCANDIR}/diffxsec_${LABEL}.csv" \
    --out-json "${SCANDIR}/diffxsec_${LABEL}.json" \
    --pois "${POIS[@]}"
}

# run_era() {
#   local LABEL="$1" DIR="$2"
#   local WSDIR="${OUTBASE}/${LABEL}/workspace"
#   local SCANDIR="${OUTBASE}/${LABEL}/scans"
#   mkdir -p "${WSDIR}" "${SCANDIR}"

#   need_file "${DIR}/vhqq_Zee_1_13p6TeV.txt"
#   need_file "${DIR}/vhqq_Zee_6_13p6TeV.txt"

#   local CARD
#   CARD="$(build_era_card "${LABEL}" "${DIR}" "${WSDIR}")"
#   build_workspace "${LABEL}" "${CARD}" "${WSDIR}"
#   run_scans "${LABEL}" "${WSDIR}/ws_${LABEL}.root" "${SCANDIR}"
#   plot_scans "${LABEL}" "${SCANDIR}"
#   make_results "${LABEL}" "${SCANDIR}"
# }
run_era() {
  local LABEL="$1" DIR="$2"
  local WSDIR="${OUTBASE}/${LABEL}/workspace"
  local SCANDIR="${OUTBASE}/${LABEL}/scans"
  mkdir -p "${WSDIR}" "${SCANDIR}"

  # 检查文件是否存在（使用正确的文件名格式）
  need_file "${DIR}/vhqq_Zee_1_13p6TeV_${LABEL}.txt"
  # need_file "${DIR}/vhqq_Zee_12_13p6TeV_${LABEL}.txt"  # 检查最后一个文件

  local CARD
  CARD="$(build_era_card "${LABEL}" "${DIR}" "${WSDIR}")"
  build_workspace "${LABEL}" "${CARD}" "${WSDIR}"
  run_scans "${LABEL}" "${WSDIR}/ws_${LABEL}.root" "${SCANDIR}"
  plot_scans "${LABEL}" "${SCANDIR}"
  make_results "${LABEL}" "${SCANDIR}"
}
run_combo() {
  local LABEL="$1"; shift
  local DIRS=("$@")
  local WSDIR="${OUTBASE}/${LABEL}/workspace"
  local SCANDIR="${OUTBASE}/${LABEL}/scans"
  mkdir -p "${WSDIR}" "${SCANDIR}"

  local CARD
  CARD="$(build_combo_card "${LABEL}" "${WSDIR}" "${DIRS[@]}")"
  build_workspace "${LABEL}" "${CARD}" "${WSDIR}"
  run_scans "${LABEL}" "${WSDIR}/ws_${LABEL}.root" "${SCANDIR}"
  plot_scans "${LABEL}" "${SCANDIR}"
  make_results "${LABEL}" "${SCANDIR}"
}

# ---------------- run eras ----------------
run_era "2022_preEE"    "${DIR_22_PRE}"
run_era "2022_postEE"   "${DIR_22_POST}"
run_era "2023_preBPix"  "${DIR_23_PRE}"
run_era "2023_postBPix" "${DIR_23_POST}"
# run_era "2024" "${DIR_24}"
# ---------------- run combos ----------------
run_combo "2022" "${DIR_22_PRE}" "${DIR_22_POST}"
run_combo "2023" "${DIR_23_PRE}" "${DIR_23_POST}"
# run_combo "Run3_2223" "${DIR_23_PRE}" "${DIR_23_POST}" "${DIR_22_PRE}" "${DIR_22_POST}"
run_combo "Run3_full" "${DIR_22_POST}" "${DIR_22_PRE}" "${DIR_23_PRE}" "${DIR_23_POST}" "${DIR_24}"

echo "============================================================"
echo " DONE – outputs in ${OUTBASE}"
echo "============================================================"
