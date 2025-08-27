"""
Ventana principal de la aplicación de inventario GHL optimizada.
"""
import os
import sys
import tempfile
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    from .excel_generator_xlsx import ExcelGenerator
    from .highlevel_api import HighLevelAPI
except ImportError:
    from excel_generator_xlsx import ExcelGenerator
    from highlevel_api import HighLevelAPI

def get_resource_path():
    """Obtiene la ruta base para recursos, funciona tanto en desarrollo como ejecutable compilado"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller
        return sys._MEIPASS
    elif getattr(sys, 'frozen', False):
        # Otros empaquetadores como Nuitka
        return os.path.dirname(sys.executable)
    else:
        # Script Python normal
        return os.path.dirname(os.path.dirname(__file__))

# Cargar variables de entorno
base_path = get_resource_path()
env_paths = [
    os.path.join(base_path, ".env"),
    os.path.join(os.getcwd(), ".env"),
    ".env"
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break


class TokenCallbackHandler(BaseHTTPRequestHandler):
    """Handler para el callback OAuth2."""

    def __init__(self, token_callback, *args, **kwargs):
        self.token_callback = token_callback
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Maneja la petición GET del callback."""
        if self.path.startswith("/callback"):
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            if "code" in query_params:
                code = query_params["code"][0]
                self.token_callback(code)

                # Respuesta de éxito
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                html = """
                <html>
                <body>
                    <h2>✅ ¡Autorización exitosa!</h2>
                    <p>Ya puedes cerrar esta ventana y volver a la aplicación.</p>
                    <script>setTimeout(function(){ window.close(); }, 3000);</script>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            else:
                self.send_error(400, "No se recibió código de autorización")
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        """Suprimir logs del servidor."""
        pass


class TokenWorker(QThread):
    """Worker thread para obtener el token OAuth2."""

    progress_updated = Signal(str)
    token_received = Signal(dict)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, client_id, client_secret):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_code = None
        self.server = None

    def run(self):
        """Ejecuta el proceso OAuth2."""
        try:
            self.progress_updated.emit("Iniciando servidor local...")

            # Crear handler con callback
            def handler(*args, **kwargs):
                return TokenCallbackHandler(self.handle_auth_code, *args, **kwargs)

            # Iniciar servidor local
            self.server = HTTPServer(("localhost", 8080), handler)

            # Construir URL de autorización
            auth_url = (
                "https://marketplace.gohighlevel.com/oauth/chooselocation"
                "?response_type=code"
                f"&client_id={self.client_id}"
                "&redirect_uri=http://localhost:8080/callback"
                "&scope=locations.readonly products.readonly products.write products/prices.readonly products/prices.write"
            )

            self.progress_updated.emit("Abriendo navegador para autorización...")
            webbrowser.open(auth_url)

            # Esperar callback (timeout 300 segundos)
            self.server.timeout = 300
            self.server.handle_request()

            if self.auth_code:
                self.progress_updated.emit("Intercambiando código por token...")
                token_data = self.exchange_code_for_token()
                if token_data:
                    self.token_received.emit(token_data)
                else:
                    self.error_occurred.emit("Error al obtener token")
            else:
                self.error_occurred.emit("No se recibió código de autorización")

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.server:
                self.server.server_close()
            self.finished.emit()

    def handle_auth_code(self, code):
        """Maneja el código de autorización recibido."""
        self.auth_code = code

    def exchange_code_for_token(self):
        """Intercambia el código por un token de acceso."""
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": self.auth_code,
                "redirect_uri": "http://localhost:8080/callback",
            }

            response = requests.post(
                "https://services.leadconnectorhq.com/oauth/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.error_occurred.emit(f"Error en petición: {e}")
            return None


class InventoryWorker(QThread):
    """Worker thread para obtener datos del inventario."""

    progress_updated = Signal(str)
    data_received = Signal(list)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.limit = 300
        self.offset = 0

    def set_parameters(self, limit: int, offset: int):
        """Configura los parámetros de la consulta."""
        self.limit = limit
        self.offset = offset

    def run(self):
        """Ejecuta la obtención de datos en segundo plano."""
        try:
            self.progress_updated.emit("Conectando con HighLevel API...")

            inventory_data = self.api_client.get_inventory(
                limit=self.limit, offset=self.offset
            )

            self.progress_updated.emit(f"Se obtuvieron {len(inventory_data)} productos")

            formatted_data = self.api_client.format_inventory_data(inventory_data)

            self.progress_updated.emit("Datos formateados correctamente")
            self.data_received.emit(formatted_data)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()


class ExcelWorker(QThread):
    """Worker thread para generar el archivo Excel."""

    progress_updated = Signal(str)
    file_generated = Signal(str)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, inventory_data, output_path=None):
        super().__init__()
        self.inventory_data = inventory_data
        self.output_path = output_path

    def run(self):
        """Genera el archivo Excel en segundo plano."""
        try:
            generator = ExcelGenerator()

            def progress_callback(message):
                self.progress_updated.emit(message)

            file_path = generator.create_report(
                self.inventory_data, self.output_path, progress_callback=progress_callback
            )

            self.progress_updated.emit("Agregando resumen al reporte...")
            generator.add_summary(self.inventory_data)

            self.progress_updated.emit("✅ Archivo Excel generado exitosamente")
            self.file_generated.emit(file_path)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.api_client = None
        self.current_inventory_data = []
        self.inventory_worker = None
        self.excel_worker = None
        self.token_worker = None

        self.init_ui()
        self.init_api()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Inventario GHL - Generador de Reportes")
        self.setGeometry(100, 100, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Título
        title_label = QLabel("Generador de Reportes de Inventario HighLevel")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Panel izquierdo
        left_panel = self.create_config_panel()
        splitter.addWidget(left_panel)

        # Panel derecho
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([350, 550])

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para generar reportes")

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

    def create_config_panel(self) -> QWidget:
        """Crea el panel de configuración."""
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)

        # Configuración OAuth
        oauth_group = QGroupBox("Configuración OAuth")
        oauth_layout = QFormLayout(oauth_group)

        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Client ID de HighLevel")
        oauth_layout.addRow("Client ID:", self.client_id_input)

        self.client_secret_input = QLineEdit()
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        self.client_secret_input.setPlaceholderText("Client Secret de HighLevel")
        oauth_layout.addRow("Client Secret:", self.client_secret_input)

        self.get_token_btn = QPushButton("Obtener Token de Acceso")
        self.get_token_btn.clicked.connect(self.get_access_token)
        oauth_layout.addWidget(self.get_token_btn)

        config_layout.addWidget(oauth_group)

        # Configuración API
        api_group = QGroupBox("Configuración de API")
        api_layout = QFormLayout(api_group)

        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setMinimum(1)
        self.limit_spinbox.setMaximum(300)
        self.limit_spinbox.setValue(300)
        api_layout.addRow("Límite de productos:", self.limit_spinbox)

        self.offset_spinbox = QSpinBox()
        self.offset_spinbox.setMinimum(0)
        self.offset_spinbox.setMaximum(10000)
        self.offset_spinbox.setValue(0)
        api_layout.addRow("Offset:", self.offset_spinbox)

        config_layout.addWidget(api_group)

        # Botones de acción
        buttons_layout = QVBoxLayout()

        self.test_connection_btn = QPushButton("Probar Conexión API")
        self.test_connection_btn.clicked.connect(self.test_api_connection)
        buttons_layout.addWidget(self.test_connection_btn)

        self.fetch_data_btn = QPushButton("Obtener Datos de Inventario")
        self.fetch_data_btn.clicked.connect(self.fetch_inventory_data)
        buttons_layout.addWidget(self.fetch_data_btn)

        self.generate_excel_btn = QPushButton("Generar Reporte Excel")
        self.generate_excel_btn.clicked.connect(self.generate_excel_report)
        self.generate_excel_btn.setEnabled(False)
        buttons_layout.addWidget(self.generate_excel_btn)

        self.open_folder_btn = QPushButton("Abrir Carpeta de Reportes")
        self.open_folder_btn.clicked.connect(self.open_reports_folder)
        buttons_layout.addWidget(self.open_folder_btn)

        config_layout.addLayout(buttons_layout)
        config_layout.addStretch()

        return config_widget

    def create_results_panel(self) -> QWidget:
        """Crea el panel de resultados."""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)

        # Estado de configuración
        status_group = QGroupBox("Estado de Configuración")
        status_layout = QFormLayout(status_group)

        self.token_status_label = QLabel("❌ No configurado")
        status_layout.addRow("Token de acceso:", self.token_status_label)

        self.location_status_label = QLabel("❌ No disponible")
        status_layout.addRow("Location ID:", self.location_status_label)

        results_layout.addWidget(status_group)

        # Información de datos
        info_group = QGroupBox("Información del Inventario")
        info_layout = QFormLayout(info_group)

        self.products_count_label = QLabel("0")
        info_layout.addRow("Total de productos:", self.products_count_label)

        self.total_quantity_label = QLabel("0")
        info_layout.addRow("Cantidad total:", self.total_quantity_label)

        self.last_update_label = QLabel("Nunca")
        info_layout.addRow("Última actualización:", self.last_update_label)

        results_layout.addWidget(info_group)

        # Log de actividades
        log_group = QGroupBox("Log de Actividades")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        results_layout.addWidget(log_group)

        # Vista previa
        preview_group = QGroupBox("Vista Previa de Datos")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)

        results_layout.addWidget(preview_group)

        return results_widget

    def init_api(self):
        """Inicializa el cliente de API."""
        try:
            self.api_client = HighLevelAPI()
            self.log_message("Cliente de API inicializado")
            self.update_status_labels()
        except Exception as e:
            self.log_message(f"Error al inicializar API: {e}", is_error=True)

    def update_status_labels(self):
        """Actualiza las etiquetas de estado."""
        token = os.getenv("HIGHLEVEL_ACCESS_TOKEN")
        location_id = os.getenv("HIGHLEVEL_LOCATION_ID")

        if token:
            self.token_status_label.setText("✅ Configurado")
            self.token_status_label.setStyleSheet("color: green;")
        else:
            self.token_status_label.setText("❌ No configurado")
            self.token_status_label.setStyleSheet("color: red;")

        if location_id:
            self.location_status_label.setText(f"✅ {location_id[:20]}...")
            self.location_status_label.setStyleSheet("color: green;")
        else:
            self.location_status_label.setText("❌ No disponible")
            self.location_status_label.setStyleSheet("color: red;")

    def log_message(self, message: str, is_error: bool = False):
        """Agrega un mensaje al log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "ERROR" if is_error else "INFO"
        formatted_message = f"[{timestamp}] {prefix}: {message}"

        self.log_text.append(formatted_message)

        if not is_error:
            self.status_bar.showMessage(message)

    def get_access_token(self):
        """Obtiene un token de acceso OAuth2."""
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()

        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "Datos Incompletos",
                "Por favor ingresa tanto el Client ID como el Client Secret.",
            )
            return

        # Deshabilitar botón
        self.get_token_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # Crear worker
        self.token_worker = TokenWorker(client_id, client_secret)
        self.token_worker.progress_updated.connect(self.log_message)
        self.token_worker.token_received.connect(self.on_token_received)
        self.token_worker.error_occurred.connect(self.on_token_error)
        self.token_worker.finished.connect(self.on_token_finished)

        self.token_worker.start()

    def on_token_received(self, token_data):
        """Maneja el token recibido."""
        try:
            access_token = token_data.get("access_token")
            location_id = token_data.get("locationId")

            if access_token and location_id:
                # Actualizar archivo .env
                self.update_env_file(access_token, location_id)

                # Reinicializar API client
                self.init_api()

                self.log_message("✅ Token obtenido y guardado exitosamente")
                QMessageBox.information(
                    self, "Éxito", "Token de acceso obtenido y guardado correctamente."
                )

            else:
                self.log_message("Token recibido pero datos incompletos", is_error=True)

        except Exception as e:
            self.log_message(f"Error procesando token: {e}", is_error=True)

    def update_env_file(self, access_token: str, location_id: str):
        """Actualiza el archivo .env con las credenciales."""
        env_content = []
        
        # Obtener ruta del archivo .env (preferir directorio de trabajo actual)
        env_paths = [
            os.path.join(os.getcwd(), ".env"),
            os.path.join(get_resource_path(), ".env"),
            ".env"
        ]
        
        # Usar el primer path que exista o el de trabajo actual como fallback
        env_path = env_paths[0]
        for path in env_paths:
            if os.path.exists(path):
                env_path = path
                break

        # Leer archivo existente si existe
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                env_content = f.readlines()

        # Variables a actualizar
        updates = {
            "HIGHLEVEL_ACCESS_TOKEN": access_token,
            "HIGHLEVEL_LOCATION_ID": location_id,
            "HIGHLEVEL_API_VERSION": "2021-07-28",
            "API_LIMIT": "300",
            "API_OFFSET": "0",
        }

        # Actualizar líneas existentes
        updated_lines = []
        updated_keys = set()

        for line in env_content:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key = line.split("=")[0].strip()
                if key in updates:
                    updated_lines.append(f"{key}={updates[key]}")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Agregar nuevas variables
        for key, value in updates.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}")

        # Escribir archivo
        with open(env_path, "w") as f:
            f.write("\n".join(updated_lines))

        # Recargar variables de entorno
        load_dotenv(env_path, override=True)
        
        # También recargar desde las ubicaciones estándar
        for reload_path in env_paths:
            if os.path.exists(reload_path):
                load_dotenv(reload_path, override=True)

    def on_token_error(self, error_message):
        """Maneja errores en la obtención de token."""
        self.log_message(f"Error obteniendo token: {error_message}", is_error=True)
        QMessageBox.critical(self, "Error", f"Error al obtener token:\\n{error_message}")

    def on_token_finished(self):
        """Se ejecuta cuando termina la obtención de token."""
        self.get_token_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def test_api_connection(self):
        """Prueba la conexión con la API."""
        if not self.api_client:
            self.log_message("Cliente de API no disponible", is_error=True)
            return

        self.log_message("Probando conexión con HighLevel API...")
        result = self.api_client.test_connection()

        if result["success"]:
            self.log_message(f"✓ {result['message']}")
            QMessageBox.information(self, "Conexión Exitosa", result["message"])
        else:
            self.log_message(result["message"], is_error=True)
            QMessageBox.warning(self, "Error de Conexión", result["message"])

    def fetch_inventory_data(self):
        """Obtiene los datos del inventario."""
        if not self.api_client:
            self.log_message("Cliente de API no disponible", is_error=True)
            return

        self.fetch_data_btn.setEnabled(False)
        self.generate_excel_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.inventory_worker = InventoryWorker(self.api_client)
        self.inventory_worker.set_parameters(
            self.limit_spinbox.value(), self.offset_spinbox.value()
        )

        self.inventory_worker.progress_updated.connect(self.log_message)
        self.inventory_worker.data_received.connect(self.on_data_received)
        self.inventory_worker.error_occurred.connect(self.on_data_error)
        self.inventory_worker.finished.connect(self.on_fetch_finished)

        self.inventory_worker.start()

    def on_data_received(self, inventory_data):
        """Maneja los datos recibidos del inventario."""
        self.current_inventory_data = inventory_data

        total_products = len(inventory_data)
        total_quantity = sum(item.get("Cantidad disponible", 0) for item in inventory_data)

        self.products_count_label.setText(str(total_products))
        self.total_quantity_label.setText(str(total_quantity))
        self.last_update_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        # Vista previa
        preview_text = "Vista previa de los primeros 5 productos:\\n\\n"
        for i, item in enumerate(inventory_data[:5], 1):
            preview_text += f"{i}. {item['Nombre']} - {item['Nombre de producto']} "
            preview_text += f"(Cantidad: {item['Cantidad disponible']})\\n"

        if len(inventory_data) > 5:
            preview_text += f"\\n... y {len(inventory_data) - 5} productos más"

        self.preview_text.setText(preview_text)
        self.generate_excel_btn.setEnabled(True)
        self.log_message(f"✓ Datos cargados: {total_products} productos")

    def on_data_error(self, error_message):
        """Maneja errores en la obtención de datos."""
        self.log_message(f"Error: {error_message}", is_error=True)
        QMessageBox.critical(self, "Error", f"Error al obtener datos:\\n{error_message}")

    def on_fetch_finished(self):
        """Se ejecuta cuando termina la obtención de datos."""
        self.fetch_data_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def generate_excel_report(self):
        """Genera el reporte de Excel."""
        if not self.current_inventory_data:
            QMessageBox.warning(
                self, "Sin Datos", "No hay datos de inventario para generar el reporte."
            )
            return

        default_name = f"inventario_ghl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Reporte de Excel",
            default_name,
            "Archivos Excel (*.xlsx);;Todos los archivos (*)",
        )

        if not file_path:
            return

        self.generate_excel_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.excel_worker = ExcelWorker(self.current_inventory_data, file_path)
        self.excel_worker.progress_updated.connect(self.log_message)
        self.excel_worker.file_generated.connect(self.on_excel_generated)
        self.excel_worker.error_occurred.connect(self.on_excel_error)
        self.excel_worker.finished.connect(self.on_excel_finished)

        self.excel_worker.start()

    def on_excel_generated(self, file_path):
        """Se ejecuta cuando se genera el archivo Excel."""
        self.log_message(f"✓ Reporte Excel generado: {file_path}")

        reply = QMessageBox.question(
            self,
            "Reporte Generado",
            f"El reporte se ha generado exitosamente:\\n{file_path}\\n\\n¿Deseas abrirlo ahora?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            os.startfile(file_path)

    def on_excel_error(self, error_message):
        """Maneja errores en la generación de Excel."""
        self.log_message(f"Error Excel: {error_message}", is_error=True)
        QMessageBox.critical(self, "Error", f"Error al generar Excel:\\n{error_message}")

    def on_excel_finished(self):
        """Se ejecuta cuando termina la generación de Excel."""
        self.generate_excel_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def open_reports_folder(self):
        """Abre la carpeta donde se guardan los reportes."""
        current_dir = os.getcwd()
        os.startfile(current_dir)


def main():
    """Función principal."""
    app = QApplication(sys.argv)
    app.setApplicationName("Inventario GHL")
    app.setApplicationVersion("2.0.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()