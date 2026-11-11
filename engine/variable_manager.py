from typing import Dict, Optional
from .variable_registry import Variable, VariableRegistry

class VariableManager:
    """
    Gestiona el estado dinámico de las variables (activación, pesos).
    Actúa como puente entre el registro y el motor de cálculo.
    """
    def __init__(self, registry: VariableRegistry):
        self.registry = registry

    def set_active(self, var_name: str, active: bool) -> bool:
        """Activa o desactiva una variable para los cálculos."""
        var = self.registry.get(var_name)
        if var:
            var.active = active
            return True
        return False

    def set_weight(self, var_name: str, weight: float) -> bool:
        """Modifica el peso actual de una variable."""
        var = self.registry.get(var_name)
        if var:
            var.current_weight = max(0.0, float(weight))  # No permitir pesos negativos
            return True
        return False

    def reset_to_defaults(self) -> None:
        """Restaura todos los pesos y estados a su valor original."""
        for var in self.registry.get_all().values():
            var.current_weight = var.default_weight
            var.active = True

    def get_active_variables(self) -> Dict[str, Variable]:
        """Devuelve solo las variables que están activas actualmente."""
        return {k:v for k,v in self.registry.get_all().items() if v.active}