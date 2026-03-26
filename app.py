from flask import Flask, render_template, request, jsonify
from grafo import construir_grafo, visualizar
from analizador import analizar, simular_falla, ruta_corta
import io
import base64
import matplotlib.pyplot as plt
import networkx as nx

app = Flask(__name__)
G = construir_grafo()

@app.route("/")
def index():
    return render_template("index.html", paradas=list(G.nodes()))

@app.route("/analizar")
def analizar_red():
    errores, advertencias = analizar(G)
    return jsonify({"errores": errores, "advertencias": advertencias})

@app.route("/ruta")
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

if __name__ == "__main__":
    app.run(debug=True)