"""
Archivo de configuración central.
Proyecto: Simulador de Partidos - Mundial 2026
"""

import os

# ───────────────────────────────────────────────
# RUTAS BASE
# ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # carpeta engine/
DATA_FOLDER = os.path.join(BASE_DIR, "..", "data")     # sube un nivel → data/

# ───────────────────────────────────────────────
# ARCHIVOS JSON EN /data
# ───────────────────────────────────────────────

DATOS_GENERALES = [
    "Datos_Generales_A_B_C_D.json",
    "Datos_Generales_D_F_H_I.json",
    "Datos_Generales_G.json",
#   "Datos_Generales_I_J_K_L.json",
]

#DEFINICION_COMPLETA = [
#    "Definicion_Completa_E_F_H_I.json",
#    "Definicion_Completa_G.json",
#    "Definicion_Completa_I_J_K_L.json",
#]

ESTADISTICAS_JUGADORES = []

JUGADORES = []

PORTERIA = [
    "Porteria_A_B_C_D.json",
    "Porteria_E_F_H_I.json",
    "Porteria_G.json",
    "Porteria_I_J_K_L.json",
]

RENDIMIENTO_EQUIPO = [
    "Rendimiento_Equipo_A_B_C_D.json",
    "Rendimiento_Equipo_E_F_H_I.json",
    "Rendimiento_Equipo_G.json",
    "Rendimiento_Equipo_I_J_K_L.json",
]

TIROS = [
    "Tiros_A_B_C_D.json",
    "Tiros_E_F_H_I.json",
    "Tiros_G.json",
    "Tiros_I_j_K_L.json",  # ojo: 'j' minúscula, no tocar
]

# Lista plana que consume data_manager.py
DATA_FILES = (
    DATOS_GENERALES
#   + DEFINICION_COMPLETA
    + ESTADISTICAS_JUGADORES
    + JUGADORES
    + PORTERIA
    + RENDIMIENTO_EQUIPO
    + TIROS
)

# ───────────────────────────────────────────────
# ARCHIVOS JSON EN LA RAÍZ DEL PROYECTO
# ───────────────────────────────────────────────
ROOT_DIR = os.path.join(BASE_DIR, "..")

FIFA_RANKINGS_FILE  = os.path.join(ROOT_DIR, "fifa_rankings_full.json")
MUNDIAL_DATOS_FILE  = os.path.join(ROOT_DIR, "mundial_2026_datos_con_ids.json")
WC2026_TEAMS_FILE   = os.path.join(ROOT_DIR, "wc2026_teams.json")

# ───────────────────────────────────────────────
# APIS (FUTURO)
# ───────────────────────────────────────────────
API_FOOTBALL_KEY      = ""
FOOTBALL_DATA_ORG_KEY = ""
WORLD_BANK_API_KEY    = ""

# ───────────────────────────────────────────────
# CONFIGURACIÓN DEL MOTOR
# ───────────────────────────────────────────────
DEFAULT_NORMALIZATION = "MIN_MAX"   # MIN_MAX | Z_SCORE | PERCENTILE
MISSING_DATA_POLICY   = "EXCLUDE"   # EXCLUDE | MEAN | MEDIAN | ZERO