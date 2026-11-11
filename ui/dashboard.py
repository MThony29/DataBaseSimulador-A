"""
Sharp Lab - Dashboard UI
Conecta con FootballAnalysisEngine para simular y rankear selecciones.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock

import sys
import os

# Agregar raíz del proyecto al path para poder importar engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.engine import FootballAnalysisEngine
from engine.variable_registry import Variable, SourceType, Direction, DataType

# ─────────────────────────────────────────────
# PALETA DE COLORES
# ─────────────────────────────────────────────
BG_DARK      = (0.05, 0.05, 0.08, 1)
BG_PANEL     = (0.08, 0.09, 0.13, 1)
BG_CARD      = (0.11, 0.12, 0.17, 1)
ACCENT       = (0.0,  0.85, 0.6,  1)   # verde neón
ACCENT_DIM   = (0.0,  0.5,  0.35, 1)
TEXT_BRIGHT  = (0.95, 0.95, 0.95, 1)
TEXT_DIM     = (0.5,  0.55, 0.6,  1)
DANGER       = (0.9,  0.2,  0.2,  1)
GOLD         = (1.0,  0.78, 0.1,  1)

Window.clearcolor = BG_DARK


# ─────────────────────────────────────────────
# VARIABLES PREDEFINIDAS DEL MOTOR
# ─────────────────────────────────────────────
DEFAULT_VARIABLES = [
    {"name": "victorias",         "description": "Partidos ganados",         "direction": Direction.MAXIMIZE, "weight": 3.0},
    {"name": "puntos",            "description": "Puntos acumulados",         "direction": Direction.MAXIMIZE, "weight": 3.0},
    {"name": "goles_favor",       "description": "Goles a favor",            "direction": Direction.MAXIMIZE, "weight": 2.5},
    {"name": "goles_contra",      "description": "Goles en contra",          "direction": Direction.MINIMIZE, "weight": 2.5},
    {"name": "xg_por_partido",    "description": "xG por partido",           "direction": Direction.MAXIMIZE, "weight": 2.0},
    {"name": "porterias_a_cero",  "description": "Porterías a cero",         "direction": Direction.MAXIMIZE, "weight": 2.0},
    {"name": "edad_promedio",     "description": "Edad promedio del plantel", "direction": Direction.TARGET,   "weight": 1.0},
]


# ─────────────────────────────────────────────
# WIDGET: FILA DE VARIABLE
# ─────────────────────────────────────────────
class VariableRow(BoxLayout):
    def __init__(self, var_name, description, default_weight=1.0, **kwargs):
        super().__init__(**kwargs)
        self.orientation  = 'horizontal'
        self.size_hint_y  = None
        self.height       = dp(52)
        self.spacing      = dp(8)
        self.padding      = [dp(8), dp(4)]

        self.var_name = var_name

        with self.canvas.before:
            Color(*BG_CARD)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Checkbox activo/inactivo
        self.checkbox = CheckBox(
            active=True,
            size_hint=(None, 1),
            width=dp(36),
            color=list(ACCENT)
        )

        # Nombre + descripción
        name_box = BoxLayout(orientation='vertical', size_hint=(0.3, 1))
        name_box.add_widget(Label(
            text=var_name,
            font_size=dp(13),
            color=TEXT_BRIGHT,
            halign='left', valign='middle',
            size_hint_y=0.6
        ))
        name_box.add_widget(Label(
            text=description,
            font_size=dp(10),
            color=TEXT_DIM,
            halign='left', valign='middle',
            size_hint_y=0.4
        ))

        # Slider de peso
        self.slider = Slider(
            min=0.1, max=5.0,
            value=default_weight,
            step=0.1,
            size_hint=(0.5, 1),
            cursor_size=(dp(18), dp(18)),
        )

        # Label del valor
        self.weight_label = Label(
            text=f"{default_weight:.1f}",
            font_size=dp(13),
            color=list(ACCENT),
            size_hint=(None, 1),
            width=dp(36),
            halign='center'
        )
        self.slider.bind(value=self._on_slider)

        self.add_widget(self.checkbox)
        self.add_widget(name_box)
        self.add_widget(self.slider)
        self.add_widget(self.weight_label)

    def _on_slider(self, instance, value):
        self.weight_label.text = f"{value:.1f}"

    def _update_bg(self, *args):
        self.bg_rect.pos  = self.pos
        self.bg_rect.size = self.size

    @property
    def is_active(self):
        return self.checkbox.active

    @property
    def weight(self):
        return self.slider.value


# ─────────────────────────────────────────────
# WIDGET: FILA DE RESULTADO
# ─────────────────────────────────────────────
class ResultRow(BoxLayout):
    def __init__(self, pos_num, country, score, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height      = dp(40)
        self.spacing     = dp(8)
        self.padding     = [dp(12), dp(4)]

        color_pos = GOLD if pos_num <= 3 else TEXT_BRIGHT

        self.add_widget(Label(
            text=f"{pos_num:2d}.",
            font_size=dp(13),
            color=color_pos,
            size_hint=(None, 1),
            width=dp(30),
            halign='right'
        ))
        self.add_widget(Label(
            text=country,
            font_size=dp(14),
            color=color_pos,
            halign='left',
            size_hint=(0.5, 1)
        ))

        # Barra de progreso
        bar_box = BoxLayout(size_hint=(0.35, 1), padding=[0, dp(14)])
        bar_bg = BoxLayout(size_hint=(1, 1))
        with bar_bg.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self._bar_bg = Rectangle(pos=bar_bg.pos, size=bar_bg.size)
        bar_bg.bind(pos=lambda i, v: setattr(self._bar_bg, 'pos', v),
                    size=lambda i, v: setattr(self._bar_bg, 'size', v))

        fill = BoxLayout(size_hint=(score / 100.0, 1))
        with fill.canvas.before:
            Color(*ACCENT)
            self._bar_fill = Rectangle(pos=fill.pos, size=fill.size)
        fill.bind(pos=lambda i, v: setattr(self._bar_fill, 'pos', v),
                  size=lambda i, v: setattr(self._bar_fill, 'size', v))

        bar_bg.add_widget(fill)
        bar_box.add_widget(bar_bg)

        self.add_widget(bar_box)
        self.add_widget(Label(
            text=f"{score:.1f}",
            font_size=dp(13),
            color=list(ACCENT),
            size_hint=(None, 1),
            width=dp(45),
            halign='right'
        ))


# ─────────────────────────────────────────────
# ROOT WIDGET
# ─────────────────────────────────────────────
class SharpLabDashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing     = dp(8)
        self.padding     = dp(12)

        self.engine = FootballAnalysisEngine()
        self.var_rows = {}  # name -> VariableRow

        self._build_left_panel()
        self._build_right_panel()
        self._init_engine()

    # ── PANEL IZQUIERDO: variables + custom ──
    def _build_left_panel(self):
        left = BoxLayout(orientation='vertical', size_hint=(0.45, 1), spacing=dp(8))

        # Título
        title = Label(
            text="SHARP LAB  //  VARIABLES",
            font_size=dp(14),
            color=list(ACCENT),
            size_hint_y=None,
            height=dp(36),
            halign='left'
        )
        left.add_widget(title)

        # Lista de variables con scroll
        scroll = ScrollView(size_hint=(1, 0.6))
        self.var_list = GridLayout(
            cols=1,
            spacing=dp(4),
            size_hint_y=None,
            padding=[0, dp(4)]
        )
        self.var_list.bind(minimum_height=self.var_list.setter('height'))
        scroll.add_widget(self.var_list)
        left.add_widget(scroll)

        # Separador
        left.add_widget(Label(
            text="── AGREGAR VARIABLE PROPIA ──",
            font_size=dp(11),
            color=TEXT_DIM,
            size_hint_y=None,
            height=dp(24)
        ))

        # Panel custom
        custom_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(130), spacing=dp(6))

        # Input nombre
        self.custom_name = TextInput(
            hint_text="nombre_variable",
            multiline=False,
            size_hint_y=None,
            height=dp(36),
            background_color=list(BG_CARD),
            foreground_color=list(TEXT_BRIGHT),
            cursor_color=list(ACCENT),
            font_size=dp(13)
        )

        # Slider peso custom
        weight_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        weight_row.add_widget(Label(text="Peso:", color=TEXT_DIM, size_hint=(None, 1), width=dp(40), font_size=dp(12)))
        self.custom_slider = Slider(min=0.1, max=5.0, value=1.0, step=0.1)
        self.custom_weight_label = Label(text="1.0", color=list(ACCENT), size_hint=(None, 1), width=dp(36), font_size=dp(13))
        self.custom_slider.bind(value=lambda i, v: setattr(self.custom_weight_label, 'text', f"{v:.1f}"))
        weight_row.add_widget(self.custom_slider)
        weight_row.add_widget(self.custom_weight_label)

        # Botón agregar
        btn_add = Button(
            text="+ AGREGAR VARIABLE",
            size_hint_y=None,
            height=dp(36),
            background_color=list(ACCENT_DIM),
            color=list(TEXT_BRIGHT),
            font_size=dp(12)
        )
        btn_add.bind(on_press=self._add_custom_variable)

        custom_box.add_widget(self.custom_name)
        custom_box.add_widget(weight_row)
        custom_box.add_widget(btn_add)
        left.add_widget(custom_box)

        # Botón simular
        btn_sim = Button(
            text="▶  SIMULAR RANKING",
            size_hint_y=None,
            height=dp(48),
            background_color=list(ACCENT),
            color=(0, 0, 0, 1),
            font_size=dp(15),
            bold=True
        )
        btn_sim.bind(on_press=self._run_simulation)
        left.add_widget(btn_sim)

        self.add_widget(left)

    # ── PANEL DERECHO: resultados ──
    def _build_right_panel(self):
        right = BoxLayout(orientation='vertical', size_hint=(0.55, 1), spacing=dp(8))

        right.add_widget(Label(
            text="RANKING  //  RESULTADOS",
            font_size=dp(14),
            color=list(ACCENT),
            size_hint_y=None,
            height=dp(36),
            halign='left'
        ))

        self.results_scroll = ScrollView(size_hint=(1, 1))
        self.results_list = GridLayout(
            cols=1,
            spacing=dp(3),
            size_hint_y=None,
            padding=[0, dp(4)]
        )
        self.results_list.bind(minimum_height=self.results_list.setter('height'))

        # Placeholder inicial
        self.results_list.add_widget(Label(
            text="Configura las variables\ny presiona SIMULAR",
            color=TEXT_DIM,
            font_size=dp(13),
            halign='center'
        ))

        self.results_scroll.add_widget(self.results_list)
        right.add_widget(self.results_scroll)
        self.add_widget(right)

    # ── INICIALIZAR MOTOR ──
    def _init_engine(self):
        for var_def in DEFAULT_VARIABLES:
            row = VariableRow(
                var_name=var_def["name"],
                description=var_def["description"],
                default_weight=var_def["weight"]
            )
            self.var_rows[var_def["name"]] = row
            self.var_list.add_widget(row)

        self.engine.load_data()

    # ── AGREGAR VARIABLE CUSTOM ──
    def _add_custom_variable(self, *args):
        name = self.custom_name.text.strip().replace(" ", "_")
        if not name:
            self._show_popup("Error", "Ingresa un nombre para la variable.")
            return
        if name in self.var_rows:
            self._show_popup("Error", f"La variable '{name}' ya existe.")
            return

        weight = self.custom_slider.value
        row = VariableRow(var_name=name, description="Variable personalizada", default_weight=weight)
        self.var_rows[name] = row
        self.var_list.add_widget(row)
        self.custom_name.text = ""

    # ── CORRER SIMULACIÓN ──
    def _run_simulation(self, *args):
        # Resetear motor
        self.engine = FootballAnalysisEngine()
        self.engine.load_data()

        # Registrar variables activas
        active_count = 0
        for var_def in DEFAULT_VARIABLES:
            name = var_def["name"]
            row  = self.var_rows.get(name)
            if row and row.is_active:
                self.engine.register_variable(Variable(
                    name=name,
                    description=var_def["description"],
                    category="General",
                    data_type=DataType.FOOTBALL,
                    source_type=SourceType.DIRECT,
                    direction=var_def["direction"],
                    default_weight=row.weight
                ))
                self.engine.set_variable_weight(name, row.weight)
                active_count += 1

        # Variables custom
        for name, row in self.var_rows.items():
            if name not in [v["name"] for v in DEFAULT_VARIABLES] and row.is_active:
                self.engine.register_variable(Variable(
                    name=name,
                    description="Variable personalizada",
                    category="Custom",
                    data_type=DataType.FOOTBALL,
                    source_type=SourceType.USER_DEFINED,
                    direction=Direction.MAXIMIZE,
                    default_weight=row.weight
                ))
                active_count += 1

        if active_count == 0:
            self._show_popup("Atención", "Activa al menos una variable.")
            return

        ranking = self.engine.rank_all_teams()

        # Limpiar resultados anteriores
        self.results_list.clear_widgets()

        for pos, (country, score) in enumerate(ranking, 1):
            self.results_list.add_widget(ResultRow(pos, country, score))

    # ── POPUP ──
    def _show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        content.add_widget(Label(text=message, color=TEXT_BRIGHT, font_size=dp(13)))
        btn = Button(text="OK", size_hint_y=None, height=dp(36), background_color=list(ACCENT_DIM))
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.3))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
class SharpLabApp(App):
    def build(self):
        self.title = "Sharp Lab — Simulador Mundial 2026"
        return SharpLabDashboard()


if __name__ == "__main__":
    SharpLabApp().run()
