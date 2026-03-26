import networkx as nx
import matplotlib.pyplot as plt
from datos import PARADAS, CONEXIONES

def construir_grafo():
    G = nx.Graph()
    G.add_nodes_from(PARADAS)
    for origen, destino, peso in CONEXIONES:
        G.add_edge(origen, destino, weight=peso)
    return G

def visualizar(G):
    criticos = list(nx.articulation_points(G))
    colores = ["red" if n in criticos else "steelblue" for n in G.nodes()]
    pesos = nx.get_edge_attributes(G, "weight")
    pos = nx.spring_layout(G)
    nx.draw(G, pos=pos, with_labels=True, node_color=colores,
            node_size=1500, font_size=10, font_color="white")
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=pesos)
    plt.title("Red de Transporte Público - Tijuana")
    plt.savefig("red_transporte.png")
    print("Grafo guardado como red_transporte.png")