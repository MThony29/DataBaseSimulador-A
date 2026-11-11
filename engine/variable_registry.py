from typing import Dict, List, Optional, Any
# Enumeraciones de configuración
class Direction:
    MAXIMIZE = "MAXIMIZE"  # Más valor = mejor
    MINIMIZE = "MINIMIZE"  # Menos valor = mejor
    TARGET = "TARGET"      # Cerca de valor objetivo = mejor

class DataType:
    FOOTBALL = "FOOTBALL"  # Rendimiento deportivo
    CONTEXT = "CONTEXT"     # Factores externos

class SourceType:
    DIRECT = "DIRECT"           # Dato bruto original (PRIORIDAD MÁXIMA)
    DERIVED = "DERIVED"         # Índice o cálculo externo
    USER_DEFINED = "USER"       # Creado por el usuario

class Variable:
    """
    Representa la definición completa de una variable.
    Aquí se almacenan TODAS las propiedades fijas y configurables.
    """
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        data_type: str,
        source_type: str,
        direction: str,
        unit: str = "",
        default_weight: float = 1.0,
        target_value: Optional[float] = None,
        active_by_default: bool = True
    ):
        # Identificación
        self.name = name
        self.description = description
        self.category = category
        self.unit = unit

        # Clasificación
        self.data_type = data_type
        self.source_type = source_type

        # Comportamiento
        self.direction = direction
        self.target_value = target_value

        # Configuración usuario
        self.default_weight = default_weight
        self.current_weight = default_weight
        self.active = active_by_default

    def __repr__(self) -> str:
        return f"<Variable:{self.name} | Origen:{self.source_type} | Activa:{self.active}>"


class VariableRegistry:
    """
    Registro único y centralizado de TODAS las variables existentes.
    Permite administrar cientos de variables sin duplicidad.
    """
    def __init__(self):
        self._variables: Dict[str, Variable] = {}

    def register(self, variable: Variable) -> None:
        """Agrega una variable al catálogo."""
        if variable.name in self._variables:
            raise ValueError(f"La variable {variable.name} ya existe")
        self._variables[variable.name] = variable

    def get(self, name: str) -> Optional[Variable]:
        """Obtiene definición de variable por nombre."""
        return self._variables.get(name)

    def get_all(self) -> Dict[str, Variable]:
        """Devuelve todo el catálogo."""
        return self._variables

    def get_by_category(self, category: str) -> Dict[str, Variable]:
        """Filtra variables por categoría."""
        return {k:v for k,v in self._variables.items() if v.category == category}

    def get_by_source_type(self, source_type: str) -> Dict[str, Variable]:
        """Filtra por origen: DIRECT / DERIVED / USER"""
        return {k:v for k,v in self._variables.items() if v.source_type == source_type}

    def list_names(self) -> List[str]:
        """Lista solo nombres de variables."""
        return list(self._variables.keys())