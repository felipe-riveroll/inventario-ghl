"""
Módulo para generar reportes de Excel con XlsxWriter.
"""
from datetime import datetime
from typing import Dict, List, Optional

import xlsxwriter


class ExcelGenerator:
    """Generador de reportes de Excel para inventario usando XlsxWriter"""
    
    def __init__(self):
        self.workbook = None
        self.worksheet = None
    
    def create_report(
        self,
        inventory_data: List[Dict],
        output_path: Optional[str] = None,
        progress_callback=None,
    ) -> str:
        """
        Crea un reporte de Excel con los datos del inventario
        
        Args:
            inventory_data: Lista de items del inventario
            output_path: Ruta donde guardar el archivo (opcional)
            progress_callback: Función callback para reportar progreso
            
        Returns:
            Ruta del archivo generado
        """
        if progress_callback:
            progress_callback("Creando estructura del reporte...")
        
        # Generar nombre de archivo si no se proporciona
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"inventario_ghl_{timestamp}.xlsx"
        
        # Crear workbook
        self.workbook = xlsxwriter.Workbook(output_path)
        today = datetime.now().strftime("%d-%m-%Y")
        self.worksheet = self.workbook.add_worksheet(f'Inventario_{today}')
        
        # Crear formatos
        self._create_formats()
        
        # Crear encabezados
        self._create_headers()
        
        if progress_callback:
            progress_callback("Agregando datos del inventario...")
        
        # Agregar datos
        self._add_data(inventory_data, progress_callback)
        
        if progress_callback:
            progress_callback("Aplicando formato...")
        
        # Ajustar formato final
        self._adjust_formatting()
        
        if progress_callback:
            progress_callback("Guardando archivo...")
        
        # NO cerrar aquí para permitir agregar el resumen después
        # El workbook se cerrará en add_summary()
        
        return output_path
    
    def _create_formats(self):
        """Crea los formatos para el reporte"""
        # Formato para encabezados
        self.header_format = self.workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#366092',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#000000'
        })
        
        # Formato para celdas normales
        self.cell_format = self.workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'valign': 'vcenter'
        })
        
        # Formato para celdas de cantidad (centrado)
        self.quantity_format = self.workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Formato para filas alternadas
        self.alt_row_format = self.workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'bg_color': '#F2F2F2',
            'valign': 'vcenter'
        })
        
        # Formato para cantidad en filas alternadas
        self.alt_quantity_format = self.workbook.add_format({
            'border': 1,
            'border_color': '#000000',
            'bg_color': '#F2F2F2',
            'align': 'center',
            'valign': 'vcenter'
        })
    
    def _create_headers(self):
        """Crea los encabezados de la tabla"""
        headers = ['Nombre', 'Nombre de producto', 'Cantidad disponible', 'Imagen']
        
        # Configurar altura del encabezado (será ajustada por las instrucciones)
        # self.worksheet.set_row(0, 30)  # Se ajustará en _add_instructions()
        
        for col, header in enumerate(headers):
            self.worksheet.write(0, col, header, self.header_format)
    
    def _add_data(self, inventory_data: List[Dict], progress_callback=None):
        """Agrega los datos del inventario a la hoja"""
        total_items = len(inventory_data)
        
        for i, item in enumerate(inventory_data):
            row = i + 1  # Empezar en fila 1 (después del encabezado)
            
            if progress_callback and i % 10 == 0:  # Actualizar cada 10 productos
                progress = f"Procesando producto {i + 1} de {total_items}"
                progress_callback(progress)
            
            # Configurar altura de fila a 100px (aproximadamente 75 puntos)
            self.worksheet.set_row(row, 75)
            
            # Determinar formato (fila alternada o no)
            is_alt_row = row % 2 == 0
            row_format = self.alt_row_format if is_alt_row else self.cell_format
            qty_format = self.alt_quantity_format if is_alt_row else self.quantity_format
            
            # Nombre
            self.worksheet.write(row, 0, item.get('Nombre', ''), row_format)
            
            # Nombre de producto
            self.worksheet.write(row, 1, item.get('Nombre de producto', ''), row_format)
            
            # Cantidad disponible
            cantidad = item.get('Cantidad disponible', 0)
            self.worksheet.write(row, 2, cantidad, qty_format)
            
            # Imagen del producto - solución definitiva: texto + macro VBA
            imagen_url = item.get('Imagen', '')
            if imagen_url and imagen_url.strip():
                # Escribir SOLO como texto para evitar cualquier procesamiento
                formula_text = f'=IMAGEN("{imagen_url}",1)'
                self.worksheet.write_string(row, 3, formula_text, row_format)
                
                # Comentario con instrucciones simplificadas
                comment_text = ('Para activar imágenes:\n'
                              '1. Seleccionar toda la columna D\n'
                              '2. Ctrl+L (Buscar y Reemplazar)\n'
                              '3. Buscar: =IMAGEN   Reemplazar: =IMAGEN\n'
                              '4. Reemplazar todo\n'
                              'O individual: F2 → Enter')
                self.worksheet.write_comment(row, 3, comment_text)
            else:
                self.worksheet.write(row, 3, 'Sin imagen', row_format)
    
    def _adjust_formatting(self):
        """Ajusta el formato final de la hoja"""
        # Ajustar ancho de columnas
        self.worksheet.set_column('A:A', 20)  # Nombre
        self.worksheet.set_column('B:B', 25)  # Nombre de producto
        self.worksheet.set_column('C:C', 18)  # Cantidad disponible
        self.worksheet.set_column('D:D', 20)  # Imagen
        
        # Congelar primera fila (encabezados)
        self.worksheet.freeze_panes(1, 0)
        
        # Agregar instrucciones en una celda visible
        self._add_instructions()
    
    def add_summary(self, inventory_data: List[Dict]):
        """
        Agrega un resumen al final del reporte
        
        Args:
            inventory_data: Lista de items del inventario
        """
        if not self.worksheet:
            return
        
        # Encontrar la última fila con datos
        last_row = len(inventory_data) + 1
        summary_row = last_row + 2
        
        # Crear formato para el resumen
        summary_format = self.workbook.add_format({
            'bold': True,
            'border': 1,
            'bg_color': '#E6E6E6'
        })
        
        # Total de productos
        total_productos = len(inventory_data)
        self.worksheet.write(summary_row, 0, "Total de productos:", summary_format)
        self.worksheet.write(summary_row, 1, total_productos, summary_format)
        
        # Total de cantidad disponible
        total_cantidad = sum(item.get('Cantidad disponible', 0) for item in inventory_data)
        self.worksheet.write(summary_row + 1, 0, "Total cantidad disponible:", summary_format)
        self.worksheet.write(summary_row + 1, 1, total_cantidad, summary_format)
        
        # Fecha de generación
        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.worksheet.write(summary_row + 2, 0, "Fecha de generación:", summary_format)
        self.worksheet.write(summary_row + 2, 1, fecha_generacion, summary_format)
        
        # Cerrar workbook después de agregar el resumen
        if self.workbook:
            self.workbook.close()
    
    def _add_instructions(self):
        """Agrega instrucciones visibles en el archivo"""
        # Crear formato para instrucciones
        instruction_format = self.workbook.add_format({
            'bold': True,
            'font_color': 'red',
            'bg_color': '#FFFF99',
            'border': 2,
            'border_color': 'red',
            'text_wrap': True,
            'valign': 'top'
        })
        
        # Agregar instrucciones en la columna F
        instructions = (
            "📋 INSTRUCCIONES PARA ACTIVAR IMÁGENES:\n\n"
            "1️⃣ Selecciona toda la columna D (clic en header 'D')\n"
            "2️⃣ Presiona Ctrl+L (Buscar y Reemplazar)\n"
            "3️⃣ En 'Buscar': =IMAGEN\n"
            "4️⃣ En 'Reemplazar': =IMAGEN (exactamente igual)\n"
            "5️⃣ Clic en 'Reemplazar todo'\n"
            "6️⃣ ¡Listo! Las imágenes aparecerán automáticamente\n\n"
            "💡 Tip: También puedes hacer F2 + Enter en cada celda individual\n"
            "📝 Nota: En Excel español usa Ctrl+L, no Ctrl+H"
        )
        
        self.worksheet.write(0, 5, instructions, instruction_format)
        self.worksheet.set_column('F:F', 40)  # Ancho para instrucciones
        self.worksheet.set_row(0, 150)  # Altura para que se vea completo