import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
from supabase import create_client, Client

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Miscelanea los Garcia", page_icon="🏪", layout="wide")

# --- CREDENCIALES DE SUPABASE ---
SUPABASE_URL = "https://ewspkrvfdjotudsmrchb.supabase.co"
SUPABASE_KEY = "sb_publishable_KSUQQHxPg3xO84xHJzCKtw_E6Yix3QZ"

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

# --- FUNCIONES DE BASE DE DATOS ---
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
    # Ordenamos alfabéticamente desde la base de datos
    res = supabase.table("productos").select("*").order("nombre").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "nombre", "precio_venta", "stock", "unidad_medida"])

def registrar_auditoria(producto_id, producto_nombre, tipo, cantidad, usuario, detalle=""):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    supabase.table("movimientos").insert({
        "producto_id": producto_id, "producto_nombre": producto_nombre,
        "tipo": tipo, "cantidad": cantidad, "usuario": usuario,
        "detalle": detalle, "fecha": fecha_actual
    }).execute()

def agregar_producto(nombre, precio, unidad_medida, usuario):
    res = supabase.table("productos").insert({"nombre": nombre, "precio_venta": precio, "stock": 0, "unidad_medida": unidad_medida}).execute()
    prod_id = res.data[0]["id"]
    registrar_auditoria(prod_id, nombre, "Alta Producto", 0, usuario, f"Precio: ${precio} | Unidad: {unidad_medida}")

