#!/usr/bin/env python3
"""
Script para obtener el Location ID real de tu cuenta HighLevel
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_locations():
    """Obtiene información de location de HighLevel"""
    
    token = os.getenv('HIGHLEVEL_ACCESS_TOKEN')
    
    if not token:
        print("❌ Error: HIGHLEVEL_ACCESS_TOKEN no configurado")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Version': '2021-07-28'
    }
    
    # Diferentes endpoints para probar
    endpoints = [
        "https://services.leadconnectorhq.com/locations",
        "https://services.leadconnectorhq.com/locations/",
        "https://services.leadconnectorhq.com/location",
        "https://services.leadconnectorhq.com/contacts/",
        "https://services.leadconnectorhq.com/users/",
        "https://services.leadconnectorhq.com/users/location",
        "https://rest.gohighlevel.com/v1/locations/",
        "https://services.leadconnectorhq.com/oauth/userinfo"
    ]
    
    print("🔍 Probando diferentes endpoints para obtener Location ID...")
    
    for endpoint in endpoints:
        try:
            print(f"\n📍 Probando: {endpoint}")
            
            response = requests.get(endpoint, headers=headers, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Éxito!")
                
                # Buscar cualquier referencia a location ID
                location_id = find_location_id_in_response(data)
                
                if location_id:
                    print(f"🎯 Location ID encontrado: {location_id}")
                    update_env_with_location_id(location_id)
                    return location_id
                else:
                    print(f"🔍 Estructura de respuesta: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    print(f"📄 Muestra de respuesta: {str(data)[:500]}...")
                    
            elif response.status_code == 401:
                print(f"🔐 No autorizado - verifica tu token")
            elif response.status_code == 404:
                print(f"❌ Endpoint no existe")
            else:
                print(f"❌ Error {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🤔 No se pudo encontrar automáticamente el Location ID.")
    print(f"💡 Posibles soluciones:")
    print(f"   1. Busca en tu dashboard de HighLevel en la URL")
    print(f"   2. Ve a Settings → Company → Company Details")
    print(f"   3. El Location ID puede estar en la configuración de la API")

def find_location_id_in_response(data, path=""):
    """Busca recursivamente location ID en la respuesta"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in ['locationid', 'location_id', 'id', 'companyid', 'company_id']:
                if isinstance(value, str) and len(value) > 10:  # IDs suelen ser largos
                    print(f"🔍 Posible Location ID en {path}.{key}: {value}")
                    return value
            elif isinstance(value, (dict, list)):
                result = find_location_id_in_response(value, f"{path}.{key}")
                if result:
                    return result
    elif isinstance(data, list):
        for i, item in enumerate(data):
            result = find_location_id_in_response(item, f"{path}[{i}]")
            if result:
                return result
    return None

def update_env_with_location_id(location_id):
    """Actualiza el archivo .env con el Location ID correcto"""
    try:
        # Leer archivo .env
        env_content = ""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
        
        lines = env_content.split('\n') if env_content else []
        updated_lines = []
        location_id_updated = False
        
        for line in lines:
            if line.startswith('HIGHLEVEL_LOCATION_ID='):
                updated_lines.append(f'HIGHLEVEL_LOCATION_ID={location_id}')
                location_id_updated = True
                print(f"✅ Actualizado HIGHLEVEL_LOCATION_ID a: {location_id}")
            else:
                updated_lines.append(line)
        
        # Si no existía, agregarlo
        if not location_id_updated:
            updated_lines.append(f'HIGHLEVEL_LOCATION_ID={location_id}')
            print(f"✅ Agregado HIGHLEVEL_LOCATION_ID: {location_id}")
        
        # Escribir archivo
        with open('.env', 'w') as f:
            f.write('\n'.join(updated_lines))
            
        print("📁 Archivo .env actualizado correctamente")
        
    except Exception as e:
        print(f"❌ Error al actualizar .env: {e}")

if __name__ == "__main__":
    get_locations()