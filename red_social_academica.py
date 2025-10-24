# red_social_academica_avanzada.py
# Sistema avanzado con visualización interactiva en el grafo

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import defaultdict
import math

# -----------------------------
# Estado en memoria
# -----------------------------
nodes: dict[str, dict] = {}
collaborations: list[tuple[str, str]] = []
removed_nodes: set[str] = set()  # Nodos temporalmente removidos
suggested_connections: list[tuple[str, str]] = []  # Conexiones sugeridas
visualization_mode: str = "normal"  # normal, recommendations, resilience, gaps

# -----------------------------
# Colores por carrera
# -----------------------------
COLOR_MAP = {
    "Ing.": "#87CEEB",
    "Int.": "#90EE90",
    "Med.": "#FA8072",
    "Adm.": "#FFD700",
    "Mat.": "#DDA0DD",
    "Eco.": "#F0E68C",
}

# -----------------------------
# Utilidades
# -----------------------------
def normalize_pair(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a <= b else (b, a)

def parse_interests(text: str) -> set[str]:
    return {p.strip() for p in text.split(",") if p.strip()}

# -----------------------------
# 1. RECOMENDACIÓN INTERDISCIPLINARIA
# -----------------------------
def calculate_interdisciplinary_score(n1: str, n2: str) -> float:
    """Calcula puntuación de recomendación interdisciplinaria"""
    if n1 not in nodes or n2 not in nodes:
        return 0.0
    
    info1, info2 = nodes[n1], nodes[n2]
    score = 0.0
    
    # Bonus por carreras diferentes (interdisciplinariedad)
    if info1["carrera"] != info2["carrera"]:
        score += 3.0
    
    # Coincidencia de intereses (Jaccard similarity)
    int1, int2 = info1["intereses"], info2["intereses"]
    if int1 or int2:
        intersection = len(int1 & int2)
        union = len(int1 | int2)
        if union > 0:
            jaccard = intersection / union
            score += jaccard * 2.0
    
    return score

def recommend_interdisciplinary_connections(top_n: int = 10) -> list[tuple[str, str, float]]:
    """Genera recomendaciones de conexiones interdisciplinarias"""
    recommendations = []
    node_list = list(nodes.keys())
    
    for i, n1 in enumerate(node_list):
        for n2 in node_list[i+1:]:
            pair = normalize_pair(n1, n2)
            if pair not in collaborations:
                score = calculate_interdisciplinary_score(n1, n2)
                if score > 0:
                    recommendations.append((n1, n2, score))
    
    recommendations.sort(key=lambda x: x[2], reverse=True)
    return recommendations[:top_n]

# -----------------------------
# 2. ANÁLISIS DE RESILIENCIA
# -----------------------------
def calculate_network_metrics(G: nx.Graph) -> dict:
    """Calcula métricas básicas de la red"""
    if len(G) == 0:
        return {
            "nodos": 0,
            "aristas": 0,
            "componentes": 0
        }
    
    metrics = {
        "nodos": G.number_of_nodes(),
        "aristas": G.number_of_edges(),
        "componentes": nx.number_connected_components(G)
    }
    
    return metrics

# -----------------------------
# 3. DETECCIÓN DE BRECHAS (CENTRALIDAD Y SUGERENCIAS)
# -----------------------------
def calculate_centrality_metrics() -> dict:
    """Calcula métricas de centralidad para todos los nodos"""
    G = nx.Graph()
    for n in nodes:
        if n not in removed_nodes:
            G.add_node(n)
    for a, b in collaborations:
        if a not in removed_nodes and b not in removed_nodes:
            G.add_edge(a, b)
    
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    
    degree_cent = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G)
    
    # Combinar métricas
    combined = {}
    for node in G.nodes():
        combined[node] = {
            "grado": degree_cent.get(node, 0),
            "intermediacion": betweenness_cent.get(node, 0),
            "score_total": degree_cent.get(node, 0) * 0.5 + betweenness_cent.get(node, 0) * 0.5
        }
    
    return combined

