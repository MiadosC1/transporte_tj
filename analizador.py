import networkx as nx

def analizar(G):
    errores = []
    advertencias = []

    # 1. Nodos aislados
    aislados = [n for n in G.nodes() if G.degree(n) == 0]
    for n in aislados:
        errores.append(f"ERROR: '{n}' es un nodo aislado, no tiene conexiones.")

    # 2. Red conexa
    if not nx.is_connected(G):
        errores.append("ERROR: La red no es completamente conexa, hay zonas incomunicadas.")

    # 3. Pesos inválidos
    for u, v, data in G.edges(data=True):
        if data.get("weight", 0) <= 0:
            errores.append(f"ERROR: Conexión '{u}' -> '{v}' tiene peso inválido ({data['weight']}).")

    # 4. Paradas críticas (puntos de articulación)
    criticos = list(nx.articulation_points(G))
    for n in criticos:
        advertencias.append(f"ADVERTENCIA: '{n}' es parada crítica, su falla desconecta la red.")

    return errores, advertencias

def simular_falla(G, parada):
    if parada not in G.nodes():
        print(f"ERROR: '{parada}' no existe en la red.")
        return

    G_temp = G.copy()
    G_temp.remove_node(parada)

    print(f"\n=== SIMULACIÓN: falla de '{parada}' ===")
    if nx.is_connected(G_temp):
        print("La red sigue siendo conexa. No hay zonas incomunicadas.")
    else:
        componentes = list(nx.connected_components(G_temp))
        print(f"La red se fragmentó en {len(componentes)} zonas:")
        for i, comp in enumerate(componentes, 1):
            print(f"  Zona {i}: {sorted(comp)}")

def ruta_corta(G, origen, destino):
    if origen not in G.nodes():
        print(f"ERROR: '{origen}' no existe en la red.")
        return
    if destino not in G.nodes():
        print(f"ERROR: '{destino}' no existe en la red.")
        return

    try:
        ruta = nx.dijkstra_path(G, origen, destino, weight="weight")
        costo = nx.dijkstra_path_length(G, origen, destino, weight="weight")
        print(f"\n=== RUTA MÁS CORTA: {origen} → {destino} ===")
        print(f"Paradas: {' → '.join(ruta)}")
        print(f"Tiempo estimado: {costo} minutos")
    except nx.NetworkXNoPath:
        print(f"ERROR: No existe ruta entre '{origen}' y '{destino}'.")