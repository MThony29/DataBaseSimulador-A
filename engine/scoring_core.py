from typing import Dict, Any
from .data_manager import DataManager
from .variable_manager import VariableManager
from .normalizer import Normalizer
from .cache_system import CacheSystem

class ScoringCore:
    """
    ❤️ CORAZÓN DEL SISTEMA.
    Toda lógica de puntuación nace aquí.
    """
    def __init__(
        self,
        data_manager: DataManager,
        variable_manager: VariableManager,
        normalizer: Normalizer,
        cache: CacheSystem
    ):
        self.data = data_manager
        self.variables = variable_manager
        self.normalizer = normalizer
        self.cache = cache

    def calculate_team_score(self, country_id: str) -> Dict[str, Any]:
        """
        FUNCIÓN PRINCIPAL OBLIGATORIA.
        Calcula puntuación completa de una selección siguiendo:
        - Variables activas
        - Pesos definidos
        - Método de normalización
        - Reglas de datos faltantes

        :param country_id: Código del país
        :return: Diccionario con puntuaciones y desglose detallado
        """
        # Precálculo si caché está sucia
        if self.cache.is_dirty():
            self._precalculate_all_normalizations()
            self.cache.mark_clean()

        total_score = 0.0
        football_score = 0.0
        context_score = 0.0
        weight_sum_foot = 0.0
        weight_sum_cont = 0.0
        breakdown = {}
        category_contrib = {}
        warnings = []

        # Obtener solo variables activas
        active_vars = self.variables.get_active_variables()

        for var in active_vars.values():
            val = self.data.get_value(country_id, var.name)

            if val is None:
                warnings.append(f"Dato faltante: {var.name}")
                continue

            # Obtener valor ya normalizado desde caché
            norm_val = self.cache.get(var.name, country_id)
            if norm_val is None:
                continue

            # Contribución real = valor * peso
            contribution = norm_val * var.current_weight
            total_score += contribution

            # Acumular por tipo (Deportivo / Contexto)
            if var.data_type == "FOOTBALL":
                football_score += contribution
                weight_sum_foot += var.current_weight
            else:
                context_score += contribution
                weight_sum_cont += var.current_weight

            # Acumular por categoría
            if var.category not in category_contrib:
                category_contrib[var.category] = 0.0
            category_contrib[var.category] += contribution

            # Guardar detalle
            breakdown[var.name] = {
                "original_value": val,
                "normalized_value": norm_val,
                "weight": var.current_weight,
                "contribution": round(contribution, 3),
                "source": var.source_type
            }

        # Normalizar puntuaciones por peso total para mantener escala 0-100
        if weight_sum_foot > 0:
            football_score /= weight_sum_foot
        if weight_sum_cont > 0:
            context_score /= weight_sum_cont
        total_weight = weight_sum_foot + weight_sum_cont
        if total_weight > 0:
            total_score /= total_weight
        else:
            total_score = 0.0

        return {
            "total_score": round(total_score, 3),
            "football_score": round(football_score, 3),
            "context_score": round(context_score, 3),
            "breakdown": breakdown,
            "category_contribution": category_contrib,
            "warnings": warnings
        }

    def _precalculate_all_normalizations(self) -> None:
        """
        Calcula y guarda en caché TODOS los valores normalizados.
        Se ejecuta una sola vez hasta que cambie algo en la configuración.
        """
        self.cache.mark_dirty()
        active_vars = self.variables.get_active_variables()
        all_countries = self.data.get_all_countries()

        for var in active_vars.values():
            stats = self.data.get_statistics(var.name)
            for cid in all_countries:
                val = self.data.get_value(cid, var.name)
                if val is not None and stats:
                    norm_val = self.normalizer.normalize(val, var, stats)
                    self.cache.set(var.name, cid, norm_val)