import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import bcrypt
from supabase import create_client, Client

# ================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ================================================================
st.set_page_config(
    page_title="Miscelánea Los García",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# CREDENCIALES SEGURAS
# ================================================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except (FileNotFoundError, KeyError) as e:
    st.error(f"⚠️ Credencial faltante en st.secrets: {e}")
    st.stop()

@st.cache_resource(ttl=3600)
def conectar_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = conectar_supabase()

# ================================================================
# ESTILOS — TEMA OSCURO PROFESIONAL "COMMAND CENTER"
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&display=swap');

/* ── GLOBAL ── */
/* Fondo general de la app */
.stApp {
    background-color: #0b0f19 !important;
}

/* Aplicar la fuente SOLO a textos reales y controles. 
   ¡NO PONER 'span' ni 'div' aquí para evitar romper los íconos de Streamlit! */
p, h1, h2, h3, h4, h5, h6, label, input, select, button, textarea {
    font-family: 'Sora', sans-serif !important;
}

.main .block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1300px !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #111827 0%, #0b0f19 100%) !important;
    border-right: 1px solid rgba(0, 210, 211, 0.12) !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 2px !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin: 1px 0 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #8892a4 !important;
    transition: all 0.18s ease !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(0, 210, 211, 0.08) !important;
    color: #00d2d3 !important;
    border-color: rgba(0, 210, 211, 0.15) !important;
    padding-left: 18px !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(0, 210, 211, 0.1) !important;
    color: #00d2d3 !important;
    border-color: rgba(0, 210, 211, 0.25) !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label span:first-child {
    display: none !important;
}

/* ── METRIC CARDS ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #161b27 0%, #1a2035 100%) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(0, 210, 211, 0.1) !important;
    border-left: 4px solid #00d2d3 !important;
    padding: 20px 22px !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4), 0 0 0 0 rgba(0, 210, 211, 0) !important;
    transition: transform 0.22s ease, box-shadow 0.22s ease !important;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 210, 211, 0.1) !important;
}

div[data-testid="stMetricValue"] > div {
    color: #00d2d3 !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}

div[data-testid="stMetricLabel"] > div {
    color: #556070 !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

div[data-testid="stMetricDelta"] > div {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* ── TÍTULOS Y TEXTOS EXTRA ── */
h1 { color: #e6edf3 !important; font-size: 1.7rem !important; font-weight: 800 !important; letter-spacing: -0.02em !important; }
h2 { color: #e6edf3 !important; font-size: 1.35rem !important; font-weight: 700 !important; }
h3 { color: #00d2d3 !important; font-size: 1.05rem !important; font-weight: 600 !important; }
p, span, div { color: #c9d1d9; }

hr {
    border: none !important;
    border-top: 1px solid rgba(0, 210, 211, 0.08) !important;
    margin: 0.8rem 0 1.4rem 0 !important;
}

/* ── FORMS Y CONTENEDORES ── */
div[data-testid="stForm"] {
    background: #111827 !important;
    border: 1px solid rgba(0, 210, 211, 0.08) !important;
    border-radius: 18px !important;
    padding: 26px 28px !important;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3) !important;
}

/* ── INPUTS ── */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #0b0f19 !important;
    border: 1px solid rgba(0, 210, 211, 0.15) !important;
    border-radius: 9px !important;
    color: #e6edf3 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: border-color 0.18s !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: #00d2d3 !important;
    box-shadow: 0 0 0 3px rgba(0, 210, 211, 0.1) !important;
}

div[data-baseweb="select"] > div {
    background: #0b0f19 !important;
    border-color: rgba(0, 210, 211, 0.15) !important;
    border-radius: 9px !important;
    color: #e6edf3 !important;
}

/* Labels de inputs */
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label {
    color: #7d8fa9 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}

/* ── BOTONES PRINCIPALES (VERDES) ── */
button[kind="primary"] {
    background-color: #05c46b !important; /* Verde principal */
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.55rem 1.6rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 12px rgba(5, 196, 107, 0.2) !important; /* Sombra verde sutil */
}

button[kind="primary"]:hover {
    background-color: #04aa5d !important; /* Verde un poco más oscuro al pasar el ratón */
    color: white !important;
    box-shadow: 0 4px 22px rgba(5, 196, 107, 0.38) !important; /* Sombra más pronunciada */
    transform: translateY(-2px) !important;
}

button[kind="primary"]:active {
    transform: translateY(0) !important;
}

/* ── BOTONES SECUNDARIOS ── */
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(0, 210, 211, 0.25) !important;
    color: #00d2d3 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: 10px !important;
    transition: all 0.18s ease !important;
}

button[kind="secondary"]:hover {
    background: rgba(0, 210, 211, 0.07) !important;
    border-color: rgba(0, 210, 211, 0.45) !important;
}

button:disabled {
    opacity: 0.3 !important;
    cursor: not-allowed !important;
}

/* ── COMPONENTES EXTRA ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 210, 211, 0.08) !important;
}

div[data-testid="stTabs"] button[role="tab"] {
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: #556070 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0.5rem 1rem !important;
    transition: color 0.18s !important;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #00d2d3 !important;
    border-bottom: 2px solid #00d2d3 !important;
}

label[data-testid="stCheckbox"] {
    font-size: 0.87rem !important;
    font-weight: 500 !important;
    color: #c9d1d9 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

div[data-testid="stSubheader"] {
    color: #e6edf3 !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}

div[data-testid="stCaptionContainer"] p {
    color: #445060 !important;
    font-size: 0.75rem !important;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0b0f19; }
::-webkit-scrollbar-thumb { background: rgba(0, 210, 211, 0.2); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 210, 211, 0.4); }

/* ── CLASES PERSONALIZADAS ── */
.login-card {
    background: linear-gradient(145deg, #111827, #161f30);
    border: 1px solid rgba(0, 210, 211, 0.12);
    border-radius: 22px;
    padding: 44px 40px 36px 40px;
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(0, 210, 211, 0.04);
    margin-bottom: -12px;
}

.login-logo {
    text-align: center;
    font-size: 3rem;
    margin-bottom: 0.4rem;
}

.login-title {
    text-align: center;
    font-size: 1.55rem;
    font-weight: 800;
    color: #e6edf3;
    letter-spacing: -0.02em;
    margin-bottom: 0.1rem;
}

.login-sub {
    text-align: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: #445060;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 2rem;
}

.user-card {
    background: linear-gradient(135deg, rgba(0,210,211,0.07), rgba(0,210,211,0.03));
    border: 1px solid rgba(0, 210, 211, 0.14);
    border-radius: 13px;
    padding: 14px 16px;
    margin-bottom: 1.2rem;
}

.user-card .name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #e6edf3;
    display: block;
}

.user-card .role {
    font-size: 0.68rem;
    font-weight: 700;
    color: #00d2d3;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    display: block;
    margin-top: 2px;
}

.page-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.4rem;
}

.page-badge {
    background: rgba(0, 210, 211, 0.08);
    border: 1px solid rgba(0, 210, 211, 0.18);
    color: #00d2d3;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.danger-card {
    background: rgba(239, 68, 68, 0.06);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-left: 4px solid #ef4444;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 1rem 0;
}

.danger-card .title {
    color: #fca5a5;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}

.danger-card .producto {
    color: #e6edf3;
    font-size: 1.05rem;
    font-weight: 700;
}

.danger-card .meta {
    color: #556070;
    font-size: 0.8rem;
    margin-top: 4px;
}

.nav-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: #2d3748;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 0 4px;
    margin-bottom: 4px;
    display: block;
}

.version-footer {
    font-size: 0.68rem;
    color: #2d3748;
    text-align: center;
    padding-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
# SEGURIDAD — BCRYPT + MIGRACIÓN EN CALIENTE
# ================================================================
def _hash_sha256_legacy(password):
    return hashlib.sha256(password.encode()).hexdigest()

def encriptar_bcrypt(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verificar_login(username, password):
    res = supabase.table("usuarios").select("*").eq("username", username).execute()

    if not res.data:
        _dummy_hash = encriptar_bcrypt("timing_guard_dummy_xyz")
        bcrypt.checkpw(b"timing_guard_dummy_xyz", _dummy_hash.encode())
        return None

    user = res.data[0]
    db_hash = user["password"]

    if len(db_hash) == 64:
        if db_hash == _hash_sha256_legacy(password):
            supabase.table("usuarios").update(
                {"password": encriptar_bcrypt(password)}
            ).eq("username", username).execute()
            return user
        return None

    try:
        if bcrypt.checkpw(password.encode(), db_hash.encode()):
            return user
    except ValueError:
        pass
    return None

def crear_usuario(username, password, rol):
    try:
        supabase.table("usuarios").insert({
            "username": username,
            "password": encriptar_bcrypt(password),
            "rol": rol
        }).execute()
        return True
    except Exception:
        return False

def cambiar_password(username, nueva_password):
    supabase.table("usuarios").update({
        "password": encriptar_bcrypt(nueva_password)
    }).eq("username", username).execute()

def eliminar_usuario(user_id):
    supabase.table("usuarios").delete().eq("id", user_id).execute()

# ================================================================
# BASE DE DATOS — CON CACHÉ Y AUDITORÍA
# ================================================================
@st.cache_data(ttl=30)
def obtener_productos():
    res = supabase.table("productos").select("*").order("nombre").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame(
        columns=["id", "nombre", "precio_venta", "stock", "unidad_medida", "alerta_stock"]
    )

def invalidar_cache():
    obtener_productos.clear()

def registrar_auditoria(producto_id, producto_nombre, tipo, cantidad, usuario, detalle=""):
    supabase.table("movimientos").insert({
        "producto_id": producto_id,
        "producto_nombre": producto_nombre,
        "tipo": tipo,
        "cantidad": float(cantidad),
        "usuario": usuario,
        "detalle": detalle,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }).execute()

def agregar_producto(nombre, precio, unidad_medida, alerta_stock, usuario):
    res = supabase.table("productos").insert({
        "nombre": nombre,
        "precio_venta": float(precio),
        "stock": 0.0,
        "unidad_medida": unidad_medida,
        "alerta_stock": float(alerta_stock)
    }).execute()
    prod_id = res.data[0]["id"]
    registrar_auditoria(prod_id, nombre, "Alta Producto", 0, usuario,
                        f"Precio: ${precio:.2f} | Unidad: {unidad_medida} | Alerta: {alerta_stock:g}")
    invalidar_cache()

def modificar_producto(producto_id, nombre_viejo, nombre_nuevo, precio_viejo, precio_nuevo,
                       unidad_vieja, unidad_nueva, alerta_vieja, alerta_nueva, usuario):
    nombre_nuevo_up = nombre_nuevo.strip().upper()
    supabase.table("productos").update({
        "nombre": nombre_nuevo_up,
        "precio_venta": float(precio_nuevo),
        "unidad_medida": unidad_nueva,
        "alerta_stock": float(alerta_nueva)
    }).eq("id", producto_id).execute()

    detalles = []
    if nombre_viejo != nombre_nuevo_up:
        detalles.append(f"Nombre: {nombre_viejo} → {nombre_nuevo_up}")
    if round(float(precio_viejo), 4) != round(float(precio_nuevo), 4):
        detalles.append(f"Precio: ${precio_viejo} → ${precio_nuevo}")
    if unidad_vieja != unidad_nueva:
        detalles.append(f"Unidad: {unidad_vieja} → {unidad_nueva}")
    if round(float(alerta_vieja), 4) != round(float(alerta_nueva), 4):
        detalles.append(f"Alerta: {alerta_vieja:g} → {alerta_nueva:g}")

    if detalles:
        registrar_auditoria(producto_id, nombre_nuevo_up, "Modificación", 0, usuario, " | ".join(detalles))
    invalidar_cache()

def registrar_movimiento(producto_id, nombre, tipo, cantidad, usuario):
    res_actual = supabase.table("productos").select("stock").eq("id", producto_id).execute()
    stock_real = float(res_actual.data[0]["stock"])

    if tipo == "Salida (Venta)" and cantidad > stock_real:
        return False, stock_real  

    nuevo_stock = (stock_real + cantidad) if tipo == "Entrada" else (stock_real - cantidad)
    supabase.table("productos").update({"stock": float(nuevo_stock)}).eq("id", producto_id).execute()
    registrar_auditoria(producto_id, nombre, tipo, cantidad, usuario)
    invalidar_cache()
    return True, nuevo_stock

def eliminar_producto(producto_id, nombre, usuario):
    supabase.table("productos").delete().eq("id", producto_id).execute()
    registrar_auditoria(producto_id, nombre, "Eliminación", 0, usuario, "Producto borrado del sistema")
    invalidar_cache()

# ================================================================
# ESTADO DE SESIÓN
# ================================================================
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None
    st.session_state["rol_actual"] = None

# ================================================================
# PANTALLA DE LOGIN
# ================================================================
if st.session_state["usuario_actual"] is None:

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_c, _ = st.columns([1, 1.05, 1])

    with col_c:
        st.markdown("""
            <div class="login-card">
                <div class="login-logo">🏪</div>
                <div class="login-title">Miscelánea Los García</div>
                <div class="login-sub">Sistema de Inventario</div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            user_input = st.text_input("Usuario", placeholder="tu_usuario")
            pass_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button(
                "Ingresar al Sistema →", type="primary", use_container_width=True
            )

            if submit_login:
                if not user_input.strip() or not pass_input:
                    st.error("Ingresa usuario y contraseña.")
                else:
                    with st.spinner("Verificando acceso..."):
                        usuario_db = verificar_login(user_input.strip().lower(), pass_input)
                    if usuario_db:
                        st.session_state["usuario_actual"] = usuario_db["username"]
                        st.session_state["rol_actual"] = usuario_db["rol"]
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")

# ================================================================
# APLICACIÓN PRINCIPAL
# ================================================================
else:
    usuario_sesion = st.session_state["usuario_actual"]
    rol_sesion = st.session_state["rol_actual"]
    es_admin = rol_sesion == "Administrador"

    # ── SIDEBAR ──────────────────────────────────────────────────
    with st.sidebar:
        icono_rol = "👑" if es_admin else "🧑‍💼"
        st.markdown(f"""
            <div class="user-card">
                <span class="name">{icono_rol} {usuario_sesion.capitalize()}</span>
                <span class="role">{rol_sesion}</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="nav-label">Menú</span>', unsafe_allow_html=True)

        opciones = [
            "📊 Ver Inventario",
            "📦 Registrar Movimiento",
            "✏️ Modificar Producto",
            "➕ Nuevo Producto",
        ]
        if es_admin:
            opciones += [
                "🗑️ Eliminar Producto",
                "📜 Historial",
                "👥 Usuarios",
            ]

        menu = st.radio("nav", opciones, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown(
            f'<div class="version-footer">🏪 Los García · v3.0<br>{datetime.now().strftime("%d/%m/%Y")}</div>',
            unsafe_allow_html=True
        )

    # ── HEADER DE PÁGINA ─────────────────────────────────────────
    titulos = {
        "📊 Ver Inventario":       ("📊", "Tablero de Inventario"),
        "📦 Registrar Movimiento": ("📦", "Registrar Movimiento"),
        "✏️ Modificar Producto":   ("✏️", "Modificar Producto"),
        "➕ Nuevo Producto":       ("➕", "Nuevo Producto"),
        "🗑️ Eliminar Producto":    ("🗑️", "Eliminar Producto"),
        "📜 Historial":            ("📜", "Historial de Auditoría"),
        "👥 Usuarios":             ("👥", "Administrar Usuarios"),
    }
    emoji_p, titulo_p = titulos.get(menu, ("", menu))
    st.markdown(f"""
        <div class="page-header">
            <h2 style="margin:0; color:#e6edf3;">{emoji_p} {titulo_p}</h2>
            <span class="page-badge">{rol_sesion}</span>
        </div>
        <hr>
    """, unsafe_allow_html=True)

    # Cargar productos
    df_productos = obtener_productos()
    if not df_productos.empty:
        df_productos["alerta_stock"] = df_productos["alerta_stock"].fillna(5)

    # ============================================================
    # 1. VER INVENTARIO
    # ============================================================
    if menu == "📊 Ver Inventario":
        if not df_productos.empty:
            total_prods  = len(df_productos)
            vol_total    = df_productos["stock"].astype(float).sum()
            valor_inv    = (df_productos["precio_venta"].astype(float) *
                            df_productos["stock"].astype(float)).sum()
            bajo_stock_n = len(df_productos[
                df_productos["stock"].astype(float) <=
                df_productos["alerta_stock"].astype(float)
            ])

            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Productos Registrados", total_prods)
            with c2: st.metric("Volumen Total en Stock", f"{vol_total:,.1f}")
            with c3: st.metric("Valor del Inventario", f"${valor_inv:,.2f}")
            with c4: st.metric("⚠️ Con Stock Bajo", bajo_stock_n)

            st.markdown("<br>", unsafe_allow_html=True)

            busqueda = st.text_input("🔍 Filtrar producto...", placeholder="Escribe parte del nombre")

            df_v = df_productos.copy()
            if busqueda.strip():
                df_v = df_v[df_v["nombre"].str.contains(busqueda.strip().upper(), na=False)]

            df_v["_stock"] = df_v["stock"].astype(float)
            df_v["_alerta"] = df_v["alerta_stock"].astype(float)
            df_v["precio_venta"] = df_v["precio_venta"].apply(lambda x: f"${float(x):,.2f}")

            def fmt_stock(row):
                val   = float(row["_stock"])
                lim   = float(row["_alerta"])
                unid  = "kg" if row.get("unidad_medida") == "Kilo" else "pz"
                badge = "  🔴 BAJO" if val <= lim else "  ✅"
                return f"{val:g} {unid}{badge}"

            df_v["stock_fmt"] = df_v.apply(fmt_stock, axis=1)
            df_show = df_v[["nombre", "precio_venta", "stock_fmt", "unidad_medida", "_stock", "_alerta"]].copy()
            df_show.columns = ["Producto", "Precio Unitario", "Stock Actual", "Se vende por", "_s", "_a"]

            def resaltar(row):
                if row["_s"] <= row["_a"]:
                    return ["background-color:rgba(239,68,68,0.10);color:#fca5a5;font-weight:700"] * len(row)
                return [""] * len(row)

            st.dataframe(
                df_show.style.apply(resaltar, axis=1),
                use_container_width=True,
                hide_index=True,
                column_config={"_s": None, "_a": None}
            )

            if bajo_stock_n > 0:
                st.warning(f"⚠️ **{bajo_stock_n} producto(s)** tienen stock igual o por debajo del mínimo.")
        else:
            st.info("💡 El inventario está vacío. Ve a **Nuevo Producto** para empezar.")

    # ============================================================
    # 2. REGISTRAR MOVIMIENTO
    # ============================================================
    elif menu == "📦 Registrar Movimiento":
        if not df_productos.empty:
            with st.form("form_movimiento"):
                producto_sel = st.selectbox("Producto", df_productos["nombre"])
                datos = df_productos.loc[df_productos["nombre"] == producto_sel].iloc[0]
                stock_ui = float(datos["stock"])
                unidad   = datos.get("unidad_medida", "Pieza")
                sufijo   = "kg" if unidad == "Kilo" else "pz"
                paso     = 0.25 if unidad == "Kilo" else 1.0
                alerta_v = float(datos.get("alerta_stock", 5))

                if stock_ui <= alerta_v:
                    st.warning(f"⚠️ Stock bajo: **{stock_ui:g} {sufijo}** (mínimo configurado: {alerta_v:g})")
                else:
                    st.info(f"📦 Stock disponible: **{stock_ui:g} {sufijo}**")

                tipo_ui = st.radio(
                    "Tipo de movimiento",
                    ["📤 Salida (Venta)", "📥 Entrada (Resurtir)"],
                    horizontal=True
                )
                mapeo = {
                    "📤 Salida (Venta)":    "Salida (Venta)",
                    "📥 Entrada (Resurtir)": "Entrada"
                }
                tipo_bd = mapeo[tipo_ui]

                cantidad = st.number_input(
                    f"Cantidad ({sufijo})",
                    min_value=0.01 if unidad == "Kilo" else 1.0,
                    step=paso,
                    value=paso
                )

                if st.form_submit_button("✅ Confirmar Movimiento", type="primary", use_container_width=True):
                    with st.spinner("Procesando..."):
                        ok, stock_nuevo = registrar_movimiento(
                            int(datos["id"]), producto_sel, tipo_bd, cantidad, usuario_sesion
                        )
                    if ok:
                        accion = "Venta" if tipo_bd == "Salida (Venta)" else "Entrada"
                        st.success(
                            f"✅ **{accion}** de {cantidad:g} {sufijo} registrada. "
                            f"Stock nuevo: **{stock_nuevo:g} {sufijo}**"
                        )
                    else:
                        st.error(
                            f"❌ Stock insuficiente al momento de guardar. "
                            f"Disponible: **{stock_nuevo:g} {sufijo}**. Recarga e intenta de nuevo."
                        )
        else:
            st.warning("Primero agrega productos al inventario.")

    # ============================================================
    # 3. MODIFICAR PRODUCTO
    # ============================================================
    elif menu == "✏️ Modificar Producto":
        if not df_productos.empty:
            producto_sel = st.selectbox("Selecciona el producto a modificar", df_productos["nombre"])
            datos = df_productos.loc[df_productos["nombre"] == producto_sel].iloc[0]

            with st.form("form_modificar"):
                nuevo_nombre = st.text_input("Nombre del producto", value=datos["nombre"])

                c1, c2, c3 = st.columns(3)
                with c1:
                    nuevo_precio = st.number_input(
                        "Precio de venta ($)", min_value=0.0, value=float(datos["precio_venta"]), step=0.5
                    )
                with c2:
                    unidad_actual = datos.get("unidad_medida", "Pieza")
                    nueva_unidad = st.selectbox(
                        "Se vende por:", ["Pieza", "Kilo"], index=0 if unidad_actual == "Pieza" else 1
                    )
                with c3:
                    alerta_actual = float(datos.get("alerta_stock", 5))
                    nueva_alerta  = st.number_input(
                        "Alerta stock mínimo", min_value=0.0, value=alerta_actual, step=1.0
                    )

                if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                    if not nuevo_nombre.strip():
                        st.error("El nombre no puede estar vacío.")
                    else:
                        with st.spinner("Guardando cambios..."):
                            modificar_producto(
                                int(datos["id"]),
                                datos["nombre"], nuevo_nombre,
                                float(datos["precio_venta"]), nuevo_precio,
                                unidad_actual, nueva_unidad,
                                alerta_actual, nueva_alerta,
                                usuario_sesion
                            )
                        st.success("✅ Producto actualizado correctamente.")
                        st.rerun()
        else:
            st.warning("No hay productos para modificar.")

    # ============================================================
    # 4. NUEVO PRODUCTO
    # ============================================================
    elif menu == "➕ Nuevo Producto":
        with st.form("form_nuevo_prod"):
            nombre = st.text_input("Nombre del producto", placeholder="Ej: REFRESCO COLA 600ML")

            c1, c2, c3 = st.columns(3)
            with c1:
                precio = st.number_input("Precio de venta ($)", min_value=0.0, step=0.5)
            with c2:
                unidad_medida = st.selectbox("¿Cómo se vende?", ["Pieza", "Kilo"])
            with c3:
                alerta_stock = st.number_input("Avisar si stock baja de:", min_value=0.0, value=5.0, step=1.0)

            if st.form_submit_button("🚀 Registrar Producto", type="primary", use_container_width=True):
                if not nombre.strip():
                    st.error("El nombre del producto no puede estar vacío.")
                else:
                    if precio == 0:
                        st.warning("⚠️ Registrando producto con precio $0.00. ¿Es correcto?")
                    with st.spinner("Guardando producto..."):
                        agregar_producto(
                            nombre.strip().upper(), precio,
                            unidad_medida, alerta_stock, usuario_sesion
                        )
                    st.success(f"✅ **'{nombre.strip().upper()}'** agregado al inventario con stock inicial 0.")

    # ============================================================
    # 5. ELIMINAR PRODUCTO
    # ============================================================
    elif menu == "🗑️ Eliminar Producto":
        if not df_productos.empty:
            producto_sel = st.selectbox("Selecciona el producto a eliminar", df_productos["nombre"])
            datos = df_productos.loc[df_productos["nombre"] == producto_sel].iloc[0]
            prod_id   = int(datos["id"])
            stock_act = float(datos["stock"])
            sufijo    = "kg" if datos.get("unidad_medida") == "Kilo" else "pz"
            precio_fmt = f"${float(datos['precio_venta']):,.2f}"

            st.markdown(f"""
                <div class="danger-card">
                    <div class="title">⚠️ Acción irreversible</div>
                    <div class="producto">{datos['nombre']}</div>
                    <div class="meta">
                        Stock actual: {stock_act:g} {sufijo} &nbsp;·&nbsp; Precio: {precio_fmt}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            confirmacion = st.checkbox(f"Confirmo que deseo eliminar permanentemente '{datos['nombre']}'")
            if not confirmacion:
                st.info("👆 Marca la casilla para habilitar el botón.")

            if st.button("🗑️ Eliminar Definitivamente", disabled=not confirmacion, type="primary"):
                with st.spinner("Eliminando..."):
                    eliminar_producto(prod_id, producto_sel, usuario_sesion)
                st.success(f"✅ '{producto_sel}' fue eliminado del inventario.")
                st.rerun()
        else:
            st.warning("No hay productos en el inventario.")

    # ============================================================
    # 6. HISTORIAL
    # ============================================================
    elif menu == "📜 Historial":
        res_h = supabase.table("movimientos").select(
            "fecha, usuario, tipo, producto_nombre, cantidad, detalle"
        ).order("id", desc=True).limit(1000).execute()

        df_h = pd.DataFrame(res_h.data) if res_h.data else pd.DataFrame()

        if not df_h.empty:
            df_h["fecha_dt"] = pd.to_datetime(df_h["fecha"])
            df_h["Año"]      = df_h["fecha_dt"].dt.year.astype(str)
            df_h["Mes"]      = df_h["fecha_dt"].dt.month.astype(str).str.zfill(2)
            df_h["Día"]      = df_h["fecha_dt"].dt.day.astype(str).str.zfill(2)

            f1, f2, f3, f4 = st.columns(4)
            with f1:
                anio_sel = st.selectbox("Año",  ["Todos"] + sorted(df_h["Año"].unique(),  reverse=True))
            with f2:
                mes_sel  = st.selectbox("Mes",  ["Todos"] + sorted(df_h["Mes"].unique()))
            with f3:
                dia_sel  = st.selectbox("Día",  ["Todos"] + sorted(df_h["Día"].unique()))
            with f4:
                tipos_disponibles = sorted(df_h["tipo"].dropna().unique())
                tipo_sel = st.selectbox("Tipo de acción", ["Todos"] + tipos_disponibles)

            df_f = df_h.copy()
            if anio_sel != "Todos": df_f = df_f[df_f["Año"] == anio_sel]
            if mes_sel  != "Todos": df_f = df_f[df_f["Mes"] == mes_sel]
            if dia_sel  != "Todos": df_f = df_f[df_f["Día"] == dia_sel]
            if tipo_sel != "Todos": df_f = df_f[df_f["tipo"] == tipo_sel]

            st.caption(f"Mostrando **{len(df_f)}** de {len(df_h)} registros")

            df_mostrar = df_f[["fecha", "usuario", "tipo", "producto_nombre", "cantidad", "detalle"]].rename(columns={
                "fecha":           "Fecha y Hora",
                "usuario":         "Usuario",
                "tipo":            "Acción",
                "producto_nombre": "Producto",
                "cantidad":        "Cant.",
                "detalle":         "Detalle",
            })
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay movimientos registrados.")

    # ============================================================
    # 7. ADMINISTRAR USUARIOS
    # ============================================================
    elif menu == "👥 Usuarios":
        res_u = supabase.table("usuarios").select("id, username, rol").execute()
        df_u  = pd.DataFrame(res_u.data) if res_u.data else pd.DataFrame()

        tab1, tab2, tab3 = st.tabs(["➕ Nuevo Usuario", "🔑 Cambiar Contraseña", "🗑️ Eliminar Usuario"])

        with tab1:
            if not df_u.empty:
                st.dataframe(
                    df_u.rename(columns={"id": "ID", "username": "Usuario", "rol": "Nivel de Acceso"}),
                    use_container_width=True, hide_index=True
                )
            st.markdown("---")
            with st.form("form_nuevo_usuario"):
                nuevo_user = st.text_input("Nombre de usuario")
                nuevo_pass = st.text_input("Contraseña", type="password")
                nuevo_rol  = st.selectbox("Nivel de acceso", ["Empleado", "Administrador"])

                if st.form_submit_button("✅ Crear Cuenta", type="primary"):
                    if not nuevo_user.strip() or not nuevo_pass:
                        st.error("Usuario y contraseña son obligatorios.")
                    elif len(nuevo_pass) < 6:
                        st.error("La contraseña debe tener mínimo 6 caracteres.")
                    elif crear_usuario(nuevo_user.strip().lower(), nuevo_pass, nuevo_rol):
                        registrar_auditoria(0, "SISTEMA", "Alta Usuario", 0, usuario_sesion,
                                            f"Nuevo usuario: {nuevo_user.strip().lower()} ({nuevo_rol})")
                        st.success(f"✅ Cuenta '{nuevo_user.strip().lower()}' creada.")
                        st.rerun()
                    else:
                        st.error("❌ Ese nombre de usuario ya existe.")

        with tab2:
            if not df_u.empty:
                with st.form("form_cambiar_pass"):
                    user_cambiar   = st.selectbox("Usuario a actualizar", df_u["username"])
                    nueva_pass     = st.text_input("Nueva contraseña", type="password")
                    confirmar_pass = st.text_input("Confirmar nueva contraseña", type="password")

                    if st.form_submit_button("🔐 Actualizar Contraseña", type="primary"):
                        if not nueva_pass:
                            st.error("La contraseña no puede estar vacía.")
                        elif len(nueva_pass) < 6:
                            st.error("La contraseña debe tener mínimo 6 caracteres.")
                        elif nueva_pass != confirmar_pass:
                            st.error("Las contraseñas no coinciden.")
                        else:
                            cambiar_password(user_cambiar, nueva_pass)
                            registrar_auditoria(0, "SISTEMA", "Cambio Contraseña", 0, usuario_sesion,
                                                f"Contraseña actualizada: {user_cambiar}")
                            st.success(f"✅ Contraseña de '{user_cambiar}' actualizada.")

        with tab3:
            borrables = df_u[df_u["username"] != usuario_sesion]
            if not borrables.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                usr_borrar = st.selectbox("Usuario a eliminar", borrables["username"])
                conf_usr   = st.checkbox(f"Confirmo que deseo eliminar la cuenta de '{usr_borrar}'")

                if not conf_usr:
                    st.info("👆 Marca la casilla para habilitar la eliminación.")

                # Usamos el botón directo sin st.form para evitar el bug visual
                if st.button("🗑️ Eliminar Usuario", disabled=not conf_usr, type="primary"):
                    with st.spinner("Eliminando..."):
                        uid_borrar = int(borrables.loc[borrables["username"] == usr_borrar, "id"].values[0])
                        eliminar_usuario(uid_borrar)
                        registrar_auditoria(0, "SISTEMA", "Baja Usuario", 0, usuario_sesion,
                                            f"Usuario eliminado: {usr_borrar}")
                    st.success(f"✅ Usuario '{usr_borrar}' eliminado.")
                    st.rerun()
            else:
                st.info("No hay otras cuentas disponibles para eliminar.")