def suggest_gap_filling_connections(top_n: int = 10) -> list[tuple[str, str, float, str]]:
    """Sugiere conexiones para llenar brechas de conocimiento"""
    suggestions = []
    node_list = [n for n in nodes.keys() if n not in removed_nodes]
    
    # Calcular centralidad
    centrality = calculate_centrality_metrics()
    
    for i, n1 in enumerate(node_list):
        for n2 in node_list[i+1:]:
            pair = normalize_pair(n1, n2)
            if pair not in collaborations:
                # Calcular similitud de intereses
                int1, int2 = nodes[n1]["intereses"], nodes[n2]["intereses"]
                common = int1 & int2
                
                if common:
                    # Score basado en intereses comunes y centralidad
                    similarity = len(common) / max(len(int1), len(int2))
                    
                    # Bonus si uno de los nodos es líder (alta centralidad)
                    cent_bonus = 0
                    if centrality:
                        cent1 = centrality.get(n1, {}).get("score_total", 0)
                        cent2 = centrality.get(n2, {}).get("score_total", 0)
                        cent_bonus = max(cent1, cent2) * 0.5
                    
                    total_score = similarity + cent_bonus
                    reason = f"Intereses: {', '.join(sorted(common))}"
                    
                    suggestions.append((n1, n2, total_score, reason))
    
    suggestions.sort(key=lambda x: x[2], reverse=True)
    return suggestions[:top_n]

