from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
import random


class MetricaCampo(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 5
        self.padding = [0, 5, 0, 5]
        self.size_hint_y = None
        self.height = 160

        self.nombre_input = TextInput(
            hint_text="Nombre de la métrica (ej: Goles a favor)",
            size_hint_y=None,
            height=40
        )
        self.nombre_input.bind(text=self.al_escribir_nombre)
        self.add_widget(self.nombre_input)

        vals_layout = BoxLayout(orientation='horizontal', spacing=5,
                                size_hint_y=None, height=40)
        self.valor_equipo1 = TextInput(
            hint_text="Valor Equipo 1",
            input_filter='float',
            size_hint_x=0.5
        )
        self.valor_equipo2 = TextInput(
            hint_text="Valor Equipo 2",
            input_filter='float',
            size_hint_x=0.5
        )
        vals_layout.add_widget(self.valor_equipo1)
        vals_layout.add_widget(self.valor_equipo2)
        self.add_widget(vals_layout)

        self.peso_label = Label(
            text="Peso: 50%",
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=25
        )
        self.add_widget(self.peso_label)

        self.peso_slider = Slider(min=0, max=100, value=50, step=1,
                                  size_hint_y=None, height=35)
        self.peso_slider.bind(value=self.actualizar_peso)
        self.add_widget(self.peso_slider)

    def al_escribir_nombre(self, instance, valor):
        if valor.strip() != "" and self.parent:
            if hasattr(self.parent, 'agregar_nueva_metrica'):
                self.parent.agregar_nueva_metrica()

    def actualizar_peso(self, instance, valor):
        self.peso_label.text = f"Peso: {int(valor)}%"

    def obtener_datos(self):
        nombre = self.nombre_input.text.strip()
        if not nombre:
            return None
        try:
            v1 = float(self.valor_equipo1.text) if self.valor_equipo1.text.strip() else None
            v2 = float(self.valor_equipo2.text) if self.valor_equipo2.text.strip() else None
        except ValueError:
            return None
        if v1 is None or v2 is None:
            return None
        return {
            'nombre': nombre,
            'valor1': v1,
            'valor2': v2,
            'peso': self.peso_slider.value / 100.0
        }


class SimuladorPartidos(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [10, 10, 10, 10]

        with self.canvas.before:
            Color(0.07, 0.07, 0.07, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._actualizar_fondo, pos=self._actualizar_fondo)

        self.add_widget(Label(
            text="SIMULADOR DE PARTIDOS",
            font_size=22,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=45
        ))

        equipos_layout = BoxLayout(orientation='horizontal', spacing=10,
                                   size_hint_y=None, height=45)
        self.equipo1 = TextInput(
            hint_text="Equipo 1",
            multiline=False,
            size_hint_x=0.5
        )
        self.equipo2 = TextInput(
            hint_text="Equipo 2",
            multiline=False,
            size_hint_x=0.5
        )
        equipos_layout.add_widget(self.equipo1)
        equipos_layout.add_widget(self.equipo2)
        self.add_widget(equipos_layout)

        scroll = ScrollView(size_hint_y=0.55)
        self.metricas_contenedor = GridLayout(
            cols=1,
            spacing=8,
            size_hint_y=None
        )
        self.metricas_contenedor.bind(
            minimum_height=self.metricas_contenedor.setter('height')
        )
        scroll.add_widget(self.metricas_contenedor)
        self.add_widget(scroll)

        self.metricas_contenedor.agregar_nueva_metrica = self.agregar_nueva_metrica
        self.agregar_nueva_metrica()

        sim_layout = BoxLayout(orientation='horizontal', spacing=10,
                               size_hint_y=None, height=45)
        sim_layout.add_widget(Label(
            text="Simulaciones:",
            color=(0.8, 0.8, 0.8, 1),
            size_hint_x=0.5
        ))
        self.simulaciones_input = TextInput(
            text="1000",
            input_filter='int',
            multiline=False,
            size_hint_x=0.5
        )
        sim_layout.add_widget(self.simulaciones_input)
        self.add_widget(sim_layout)

        self.boton_ejecutar = Button(
            text="EJECUTAR SIMULACIÓN",
            background_color=(0.15, 0.45, 0.15, 1),
            size_hint_y=None,
            height=50
        )
        self.boton_ejecutar.bind(on_press=self.simular)
        self.add_widget(self.boton_ejecutar)

        self.resultado_label = Label(
            text="Los resultados aparecerán aquí...",
            color=(0.8, 0.8, 0.8, 1),
            font_size=14,
            size_hint_y=None,
            height=120,
            halign='left',
            valign='top'
        )
        self.resultado_label.bind(
            size=self.resultado_label.setter('text_size')
        )
        self.add_widget(self.resultado_label)

    def _actualizar_fondo(self, instance, value):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def agregar_nueva_metrica(self, *args):
        hijos = self.metricas_contenedor.children
        if hijos:
            ultimo = hijos[0]
            if hasattr(ultimo, 'nombre_input') and \
               ultimo.nombre_input.text.strip() == "":
                return
        self.metricas_contenedor.add_widget(MetricaCampo())

    def simular(self, instance):
        metricas = []
        for hijo in reversed(self.metricas_contenedor.children):
            datos = hijo.obtener_datos()
            if datos:
                metricas.append(datos)

        if not metricas:
            self.resultado_label.text = (
                "⚠ Agrega al menos una métrica con nombre "
                "y valores numéricos en ambos campos."
            )
            return

        try:
            num_sim = int(self.simulaciones_input.text)
            if num_sim <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self.resultado_label.text = "⚠ Ingresa un número válido de simulaciones."
            return

        total_peso = sum(m['peso'] for m in metricas)
        if total_peso == 0:
            self.resultado_label.text = (
                "⚠ Todas las métricas tienen peso 0%. "
                "Sube el potenciómetro en al menos una."
            )
            return

        # Ventaja acumulada ponderada por diferencia normalizada
        ventaja = 0.0
        for m in metricas:
            if m['peso'] == 0:
                continue
            rango = abs(m['valor1'] - m['valor2'])
            if rango == 0:
                continue  # Empate en esta métrica, no aporta
            diferencia_norm = (m['valor1'] - m['valor2']) / rango  # -1 o +1
            ventaja += diferencia_norm * m['peso']

        ventaja /= total_peso  # rango final [-1, +1]

        # Monte Carlo
        gana1 = gana2 = empate = 0
        for _ in range(num_sim):
            ruido = random.uniform(-1.0, 1.0)
            resultado = ventaja + ruido * 0.6
            if abs(resultado) < 0.08:
                empate += 1
            elif resultado > 0:
                gana1 += 1
            else:
                gana2 += 1

        eq1 = self.equipo1.text.strip() or "Equipo 1"
        eq2 = self.equipo2.text.strip() or "Equipo 2"
        p1 = (gana1 / num_sim) * 100
        p2 = (gana2 / num_sim) * 100
        pe = (empate / num_sim) * 100

        self.resultado_label.text = (
            f"RESULTADOS ({num_sim:,} simulaciones):\n"
            f"  {eq1}: {p1:.1f}%  ({gana1} veces)\n"
            f"  {eq2}: {p2:.1f}%  ({gana2} veces)\n"
            f"  Empate: {pe:.1f}%  ({empate} veces)"
        )


class SimuladorApp(App):
    def build(self):
        return SimuladorPartidos()


if __name__ == "__main__":
    SimuladorApp().run()