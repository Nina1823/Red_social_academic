# Red Social Académica Avanzada

Aplicación interactiva en **Python** que modela una red social académica, visualizando colaboraciones entre estudiantes y analizando su estructura mediante métricas de red.

## 🧠 Funcionalidades
- Registro y edición de nodos con carrera e intereses.  
- Creación y eliminación de colaboraciones.  
- **Visualización gráfica** del grafo con colores por carrera.  
- **Recomendaciones interdisciplinarias** basadas en intereses y carreras distintas.  
- **Análisis de resiliencia** simulando la eliminación de nodos y su impacto.  
- **Detección de brechas** mediante métricas de centralidad (grado e intermediación).

## 🧩 Tecnologías
- `Python 3.10+`
- `Tkinter`
- `NetworkX`
- `Matplotlib`

## 📊 Visualización

El sistema ofrece distintos modos interactivos del grafo:

- **Normal:** muestra la red completa con colores por carrera.  
- **Recomendaciones:** líneas rojas punteadas señalan posibles conexiones interdisciplinarias.  
- **Resiliencia:** simula la eliminación de un nodo y muestra cómo se fragmenta la red.  
- **Brechas:** resalta en naranja los nodos más centrales (top 3) según métricas de grado.


## 🚀 Ejecución
```bash
python red_social_academica_avanzada.py