# -----------------------------
# Dibujar grafo con diferentes modos
# -----------------------------
def draw_graph():
    global visualization_mode
    
    for widget in graph_frame.winfo_children():
        widget.destroy()

    G = nx.Graph()
    active_nodes = [n for n in nodes.keys() if n not in removed_nodes]
    
    for nombre in active_nodes:
        info = nodes[nombre]
        G.add_node(nombre, carrera=info["carrera"], intereses=info["intereses"])
    
    for a, b in collaborations:
        if a not in removed_nodes and b not in removed_nodes:
            G.add_edge(a, b)

    fig = plt.Figure(figsize=(6.5, 5), dpi=100)
    ax = fig.add_subplot(111)
    
    if visualization_mode == "normal":
        ax.set_title("Red Académica - Vista Normal", fontsize=14, fontweight="bold")
    elif visualization_mode == "recommendations":
        ax.set_title("Red Académica - Recomendaciones Interdisciplinarias", fontsize=12, fontweight="bold")
    elif visualization_mode == "resilience":
        ax.set_title("Red Académica - Análisis de Resiliencia", fontsize=12, fontweight="bold")
    elif visualization_mode == "gaps":
        ax.set_title("Red Académica - Detección de Brechas", fontsize=12, fontweight="bold")

    if len(G.nodes) == 0:
        ax.text(0.5, 0.5, "(sin nodos activos)", ha="center", va="center", color="#777")
        ax.axis("off")
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return

    pos = nx.spring_layout(G, seed=42, k=1.2, iterations=100)
    
    # Dibujar según el modo
    if visualization_mode == "normal":
        # Vista normal
        node_colors = [COLOR_MAP.get(G.nodes[n].get("carrera", ""), "#C0C0C0") for n in G.nodes()]
        nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, alpha=0.6, edge_color="#555")
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=650, edgecolors="black")
        
    elif visualization_mode == "recommendations":
        # Mostrar recomendaciones interdisciplinarias en rojo punteado
        node_colors = [COLOR_MAP.get(G.nodes[n].get("carrera", ""), "#C0C0C0") for n in G.nodes()]
        nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, alpha=0.6, edge_color="#555")
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=650, edgecolors="black")
        
        # Dibujar conexiones sugeridas
        for n1, n2 in suggested_connections:
            if n1 in pos and n2 in pos:
                x1, y1 = pos[n1]
                x2, y2 = pos[n2]
                ax.plot([x1, x2], [y1, y2], 'r--', linewidth=2, alpha=0.7, zorder=1)
        
        # Leyenda
        ax.plot([], [], 'r--', linewidth=2, label='Recomendaciones')
        ax.legend(loc='upper right')
        
    elif visualization_mode == "resilience":
        # Resaltar componentes desconectados con colores diferentes
        components = list(nx.connected_components(G))
        component_colors = ['#87CEEB', '#90EE90', '#FA8072', '#FFD700', '#DDA0DD']
        
        node_colors = []
        for node in G.nodes():
            for idx, component in enumerate(components):
                if node in component:
                    node_colors.append(component_colors[idx % len(component_colors)])
                    break
        
        nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, alpha=0.6, edge_color="#555")
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=650, 
                              edgecolors="black", linewidths=2)
        
        # Mostrar métricas
        metrics = calculate_network_metrics(G)
        metrics_text = f"Componentes: {metrics['componentes']}\n"
        metrics_text += f"Aristas: {metrics['aristas']}"
        ax.text(0.02, 0.98, metrics_text, transform=ax.transAxes, 
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
    elif visualization_mode == "gaps":
        # Calcular centralidad y destacar nodos centrales
        centrality = calculate_centrality_metrics()
        
        if centrality:
            # Identificar top 3 nodos más centrales
            sorted_by_centrality = sorted(centrality.items(), 
                                         key=lambda x: x[1]["grado"], reverse=True)
            top_central = {node for node, _ in sorted_by_centrality[:3]}
            
            node_colors = []
            node_sizes = []
            for node in G.nodes():
                if node in top_central:
                    node_colors.append("#FF4500")  # Naranja rojizo para nodos centrales
                    node_sizes.append(900)
                else:
                    node_colors.append(COLOR_MAP.get(G.nodes[node].get("carrera", ""), "#C0C0C0"))
                    node_sizes.append(650)
        else:
            node_colors = [COLOR_MAP.get(G.nodes[n].get("carrera", ""), "#C0C0C0") for n in G.nodes()]
            node_sizes = [650 for _ in G.nodes()]
        
        nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, alpha=0.6, edge_color="#555")
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes, 
                              edgecolors="black", linewidths=2)
        
        # Leyenda para nodos centrales
        if centrality and top_central:
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF4500', 
                      markersize=10, label='Nodos Centrales (Top 3)')
            ]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
    
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=9, font_weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=1)
    )

    ax.axis("off")
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# -----------------------------
# Acciones básicas
# -----------------------------
def refresh_nodes_table(data: dict[str, dict] | None = None):
    table = nodes_tv
    for i in table.get_children():
        table.delete(i)
    src = data if data is not None else nodes
    for nombre, info in src.items():
        if nombre not in removed_nodes:
            intereses_txt = ", ".join(sorted(info["intereses"])) if info["intereses"] else ""
            table.insert("", "end", iid=nombre, values=(info["carrera"], intereses_txt), text=nombre)

def refresh_collab_table():
    table = collab_tv
    for i in table.get_children():
        table.delete(i)
    for a, b in collaborations:
        if a not in removed_nodes and b not in removed_nodes:
            table.insert("", "end", values=(a, b))

def add_or_update_node():
    nombre = nodo_nombre_var.get().strip()
    carrera = nodo_carrera_var.get().strip()
    intereses = parse_interests(nodo_intereses_var.get())

    if not nombre or not carrera:
        messagebox.showwarning("Campos obligatorios", "Nombre y Carrera son obligatorios.")
        return

    nodes[nombre] = {"carrera": carrera, "intereses": intereses}
    removed_nodes.discard(nombre)  # Si estaba removido, restaurarlo
    refresh_nodes_table()
    draw_graph()
    messagebox.showinfo("Éxito", f"Nodo '{nombre}' agregado/actualizado.")

