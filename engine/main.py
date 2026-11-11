"""
Archivo principal de ejemplo.
AQUÍ PUEDES PROBAR EL MOTOR ANTES DE CONECTAR LA UI
"""
from engine.engine import FootballAnalysisEngine
from engine.variable_registry import Variable, SourceType, Direction, DataType

if __name__ == "__main__":
    # 1. Inicializar motor
    engine = FootballAnalysisEngine()

    # 2. DEFINIR VARIABLES
    engine.register_variable(Variable(
        name="victorias",
        description="Partidos ganados",
        category="Resultados",
        data_type=DataType.FOOTBALL,
        source_type=SourceType.DIRECT,
        direction=Direction.MAXIMIZE,
        default_weight=3.0
    ))
    engine.register_variable(Variable(
        name="goles_favor",
        description="Goles totales a favor",
        category="Ataque",
        data_type=DataType.FOOTBALL,
        source_type=SourceType.DIRECT,
        direction=Direction.MAXIMIZE,
        default_weight=2.5
    ))
    engine.register_variable(Variable(
        name="goles_contra",
        description="Goles totales en contra",
        category="Defensa",
        data_type=DataType.FOOTBALL,
        source_type=SourceType.DIRECT,
        direction=Direction.MINIMIZE,
        default_weight=2.5
    ))
    engine.register_variable(Variable(
        name="edad_promedio",
        description="Edad media del plantel",
        category="Físico",
        data_type=DataType.FOOTBALL,
        source_type=SourceType.DIRECT,
        direction=Direction.TARGET,
        target_value=27.0,
        default_weight=1.0
    ))
    engine.register_variable(Variable(
        name="xg_por_partido",
        description="Expected goals por partido",
        category="Ataque",
        data_type=DataType.FOOTBALL,
        source_type=SourceType.DIRECT,
        direction=Direction.MAXIMIZE,
        default_weight=2.0
    ))
    engine.register_variable(Variable(
        name="porterias_a_cero",
        description="Partidos sin recibir gol",
        category="Defensa",
        data_type=DataType.FOOTBALL,
        source_type=SourceType.DIRECT,
        direction=Direction.MAXIMIZE,
        default_weight=2.0
    ))
    engine.register_variable(Variable(
        name="puntos",
        description="Puntos acumulados",
        category="Resultados",
        data_type=DataType.FOOTBALL,
        source_type=SourceType.DIRECT,
        direction=Direction.MAXIMIZE,
        default_weight=3.0
    ))

    # 3. Cargar datos
    engine.load_data()

    # 4. RESULTADOS
    print("🏆 RANKING DE SELECCIONES")
    ranking = engine.rank_all_teams()
    for pos, (pais, pts) in enumerate(ranking, 1):
        print(f"{pos:2d}. {pais} -> {pts:.2f}")

    print("\n⚽ COMPARACIÓN MEX vs RSA")
    comp = engine.compare_teams("MEX", "RSA")
    print(f"MEX: {comp['scores']['percent_a']}% | RSA: {comp['scores']['percent_b']}%")