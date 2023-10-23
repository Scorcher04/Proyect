from kivy.config import Config
Config.set('modules', 'inspector', 'enable')
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.uix.widget import Widget
import serial
import time
from functools import partial
from kivymd.uix.label import MDLabel
from PIL import Image as PILImage
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from plyer import bluetooth


# Intentar establecer la conexión con el Arduino
try:
    ser = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)  # Espera para que la conexión serial se inicialice
    ARDUINO_CONNECTED = True
except:
    ARDUINO_CONNECTED = False

current_temperature = "N/A"

def resize_image(input_path, output_path, size):
    with PILImage.open(input_path) as image:
        image_resized = image.resize(size, PILImage.LANCZOS)
        image_resized.save(output_path)

# Ruta completa al archivo APP.png
path_to_image = 'C:\\Users\\Roberto\\Documents\\Pyton\\APP\\APP.png'
path_to_resized_image = 'C:\\Users\\Roberto\\Documents\\Pyton\\APP\\APP_resized.png'
resize_image(path_to_image, path_to_resized_image, (400, 400))

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=[50, 50, 50, 50])
        self.image = Image(source=path_to_resized_image, size_hint=(1, 0.5), allow_stretch=True)
        layout.add_widget(self.image)
        
        self.monitoring_button = Button(text="Monitoreo", size_hint=(1, 0.1), background_color=(0.6, 0.8, 1, 1), color=(0, 0, 0, 1), bold=True, border=[2,2,2,2])
        self.monitoring_button.bind(on_press=self.go_to_monitoring)
        layout.add_widget(self.monitoring_button)
        
        self.maintenance_button = Button(text="Tipos de Mantenimiento", size_hint=(1, 0.1), background_color=(0.6, 0.8, 1, 1), color=(0, 0, 0, 1), bold=True, border=[2,2,2,2])
        self.maintenance_button.bind(on_press=self.go_to_maintenance)
        layout.add_widget(self.maintenance_button)
        
        self.exit_button = Button(text="Salir", size_hint=(1, 0.1), background_color=(0.6, 0.8, 1, 1), color=(0, 0, 0, 1), bold=True, border=[2,2,2,2])
        self.exit_button.bind(on_press=self.exit_app)
        layout.add_widget(self.exit_button)
        
        self.add_widget(layout)

    def go_to_monitoring(self, instance):
        self.manager.current = 'monitoring'

    def go_to_maintenance(self, instance):
        self.manager.current = 'maintenance'

    def exit_app(self, instance):
        MDApp.get_running_app().stop()