def add_collaboration():
    n1, n2 = colab_n1_var.get().strip(), colab_n2_var.get().strip()
    if not n1 or not n2:
        messagebox.showwarning("Campos obligatorios", "Nodo 1 y Nodo 2 son obligatorios.")
        return
    if n1 == n2:
        messagebox.showwarning("Validación", "Seleccione dos nodos distintos.")
        return
    if n1 not in nodes or n2 not in nodes:
        messagebox.showwarning("Validación", "Ambos nodos deben existir.")
        return
    pair = normalize_pair(n1, n2)
    if pair in collaborations:
        messagebox.showinfo("Duplicado", "La colaboración ya existe.")
        return
    collaborations.append(pair)
    refresh_collab_table()
    draw_graph()
    messagebox.showinfo("Agregado", f"Colaboración {pair[0]} — {pair[1]} creada.")

def delete_collaboration():
    n1, n2 = colab_n1_var.get().strip(), colab_n2_var.get().strip()
    if not n1 or not n2:
        messagebox.showwarning("Campos obligatorios", "Nodo 1 y Nodo 2 son obligatorios.")
        return
    pair = normalize_pair(n1, n2)
    if pair not in collaborations:
        messagebox.showinfo("Sin cambios", "No se encontró esa colaboración.")
        return
    collaborations.remove(pair)
    refresh_collab_table()
    draw_graph()
    messagebox.showinfo("Eliminado", f"Colaboración {pair[0]} — {pair[1]} eliminada.")

# -----------------------------
# Acciones avanzadas con visualización
# -----------------------------
def show_interdisciplinary_recommendations():
    """Activa modo de recomendaciones interdisciplinarias"""
    global visualization_mode, suggested_connections
    
    recommendations = recommend_interdisciplinary_connections(8)
    
    if not recommendations:
        messagebox.showinfo("Recomendaciones", "No hay recomendaciones interdisciplinarias disponibles.")
        return
    
    visualization_mode = "recommendations"
    suggested_connections = [(n1, n2) for n1, n2, _ in recommendations]
    draw_graph()
    
    # Mostrar ventana con detalles
    window = tk.Toplevel(root)
    window.title("Recomendaciones Interdisciplinarias")
    window.geometry("700x450")
    
    text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=16)
    text.pack(padx=10, pady=10, fill="both", expand=True)
    
    text.insert(tk.END, "=== RECOMENDACIONES INTERDISCIPLINARIAS ===\n\n")
    text.insert(tk.END, "Las líneas rojas punteadas en el grafo muestran las conexiones sugeridas.\n")
    text.insert(tk.END, "Haga clic en 'Aplicar Conexión' para agregar la colaboración a la red.\n\n")
    
    for i, (n1, n2, score) in enumerate(recommendations, 1):
        c1 = nodes[n1]["carrera"]
        c2 = nodes[n2]["carrera"]
        int1 = nodes[n1]["intereses"]
        int2 = nodes[n2]["intereses"]
        common = int1 & int2
        
        text.insert(tk.END, f"{i}. {n1} ({c1}) ↔ {n2} ({c2})\n")
        text.insert(tk.END, f"   Puntuación: {score:.2f}\n")
        if common:
            text.insert(tk.END, f"   Intereses comunes: {', '.join(sorted(common))}\n")
        text.insert(tk.END, "\n")
    
    text.config(state=tk.DISABLED)
    
    # Frame para aplicar conexiones
    frame_bottom = ttk.Frame(window, padding=10)
    frame_bottom.pack(fill="x")
    
    ttk.Label(frame_bottom, text="Aplicar conexión (formato: Nodo1,Nodo2):").pack(side="left", padx=5)
    connection_var = tk.StringVar()
    ttk.Entry(frame_bottom, textvariable=connection_var, width=25).pack(side="left", padx=5)
    
    def apply_connection():
        conn = connection_var.get().strip()
        if not conn:
            messagebox.showwarning("Campo vacío", "Ingrese una conexión (ej: María,Pedro)")
            return
        
        parts = [p.strip() for p in conn.split(",")]
        if len(parts) != 2:
            messagebox.showwarning("Formato inválido", "Use el formato: Nodo1,Nodo2")
            return
        
        n1, n2 = parts
        if n1 not in nodes or n2 not in nodes:
            messagebox.showwarning("Nodos no existen", "Ambos nodos deben existir en la red.")
            return
        
        pair = normalize_pair(n1, n2)
        if pair in collaborations:
            messagebox.showinfo("Ya existe", "Esta colaboración ya está en la red.")
            return
        
        collaborations.append(pair)
        refresh_collab_table()
        draw_graph()
        messagebox.showinfo("Éxito", f"Colaboración {n1} ↔ {n2} agregada a la red.")
        connection_var.set("")
    
    ttk.Button(frame_bottom, text="Aplicar Conexión", command=apply_connection).pack(side="left", padx=5)
    ttk.Button(frame_bottom, text="Cerrar", command=lambda: [window.destroy(), reset_normal_mode()]).pack(side="left", padx=5)

