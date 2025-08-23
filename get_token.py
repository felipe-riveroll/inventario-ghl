#!/usr/bin/env python3
"""
Script helper para obtener el token de acceso de HighLevel mediante OAuth2
"""
import os
import sys
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from urllib.parse import parse_qs, urlparse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración OAuth desde .env
CLIENT_ID = os.getenv('HIGHLEVEL_CLIENT_ID')
CLIENT_SECRET = os.getenv('HIGHLEVEL_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "locations.readonly products.readonly products.write products/prices.readonly products/prices.write"

# URLs de HighLevel
AUTH_URL = "https://marketplace.gohighlevel.com/oauth/chooselocation"
TOKEN_URL = "https://services.leadconnectorhq.com/oauth/token"

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            # Parsear el código de autorización
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                code = query_params['code'][0]
                print(f"✓ Código de autorización recibido: {code}")
                
                # Intercambiar código por token
                token_data = exchange_code_for_token(code)
                
                if token_data:
                    # Mostrar resultado
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    html = f"""
                    <html>
                    <body>
                        <h2>✓ Token obtenido exitosamente!</h2>
                        <p><strong>Access Token:</strong></p>
                        <textarea rows="3" cols="80" readonly>{token_data.get('access_token', '')}</textarea>
                        
                        <p><strong>Location ID:</strong> {token_data.get('locationId', '')}</p>
                        
                        <p>Copia el Access Token y Location ID a tu archivo .env</p>
                        
                        <p>Puedes cerrar esta ventana.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                    
                    # Guardar en archivo
                    save_token_to_file(token_data)
                else:
                    self.send_error(400, "Error al obtener el token")
            else:
                self.send_error(400, "No se recibió código de autorización")
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        # Suprimir logs del servidor
        pass

def exchange_code_for_token(code):
    """Intercambia el código de autorización por un token de acceso"""
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        
        token_data = response.json()
        print(f"✓ Token obtenido exitosamente")
        return token_data
        
    except requests.RequestException as e:
        print(f"✗ Error al obtener token: {e}")
        return None

def save_token_to_file(token_data):
    """Actualiza el archivo .env con el token obtenido"""
    try:
        # Leer archivo .env existente
        env_content = ""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
        
        # Actualizar o agregar valores
        lines = env_content.split('\n') if env_content else []
        
        # Variables a actualizar
        updates = {
            'HIGHLEVEL_ACCESS_TOKEN': token_data.get('access_token', ''),
            'HIGHLEVEL_LOCATION_ID': token_data.get('locationId', ''),
        }
        
        # Actualizar líneas existentes
        updated_lines = []
        updated_keys = set()
        
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                if key in updates:
                    updated_lines.append(f"{key}={updates[key]}")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Agregar nuevas variables si no existían
        for key, value in updates.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}")
        
        # Escribir archivo actualizado
        with open('.env', 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✓ Token y Location ID actualizados en .env")
        
    except Exception as e:
        print(f"✗ Error al actualizar archivo .env: {e}")

def main():
    # Verificar configuración
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: CLIENT_ID y CLIENT_SECRET no están configurados en .env")
        print("\n📝 Pasos para configurar:")
        print("1. Ve a HighLevel → Settings → Integrations → My Apps")
        print("2. Crea una nueva aplicación")
        print("3. Configura redirect URI: http://localhost:8080/callback")
        print("4. Copia CLIENT_ID y CLIENT_SECRET a tu archivo .env:")
        print("   HIGHLEVEL_CLIENT_ID=tu_client_id")
        print("   HIGHLEVEL_CLIENT_SECRET=tu_client_secret")
        return
    
    # Construir URL de autorización
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    
    print("🚀 Iniciando proceso de autorización OAuth2...")
    print(f"📱 Abriendo navegador en: {auth_url}")
    print("🔄 Esperando callback en http://localhost:8080/callback...")
    
    # Iniciar servidor local
    try:
        server = HTTPServer(('localhost', 8080), CallbackHandler)
        
        # Abrir navegador
        webbrowser.open(auth_url)
        
        # Manejar una sola petición
        server.handle_request()
        
        print("✅ Proceso completado")
        
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()