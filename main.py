from grafo import construir_grafo, visualizar
from analizador import analizar, simular_falla, ruta_corta

G = construir_grafo()
errores, advertencias = analizar(G)

print("=== ANÁLISIS SEMÁNTICO ===")
if errores:
    for e in errores:
        print(e)
else:
    print("Sin errores estructurales.")

if advertencias:
    for a in advertencias:
        print(a)
else:
    print("Sin paradas críticas.")

simular_falla(G, "Centro")
ruta_corta(G, "IMSS", "El Florido")

visualizar(G)