def show_resilience_analysis():
    """Activa modo de análisis de resiliencia"""
    global visualization_mode
    
    window = tk.Toplevel(root)
    window.title("Análisis de Resiliencia")
    window.geometry("700x500")
    
    frame_top = ttk.Frame(window, padding=10)
    frame_top.pack(fill="x")
    
    ttk.Label(frame_top, text="Simular eliminación del nodo:").grid(row=0, column=0, padx=5)
    node_var = tk.StringVar()
    combo = ttk.Combobox(frame_top, textvariable=node_var, 
                         values=[n for n in nodes.keys() if n not in removed_nodes], width=20)
    combo.grid(row=0, column=1, padx=5)
    
    text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=20)
    text.pack(padx=10, pady=10, fill="both", expand=True)
    
    def run_simulation():
        node_name = node_var.get()
        
        if not node_name:
            text.delete(1.0, tk.END)
            text.insert(tk.END, "Por favor seleccione un nodo.\n")
            return
        
        if node_name not in nodes or node_name in removed_nodes:
            text.delete(1.0, tk.END)
            text.insert(tk.END, f"El nodo '{node_name}' no está disponible.\n")
            return
        
        # Calcular métricas antes
        G_before = nx.Graph()
        for n in nodes:
            if n not in removed_nodes:
                G_before.add_node(n)
        for a, b in collaborations:
            if a not in removed_nodes and b not in removed_nodes:
                G_before.add_edge(a, b)
        
        metrics_before = calculate_network_metrics(G_before)
        
        # Remover nodo temporalmente
        removed_nodes.add(node_name)
        visualization_mode = "resilience"
        draw_graph()
        refresh_nodes_table()
        refresh_collab_table()
        
        # Calcular métricas después
        G_after = nx.Graph()
        for n in nodes:
            if n not in removed_nodes:
                G_after.add_node(n)
        for a, b in collaborations:
            if a not in removed_nodes and b not in removed_nodes:
                G_after.add_edge(a, b)
        
        metrics_after = calculate_network_metrics(G_after)
        
        text.delete(1.0, tk.END)
        text.insert(tk.END, f"=== ANÁLISIS DE RESILIENCIA: Eliminación de '{node_name}' ===\n\n")
        text.insert(tk.END, "El grafo ahora muestra la red sin el nodo eliminado.\n")
        text.insert(tk.END, "Los componentes desconectados se muestran en diferentes colores.\n\n")
        
        text.insert(tk.END, "MÉTRICAS ANTES:\n")
        for key, val in metrics_before.items():
            text.insert(tk.END, f"  {key.capitalize()}: {val}\n")
        
        text.insert(tk.END, "\nMÉTRICAS DESPUÉS:\n")
        for key, val in metrics_after.items():
            text.insert(tk.END, f"  {key.capitalize()}: {val}\n")
        
        text.insert(tk.END, "\nIMPACTO:\n")
        comp_change = metrics_after["componentes"] - metrics_before["componentes"]
        edge_change = metrics_before["aristas"] - metrics_after["aristas"]
        
        text.insert(tk.END, f"  Componentes nuevos: {comp_change}\n")
        text.insert(tk.END, f"  Conexiones perdidas: {edge_change}\n")
        
        if comp_change > 0:
            text.insert(tk.END, f"\n⚠️ ALERTA: La red se fragmentó en {comp_change} componente(s) adicional(es)!\n")
        if edge_change > 3:
            text.insert(tk.END, f"⚠️ ALERTA: Se perdieron {edge_change} conexiones. ¡Nodo crítico!\n")
    
    def restore_node():
        node_name = node_var.get()
        if node_name in removed_nodes:
            removed_nodes.remove(node_name)
            visualization_mode = "normal"
            draw_graph()
            refresh_nodes_table()
            refresh_collab_table()
            text.delete(1.0, tk.END)
            text.insert(tk.END, f"Nodo '{node_name}' restaurado. Red vuelta a la normalidad.\n")
            combo['values'] = [n for n in nodes.keys() if n not in removed_nodes]
    
    ttk.Button(frame_top, text="🗑️ Simular Eliminación", command=run_simulation).grid(row=0, column=2, padx=5)
    ttk.Button(frame_top, text="↩️ Restaurar Nodo", command=restore_node).grid(row=0, column=3, padx=5)
    
    frame_bottom = ttk.Frame(window, padding=10)
    frame_bottom.pack(fill="x")
    ttk.Button(frame_bottom, text="Cerrar y Restaurar Todo", 
              command=lambda: [removed_nodes.clear(), window.destroy(), reset_normal_mode()]).pack()

