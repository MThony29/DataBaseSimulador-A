from typing import Dict, List, Optional, Any
import json
import os
import math
from engine.config import DATA_FOLDER, DATA_FILES


class DataManager:
    """
    Capa de acceso y gestión de datos.
    Responsable de cargar desde archivos o APIs, almacenar valores y calcular estadísticas globales.
    """
    def __init__(self, missing_policy: str = "EXCLUDE"):
        self.data: Dict[str, Dict[str, float]] = {}  # {PAIS: {VARIABLE: VALOR}}
        self.statistics: Dict[str, Dict[str, Any]] = {}  # Estadísticas por variable
        self.missing_policy = missing_policy

    def load_from_json(self, folder: str = DATA_FOLDER, files: List[str] = None) -> None:
        """
        Carga datos desde múltiples archivos JSON.
        Soporta valores directos y anidados en subobjetos (ej: estadisticas_generales).
        Ignora listas (ej: jugadores individuales).
        """
        files = files or DATA_FILES
        for filename in files:
            path = os.path.join(folder, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    chunk = json.load(f)

                for country_id, values in chunk.items():
                    # Saltar entradas que no sean diccionarios (listas de jugadores, etc.)
                    if not isinstance(values, dict):
                        continue

                    if country_id not in self.data:
                        self.data[country_id] = {}

                    # Extraer valores numéricos directos
                    for var_name, val in values.items():
                        if isinstance(val, (int, float)) and not math.isnan(val):
                            self.data[country_id][var_name] = float(val)

                    # Extraer valores numéricos de subobjetos (ej: estadisticas_generales)
                    for var_name, val in values.items():
                        if isinstance(val, dict):
                            for sub_key, sub_val in val.items():
                                if isinstance(sub_val, (int, float)) and not math.isnan(sub_val):
                                    self.data[country_id][sub_key] = float(sub_val)

            except Exception as e:
                print(f"⚠️ [DataManager] Error cargando {filename}: {e}")

        self._calculate_global_statistics()

    def load_from_api(self, api_name: str) -> None:
        """
        Esqueleto para carga desde APIs externas.
        """
        raise NotImplementedError("Conexión API pendiente de implementación")

    def _calculate_global_statistics(self) -> None:
        """Calcula min, max, media, mediana, desviación estándar para cada variable."""
        all_values: Dict[str, List[float]] = {}

        for country_data in self.data.values():
            for var_name, val in country_data.items():
                if var_name not in all_values:
                    all_values[var_name] = []
                all_values[var_name].append(val)

        for var_name, values in all_values.items():
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            mean = sum(values) / n
            median = sorted_vals[n//2] if n % 2 else (sorted_vals[n//2-1] + sorted_vals[n//2]) / 2
            min_val = sorted_vals[0]
            max_val = sorted_vals[-1]
            std_dev = math.sqrt(sum((x - mean)**2 for x in values) / n) if n > 0 else 0.0

            self.statistics[var_name] = {
                "count": n, "mean": mean, "median": median,
                "min": min_val, "max": max_val, "std_dev": std_dev,
                "values": sorted_vals
            }

    def get_value(self, country_id: str, var_name: str) -> Optional[float]:
        """
        Obtiene valor aplicando política de datos faltantes.
        """
        country_data = self.data.get(country_id, {})
        if var_name in country_data:
            return country_data[var_name]

        stats = self.statistics.get(var_name, {})
        if self.missing_policy == "EXCLUDE":
            return None
        elif self.missing_policy == "MEAN":
            return stats.get("mean", 0.0)
        elif self.missing_policy == "MEDIAN":
            return stats.get("median", 0.0)
        elif self.missing_policy == "ZERO":
            return 0.0
        return None

    def get_all_countries(self) -> List[str]:
        """Devuelve lista de todos los códigos de países cargados."""
        return list(self.data.keys())

    def get_statistics(self, var_name: str) -> Dict[str, Any]:
        """Devuelve estadísticas calculadas para una variable."""
        return self.statistics.get(var_name, {})