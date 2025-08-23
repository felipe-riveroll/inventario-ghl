#!/usr/bin/env python3
"""
Script para probar diferentes combinaciones de scopes
"""

# Diferentes combinaciones de scopes para probar
SCOPE_OPTIONS = [
    "locations.readonly products.readonly locations/customValues.readonly locations.write products.write",
    "locations.readonly products.readonly opportunities.readonly",
    "locations.readonly contacts.readonly opportunities.readonly",
    "locations.readonly locations.write contacts.readonly",
    "companies.readonly locations.readonly products.readonly",
    "locations.readonly surveys.readonly funnels.readonly",
    "locations.readonly workflows.readonly",
    # Scope más amplio
    "locations.readonly locations.write products.readonly products.write contacts.readonly opportunities.readonly workflows.readonly"
]

print("🔍 Scopes disponibles para probar:")
for i, scope in enumerate(SCOPE_OPTIONS, 1):
    print(f"{i}. {scope}")

print("\n💡 Instrucciones:")
print("1. Copia uno de estos scopes")
print("2. Pégalo en get_token.py reemplazando la línea SCOPE = ...")
print("3. Ejecuta: uv run python get_token.py")
print("4. Prueba la aplicación")

print("\n🎯 Nota: También verifica que tu app en HighLevel tenga estos scopes habilitados:")
print("   - Ve a Settings → Integrations → My Apps → Tu App")
print("   - En la sección Scopes, marca todos los que necesites")
print("   - Guarda y regenera el token")