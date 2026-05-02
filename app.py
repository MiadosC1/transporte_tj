from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from grafo import construir_grafo
from analizador import analizar, simular_falla, ruta_corta
from database import db, Usuario
import io
import base64
import matplotlib.pyplot as plt
import networkx as nx

app = Flask(__name__)
app.secret_key = "transporte_tj_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Debes iniciar sesión para acceder."

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

G = construir_grafo()

# ─── AUTH ─────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos.")
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if Usuario.query.filter_by(username=username).first():
            flash("El usuario ya existe.")
            return redirect(url_for("registro"))
        user = Usuario(username=username, rol="usuario")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("index"))
    return render_template("registro.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ─── RUTAS PRINCIPALES ────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    return render_template("index.html", paradas=list(G.nodes()), user=current_user)

@app.route("/analizar")
@login_required
def analizar_red():
    errores, advertencias = analizar(G)
    return jsonify({"errores": errores, "advertencias": advertencias})

@app.route("/ruta")
@login_required
def calcular_ruta():
    origen = request.args.get("origen")
    destino = request.args.get("destino")
    try:
        ruta = nx.dijkstra_path(G, origen, destino, weight="weight")
        costo = nx.dijkstra_path_length(G, origen, destino, weight="weight")
        return jsonify({"ruta": ruta, "tiempo": costo})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/grafo")
@login_required
def grafo_imagen():
    criticos = list(nx.articulation_points(G))
    colores = ["red" if n in criticos else "steelblue" for n in G.nodes()]
    pos = nx.spring_layout(G, seed=42)
    pesos = nx.get_edge_attributes(G, "weight")
    plt.figure(figsize=(10, 7))
    nx.draw(G, pos=pos, with_labels=True, node_color=colores,
            node_size=1500, font_size=10, font_color="white")
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=pesos)
    plt.title("Red de Transporte Público - Tijuana")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode("utf-8")
    return jsonify({"imagen": img})

@app.route("/mapa")
@login_required
def mapa():
    from datos import COORDENADAS
    nodos = []
    criticos = list(nx.articulation_points(G))
    for nodo in G.nodes():
        if nodo in COORDENADAS:
            nodos.append({
                "nombre": nodo,
                "coords": COORDENADAS[nodo],
                "critico": nodo in criticos
            })
    aristas = []
    for u, v, data in G.edges(data=True):
        if u in COORDENADAS and v in COORDENADAS:
            aristas.append({
                "origen": COORDENADAS[u],
                "destino": COORDENADAS[v],
                "peso": data.get("weight", 0)
            })
    return render_template("mapa.html", nodos=nodos, aristas=aristas)

# ─── ADMIN ────────────────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
def admin_panel():
    if current_user.rol != "admin":
        return redirect(url_for("index"))
    usuarios = Usuario.query.all()
    return render_template("admin.html", 
        paradas=list(G.nodes()),
        aristas=list(G.edges(data=True)),
        usuarios=usuarios,
        user=current_user
    )

@app.route("/admin/agregar_parada", methods=["POST"])
@login_required
def agregar_parada():
    if current_user.rol != "admin":
        return jsonify({"error": "Sin permisos"}), 403
    nombre = request.form.get("nombre")
    if nombre and nombre not in G.nodes():
        G.add_node(nombre)
        return jsonify({"ok": True, "mensaje": f"Parada '{nombre}' agregada."})
    return jsonify({"error": "Nombre inválido o ya existe."})

@app.route("/admin/agregar_conexion", methods=["POST"])
@login_required
def agregar_conexion():
    if current_user.rol != "admin":
        return jsonify({"error": "Sin permisos"}), 403
    origen = request.form.get("origen")
    destino = request.form.get("destino")
    peso = request.form.get("peso")
    try:
        peso = int(peso)
        if origen in G.nodes() and destino in G.nodes():
            G.add_edge(origen, destino, weight=peso)
            return jsonify({"ok": True, "mensaje": f"Conexión {origen} → {destino} agregada."})
        return jsonify({"error": "Una o ambas paradas no existen."})
    except:
        return jsonify({"error": "Peso inválido."})

@app.route("/admin/eliminar_parada", methods=["POST"])
@login_required
def eliminar_parada():
    if current_user.rol != "admin":
        return jsonify({"error": "Sin permisos"}), 403
    nombre = request.form.get("nombre")
    if nombre in G.nodes():
        G.remove_node(nombre)
        return jsonify({"ok": True, "mensaje": f"Parada '{nombre}' eliminada."})
    return jsonify({"error": "Parada no encontrada."})

if __name__ == "__main__":
    app.run(debug=True)