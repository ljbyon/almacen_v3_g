import streamlit as st

st.title("🔍 Debug de Secrets en Streamlit Cloud")

# ─────────────────────────────────────────────────────────────
# Test 1: Ver todos los secrets disponibles
# ─────────────────────────────────────────────────────────────
st.subheader("1. 🔍 Secrets Disponibles")

try:
    # Mostrar todas las keys disponibles en secrets
    available_keys = list(st.secrets.keys())
    st.success(f"✅ Secrets encontrados: {len(available_keys)}")
    st.write("**Keys disponibles:**")
    for key in available_keys:
        st.write(f"  - `{key}`")
    
    if not available_keys:
        st.error("❌ NO se encontraron secrets")
        st.error("🔧 **Acción requerida**: Configurar secrets en Streamlit Cloud")
        
except Exception as e:
    st.error(f"❌ Error accediendo secrets: {str(e)}")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Test 2: Verificar secrets específicos que necesitamos
# ─────────────────────────────────────────────────────────────
st.subheader("2. 🎯 Secrets Específicos Requeridos")

required_secrets = [
    "google_service_account",
    "GOOGLE_SHEET_NAME", 
    "GOOGLE_SHEET_ID",
    "EMAIL_HOST",
    "EMAIL_USER"
]

missing_secrets = []
found_secrets = []

for secret_key in required_secrets:
    try:
        if secret_key in st.secrets:
            found_secrets.append(secret_key)
            
            # Mostrar valor (censurado para seguridad)
            value = st.secrets[secret_key]
            if isinstance(value, str) and len(value) > 20:
                display_value = value[:10] + "..." + value[-5:]
            else:
                display_value = str(value)
            
            st.success(f"✅ `{secret_key}`: {display_value}")
        else:
            missing_secrets.append(secret_key)
            st.error(f"❌ `{secret_key}`: **FALTA**")
            
    except Exception as e:
        st.error(f"❌ Error accediendo `{secret_key}`: {str(e)}")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Test 3: Verificar estructura de google_service_account
# ─────────────────────────────────────────────────────────────
st.subheader("3. 🔧 Estructura Google Service Account")

try:
    if "google_service_account" in st.secrets:
        gsa = st.secrets["google_service_account"]
        st.success("✅ google_service_account encontrado")
        
        # Verificar keys requeridas
        required_gsa_keys = [
            "type", "project_id", "private_key_id", "private_key", 
            "client_email", "client_id", "auth_uri", "token_uri"
        ]
        
        st.write("**Keys en google_service_account:**")
        for key in required_gsa_keys:
            if key in gsa:
                if key == "private_key":
                    # Mostrar solo el inicio y final de la private key
                    pk = str(gsa[key])
                    if pk.startswith("-----BEGIN"):
                        display_pk = pk[:30] + "..." + pk[-30:]
                    else:
                        display_pk = "**Key presente pero formato incorrecto**"
                    st.success(f"  ✅ `{key}`: {display_pk}")
                else:
                    st.success(f"  ✅ `{key}`: {gsa[key]}")
            else:
                st.error(f"  ❌ `{key}`: **FALTA**")
    else:
        st.error("❌ google_service_account NO encontrado")
        
except Exception as e:
    st.error(f"❌ Error verificando google_service_account: {str(e)}")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Test 4: Formato correcto para Streamlit Cloud
# ─────────────────────────────────────────────────────────────
st.subheader("4. 📋 Formato Correcto para Streamlit Cloud")