class MaintenanceScreen(Screen):
    def __init__(self, **kwargs):
        super(MaintenanceScreen, self).__init__(**kwargs)

        main_layout = GridLayout(rows=4, spacing=5)
        self.add_widget(main_layout)

        vertical_layout = BoxLayout(orientation='vertical', spacing=5)
        main_layout.add_widget(vertical_layout)

        # FUNCIONES PARA AGREGAR LOS ELEMENTOS
        def add_temperature_label():
            temp_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
            temp_label_part = MDLabel(text="Temperatura:", font_style="H5", halign="right", valign="middle", bold=True)
            self.temp_label_value = MDLabel(text="XX°C", font_style="H5", halign="left", valign="middle")
            temp_layout.add_widget(temp_label_part)
            temp_layout.add_widget(self.temp_label_value)
            vertical_layout.add_widget(temp_layout)

        def add_table_headers():
            headers_layout = GridLayout(cols=4, spacing=5, size_hint_y=None, height=50)
            headers = ["Rango de Temperatura (°C)", "Tipo de Mantenimiento", "Descripción de la Temperatura", "Acciones Sugeridas y Explicación"]
            for header in headers:
                headers_layout.add_widget(MDLabel(text=header, font_style="H6", halign="center", valign="middle", bold=True))
            vertical_layout.add_widget(headers_layout)

        # AGREGANDO LOS ELEMENTOS
        add_temperature_label()
        add_table_headers()

        # Layout para los valores de la tabla
        self.values_layout = GridLayout(cols=4, spacing=5)
        vertical_layout.add_widget(self.values_layout)  # Agregamos los valores justo después de los encabezados

        # Datos de la tabla en formato de matriz
        self.data_matrix = [
            ["7°C - 10°C", 
            "Predictivo", 
            "Muy frío (funcionamiento a máxima capacidad o en ambientes muy cálidos)", 
            "- Monitorizar la carga del compresor: Es esencial para prevenir sobrecargas o congelamientos.\n"
            "- Verificar el nivel de refrigerante: Para evitar sobrecargas o congelamientos.\n"
            "- Inspeccionar los conductos y sellos: Para prevenir fugas de aire que afecten el rendimiento."],
            
            ["10°C - 15°C", 
            "Preventivo", 
            "Normalmente frío (funcionamiento estándar para muchos modelos)", 
            "- Limpieza de filtros: Esto garantiza un flujo de aire adecuado y evita que el polvo bloquee el sistema.\n"
            "- Inspeccionar y limpiar las bobinas del evaporador y condensador: Ayuda a mantener un rendimiento óptimo.\n"
            "- Verificar conexiones eléctricas: Para asegurarse de que todo esté conectado correctamente y sin riesgos.\n"
            "- Lubricar motores y rodamientos: Si el equipo lo requiere, para mantener un funcionamiento suave."],

            ["15°C - 20°C", 
            "Predictivo", 
            "Enfriamiento leve (ajustes más altos o ambientes menos calurosos)", 
            "- Comprobar el nivel de refrigerante: Si el equipo no enfría lo suficiente, podría ser necesario recargar.\n"
            "- Inspeccionar posibles fugas en el sistema: Para asegurarse de que el refrigerante no se esté perdiendo.\n"
            "- Verificar el funcionamiento de termostatos y controles: Para asegurarse de que el equipo responde adecuadamente a los ajustes."],

            ["20°C - Temperatura ambiente (puede variar)", 
            "Correctivo", 
            "Funcionamiento mínimo de enfriamiento o cercano al modo \"fan\" o \"ventilador\" donde el aire no se enfría activamente", 
            "- Comprobar el funcionamiento del compresor: Si el equipo no está enfriando adecuadamente, podría ser un problema con el compresor.\n"
            "- Inspeccionar y, si es necesario, limpiar o reemplazar la bobina del evaporador: Para mantener un rendimiento óptimo.\n"
            "- Verificar el sistema eléctrico: Si hay problemas de alimentación, pueden afectar el rendimiento.\n"
            "- Reemplazar el refrigerante: Si parece que se ha agotado o hay una fuga importante."],

            ["Temperatura ambiente y superior", 
            "Correctivo", 
            "Modo \"fan\" o \"ventilador\" activo sin enfriamiento. El aire acondicionado no está enfriando, solo circula el aire", 
            "- Evaluar y, si es necesario, reemplazar el compresor: Si el equipo no está enfriando en absoluto, podría ser necesario un reemplazo.\n"
            "- Realizar una revisión completa: Para detectar y solucionar fugas importantes.\n"
            "- Reemplazar componentes eléctricos dañados: Si hay problemas eléctricos que afectan el funcionamiento.\n"
            "- Considerar reemplazar el equipo: Si su vida útil ha llegado a su fin o las reparaciones son demasiado costosas."]
        ]

        help_layout = BoxLayout(size_hint_y=None, height=80, spacing=10)
        help_button = Button(text="Tipos de Mantenimiento", background_color=(0.6, 0.8, 1, 1), color=(0, 0, 0, 1))
        help_button.bind(on_press=self.show_maintenance_types)
        help_layout.add_widget(help_button)
        main_layout.add_widget(help_layout)

        bottom_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10)
        main_menu_button = Button(text="Menú Principal", size_hint=(0.5, 1), background_color=(0.6, 0.8, 1, 1), color=(0, 0, 0, 1), bold=True)
        main_menu_button.bind(on_press=self.go_to_main_menu)  # Función para regresar al menú principal
        exit_button = Button(text="Salir", size_hint=(0.5, 1), background_color=(0.6, 0.8, 1, 1), color=(0, 0, 0, 1), bold=True)
        exit_button.bind(on_press=self.exit_app)  # Función para salir del programa
        bottom_layout.add_widget(main_menu_button)
        bottom_layout.add_widget(exit_button)
        main_layout.add_widget(bottom_layout)

    def show_maintenance_types(self, instance):
        self.manager.current = 'maintenance_types'


    def go_to_main_menu(self, instance):
        """Función para regresar al menú principal."""
        self.manager.current = 'main_menu'

    def exit_app(self, instance):
        """Función para salir del programa."""
        MDApp.get_running_app().stop()

    def on_enter(self):
        Clock.schedule_interval(self.update_temperature, 1)  # Actualizar cada segundo

    def update_temperature(self, dt):
        # Utilizar la variable global current_temperature
        global current_temperature
        if ARDUINO_CONNECTED:
            temperature_str = ser.readline().decode('utf-8').strip()
            print(f"Datos crudos: {temperature_str}")
            
            try:
                temperature = float(temperature_str)
                current_temperature = f"{temperature} °C"  # Actualiza la variable compartida
                self.temp_label_value.text = current_temperature
                self.update_table_values(temperature)
            except ValueError:
                self.set_na_values()
        else:
            self.set_na_values()
            current_temperature = "N/A"

    def set_na_values(self):
        self.temp_label_value.text = "N/A"


    def update_table_values(self, temperature):
        # Limpia el layout de valores para actualizarlo
        self.values_layout.clear_widgets()

        # Determina qué fila de la matriz usar según la temperatura actual
        row_data = []
        if 7 <= temperature <= 10:
            row_data = self.data_matrix[0]
        elif 10 < temperature <= 15:
            row_data = self.data_matrix[1]
        elif 15 < temperature <= 20:
            row_data = self.data_matrix[2]
        elif 20 < temperature <= 25:
            row_data = self.data_matrix[3]
        else:
            row_data = self.data_matrix[4]


        # Agrega los valores al layout
        for value in row_data:
            self.values_layout.add_widget(MDLabel(text=value, halign="center", valign="middle"))

class MaintenanceTypesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout principal
        main_layout = BoxLayout(orientation='vertical')

        # Parte superior: botones
        top_layout = GridLayout(rows=1, size_hint_y=0.1)
        temp_button = Button(text="TEMPERATURA", on_press=self.show_temperature_table)
        top_layout.add_widget(temp_button)
        main_layout.add_widget(top_layout)

        # Parte central: tabla
        self.table_layout = GridLayout(cols=4, spacing=(10, 200), size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))

        scrollview = ScrollView(size_hint=(1, 0.7), do_scroll_x=False)  # Only vertical scroll
        scrollview.add_widget(self.table_layout)
        main_layout.add_widget(scrollview)



        ## Parte inferior: botón de regresar
        back_button = Button(text="Regresar", size_hint_y=0.1, on_press=self.return_to_previous_screen)
        main_layout.add_widget(back_button)


        self.add_widget(main_layout)

    def show_temperature_table(self, instance):
        # Limpia el layout de la tabla
        self.table_layout.clear_widgets()

        # Muestra los encabezados
        self.add_table_headers()

        # Muestra los datos
        self.add_table_data()

    def add_table_headers(self):
        headers = ["Rango de Temperatura (°C)", "Tipo de Mantenimiento", "Descripción de la Temperatura", "Acciones Sugeridas y Explicación"]
        for header in headers:
            self.table_layout.add_widget(MDLabel(text=header, font_style="H6", halign="center", valign="middle", bold=True, size_hint_y=None, height=75))

    def add_table_data(self): # Nota que esta línea está indentada para estar dentro de la clase
        data_matrix = [
                        ["7°C - 10°C", 
            "Predictivo", 
            "Muy frío (funcionamiento a máxima capacidad o en ambientes muy cálidos)", 
            "- Monitorizar la carga del compresor: Es esencial para prevenir sobrecargas o congelamientos.\n"
            "- Verificar el nivel de refrigerante: Para evitar sobrecargas o congelamientos.\n"
            "- Inspeccionar los conductos y sellos: Para prevenir fugas de aire que afecten el rendimiento."],
            
            ["10°C - 15°C", 
            "Preventivo", 
            "Normalmente frío (funcionamiento estándar para muchos modelos)", 
            "- Limpieza de filtros: Esto garantiza un flujo de aire adecuado y evita que el polvo bloquee el sistema.\n"
            "- Inspeccionar y limpiar las bobinas del evaporador y condensador: Ayuda a mantener un rendimiento óptimo.\n"
            "- Verificar conexiones eléctricas: Para asegurarse de que todo esté conectado correctamente y sin riesgos.\n"
            "- Lubricar motores y rodamientos: Si el equipo lo requiere, para mantener un funcionamiento suave."],

            ["15°C - 20°C", 
            "Predictivo", 
            "Enfriamiento leve (ajustes más altos o ambientes menos calurosos)", 
            "- Comprobar el nivel de refrigerante: Si el equipo no enfría lo suficiente, podría ser necesario recargar.\n"
            "- Inspeccionar posibles fugas en el sistema: Para asegurarse de que el refrigerante no se esté perdiendo.\n"
            "- Verificar el funcionamiento de termostatos y controles: Para asegurarse de que el equipo responde adecuadamente a los ajustes."],

            ["20°C - Temperatura ambiente (puede variar)", 
            "Correctivo", 
            "Funcionamiento mínimo de enfriamiento o cercano al modo \"fan\" o \"ventilador\" donde el aire no se enfría activamente", 
            "- Comprobar el funcionamiento del compresor: Si el equipo no está enfriando adecuadamente, podría ser un problema con el compresor.\n"
            "- Inspeccionar y, si es necesario, limpiar o reemplazar la bobina del evaporador: Para mantener un rendimiento óptimo.\n"
            "- Verificar el sistema eléctrico: Si hay problemas de alimentación, pueden afectar el rendimiento.\n"
            "- Reemplazar el refrigerante: Si parece que se ha agotado o hay una fuga importante."],

            ["Temperatura ambiente y superior", 
            "Correctivo", 
            "Modo \"fan\" o \"ventilador\" activo sin enfriamiento. El aire acondicionado no está enfriando, solo circula el aire", 
            "- Evaluar y, si es necesario, reemplazar el compresor: Si el equipo no está enfriando en absoluto, podría ser necesario un reemplazo.\n"
            "- Realizar una revisión completa: Para detectar y solucionar fugas importantes.\n"
            "- Reemplazar componentes eléctricos dañados: Si hay problemas eléctricos que afectan el funcionamiento.\n"
            "- Considerar reemplazar el equipo: Si su vida útil ha llegado a su fin o las reparaciones son demasiado costosas."]
        ]

        for row in data_matrix:
            for cell in row:
                self.table_layout.add_widget(MDLabel(text=cell, halign="center", valign="middle", size_hint_y=None, height=70))

        # Agrega los datos de la matriz
        for row in data_matrix:
            for cell in row:
                self.table_layout.add_widget(Label(text=cell))

    def return_to_previous_screen(self, instance):
        self.manager.current = 'maintenance'


class MonitoringScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.main_layout = BoxLayout(orientation='vertical')
        self.content_layout = BoxLayout(orientation='vertical', padding='20dp', spacing='20dp')
        
        # Etiquetas actuales de MonitoringScreen
        self.label_temp = MDLabel(text="Temperatura: -- °C", font_style="H4", halign="center")
        self.content_layout.add_widget(self.label_temp)
        
        self.label_status = MDLabel(text="Estado: ---", font_style="H4", halign="center", theme_text_color="Secondary")
        self.content_layout.add_widget(self.label_status)
        
        self.main_layout.add_widget(self.content_layout)
        
        # Layout para los botones en la parte inferior
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), padding=[50, 10, 50, 50], spacing=20)
        
        self.main_menu_button = Button(text="Menú Principal", size_hint_y=None, height=60, background_color=(0.6, 0.8, 1, 1), color=(0, 0, 0, 1), bold=True, border=[2,2,2,2])
        self.main_menu_button.bind(on_press=self.go_to_main_menu)
        button_layout.add_widget(self.main_menu_button)
        
        self.exit_button = Button(text="Salir", size_hint_y=None, height=60, background_color=(0.6, 0.8, 1, 1), color=(0, 0, 0, 1), bold=True, border=[2,2,2,2])
        self.exit_button.bind(on_press=self.exit_app)
        button_layout.add_widget(self.exit_button)
        
        self.main_layout.add_widget(button_layout)
        
        self.add_widget(self.main_layout)

    def go_to_main_menu(self, instance):
        self.manager.current = 'main_menu'

    def exit_app(self, instance):
        MDApp.get_running_app().stop()

    def on_enter(self):
        Clock.schedule_interval(self.update_temperature, 1)  # Actualizar cada segundo

    def update_temperature(self, dt):
        global current_temperature
        if ARDUINO_CONNECTED:
            temperature_str = ser.readline().decode('utf-8').strip()
            print(f"Datos crudos: {temperature_str}")
            
            try:
                temperature = float(temperature_str)
                current_temperature = f"{temperature} °C"  # Actualiza la variable compartida
                self.label_temp.text = f"Temperatura: {current_temperature}"
                # ... (resto de tu código para actualizar el estado basado en la temperatura)
            except ValueError:
                self.label_temp.text = "Error de lectura"
        else:
            self.label_status.text = "Estado: ---"
            self.label_status.theme_text_color = "Secondary"

class ClasePrincipal(MDApp):
    def build(self):
        self.title = "Mi Aplicación"
        self.theme_cls.primary_palette = "Blue"
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(MonitoringScreen(name='monitoring'))
        sm.add_widget(MaintenanceScreen(name='maintenance'))
        sm.add_widget(MaintenanceTypesScreen(name='maintenance_types'))
        return sm

KV = '''
<MonitoringScreen>:
    # ()
'''
Builder.load_string(KV)

if __name__ == "__main__":
    ClasePrincipal().run()

