"""
Módulo para la conexión con la API de HighLevel.
"""
import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


class HighLevelAPI:
    """Cliente para la API de HighLevel."""

    def __init__(self):
        self.access_token = os.getenv("HIGHLEVEL_ACCESS_TOKEN")
        self.location_id = os.getenv("HIGHLEVEL_LOCATION_ID")
        self.api_version = os.getenv("HIGHLEVEL_API_VERSION", "2021-07-28")
        self.base_url = "https://services.leadconnectorhq.com"

        if not self.access_token:
            raise ValueError("HIGHLEVEL_ACCESS_TOKEN no está configurado")

        if not self.location_id:
            raise ValueError("HIGHLEVEL_LOCATION_ID no está configurado")
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtiene los headers para las peticiones"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Version': self.api_version
        }
    
    def get_inventory(self, limit: int = 300, offset: int = 0) -> List[Dict]:
        """
        Obtiene el inventario de HighLevel
        
        Args:
            limit: Límite de resultados (máximo 300)
            offset: Offset para paginación
            
        Returns:
            Lista de items del inventario
            
        Raises:
            requests.RequestException: Error en la petición HTTP
            ValueError: Error en la respuesta de la API
        """
        # Probar diferentes endpoints posibles
        endpoints = [
            f"{self.base_url}/products/inventory",
            f"{self.base_url}/products",
            f"{self.base_url}/locations/{self.location_id}/products"
        ]
        
        params = {
            'limit': min(limit, 300),
            'offset': offset,
            'locationId': self.location_id  # Cambiar a locationId en lugar de altId/altType
        }
        
        # También probar con altId/altType por si funciona
        alt_params = {
            'limit': min(limit, 300),
            'offset': offset,
            'altId': self.location_id,
            'altType': 'location'
        }
        
        for endpoint in endpoints:
            for param_set in [params, alt_params]:
                try:
                    print(f"🔍 Probando: {endpoint} con params: {param_set}")
                    
                    response = requests.get(
                        endpoint,
                        headers=self._get_headers(),
                        params=param_set,
                        timeout=30
                    )
                    
                    print(f"📊 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Éxito con {endpoint}")
                        
                        # Diferentes formatos de respuesta posibles
                        if 'inventory' in data:
                            return data['inventory']
                        elif 'products' in data:
                            return data['products']
                        elif isinstance(data, list):
                            return data
                        else:
                            print(f"🔍 Estructura de respuesta: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                            return []
                    else:
                        print(f"❌ Error {response.status_code}: {response.text[:200]}")
                        
                except requests.RequestException as e:
                    print(f"❌ Error en {endpoint}: {e}")
                    continue
        
        # Si llegamos aquí, ningún endpoint funcionó
        raise requests.RequestException(f"No se pudo conectar a ningún endpoint de inventario. Verifica tu token y location ID.")
    
    def format_inventory_data(self, inventory_items: List[Dict]) -> List[Dict]:
        """
        Formatea los datos del inventario para el reporte
        
        Args:
            inventory_items: Lista de items del inventario de la API
            
        Returns:
            Lista de items formateados para el reporte
        """
        formatted_items = []
        
        for item in inventory_items:
            formatted_item = {
                'Nombre': item.get('name', ''),
                'Nombre de producto': item.get('productName', ''),
                'Cantidad disponible': item.get('availableQuantity', 0),
                'Imagen': item.get('image', '')
            }
            formatted_items.append(formatted_item)
        
        return formatted_items
    
    def test_connection(self) -> Dict[str, any]:
        """
        Prueba la conexión con la API
        
        Returns:
            Diccionario con el resultado de la prueba
        """
        try:
            # Hacemos una petición pequeña para probar la conexión
            inventory = self.get_inventory(limit=1)
            return {
                'success': True,
                'message': 'Conexión exitosa',
                'items_count': len(inventory)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error de conexión: {str(e)}'
            }