def modificar_producto(producto_id, nombre_viejo, nombre_nuevo, precio_viejo, precio_nuevo, unidad_vieja, unidad_nueva, usuario):
    supabase.table("productos").update({
        "nombre": nombre_nuevo.upper(),
        "precio_venta": precio_nuevo,
        "unidad_medida": unidad_nueva
    }).eq("id", producto_id).execute()
    
    detalles = []
    if nombre_viejo != nombre_nuevo.upper(): detalles.append(f"Nombre: {nombre_viejo} -> {nombre_nuevo.upper()}")
    if float(precio_viejo) != float(precio_nuevo): detalles.append(f"Precio: ${precio_viejo} -> ${precio_nuevo}")
    if unidad_vieja != unidad_nueva: detalles.append(f"Unidad: {unidad_vieja} -> {unidad_nueva}")
    
    if detalles:
        registrar_auditoria(producto_id, nombre_nuevo.upper(), "Modificación", 0, usuario, " | ".join(detalles))

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
    
    # Actualizamos el menú para incluir "Modificar Producto"
    opciones_menu = ["Ver Inventario", "Sumar/Restar Mercancía", "Modificar Producto", "Nuevo Producto"]
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
                st.metric("Volumen Total en Stock", f"{total_piezas:,.2f}")
            with col3:
                valor_inventario = (df_productos['precio_venta'].astype(float) * df_productos['stock'].astype(float)).sum()
                st.metric("Valor del Inventario", f"${valor_inventario:,.2f}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            df_mostrar = df_productos.copy()
            
            # Formatear la tabla visualmente
            df_mostrar['precio_venta'] = df_mostrar['precio_venta'].apply(lambda x: f"${float(x):,.2f}")
            
            # Lógica para mostrar Alertas de Stock y Unidades
            def formato_stock(row):
                stock_val = float(row['stock'])
                unidad = "kg" if row.get('unidad_medida') == "Kilo" else "pz"
                alerta = " ⚠️ (Bajo)" if stock_val <= 5 else ""
                return f"{stock_val:g} {unidad}{alerta}"

            df_mostrar['stock'] = df_mostrar.apply(formato_stock, axis=1)
            
            df_mostrar = df_mostrar.rename(columns={"id": "ID", "nombre": "Producto", "precio_venta": "Precio Unitario", "stock": "Stock Actual", "unidad_medida": "Se vende por:"})
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        else:
            st.info("El inventario está vacío.")

    # 2. PANTALLA: ENTRADAS Y SALIDAS
    elif menu == "Sumar/Restar Mercancía":
        st.subheader("🔄 Ingresar o vender mercancía")
        st.caption("*Tip: Haz clic en la caja de producto y escribe en tu teclado para buscar rápidamente.*")
        if not df_productos.empty and len(df_productos) > 0:
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.form("form_movimiento"):
                    producto_seleccionado = st.selectbox("Buscar Producto", df_productos['nombre'])
                    datos_prod = df_productos.loc[df_productos['nombre'] == producto_seleccionado].iloc[0]
                    
                    stock_actual = float(datos_prod['stock'])
                    unidad = datos_prod.get('unidad_medida', 'Pieza')
                    sufijo = "kg" if unidad == "Kilo" else "pz"
                    
                    st.caption(f"Stock actual: **{stock_actual:g} {sufijo}**")
                    
                    tipo_mov = st.radio("Tipo de movimiento", ["Entrada", "Salida (Venta)"], horizontal=True)
                    # Cambiamos step a 0.1 para permitir decimales (kilos)
                    cantidad = st.number_input(f"Cantidad ({sufijo})", min_value=0.01, step=1.0 if sufijo=="pz" else 0.250)
                    submit = st.form_submit_button("Registrar Movimiento", type="primary")
                    
                    if submit:
                        if tipo_mov == "Salida (Venta)" and cantidad > stock_actual:
                            st.error(f"❌ No puedes vender {cantidad:g} {sufijo}. Solo tienes {stock_actual:g} {sufijo}.")
                        else:
                            prod_id = int(datos_prod['id'])
                            registrar_movimiento(prod_id, producto_seleccionado, tipo_mov, cantidad, stock_actual, usuario_sesion)
                            st.success(f"✅ Registrado: {tipo_mov} de {cantidad:g} {sufijo}.")
        else:
            st.warning("Agrega productos primero.")

    # 3. PANTALLA: MODIFICAR PRODUCTO (Corregir nombre, precio y unidad)
    elif menu == "Modificar Producto":
        st.subheader("✏️ Corregir o actualizar producto")
        if not df_productos.empty and len(df_productos) > 0:
            col1, col2 = st.columns([1, 1])
            with col1:
                producto_seleccionado = st.selectbox("Selecciona el producto a corregir", df_productos['nombre'])
                datos_prod = df_productos.loc[df_productos['nombre'] == producto_seleccionado].iloc[0]
                
                with st.form("form_modificar"):
                    nuevo_nombre = st.text_input("Nombre correcto del producto", value=datos_prod['nombre'])
                    nuevo_precio = st.number_input("Precio ($)", min_value=0.0, value=float(datos_prod['precio_venta']), step=0.5)
                    
                    unidad_actual = datos_prod.get('unidad_medida', 'Pieza')
                    index_unidad = 0 if unidad_actual == "Pieza" else 1
                    nueva_unidad = st.selectbox("Se vende por:", ["Pieza", "Kilo"], index=index_unidad)
                    
                    submit = st.form_submit_button("Guardar Cambios", type="primary")
                    
                    if submit:
                        if not nuevo_nombre.strip():
                            st.error("El nombre no puede estar vacío.")
                        else:
                            prod_id = int(datos_prod['id'])
                            modificar_producto(prod_id, datos_prod['nombre'], nuevo_nombre, float(datos_prod['precio_venta']), nuevo_precio, unidad_actual, nueva_unidad, usuario_sesion)
                            st.success("✅ Producto actualizado correctamente.")
                            st.rerun()
        else:
            st.warning("Agrega productos primero.")

    # 4. PANTALLA: NUEVO PRODUCTO
    elif menu == "Nuevo Producto":
        st.subheader("➕ Alta de producto")
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.form("form_nuevo_prod"):
                nombre = st.text_input("Nombre del producto")
                precio = st.number_input("Precio ($)", min_value=0.0, step=0.5)
                unidad_medida = st.selectbox("¿Cómo se vende este producto?", ["Pieza", "Kilo"])
                
                submit = st.form_submit_button("Guardar", type="primary")
                if submit and nombre:
                    agregar_producto(nombre.upper(), precio, unidad_medida, usuario_sesion)
                    st.success(f"✅ '{nombre.upper()}' agregado.")

    # 5. PANTALLA: ELIMINAR PRODUCTO
    elif menu == "Eliminar Producto":
        st.subheader("🗑️ Eliminar un producto")
        if not df_productos.empty and len(df_productos) > 0:
            col1, col2 = st.columns([1, 1])
            with col1:
                producto_seleccionado = st.selectbox("Producto", df_productos['nombre'])
                prod_id = int(df_productos.loc[df_productos['nombre'] == producto_seleccionado, 'id'].values[0])
                confirmacion = st.checkbox("Confirmo que deseo borrar este producto permanentemente.")
                
                if st.button("Eliminar", type="primary", disabled=not confirmacion):
                    eliminar_producto(prod_id, producto_seleccionado, usuario_sesion)
                    st.success(f"❌ Producto eliminado.")
                    st.rerun()

    # 6. PANTALLA: HISTORIAL
    elif menu == "📜 Ver Historial (Auditoría)":
        st.subheader("🕵️‍♂️ Registro de Actividad")
        res_historial = supabase.table("movimientos").select("fecha, usuario, tipo, producto_nombre, cantidad, detalle").order("id", desc=True).limit(200).execute()
        df_historial = pd.DataFrame(res_historial.data) if res_historial.data else pd.DataFrame()
        
        if not df_historial.empty:
            df_historial = df_historial.rename(columns={
                "fecha": "Fecha", "usuario": "Usuario", "tipo": "Acción", 
                "producto_nombre": "Producto", "cantidad": "Cant.", "detalle": "Detalle Extra"
            })
            st.dataframe(df_historial, use_container_width=True, hide_index=True)
        else:
            st.info("Sin movimientos.")

    # 7. PANTALLA: ADMINISTRAR USUARIOS
    elif menu == "👥 Administrar Usuarios":
        st.subheader("👥 Gestión de Cuentas")
        res_users = supabase.table("usuarios").select("id, username, rol").execute()
        df_usuarios = pd.DataFrame(res_users.data) if res_users.data else pd.DataFrame()
        
        if not df_usuarios.empty:
            st.dataframe(df_usuarios.rename(columns={"id": "ID", "username": "Usuario", "rol": "Acceso"}), hide_index=True)
        
        st.write("**➕ Crear cuenta**")
        with st.form("form_nuevo_usuario"):
            nuevo_user = st.text_input("Nombre de Usuario")
            nuevo_pass = st.text_input("Contraseña", type="password")
            nuevo_rol = st.selectbox("Tipo de cuenta", ["Empleado", "Administrador"])
            if st.form_submit_button("Crear Usuario", type="primary") and nuevo_user and nuevo_pass:
                if crear_usuario(nuevo_user.strip().lower(), nuevo_pass, nuevo_rol):
                    st.success(f"✅ Cuenta '{nuevo_user.strip().lower()}' creada!")
                    st.rerun()
                else:
                    st.error("❌ Ese usuario ya existe.")