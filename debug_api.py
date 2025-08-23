#!/usr/bin/env python3
"""
Script para debuggear la conexión con HighLevel API
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def debug_api_connection():
    """Debug de la conexión con HighLevel API"""
    
    # Obtener credenciales
    token = os.getenv('HIGHLEVEL_ACCESS_TOKEN')
    location_id = os.getenv('HIGHLEVEL_LOCATION_ID')
    api_version = os.getenv('HIGHLEVEL_API_VERSION', '2021-07-28')
    
    print("🔍 Verificando credenciales...")
    print(f"Token presente: {'✓' if token else '✗'}")
    print(f"Token (primeros 10 chars): {token[:10] if token else 'N/A'}...")
    print(f"Location ID: {location_id}")
    print(f"API Version: {api_version}")
    
    if not token:
        print("\n❌ Error: HIGHLEVEL_ACCESS_TOKEN no configurado")
        return
    
    if not location_id:
        print("\n❌ Error: HIGHLEVEL_LOCATION_ID no configurado")
        return
    
    # Headers
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Version': api_version
    }
    
    # Parámetros
    params = {
        'limit': 1,
        'offset': 0,
        'altId': location_id,
        'altType': 'location'
    }
    
    # URL
    url = "https://services.leadconnectorhq.com/products/inventory"
    
    print(f"\n🌐 Haciendo petición a:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"\n📊 Respuesta:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito! Datos recibidos:")
            print(f"Keys en respuesta: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
            if 'inventory' in data:
                print(f"Items en inventario: {len(data['inventory'])}")
            else:
                print(f"Respuesta completa: {data}")
        else:
            print(f"❌ Error {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Excepción: {e}")

def test_alternative_endpoints():
    """Prueba endpoints alternativos"""
    token = os.getenv('HIGHLEVEL_ACCESS_TOKEN')
    location_id = os.getenv('HIGHLEVEL_LOCATION_ID')
    
    if not token or not location_id:
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Version': '2021-07-28'
    }
    
    # Endpoints alternativos para probar
    endpoints = [
        f"https://services.leadconnectorhq.com/locations/{location_id}",
        "https://services.leadconnectorhq.com/locations/",
        f"https://services.leadconnectorhq.com/products/?locationId={location_id}",
    ]
    
    print(f"\n🧪 Probando endpoints alternativos...")
    
    for endpoint in endpoints:
        try:
            print(f"\n📍 Probando: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Funciona!")
            else:
                print(f"❌ Error: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Excepción: {e}")

if __name__ == "__main__":
    debug_api_connection()
    test_alternative_endpoints()