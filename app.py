import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# Configurar página
st.set_page_config(
    page_title="Google Sheets Test - Dismac", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧪 Google Sheets Connection Test")
st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Función para configurar Google Sheets
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def setup_google_sheets():
    """Configurar conexión a Google Sheets"""
    try:
        # Obtener credenciales de Streamlit secrets
        credentials_info = dict(st.secrets["google_service_account"])
        
        # Configurar scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Crear credenciales
        credentials = Credentials.from_service_account_info(
            credentials_info, 
            scopes=scopes
        )
        
        # Crear cliente gspread
        gc = gspread.authorize(credentials)
        
        return gc, None
        
    except Exception as e:
        return None, str(e)

# ─────────────────────────────────────────────────────────────
# Test 1: Verificar Configuración
# ─────────────────────────────────────────────────────────────
def test_configuration():
    """Verificar que la configuración esté correcta"""
    st.subheader("📋 Test 1: Verificar Configuración")
    
    try:
        # Verificar secrets
        required_keys = [
            "google_service_account",
            "GOOGLE_SHEET_NAME", 
            "GOOGLE_SHEET_ID",
            "EMAIL_HOST",
            "EMAIL_USER"
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in st.secrets:
                missing_keys.append(key)
        
        if missing_keys:
            st.error(f"❌ Faltan configuraciones: {missing_keys}")
            return False
        
        # Mostrar configuración
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Configuración encontrada:")
            st.info(f"📊 Sheet Name: {st.secrets['GOOGLE_SHEET_NAME']}")
            st.info(f"🆔 Sheet ID: {st.secrets['GOOGLE_SHEET_ID']}")
            st.info(f"📧 Email: {st.secrets['EMAIL_USER']}")
        
        with col2:
            st.success("✅ Service Account:")
            st.info(f"📧 Client Email: {st.secrets['google_service_account']['client_email']}")
            st.info(f"🔧 Project ID: {st.secrets['google_service_account']['project_id']}")
            st.info(f"🔑 Client ID: {st.secrets['google_service_account']['client_id']}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error verificando configuración: {str(e)}")
        return False

# ─────────────────────────────────────────────────────────────
# Test 2: Conectar a Google Sheets
# ─────────────────────────────────────────────────────────────
def test_connection():
    """Probar conexión básica a Google Sheets"""
    st.subheader("🔗 Test 2: Conexión a Google Sheets")
    
    try:
        gc, error = setup_google_sheets()
        
        if error:
            st.error(f"❌ Error creando cliente: {error}")
            return None
        
        st.success("✅ Cliente Google Sheets creado exitosamente!")
        return gc
        
    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")
        
        # Diagnóstico de errores comunes
        error_str = str(e).lower()
        if "authentication" in error_str:
            st.error("🔧 **Error de Autenticación**: Verificar credenciales del service account")
        elif "permission" in error_str:
            st.error("🔧 **Error de Permisos**: El service account necesita acceso al sheet")
        elif "quota" in error_str:
            st.error("🔧 **Error de Cuota**: Límite de API excedido")
        
        return None

# ─────────────────────────────────────────────────────────────
# Test 3: Acceder al Spreadsheet
# ─────────────────────────────────────────────────────────────
def test_spreadsheet_access(gc):
    """Probar acceso al spreadsheet específico"""
    st.subheader("📊 Test 3: Acceso al Spreadsheet")
    
    if not gc:
        st.warning("⚠️ Primero debe pasar el test de conexión")
        return None
    
    try:
        # Intentar abrir por ID
        sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        spreadsheet = gc.open_by_key(sheet_id)
        
        st.success(f"✅ Spreadsheet abierto: **{spreadsheet.title}**")
        
        # Información del spreadsheet
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"🆔 ID: {spreadsheet.id}")
            st.info(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
        
        with col2:
            # Listar hojas
            worksheets = spreadsheet.worksheets()
            st.info(f"📋 Hojas encontradas ({len(worksheets)}):")
            for ws in worksheets:
                st.write(f"  - {ws.title} ({ws.row_count} filas, {ws.col_count} columnas)")
        
        return spreadsheet
        
    except gspread.SpreadsheetNotFound:
        st.error("❌ **Spreadsheet no encontrado**")
        st.error("🔧 Verificar que:")
        st.error("  - El GOOGLE_SHEET_ID es correcto")
        st.error("  - El spreadsheet existe")
        st.error("  - El service account tiene acceso")
        return None
        
    except gspread.APIError as e:
        st.error(f"❌ **Error de API**: {str(e)}")
        return None
        
    except Exception as e:
        st.error(f"❌ **Error inesperado**: {str(e)}")
        return None

# ─────────────────────────────────────────────────────────────
# Test 4: Leer Datos
# ─────────────────────────────────────────────────────────────
def test_read_data(spreadsheet):
    """Probar lectura de datos"""
    st.subheader("📖 Test 4: Lectura de Datos")
    
    if not spreadsheet:
        st.warning("⚠️ Primero debe pasar el test de acceso al spreadsheet")
        return
    
    try:
        worksheets = spreadsheet.worksheets()
        
        for ws in worksheets:
            with st.expander(f"📋 Hoja: {ws.title}"):
                try:
                    # Obtener todos los datos
                    data = ws.get_all_records()
                    
                    if data:
                        df = pd.DataFrame(data)
                        st.success(f"✅ Datos leídos: {len(df)} filas, {len(df.columns)} columnas")
                        st.dataframe(df.head(5), use_container_width=True)
                        
                        # Mostrar columnas
                        st.info(f"📋 Columnas: {list(df.columns)}")
                    else:
                        st.warning("⚠️ Hoja vacía o sin headers")
                        
                        # Mostrar datos raw
                        all_values = ws.get_all_values()
                        if all_values:
                            st.info(f"📊 Datos raw: {len(all_values)} filas")
                            st.write("Primeras 3 filas:")
                            for i, row in enumerate(all_values[:3]):
                                st.write(f"  Fila {i+1}: {row}")
                        else:
                            st.warning("📊 Hoja completamente vacía")
                            
                except Exception as e:
                    st.error(f"❌ Error leyendo {ws.title}: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ Error general leyendo datos: {str(e)}")

# ─────────────────────────────────────────────────────────────
# Test 5: Escribir Datos
# ─────────────────────────────────────────────────────────────
def test_write_data(spreadsheet):
    """Probar escritura de datos"""
    st.subheader("✏️ Test 5: Escritura de Datos")
    
    if not spreadsheet:
        st.warning("⚠️ Primero debe pasar el test de acceso al spreadsheet")
        return
    
    if st.button("🧪 Probar Escritura"):
        try:
            # Buscar o crear hoja de prueba
            try:
                test_sheet = spreadsheet.worksheet("test_sheet")
                st.info("📋 Usando hoja existente: test_sheet")
            except gspread.WorksheetNotFound:
                # Crear nueva hoja
                test_sheet = spreadsheet.add_worksheet("test_sheet", rows=10, cols=5)
                st.success("✅ Hoja 'test_sheet' creada")
            
            # Datos de prueba
            test_data = [
                ["Fecha", "Hora", "Usuario", "Accion", "Timestamp"],
                [datetime.now().strftime("%Y-%m-%d"), 
                 datetime.now().strftime("%H:%M:%S"), 
                 "Test User", 
                 "Prueba Conexion", 
                 str(int(time.time()))]
            ]
            
            # Escribir headers
            test_sheet.update("A1:E1", [test_data[0]])
            st.success("✅ Headers escritos")
            
            # Agregar fila de datos
            test_sheet.append_row(test_data[1])
            st.success("✅ Datos agregados")
            
            # Leer de vuelta para verificar
            written_data = test_sheet.get_all_records()
            if written_data:
                st.success(f"✅ Verificación: {len(written_data)} registros encontrados")
                st.dataframe(pd.DataFrame(written_data), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error escribiendo datos: {str(e)}")
            
            # Diagnóstico
            error_str = str(e).lower()
            if "permission" in error_str:
                st.error("🔧 **Error de Permisos**: Verificar que el service account tiene permisos de 'Editor'")
            elif "quota" in error_str:
                st.error("🔧 **Cuota Excedida**: Esperar antes de hacer más requests")

# ─────────────────────────────────────────────────────────────
# Test 6: Verificar Hojas Necesarias
# ─────────────────────────────────────────────────────────────
def test_required_sheets(spreadsheet):
    """Verificar que existen las hojas necesarias para la aplicación"""
    st.subheader("📋 Test 6: Hojas Requeridas para la Aplicación")
    
    if not spreadsheet:
        st.warning("⚠️ Primero debe pasar el test de acceso al spreadsheet")
        return
    
    required_sheets = [
        "proveedor_credencial",
        "proveedor_reservas", 
        "proveedor_gestion"
    ]
    
    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
    
    st.info(f"📊 Hojas existentes: {existing_sheets}")
    
    for sheet_name in required_sheets:
        if sheet_name in existing_sheets:
            st.success(f"✅ {sheet_name} - Existe")
        else:
            st.error(f"❌ {sheet_name} - **FALTA**")
            
            if st.button(f"Crear {sheet_name}", key=f"create_{sheet_name}"):
                try:
                    # Crear hoja con estructura básica
                    new_sheet = spreadsheet.add_worksheet(sheet_name, rows=100, cols=10)
                    
                    # Agregar headers según el tipo de hoja
                    if sheet_name == "proveedor_credencial":
                        headers = ["usuario", "password", "Email", "cc"]
                    elif sheet_name == "proveedor_reservas":
                        headers = ["Fecha", "Hora", "Proveedor", "Numero_de_bultos", "Orden_de_compra"]
                    elif sheet_name == "proveedor_gestion":
                        headers = ["Orden_de_compra", "Proveedor", "Numero_de_bultos", "Hora_llegada", 
                                 "Hora_inicio_atencion", "Hora_fin_atencion", "Tiempo_espera", 
                                 "Tiempo_atencion", "Tiempo_total", "Tiempo_retraso", 
                                 "numero_de_semana", "hora_de_reserva"]
                    
                    # Escribir headers
                    new_sheet.update(f"A1:{chr(65+len(headers)-1)}1", [headers])
                    
                    st.success(f"✅ Hoja {sheet_name} creada con headers!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error creando {sheet_name}: {str(e)}")

# ─────────────────────────────────────────────────────────────
# Sidebar con información
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔧 Información del Test")
    
    st.markdown("""
    **Tests que se ejecutan:**
    1. ✅ Verificar configuración
    2. 🔗 Conexión a Google Sheets
    3. 📊 Acceso al spreadsheet
    4. 📖 Lectura de datos
    5. ✏️ Escritura de datos
    6. 📋 Hojas requeridas
    
    **Si todo pasa:**
    ✅ Tu configuración está correcta
    ✅ Puedes migrar de SharePoint
    ✅ No más errores AADSTS80002
    """)
    
    if st.button("🔄 Limpiar Cache"):
        st.cache_resource.clear()
        st.success("Cache limpiado!")

# ─────────────────────────────────────────────────────────────
# Ejecutar Tests
# ─────────────────────────────────────────────────────────────
def main():
    """Función principal que ejecuta todos los tests"""
    
    # Test 1: Configuración
    config_ok = test_configuration()
    st.markdown("---")
    
    # Test 2: Conexión
    if config_ok:
        gc = test_connection()
    else:
        st.stop()
    
    st.markdown("---")
    
    # Test 3: Acceso al Spreadsheet
    if gc:
        spreadsheet = test_spreadsheet_access(gc)
    else:
        st.stop()
    
    st.markdown("---")
    
    # Test 4: Lectura de datos
    if spreadsheet:
        test_read_data(spreadsheet)
    
    st.markdown("---")
    
    # Test 5: Escritura de datos
    if spreadsheet:
        test_write_data(spreadsheet)
    
    st.markdown("---")
    
    # Test 6: Hojas requeridas
    if spreadsheet:
        test_required_sheets(spreadsheet)
    
    # Resultado final
    if spreadsheet:
        st.markdown("---")
        st.success("🎉 **¡Todos los tests básicos pasaron!**")
        st.success("✅ Tu configuración Google Sheets está lista")
        st.info("🚀 Próximo paso: Migrar tu código de SharePoint a Google Sheets")

if __name__ == "__main__":
    main()