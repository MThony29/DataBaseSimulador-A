from typing import List, Tuple, Dict, Optional, Any
from .scoring_core import ScoringCore

class RankingEngine:
    """
    Motor de clasificaciones.
    Depende exclusivamente de ScoringCore para no duplicar lógica.
    """
    def __init__(self, scoring_core: ScoringCore):
        self.scoring = scoring_core

    def rank_all_teams(self) -> List[Tuple[str, float]]:
        """
        FUNCIÓN OBLIGATORIA.
        Genera ranking completo de todas las selecciones cargadas.
        :return: Lista ordenada [(PAIS, PUNTUACIÓN), ...]
        """
        rankings = []
        countries = self.scoring.data.get_all_countries()

        for cid in countries:
            score_data = self.scoring.calculate_team_score(cid)
            rankings.append((cid, score_data["total_score"]))

        # Ordenar de mayor a menor puntuación
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings

    def get_top_n(self, n: int = 10) -> List[Tuple[str, float]]:
        """Devuelve solo los N primeros del ranking."""
        full = self.rank_all_teams()
        return full[:n]

    def compare_teams(self, country_a: str, country_b: str) -> Dict[str, Any]:
        """
        Comparación detallada entre dos selecciones.
        Reutiliza puntuación individual.
        """
        score_a = self.scoring.calculate_team_score(country_a)
        score_b = self.scoring.calculate_team_score(country_b)

        total = score_a["total_score"] + score_b["total_score"]
        pct_a = round((score_a["total_score"] / total) * 100, 2) if total > 0 else 50.0
        pct_b = round((score_b["total_score"] / total) * 100, 2) if total > 0 else 50.0

        return {
            "countries": {"a": country_a, "b": country_b},
            "scores": {
                "a": score_a["total_score"],
                "b": score_b["total_score"],
                "percent_a": pct_a,
                "percent_b": pct_b
            },
            "details": {"a": score_a, "b": score_b}
        }