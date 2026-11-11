"""
MÓDULO PRINCIPAL
Este es el archivo que importarás desde la interfaz o scripts.
Expone la API PÚBLICA del motor.
"""
from typing import List, Tuple, Dict, Optional, Any
from .data_manager import DataManager
from .variable_registry import VariableRegistry, Variable, SourceType, Direction, DataType
from .variable_manager import VariableManager
from .normalizer import Normalizer
from .scoring_core import ScoringCore
from .ranking import RankingEngine
from .simulation import SimulationEngine
from .cache_system import CacheSystem
from engine.config import DEFAULT_NORMALIZATION, MISSING_DATA_POLICY

class FootballAnalysisEngine:
    """
    Clase principal. Interfaz única para interactuar con todo el sistema.
    Aísla la complejidad interna.
    """
    def __init__(self):
        # Inicialización de subsistemas
        self.data_manager = DataManager(missing_policy=MISSING_DATA_POLICY)
        self.variable_registry = VariableRegistry()
        self.variable_manager = VariableManager(self.variable_registry)
        self.normalizer = Normalizer(method=DEFAULT_NORMALIZATION)
        self.cache = CacheSystem()

        # Núcleo de cálculo
        self.scoring_core = ScoringCore(
            data_manager=self.data_manager,
            variable_manager=self.variable_manager,
            normalizer=self.normalizer,
            cache=self.cache
        )

        # Módulos superiores
        self.ranking = RankingEngine(self.scoring_core)
        self.simulation = SimulationEngine(self.ranking)

    # ───────────────────────────────────────────────
    # MÉTODOS DE CONFIGURACIÓN
    # ───────────────────────────────────────────────
    def load_data(self) -> None:
        """Carga todos los datos definidos en config.py"""
        self.data_manager.load_from_json()
        self.cache.mark_dirty()

    def register_variable(self, variable: Variable) -> None:
        """Agrega definición de variable al sistema."""
        self.variable_registry.register(variable)
        self.cache.mark_dirty()

    def add_custom_variable(
        self, name: str, description: str, category: str,
        direction: str, values: Dict[str, float],
        unit: str = "", default_weight: float = 1.0, target: Optional[float] = None
    ) -> None:
        """
        Agrega variable definida por el usuario.
        Automáticamente clasificada como USER_DEFINED.
        """
        var = Variable(
            name=name,
            description=description,
            category=category,
            data_type=DataType.FOOTBALL,  # Por defecto, usuario define deportivas
            source_type=SourceType.USER_DEFINED,
            direction=direction,
            unit=unit,
            default_weight=default_weight,
            target_value=target
        )
        self.register_variable(var)
        # Insertar valores en datos
        for cid, val in values.items():
            if cid not in self.data_manager.data:
                self.data_manager.data[cid] = {}
            self.data_manager.data[cid][name] = val
        self.data_manager._calculate_global_statistics()

    # ───────────────────────────────────────────────
    # MÉTODOS DE CONTROL (Para conectar con UI)
    # ───────────────────────────────────────────────
    def set_variable_active(self, var_name: str, active: bool) -> None:
        """Activa/desactiva variable. API para Kivy."""
        if self.variable_manager.set_active(var_name, active):
            self.cache.mark_dirty()

    def set_variable_weight(self, var_name: str, weight: float) -> None:
        """Cambia peso de variable. API para Kivy."""
        if self.variable_manager.set_weight(var_name, weight):
            # ⚠️ Solo invalidar caché si es necesario, pero aquí no recalculamos datos
            pass

    def set_normalization_method(self, method: str) -> None:
        """Cambia método de normalización global."""
        self.normalizer.set_method(method)
        self.cache.mark_dirty()

    # ───────────────────────────────────────────────
    # MÉTODOS DE CÁLCULO Y RESULTADOS
    # ───────────────────────────────────────────────
    def calculate_team_score(self, country_id: str) -> Dict[str, Any]:
        """Obtiene puntuación individual de un equipo."""
        return self.scoring_core.calculate_team_score(country_id)

    def rank_all_teams(self) -> List[Tuple[str, float]]:
        """Obtiene ranking completo."""
        return self.ranking.rank_all_teams()

    def compare_teams(self, country_a: str, country_b: str) -> Dict[str, Any]:
        """Compara dos equipos."""
        return self.ranking.compare_teams(country_a, country_b)