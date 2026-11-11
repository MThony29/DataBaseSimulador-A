from typing import Dict, Tuple, Optional
from functools import lru_cache

class CacheSystem:
    """
    Capa transversal de caché. No contiene lógica de negocio, solo acelera cálculos.
    Almacena valores ya normalizados para evitar recálculos masivos.
    """
    def __init__(self):
        # Estructura: {(variable, pais): valor_normalizado}
        self._normalized_cache: Dict[Tuple[str, str], float] = {}
        self._dirty: bool = True  # Indica si datos cambiaron y caché es inválido

    def mark_dirty(self) -> None:
        """Marca caché como obsoleta (cuando cambian datos o configuración)."""
        self._dirty = True
        self._normalized_cache.clear()

    def mark_clean(self) -> None:
        """Marca caché como actualizada tras precálculo."""
        self._dirty = False

    def get(self, var_name: str, country_id: str) -> Optional[float]:
        """Obtiene valor de caché si existe."""
        return self._normalized_cache.get((var_name, country_id))

    def set(self, var_name: str, country_id: str, value: float) -> None:
        """Guarda valor en caché."""
        self._normalized_cache[(var_name, country_id)] = value

    def is_dirty(self) -> bool:
        """Verifica si caché necesita recálculo."""
        return self._dirty

    # Decorador para caché automática en funciones
    @staticmethod
    def cached(func):
        return lru_cache(maxsize=None)(func)