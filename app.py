import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
from supabase import create_client, Client

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Miscelanea los Garcia", page_icon="🏪", layout="wide")

# --- CREDENCIALES DE SUPABASE ---
# REEMPLAZA ESTOS DATOS CON LOS DE TU PROYECTO EN SUPABASE
SUPABASE_URL = "https://ewspkrvfdjotudsmrchb.supabase.co"
SUPABASE_KEY = "sb_publishable_KSUQQHxPg3xO84xHJzCKtw_E6Yix3QZ"

# Conexión con el servidor en la nube
@st.cache_resource
def conectar_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = conectar_supabase()

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #1e1e2e;
        border: 1px solid #3b3d5c;
        padding: 5% 5% 5% 10%;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #00d2d3;
    }
    h1 { color: #00d2d3 !important; }
    </style>
""", unsafe_allow_html=True)

# --- SEGURIDAD ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- FUNCIONES DE BASE DE DATOS EN LA NUBE ---
def verificar_login(username, password):
    res = supabase.table("usuarios").select("*").eq("username", username).eq("password", hash_password(password)).execute()
    return res.data[0] if res.data else None

def crear_usuario(username, password, rol):
    try:
        supabase.table("usuarios").insert({"username": username, "password": hash_password(password), "rol": rol}).execute()
        return True
    except Exception:
        return False

def obtener_productos():
    res = supabase.table("productos").select("*").order("id").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "nombre", "precio_venta", "stock"])

def registrar_auditoria(producto_id, producto_nombre, tipo, cantidad, usuario, detalle=""):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    supabase.table("movimientos").insert({
        "producto_id": producto_id, "producto_nombre": producto_nombre,
        "tipo": tipo, "cantidad": cantidad, "usuario": usuario,
        "detalle": detalle, "fecha": fecha_actual
    }).execute()

def agregar_producto(nombre, precio, usuario):
    res = supabase.table("productos").insert({"nombre": nombre, "precio_venta": precio, "stock": 0}).execute()
    prod_id = res.data[0]["id"]
    registrar_auditoria(prod_id, nombre, "Alta Producto", 0, usuario, f"Precio inicial: ${precio}")

def actualizar_precio(producto_id, nombre, nuevo_precio, precio_anterior, usuario):
    supabase.table("productos").update({"precio_venta": nuevo_precio}).eq("id", producto_id).execute()
    registrar_auditoria(producto_id, nombre, "Cambio Precio", 0, usuario, f"De ${precio_anterior} a ${nuevo_precio}")

def registrar_movimiento(producto_id, nombre, tipo, cantidad, stock_actual, usuario):
    nuevo_stock = (stock_actual + cantidad) if tipo == "Entrada" else (stock_actual - cantidad)
    supabase.table("productos").update({"stock": nuevo_stock}).eq("id", producto_id).execute()
    registrar_auditoria(producto_id, nombre, tipo, cantidad, usuario)

def eliminar_producto(producto_id, nombre, usuario):
    supabase.table("productos").delete().eq("id", producto_id).execute()
    registrar_auditoria(producto_id, nombre, "Eliminación", 0, usuario, "Producto borrado del sistema")


# --- SISTEMA DE INICIO DE SESIÓN ---
if 'usuario_actual' not in st.session_state:
    st.session_state['usuario_actual'] = None
    st.session_state['rol_actual'] = None

if st.session_state['usuario_actual'] is None:
    st.title("🔒 Acceso al Sistema")
    st.write("Por favor, inicia sesión para continuar.")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            user_input = st.text_input("Usuario")
            pass_input = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Ingresar", type="primary")
            
            if submit_login:
                usuario_db = verificar_login(user_input.strip().lower(), pass_input)
                if usuario_db:
                    st.session_state['usuario_actual'] = usuario_db["username"]
                    st.session_state['rol_actual'] = usuario_db["rol"]
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
else:
    usuario_sesion = st.session_state['usuario_actual']
    rol_sesion = st.session_state['rol_actual']
    
    st.title("📦 Miscelanea los Garcia")
    
    st.sidebar.markdown(f"👤 **Usuario:** `{usuario_sesion}`")
    st.sidebar.markdown(f"🛡️ **Rol:** `{rol_sesion}`")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['usuario_actual'] = None
        st.session_state['rol_actual'] = None
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Navegación")
    
    opciones_menu = ["Ver Inventario", "Registrar Sumar_Piezas/Restar_Piezas", "Actualizar Precios", "Nuevo Producto"]
    if rol_sesion == "Administrador":
        opciones_menu.extend(["Eliminar Producto", "📜 Ver Historial (Auditoría)", "👥 Administrar Usuarios"])
        
    menu = st.sidebar.radio("", opciones_menu)

    df_productos = obtener_productos()

    # 1. PANTALLA: VER INVENTARIO
    if menu == "Ver Inventario":
        st.subheader("📊 Tablero General")
        if not df_productos.empty and len(df_productos) > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Productos", len(df_productos))
            with col2:
                total_piezas = df_productos['stock'].sum()
                st.metric("Piezas Totales en Stock", f"{total_piezas} pz")
            with col3:
                valor_inventario = (df_productos['precio_venta'] * df_productos['stock']).sum()
                st.metric("Valor del Inventario", f"${valor_inventario:,.2f}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            df_mostrar = df_productos.copy()
            df_mostrar['precio_venta'] = df_mostrar['precio_venta'].apply(lambda x: f"${float(x):,.2f}")
            df_mostrar['stock'] = df_mostrar['stock'].astype(str) + " pz"
            df_mostrar = df_mostrar.rename(columns={"id": "ID", "nombre": "Producto", "precio_venta": "Precio Unitario", "stock": "Stock Actual"})
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        else:
            st.info("El inventario está vacío.")

    # 2. PANTALLA: ENTRADAS Y SALIDAS
    elif menu == "Registrar Entradas/Salidas":
        st.subheader("🔄 Registrar mercancía")
        if not df_productos.empty and len(df_productos) > 0:
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.form("form_movimiento"):
                    producto_seleccionado = st.selectbox("Producto", df_productos['nombre'])
                    stock_actual = int(df_productos.loc[df_productos['nombre'] == producto_seleccionado, 'stock'].values[0])
                    st.caption(f"Stock actual: **{stock_actual} pz**")
                    
                    tipo_mov = st.radio("Tipo de movimiento", ["Entrada", "Salida (Venta)"], horizontal=True)
                    cantidad = st.number_input("Cantidad", min_value=1, step=1)
                    submit = st.form_submit_button("Registrar Movimiento", type="primary")
                    
                    if submit:
                        if tipo_mov == "Salida (Venta)" and cantidad > stock_actual:
                            st.error(f"❌ No puedes vender {cantidad} pz. Solo tienes {stock_actual} pz.")
                        else:
                            prod_id = int(df_productos.loc[df_productos['nombre'] == producto_seleccionado, 'id'].values[0])
                            registrar_movimiento(prod_id, producto_seleccionado, tipo_mov, cantidad, stock_actual, usuario_sesion)
                            st.success(f"✅ Registrado: {tipo_mov} de {cantidad} pz.")
        else:
            st.warning("Agrega productos primero.")

    # 3. PANTALLA: ACTUALIZAR PRECIOS
    elif menu == "Actualizar Precios":
        st.subheader("💲 Cambiar precio")
        if not df_productos.empty and len(df_productos) > 0:
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.form("form_precio"):
                    producto_seleccionado = st.selectbox("Producto", df_productos['nombre'])
                    precio_actual = float(df_productos.loc[df_productos['nombre'] == producto_seleccionado, 'precio_venta'].values[0])
                    nuevo_precio = st.number_input("Nuevo precio ($)", min_value=0.0, value=precio_actual, step=0.5)
                    submit = st.form_submit_button("Actualizar", type="primary")
                    
                    if submit:
                        prod_id = int(df_productos.loc[df_productos['nombre'] == producto_seleccionado, 'id'].values[0])
                        actualizar_precio(prod_id, producto_seleccionado, nuevo_precio, precio_actual, usuario_sesion)
                        st.success(f"✅ Precio actualizado a ${nuevo_precio:,.2f}")
        else:
            st.warning("Agrega productos primero.")

    # 4. PANTALLA: NUEVO PRODUCTO
    elif menu == "Nuevo Producto":
        st.subheader("➕ Alta de producto")
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.form("form_nuevo_prod"):
                nombre = st.text_input("Nombre del producto")
                precio = st.number_input("Precio inicial ($)", min_value=0.0, step=0.5)
                submit = st.form_submit_button("Guardar", type="primary")
                if submit and nombre:
                    agregar_producto(nombre.upper(), precio, usuario_sesion)
                    st.success(f"✅ '{nombre.upper()}' agregado.")

    # 5. PANTALLA: ELIMINAR PRODUCTO (Solo Admin)
    elif menu == "Eliminar Producto":
        st.subheader("🗑️ Eliminar un producto")
        if not df_productos.empty and len(df_productos) > 0:
            col1, col2 = st.columns([1, 1])
            with col1:
                producto_seleccionado = st.selectbox("Producto", df_productos['nombre'])
                prod_id = int(df_productos.loc[df_productos['nombre'] == producto_seleccionado, 'id'].values[0])
                confirmacion = st.checkbox("Confirmo que deseo borrar este producto.")
                
                if st.button("Eliminar", type="primary", disabled=not confirmacion):
                    eliminar_producto(prod_id, producto_seleccionado, usuario_sesion)
                    st.success(f"❌ Producto eliminado.")
                    st.rerun()

    # 6. PANTALLA: HISTORIAL (Solo Admin)
    elif menu == "📜 Ver Historial (Auditoría)":
        st.subheader("🕵️‍♂️ Registro de Actividad")
        res_historial = supabase.table("movimientos").select("fecha, usuario, tipo, producto_nombre, cantidad, detalle").order("id", desc=True).execute()
        df_historial = pd.DataFrame(res_historial.data) if res_historial.data else pd.DataFrame()
        
        if not df_historial.empty:
            df_historial = df_historial.rename(columns={
                "fecha": "Fecha y Hora", "usuario": "Usuario", "tipo": "Acción", 
                "producto_nombre": "Producto", "cantidad": "Cant.", "detalle": "Detalle Extra"
            })
            st.dataframe(df_historial, use_container_width=True, hide_index=True)
        else:
            st.info("Sin movimientos.")

    # 7. PANTALLA: ADMINISTRAR USUARIOS (Solo Admin)
    elif menu == "👥 Administrar Usuarios":
        st.subheader("👥 Gestión de Cuentas")
        res_users = supabase.table("usuarios").select("id, username, rol").execute()
        df_usuarios = pd.DataFrame(res_users.data) if res_users.data else pd.DataFrame()
        
        st.write("**Cuentas registradas actualmente:**")
        if not df_usuarios.empty:
            st.dataframe(df_usuarios.rename(columns={"id": "ID", "username": "Usuario", "rol": "Nivel de Acceso"}), hide_index=True)
        
        st.markdown("---")
        st.write("**➕ Crear una nueva cuenta**")
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.form("form_nuevo_usuario"):
                nuevo_user = st.text_input("Nombre de Usuario")
                nuevo_pass = st.text_input("Contraseña", type="password")
                nuevo_rol = st.selectbox("Tipo de cuenta", ["Empleado", "Administrador"])
                submit_user = st.form_submit_button("Crear Usuario", type="primary")
                
                if submit_user and nuevo_user and nuevo_pass:
                    nuevo_user_limpio = nuevo_user.strip().lower()
                    if crear_usuario(nuevo_user_limpio, nuevo_pass, nuevo_rol):
                        st.success(f"✅ ¡Cuenta '{nuevo_user_limpio}' creada!")
                        st.rerun()
                    else:
                        st.error("❌ Ese nombre de usuario ya existe.")