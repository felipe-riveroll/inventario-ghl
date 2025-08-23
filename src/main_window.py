"""
Ventana principal de la aplicación de inventario GHL
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QTextEdit, QProgressBar, QFileDialog,
    QGroupBox, QFormLayout, QLineEdit, QSpinBox, QMessageBox,
    QStatusBar, QSplitter
)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont, QIcon

from highlevel_api import HighLevelAPI
from excel_generator_xlsx import ExcelGenerator


class InventoryWorker(QThread):
    """Worker thread para obtener datos del inventario"""
    
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
        """Configura los parámetros de la consulta"""
        self.limit = limit
        self.offset = offset
    
    def run(self):
        """Ejecuta la obtención de datos en segundo plano"""
        try:
            self.progress_updated.emit("Conectando con HighLevel API...")
            
            # Obtener datos del inventario
            inventory_data = self.api_client.get_inventory(
                limit=self.limit, 
                offset=self.offset
            )
            
            self.progress_updated.emit(f"Se obtuvieron {len(inventory_data)} productos")
            
            # Formatear datos
            formatted_data = self.api_client.format_inventory_data(inventory_data)
            
            self.progress_updated.emit("Datos formateados correctamente")
            self.data_received.emit(formatted_data)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()


class ExcelWorker(QThread):
    """Worker thread para generar el archivo Excel"""
    
    progress_updated = Signal(str)
    file_generated = Signal(str)
    error_occurred = Signal(str)
    finished = Signal()
    
    def __init__(self, inventory_data, output_path=None):
        super().__init__()
        self.inventory_data = inventory_data
        self.output_path = output_path
    
    def run(self):
        """Genera el archivo Excel en segundo plano"""
        try:
            generator = ExcelGenerator()
            
            # Crear callback de progreso
            def progress_callback(message):
                self.progress_updated.emit(message)
            
            # Generar reporte con callback de progreso
            file_path = generator.create_report(
                self.inventory_data, 
                self.output_path,
                progress_callback=progress_callback
            )
            
            # Agregar resumen
            self.progress_updated.emit("Agregando resumen al reporte...")
            generator.add_summary(self.inventory_data)
            
            # XlsxWriter se cierra automáticamente al crear el archivo
            self.progress_updated.emit("✅ Archivo Excel generado exitosamente")
            self.file_generated.emit(file_path)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.api_client = None
        self.current_inventory_data = []
        self.inventory_worker = None
        self.excel_worker = None
        
        self.init_ui()
        self.init_api()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Inventario GHL - Generador de Reportes")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Título
        title_label = QLabel("Generador de Reportes de Inventario HighLevel")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Splitter para dividir la interfaz
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo - Configuración
        config_widget = self.create_config_panel()
        splitter.addWidget(config_widget)
        
        # Panel derecho - Resultados y log
        results_widget = self.create_results_panel()
        splitter.addWidget(results_widget)
        
        # Establecer tamaños del splitter
        splitter.setSizes([300, 500])
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para generar reportes")
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def create_config_panel(self) -> QWidget:
        """Crea el panel de configuración"""
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        
        # Grupo de configuración de API
        api_group = QGroupBox("Configuración de API")
        api_layout = QFormLayout(api_group)
        
        # Campos de configuración
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
        
        self.test_connection_btn = QPushButton("Probar Conexión")
        self.test_connection_btn.clicked.connect(self.test_api_connection)
        buttons_layout.addWidget(self.test_connection_btn)
        
        self.fetch_data_btn = QPushButton("Obtener Datos de Inventario")
        self.fetch_data_btn.clicked.connect(self.fetch_inventory_data)
        buttons_layout.addWidget(self.fetch_data_btn)
        
        self.generate_excel_btn = QPushButton("Generar Reporte Excel")
        self.generate_excel_btn.clicked.connect(self.generate_excel_report)
        self.generate_excel_btn.setEnabled(False)
        buttons_layout.addWidget(self.generate_excel_btn)
        
        # Botón para abrir carpeta de reportes
        self.open_folder_btn = QPushButton("Abrir Carpeta de Reportes")
        self.open_folder_btn.clicked.connect(self.open_reports_folder)
        buttons_layout.addWidget(self.open_folder_btn)
        
        config_layout.addLayout(buttons_layout)
        config_layout.addStretch()
        
        return config_widget
    
    def create_results_panel(self) -> QWidget:
        """Crea el panel de resultados"""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
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
        
        # Vista previa de datos
        preview_group = QGroupBox("Vista Previa de Datos")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        results_layout.addWidget(preview_group)
        
        return results_widget
    
    def init_api(self):
        """Inicializa el cliente de API"""
        try:
            self.api_client = HighLevelAPI()
            self.log_message("Cliente de API inicializado correctamente")
        except Exception as e:
            self.log_message(f"Error al inicializar API: {e}", is_error=True)
            QMessageBox.critical(
                self, 
                "Error de Configuración",
                f"No se pudo inicializar la API de HighLevel:\\n{e}\\n\\n"
                "Verifica tu archivo .env con las credenciales."
            )
    
    def log_message(self, message: str, is_error: bool = False):
        """Agrega un mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "ERROR" if is_error else "INFO"
        formatted_message = f"[{timestamp}] {prefix}: {message}"
        
        self.log_text.append(formatted_message)
        
        # Actualizar status bar
        if not is_error:
            self.status_bar.showMessage(message)
    
    def test_api_connection(self):
        """Prueba la conexión con la API"""
        if not self.api_client:
            self.log_message("Cliente de API no disponible", is_error=True)
            return
        
        self.log_message("Probando conexión con HighLevel API...")
        result = self.api_client.test_connection()
        
        if result['success']:
            self.log_message(f"✓ {result['message']}")
            QMessageBox.information(self, "Conexión Exitosa", result['message'])
        else:
            self.log_message(result['message'], is_error=True)
            QMessageBox.warning(self, "Error de Conexión", result['message'])
    
    def fetch_inventory_data(self):
        """Obtiene los datos del inventario"""
        if not self.api_client:
            self.log_message("Cliente de API no disponible", is_error=True)
            return
        
        # Deshabilitar botones
        self.fetch_data_btn.setEnabled(False)
        self.generate_excel_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Progreso indeterminado
        
        # Crear y configurar worker
        self.inventory_worker = InventoryWorker(self.api_client)
        self.inventory_worker.set_parameters(
            self.limit_spinbox.value(),
            self.offset_spinbox.value()
        )
        
        # Conectar señales
        self.inventory_worker.progress_updated.connect(self.log_message)
        self.inventory_worker.data_received.connect(self.on_data_received)
        self.inventory_worker.error_occurred.connect(self.on_data_error)
        self.inventory_worker.finished.connect(self.on_fetch_finished)
        
        # Iniciar worker
        self.inventory_worker.start()
    
    def on_data_received(self, inventory_data):
        """Maneja los datos recibidos del inventario"""
        self.current_inventory_data = inventory_data
        
        # Actualizar información
        total_products = len(inventory_data)
        total_quantity = sum(item.get('Cantidad disponible', 0) for item in inventory_data)
        
        self.products_count_label.setText(str(total_products))
        self.total_quantity_label.setText(str(total_quantity))
        self.last_update_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        # Mostrar vista previa
        preview_text = "Vista previa de los primeros 5 productos:\\n\\n"
        for i, item in enumerate(inventory_data[:5], 1):
            preview_text += f"{i}. {item['Nombre']} - {item['Nombre de producto']} "
            preview_text += f"(Cantidad: {item['Cantidad disponible']})\\n"
        
        if len(inventory_data) > 5:
            preview_text += f"\\n... y {len(inventory_data) - 5} productos más"
        
        self.preview_text.setText(preview_text)
        
        # Habilitar generación de Excel
        self.generate_excel_btn.setEnabled(True)
        
        self.log_message(f"✓ Datos del inventario cargados: {total_products} productos")
    
    def on_data_error(self, error_message):
        """Maneja errores en la obtención de datos"""
        self.log_message(f"Error al obtener datos: {error_message}", is_error=True)
        QMessageBox.critical(self, "Error", f"Error al obtener datos del inventario:\\n{error_message}")
    
    def on_fetch_finished(self):
        """Se ejecuta cuando termina la obtención de datos"""
        self.fetch_data_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def generate_excel_report(self):
        """Genera el reporte de Excel"""
        if not self.current_inventory_data:
            QMessageBox.warning(self, "Sin Datos", "No hay datos de inventario para generar el reporte.")
            return
        
        # Seleccionar ubicación del archivo
        default_name = f"inventario_ghl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Reporte de Excel",
            default_name,
            "Archivos Excel (*.xlsx);;Todos los archivos (*)"
        )
        
        if not file_path:
            return
        
        # Deshabilitar botón
        self.generate_excel_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # Crear worker para Excel
        self.excel_worker = ExcelWorker(self.current_inventory_data, file_path)
        
        # Conectar señales
        self.excel_worker.progress_updated.connect(self.log_message)
        self.excel_worker.file_generated.connect(self.on_excel_generated)
        self.excel_worker.error_occurred.connect(self.on_excel_error)
        self.excel_worker.finished.connect(self.on_excel_finished)
        
        # Iniciar worker
        self.excel_worker.start()
    
    def on_excel_generated(self, file_path):
        """Se ejecuta cuando se genera el archivo Excel"""
        self.log_message(f"✓ Reporte Excel generado: {file_path}")
        
        # Preguntar si abrir el archivo
        reply = QMessageBox.question(
            self,
            "Reporte Generado",
            f"El reporte se ha generado exitosamente:\\n{file_path}\\n\\n¿Deseas abrirlo ahora?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            os.startfile(file_path)  # Windows
    
    def on_excel_error(self, error_message):
        """Maneja errores en la generación de Excel"""
        self.log_message(f"Error al generar Excel: {error_message}", is_error=True)
        QMessageBox.critical(self, "Error", f"Error al generar el reporte Excel:\\n{error_message}")
    
    def on_excel_finished(self):
        """Se ejecuta cuando termina la generación de Excel"""
        self.generate_excel_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def open_reports_folder(self):
        """Abre la carpeta donde se guardan los reportes"""
        current_dir = os.getcwd()
        os.startfile(current_dir)  # Windows


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    app.setApplicationName("Inventario GHL")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())