def show_gap_analysis():
    """Activa modo de detección de brechas"""
    global visualization_mode, suggested_connections
    
    centrality = calculate_centrality_metrics()
    
    visualization_mode = "gaps"
    suggested_connections = []
    draw_graph()
    
    window = tk.Toplevel(root)
    window.title("Detección de Brechas de Conocimiento")
    window.geometry("650x400")
    
    text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=75, height=22)
    text.pack(padx=10, pady=10, fill="both", expand=True)
    
    text.insert(tk.END, "=== LÍDERES EN LA RED (Centralidad de Grado) ===\n\n")
    text.insert(tk.END, "Los nodos se destacan en color naranja rojizo para los top 3 más centrales.\n")
    text.insert(tk.END, "La centralidad de grado indica cuántas conexiones tiene cada nodo.\n\n")
    
    if not centrality:
        text.insert(tk.END, "No hay suficientes conexiones para calcular métricas.\n\n")
    else:
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1]["grado"], reverse=True)
        
        for i, (node, metrics) in enumerate(sorted_nodes[:10], 1):
            carrera = nodes[node]["carrera"]
            marker = "⭐" if i <= 3 else "  "
            text.insert(tk.END, f"{marker} {i}. {node} ({carrera})\n")
            text.insert(tk.END, f"   Centralidad de grado: {metrics['grado']:.3f}\n")
            text.insert(tk.END, f"   Número de conexiones: {int(metrics['grado'] * (len(centrality) - 1))}\n\n")
    
    text.config(state=tk.DISABLED)
    
    ttk.Button(window, text="Cerrar", command=lambda: [window.destroy(), reset_normal_mode()]).pack(pady=5)

def reset_normal_mode():
    """Vuelve al modo de visualización normal"""
    global visualization_mode, suggested_connections
    visualization_mode = "normal"
    suggested_connections = []
    removed_nodes.clear()
    draw_graph()
    refresh_nodes_table()
    refresh_collab_table()

