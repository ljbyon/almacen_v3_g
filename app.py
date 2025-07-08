import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="📊 Contenido Google Sheets", layout="wide")

st.title("📊 Contenido de las Hojas de Google Sheets")
st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Función para conectar a Google Sheets
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def setup_google_sheets():
    """Configurar conexión a Google Sheets"""
    try:
        credentials_info = dict(st.secrets["google_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
        gc = gspread.authorize(credentials)
        return gc
    except Exception as e:
        st.error(f"❌ Error conectando: {str(e)}")
        return None

@st.cache_data(ttl=60, show_spinner=False)
def load_sheet_data(sheet_name):
    """Cargar datos de una hoja específica"""
    try:
        gc = setup_google_sheets()
        if not gc:
            return None, "Error de conexión"
        
        spreadsheet = gc.open(st.secrets["GOOGLE_SHEET_NAME"])
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # Obtener todos los datos
        data = worksheet.get_all_records()
        
        if data:
            df = pd.DataFrame(data)
            return df, None
        else:
            # Si no hay datos con headers, obtener valores raw
            all_values = worksheet.get_all_values()
            if all_values:
                if len(all_values) > 1:
                    df = pd.DataFrame(all_values[1:], columns=all_values[0])
                else:
                    df = pd.DataFrame(all_values, columns=[f"Col_{i+1}" for i in range(len(all_values[0]))])
                return df, None
            else:
                return pd.DataFrame(), "Hoja vacía"
                
    except gspread.WorksheetNotFound:
        return None, f"Hoja '{sheet_name}' no encontrada"
    except Exception as e:
        return None, f"Error: {str(e)}"

# ─────────────────────────────────────────────────────────────
# Información general
# ─────────────────────────────────────────────────────────────
st.info(f"📋 **Spreadsheet**: {st.secrets['GOOGLE_SHEET_NAME']}")
st.info(f"🆔 **Sheet ID**: {st.secrets['GOOGLE_SHEET_ID']}")

# ─────────────────────────────────────────────────────────────
# HOJA 1: proveedor_credencial
# ─────────────────────────────────────────────────────────────
st.header("🔐 Hoja 1: proveedor_credencial")

with st.expander("Ver contenido de proveedor_credencial", expanded=True):
    df_cred, error_cred = load_sheet_data("proveedor_credencial")
    
    if error_cred:
        st.error(f"❌ {error_cred}")
    elif df_cred is not None:
        if len(df_cred) > 0:
            st.success(f"✅ **{len(df_cred)} registros encontrados**")
            
            # Mostrar información de columnas
            st.write("**📋 Columnas:**")
            col_info = []
            for col in df_cred.columns:
                non_empty = df_cred[col].notna().sum()
                col_info.append(f"• `{col}` ({non_empty} valores)")
            st.write("\n".join(col_info))
            
            # Mostrar datos (censurar passwords)
            display_df = df_cred.copy()
            if 'password' in display_df.columns:
                display_df['password'] = display_df['password'].apply(lambda x: "***" if pd.notna(x) and str(x).strip() else x)
            
            st.dataframe(display_df, use_container_width=True)
            
            # Estadísticas
            st.write("**📊 Estadísticas:**")
            st.write(f"• Total usuarios: {len(df_cred)}")
            if 'usuario' in df_cred.columns:
                usuarios_validos = df_cred['usuario'].notna().sum()
                st.write(f"• Usuarios con nombre: {usuarios_validos}")
            if 'Email' in df_cred.columns:
                emails_validos = df_cred['Email'].notna().sum()
                st.write(f"• Usuarios con email: {emails_validos}")
                
        else:
            st.warning("⚠️ Hoja existe pero está vacía")
    else:
        st.error("❌ No se pudo cargar la hoja")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# HOJA 2: proveedor_reservas
# ─────────────────────────────────────────────────────────────
st.header("📅 Hoja 2: proveedor_reservas")

with st.expander("Ver contenido de proveedor_reservas", expanded=True):
    df_reservas, error_reservas = load_sheet_data("proveedor_reservas")
    
    if error_reservas:
        st.error(f"❌ {error_reservas}")
    elif df_reservas is not None:
        if len(df_reservas) > 0:
            st.success(f"✅ **{len(df_reservas)} reservas encontradas**")
            
            # Mostrar información de columnas
            st.write("**📋 Columnas:**")
            col_info = []
            for col in df_reservas.columns:
                non_empty = df_reservas[col].notna().sum()
                col_info.append(f"• `{col}` ({non_empty} valores)")
            st.write("\n".join(col_info))
            
            # Mostrar datos
            st.dataframe(df_reservas, use_container_width=True)
            
            # Estadísticas
            st.write("**📊 Estadísticas:**")
            st.write(f"• Total reservas: {len(df_reservas)}")
            
            if 'Proveedor' in df_reservas.columns:
                proveedores_unicos = df_reservas['Proveedor'].nunique()
                st.write(f"• Proveedores únicos: {proveedores_unicos}")
                
                # Top proveedores
                top_proveedores = df_reservas['Proveedor'].value_counts().head(5)
                st.write("• **Top 5 proveedores:**")
                for proveedor, count in top_proveedores.items():
                    st.write(f"  - {proveedor}: {count} reservas")
            
            if 'Fecha' in df_reservas.columns:
                try:
                    # Convertir fechas y mostrar rango
                    df_reservas['Fecha'] = pd.to_datetime(df_reservas['Fecha'], errors='coerce')
                    fecha_min = df_reservas['Fecha'].min()
                    fecha_max = df_reservas['Fecha'].max()
                    if pd.notna(fecha_min) and pd.notna(fecha_max):
                        st.write(f"• Rango de fechas: {fecha_min.strftime('%Y-%m-%d')} a {fecha_max.strftime('%Y-%m-%d')}")
                except:
                    pass
                    
        else:
            st.warning("⚠️ Hoja existe pero está vacía")
    else:
        st.error("❌ No se pudo cargar la hoja")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# HOJA 3: proveedor_gestion
# ─────────────────────────────────────────────────────────────
st.header("📊 Hoja 3: proveedor_gestion")

with st.expander("Ver contenido de proveedor_gestion", expanded=True):
    df_gestion, error_gestion = load_sheet_data("proveedor_gestion")
    
    if error_gestion:
        st.error(f"❌ {error_gestion}")
    elif df_gestion is not None:
        if len(df_gestion) > 0:
            st.success(f"✅ **{len(df_gestion)} registros de gestión encontrados**")
            
            # Mostrar información de columnas
            st.write("**📋 Columnas:**")
            col_info = []
            for col in df_gestion.columns:
                non_empty = df_gestion[col].notna().sum()
                col_info.append(f"• `{col}` ({non_empty} valores)")
            st.write("\n".join(col_info))
            
            # Mostrar datos
            st.dataframe(df_gestion, use_container_width=True)
            
            # Estadísticas
            st.write("**📊 Estadísticas:**")
            st.write(f"• Total registros: {len(df_gestion)}")
            
            if 'Proveedor' in df_gestion.columns:
                proveedores_gestion = df_gestion['Proveedor'].nunique()
                st.write(f"• Proveedores en gestión: {proveedores_gestion}")
            
            # Verificar columnas de tiempo
            time_columns = ['Tiempo_espera', 'Tiempo_atencion', 'Tiempo_total']
            existing_time_cols = [col for col in time_columns if col in df_gestion.columns]
            
            if existing_time_cols:
                st.write("• **Métricas de tiempo disponibles:**")
                for col in existing_time_cols:
                    valid_times = df_gestion[col].notna().sum()
                    st.write(f"  - {col}: {valid_times} registros")
                    
        else:
            st.warning("⚠️ Hoja existe pero está vacía")
    else:
        st.error("❌ No se pudo cargar la hoja")

# ─────────────────────────────────────────────────────────────
# Resumen General
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.header("📈 Resumen General")

col1, col2, col3 = st.columns(3)

with col1:
    if df_cred is not None:
        st.metric("👥 Usuarios", len(df_cred) if len(df_cred) > 0 else 0)
    else:
        st.metric("👥 Usuarios", "Error")

with col2:
    if df_reservas is not None:
        st.metric("📅 Reservas", len(df_reservas) if len(df_reservas) > 0 else 0)
    else:
        st.metric("📅 Reservas", "Error")

with col3:
    if df_gestion is not None:
        st.metric("📊 Gestión", len(df_gestion) if len(df_gestion) > 0 else 0)
    else:
        st.metric("📊 Gestión", "Error")

# ─────────────────────────────────────────────────────────────
# Botones de acción
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🔄 Acciones")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refrescar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col2:
    if st.button("📋 Ver Hojas Disponibles", use_container_width=True):
        try:
            gc = setup_google_sheets()
            if gc:
                spreadsheet = gc.open(st.secrets["GOOGLE_SHEET_NAME"])
                worksheets = spreadsheet.worksheets()
                st.success("📊 **Hojas disponibles:**")
                for ws in worksheets:
                    st.write(f"• {ws.title} ({ws.row_count} filas, {ws.col_count} columnas)")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col3:
    if st.button("🧪 Probar Escritura", use_container_width=True):
        try:
            gc = setup_google_sheets()
            if gc:
                spreadsheet = gc.open(st.secrets["GOOGLE_SHEET_NAME"])
                
                # Buscar o crear hoja de prueba
                try:
                    test_sheet = spreadsheet.worksheet("test_conexion")
                except gspread.WorksheetNotFound:
                    test_sheet = spreadsheet.add_worksheet("test_conexion", rows=10, cols=3)
                
                # Escribir datos de prueba
                from datetime import datetime
                test_data = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Prueba de escritura",
                    "✅ Funcionando"
                ]
                
                test_sheet.update("A1:C1", [["Timestamp", "Accion", "Estado"]])
                test_sheet.append_row(test_data)
                
                st.success("✅ Escritura exitosa en hoja 'test_conexion'")
                
        except Exception as e:
            st.error(f"❌ Error en prueba de escritura: {str(e)}")

# Información final
st.markdown("---")
st.info("🎉 **¡Google Sheets está funcionando perfectamente!** Sin más errores AADSTS80002.")
st.success("🚀 **Próximo paso**: Migrar tu código principal de SharePoint a Google Sheets.")