if missing_secrets:
    st.error("❌ **Problema encontrado**: Faltan configuraciones")
    
    st.write("**🔧 Copia EXACTAMENTE esto en Streamlit Cloud → Settings → Secrets:**")
    
    # Generar configuración corregida
    correct_config = '''[google_service_account]
type = "service_account"
project_id = "dismac-almacen-app"
private_key_id = "93fd6ef1c409dda5a84881d4b84dd336e398b1d4"
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC1ijdu4l+Grw01
DV9JZnzXpug/EuWifpD6q+bZX5p3gnTtcZ5TgKVuApdSmEO863NVDJ3Vec8mr/8r
IA7VkvyQHeOA2coGSTdnF5flutaIT2lZoMDF82ml5pi4qmWtbGkMCFLMeVYHwAbo
dPasTGMF0iDoafPPtF0Lkmbh7+zbdpE4gr6ZJhUNOSxmKkuI8vjIT7HPN7Igkv9U
A52tQRPSijAl2Czg6ftjnRLJ2TKz8uEJ7y5S9IdJoJEBLn5HM3pbfjm/1kgBP1RG
MKbfphepEyeEMIToY/6j2sIDBKzt5XYeCS17uohVJXS/X6C9lRsIpvZjgeavXYsW
mcaVinEvAgMBAAECggEACKXm8h9SkaXxKR/T9DkvpU5MLgUGb3E8EtTxkFVflGXg
kBcjhbLRLqZs8wBR6cQFoH2TX0IIPj2QGEvUqRPxeCQUXGUDnL0MKJsVH1qBMckm
qaBgzo1D8SVFDTcA1PwfHPWgjCETmhbpvVUlExwoc3SJIMk7Vh+vdweoYwb8749n
k1pFepqBcnNNxATuMtf+SrAwlOoAiJ3yTczPPvEvuW/z9w2DbnX/R8HnFh8muV0F
7vI6ipMQk+ssY4607cbo4sUqfHMykXMXLhmFz5zTxpcjHu51CZlTFzcDq/iNNw8l
zm9ev4OGgPVX9OtwyDpIfcRzNleXwIg1wltW+xlqwQKBgQD+86pm93sYgZHCnBCX
5HaDvc5aEoEb8D9K22FOIkN+S3xLEjqQsNu8o2nM7w3C3zexKCgEdtBwUthKqIDy
NDB4coN5zotEJmyr0/4k7YX7pSQQ0gzOKQzrM1KxaawzBXutS6EOFNVB0QL9Y0JH
Oy1gF1/PkcBbPYtzMUS8mwdR0QKBgQC2SUkat3sYWMDQq94nHYAi0orqGKr89uN0
iHNSWet9XmjMZQBL/r1AaS9Eimqb53KYBdgY5v9CgbVjzlaWscZGKMUvABQoC47g
G4yMrTG1Ep5s8+/kqX+w1TeiJd+DSaJK5/U6OZwhk7oWvmYGY9B3NRh+/CpU0r8L
tqqzMBtS/wKBgBCEjOe65PjDfEQVhGWy4ZLLe1EOndrHh/I7oGRFiAXoshbTCYRS
UQo5tCMY4dVcTOlnZqBTalG8rFK59BC9HN7Q3H/Jx/AUZToEtBSEZwfUvS9xzG6W
7kVWv+bKp+NuWYLywW5+HwrylbUA90xSIzB0kzqJgOLoa958tK1bhe/hAoGAVghC
o4RjaXtCDXqAT+/BcS3zeEcKNHgFpBNeckiUN0hep9EnkbZ59bNvJqc5Z7mVwSBI
/H/Ri78SMDfLcDYZQTWu0t7zpG7IEQePjzmS00YlVYDQARjqdjg7mKDNW/ZdzYKq
n79e7A3/7woPtwZW9lwt4oj7JauNlWayK/4Rd1sCgYEAouN4X81Vctt9h0RD21sQ
6o0kkhjE6L+X0R78op3GTsL3a1qXMsZDuLg2/+8s8ldZw7AF+2qyAsMNesduk6R4
cfD5OUxGTBLmhExQPLADg8m3U9joOutCrMPi1dkP5ZeC6QH3wcaGaJFd+HPYhaxP
UFP5NyHztyz4Ces48krHwUI=
-----END PRIVATE KEY-----"""
client_email = "almacen-app@dismac-almacen-app.iam.gserviceaccount.com"
client_id = "118445961711454389844"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/almacen-app%40dismac-almacen-app.iam.gserviceaccount.com"

GOOGLE_SHEET_NAME = "almacen_app_v3"
GOOGLE_SHEET_ID = "1j73PBe9OxpBN4X9CzK3pcCRN5vLyFuDDNfCfYAF3grQ"

EMAIL_HOST = "mail.dismac.com.bo"
EMAIL_PORT = 587
EMAIL_USER = "ljbyon@dismac.com.bo"
EMAIL_PASSWORD = "Dismac010324*"'''
    
    st.code(correct_config, language="toml")
    
    st.warning("**⚠️ IMPORTANTE**: Nota que uso comillas triples `\"\"\"` para la private_key")
    st.info("📋 **Pasos**: Streamlit Cloud → Tu App → ⋮ → Settings → Secrets → Pegar → Save")

else:
    st.success("🎉 **¡Todos los secrets están configurados correctamente!**")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Test 5: Información de entorno
# ─────────────────────────────────────────────────────────────
st.subheader("5. 🌍 Información del Entorno")

import os
import sys

st.write(f"**Python Version**: {sys.version}")
st.write(f"**Streamlit Version**: {st.__version__}")
st.write(f"**Environment**: {'Streamlit Cloud' if 'STREAMLIT_CLOUD' in os.environ else 'Local'}")
st.write(f"**Current Directory**: {os.getcwd()}")

# Variables de entorno relevantes
env_vars = ["STREAMLIT_CLOUD", "HOME", "USER"]
st.write("**Environment Variables**:")
for var in env_vars:
    value = os.environ.get(var, "Not set")
    st.write(f"  - `{var}`: {value}")