# -----------------------------
# Datos de ejemplo
# -----------------------------
def seed_example_data():
    example = [
        ("María", "Ing.", {"IA", "Programación", "Algoritmos"}),
        ("Ana", "Ing.", {"Sistemas", "IA", "Bases de datos"}),
        ("Luis", "Int.", {"Redes", "Seguridad"}),
        ("Carlos", "Ing.", {"Programación", "Web"}),
        ("Sofía", "Int.", {"Datos", "IA", "Estadística"}),
        ("Elena", "Med.", {"Biología", "Genética"}),
        ("Jorge", "Adm.", {"Gestión", "Economía"}),
        ("Pedro", "Mat.", {"Álgebra", "Algoritmos", "Lógica"}),
        ("Laura", "Eco.", {"Economía", "Estadística", "Datos"}),
    ]
    for nombre, carrera, intereses in example:
        nodes[nombre] = {"carrera": carrera, "intereses": set(intereses)}
    for pair in [("Ana", "María"), ("Carlos", "María"), ("Sofía", "Ana"), ("Pedro", "María")]:
        collaborations.append(normalize_pair(*pair))

# -----------------------------
# Construcción UI
# -----------------------------
root = tk.Tk()
root.title("Red Social Académica - Sistema Avanzado Interactivo")
root.geometry("1200x750")
PAD = 6

main = ttk.Frame(root)
main.pack(fill="both", expand=True)

left = ttk.Frame(main, padding=PAD)
left.grid(row=0, column=0, sticky="nsew")
separator = tk.Canvas(main, width=2, bg="#dddddd", highlightthickness=0)
separator.grid(row=0, column=1, sticky="ns")
right = ttk.Frame(main, padding=PAD)
right.grid(row=0, column=2, sticky="nsew")

main.columnconfigure(0, weight=3)
main.columnconfigure(2, weight=2)
main.rowconfigure(0, weight=1)

# ---- Sección izquierda ----
ttk.Label(left, text="Tabla Nodos", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="w")
nodes_tv = ttk.Treeview(left, columns=("carrera", "intereses"), show="tree headings", height=5)
nodes_tv.heading("#0", text="Nombre")
nodes_tv.heading("carrera", text="Carrera")
nodes_tv.heading("intereses", text="Int.")
nodes_tv.column("#0", width=120)
nodes_tv.column("carrera", width=70)
nodes_tv.column("intereses", width=220)
nodes_tv.grid(row=1, column=0, sticky="ew")

# Formulario Nodo
nodo_nombre_var = tk.StringVar()
nodo_carrera_var = tk.StringVar()
nodo_intereses_var = tk.StringVar()
frm_nodo = ttk.Frame(left)
frm_nodo.grid(row=2, column=0, sticky="ew", pady=(2, 8))
ttk.Label(frm_nodo, text="Nombre:").grid(row=0, column=0, sticky="w")
ttk.Entry(frm_nodo, textvariable=nodo_nombre_var).grid(row=0, column=1, sticky="ew")
ttk.Label(frm_nodo, text="Carrera:").grid(row=1, column=0, sticky="w")
ttk.Entry(frm_nodo, textvariable=nodo_carrera_var).grid(row=1, column=1, sticky="ew")
ttk.Label(frm_nodo, text="Intereses (coma):").grid(row=2, column=0, sticky="w")
ttk.Entry(frm_nodo, textvariable=nodo_intereses_var).grid(row=2, column=1, sticky="ew")
ttk.Button(frm_nodo, text="Agregar/Actualizar Nodo", command=add_or_update_node).grid(row=3, column=0, columnspan=2, sticky="ew")

# Tabla Colaboraciones
ttk.Label(left, text="Tabla Colaboraciones", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, sticky="w")
collab_tv = ttk.Treeview(left, columns=("n1", "n2"), show="headings", height=5)
collab_tv.heading("n1", text="Nodo1")
collab_tv.heading("n2", text="Nodo2")
collab_tv.column("n1", width=120)
collab_tv.column("n2", width=120)
collab_tv.grid(row=4, column=0, sticky="ew")

