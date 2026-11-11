from typing import Dict, Any
from abc import ABC, abstractmethod
from .variable_registry import Variable, Direction

class NormalizationStrategy(ABC):
    """Interfaz base para cualquier método de normalización."""
    @abstractmethod
    def normalize(self, value: float, var: Variable, stats: Dict[str, Any]) -> float:
        pass


class MinMaxStrategy(NormalizationStrategy):
    """Escala valores entre 0 y 100 respetando dirección de la variable."""
    def normalize(self, value: float, var: Variable, stats: Dict[str, Any]) -> float:
        min_v, max_v = stats["min"], stats["max"]
        if max_v == min_v:
            return 50.0  # Valor neutro si no hay rango

        if var.direction == Direction.MAXIMIZE:
            score = (value - min_v) / (max_v - min_v)
        elif var.direction == Direction.MINIMIZE:
            score = (max_v - value) / (max_v - min_v)
        elif var.direction == Direction.TARGET:
            range_total = max_v - min_v
            distance = abs(value - var.target_value)
            score = 1.0 - (distance / range_total) if range_total != 0 else 0.5
        else:
            score = 0.0

        return max(0.0, min(100.0, score * 100))


class ZScoreStrategy(NormalizationStrategy):
    """Puntuación estándar respecto a la media. Centrado en 50."""
    def normalize(self, value: float, var: Variable, stats: Dict[str, Any]) -> float:
        mean, std = stats["mean"], stats["std_dev"]
        if std == 0:
            return 50.0

        z = (value - mean) / std

        if var.direction == Direction.MAXIMIZE:
            score = 50 + (z * 10)
        elif var.direction == Direction.MINIMIZE:
            score = 50 - (z * 10)
        elif var.direction == Direction.TARGET:
            dist_z = abs(value - var.target_value) / std
            score = 50 - (dist_z * 10)
        else:
            score = 50

        return max(0.0, min(100.0, score))


class PercentileStrategy(NormalizationStrategy):
    """Posición relativa percentilar (0-100%)."""
    def normalize(self, value: float, var: Variable, stats: Dict[str, Any]) -> float:
        values_sorted = stats["values"]
        count = len(values_sorted)
        if count == 0:
            return 0.0

        position = next((i for i, v in enumerate(values_sorted) if v >= value), count-1)
        percentile = (position / (count - 1)) * 100 if count > 1 else 50.0

        if var.direction == Direction.MAXIMIZE:
            score = percentile
        elif var.direction == Direction.MINIMIZE:
            score = 100 - percentile
        elif var.direction == Direction.TARGET:
            closest_pos = min(range(count), key=lambda i: abs(values_sorted[i] - var.target_value))
            target_percentile = (closest_pos / (count - 1)) * 100 if count > 1 else 50.0
            score = 100 - abs(percentile - target_percentile)
        else:
            score = 50

        return max(0.0, min(100.0, score))


class Normalizer:
    """Gestor central de normalización. Permite cambiar estrategia dinámicamente."""
    def __init__(self, method: str = "MIN_MAX"):
        self.strategies: Dict[str, NormalizationStrategy] = {
            "MIN_MAX": MinMaxStrategy(),
            "Z_SCORE": ZScoreStrategy(),
            "PERCENTILE": PercentileStrategy()
        }
        self.current_method = method

    def set_method(self, method: str) -> None:
        """Cambia método de normalización global."""
        if method in self.strategies:
            self.current_method = method
        else:
            raise ValueError(f"Método {method} no disponible")

    def normalize(self, value: float, var: Variable, stats: Dict[str, Any]) -> float:
        """Ejecuta normalización según método activo."""
        return self.strategies[self.current_method].normalize(value, var, stats)