colab_n1_var = tk.StringVar()
colab_n2_var = tk.StringVar()
frm_colab = ttk.Frame(left)
frm_colab.grid(row=5, column=0, sticky="ew", pady=(2, 8))
ttk.Label(frm_colab, text="Nodo 1:").grid(row=0, column=0, sticky="w")
ttk.Entry(frm_colab, textvariable=colab_n1_var).grid(row=0, column=1, sticky="ew")
ttk.Label(frm_colab, text="Nodo 2:").grid(row=0, column=2, sticky="w")
ttk.Entry(frm_colab, textvariable=colab_n2_var).grid(row=0, column=3, sticky="ew")
ttk.Button(frm_colab, text="Agregar", command=add_collaboration).grid(row=1, column=0, columnspan=2, sticky="ew")
ttk.Button(frm_colab, text="Eliminar", command=delete_collaboration).grid(row=1, column=2, columnspan=2, sticky="ew")

# Panel de análisis avanzado
ttk.Label(left, text="Análisis Avanzado Interactivo", font=("TkDefaultFont", 10, "bold")).grid(row=6, column=0, sticky="w", pady=(10, 2))
frm_analysis = ttk.Frame(left)
frm_analysis.grid(row=7, column=0, sticky="ew")
frm_analysis.columnconfigure(0, weight=1)

ttk.Button(frm_analysis, text="🔗 Recomendaciones Interdisciplinarias", 
          command=show_interdisciplinary_recommendations).grid(row=0, column=0, sticky="ew", pady=2)
ttk.Button(frm_analysis, text="🛡️ Análisis de Resiliencia", 
          command=show_resilience_analysis).grid(row=1, column=0, sticky="ew", pady=2)
ttk.Button(frm_analysis, text="🎯 Detección de Brechas", 
          command=show_gap_analysis).grid(row=2, column=0, sticky="ew", pady=2)
ttk.Button(frm_analysis, text="↩️ Restaurar Vista Normal", 
          command=reset_normal_mode, style="Accent.TButton").grid(row=3, column=0, sticky="ew", pady=(8, 2))

# ---- Sección derecha: Grafo ----
ttk.Label(right, text="Visualización de la Red", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w")

# Tabla de leyenda de colores
legend_frame = ttk.LabelFrame(right, text="Leyenda de Carreras", padding=5)
legend_frame.grid(row=1, column=0, sticky="ew", pady=(4, 4))

# Crear tabla de leyenda
legend_items = [
    ("Ing.", "Ingeniería", "#87CEEB"),
    ("Int.", "Inteligencia de negocios", "#90EE90"),
    ("Med.", "Medicina", "#FA8072"),
    ("Adm.", "Administración", "#FFD700"),
    ("Mat.", "Matemáticas", "#DDA0DD"),
    ("Eco.", "Economía", "#F0E68C"),
]

for i, (code, name, color) in enumerate(legend_items):
    row = i // 2
    col = (i % 2) * 3
    
    # Cuadro de color
    color_canvas = tk.Canvas(legend_frame, width=20, height=20, bg=color, 
                            highlightthickness=1, highlightbackground="black")
    color_canvas.grid(row=row, column=col, padx=(5, 2), pady=2)
    
    # Texto
    ttk.Label(legend_frame, text=f"{code} = {name}", font=("TkDefaultFont", 9)).grid(
        row=row, column=col+1, sticky="w", padx=(0, 10), pady=2)

graph_frame = ttk.Frame(right, width=380, height=360)
graph_frame.grid(row=2, column=0, sticky="nsew", pady=(4, 8))

right.rowconfigure(2, weight=1)
right.columnconfigure(0, weight=1)

# -----------------------------
# Inicialización
# -----------------------------
seed_example_data()
refresh_nodes_table()
refresh_collab_table()
draw_graph()

root.mainloop()