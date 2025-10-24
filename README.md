# 🧠 Red Social Académica Avanzada

Aplicación interactiva desarrollada en **Python** que modela una **red social académica**, permitiendo analizar colaboraciones, detectar brechas de conocimiento y evaluar la resiliencia del sistema mediante visualizaciones dinámicas.

---

## 🚀 Descripción General

Este sistema permite crear y analizar una red de estudiantes, docentes o investigadores, donde cada nodo representa una persona con su **carrera** e **intereses académicos**, y cada arista representa una **colaboración** entre ellos.  
El programa incorpora análisis avanzados de **interdisciplinariedad**, **resiliencia estructural** y **centralidad**, todo dentro de una interfaz gráfica creada con **Tkinter** y visualización mediante **NetworkX** y **Matplotlib**.

---

## 🧩 Características Principales

### 👥 Gestión de Nodos
- Crear, editar y eliminar personas (nodos).
- Registrar carrera e intereses separados por comas.
- Colores personalizados según carrera para identificación rápida.

### 🔗 Colaboraciones
- Agregar o eliminar relaciones entre nodos.
- Validaciones para evitar duplicados o conexiones inválidas.
- Visualización automática de las nuevas conexiones en el grafo.

### 📊 Análisis Interactivo
- **Recomendaciones interdisciplinarias:**  
  Sugiere nuevas conexiones entre personas de distintas carreras con intereses similares.  
  Las líneas rojas punteadas en el grafo representan las sugerencias.

- **Análisis de resiliencia:**  
  Permite simular la eliminación de un nodo y observar cómo cambia la estructura de la red.  
  Muestra el número de componentes y las conexiones perdidas.

- **Detección de brechas:**  
  Calcula métricas de **centralidad de grado** e **intermediación** para identificar los nodos más influyentes y las posibles áreas desconectadas.

### 🧮 Métricas Internas
- Número de nodos y aristas.
- Número de componentes conectados.
- Centralidad de grado e intermediación por nodo.
- Puntuación combinada de relevancia.

---

## 📊 Visualización

El grafo interactivo puede mostrarse en distintos modos:

- **Normal:** visualización base con colores por carrera.  
- **Recomendaciones:** muestra sugerencias interdisciplinarias con líneas rojas punteadas.  
- **Resiliencia:** simula eliminación de nodos y colorea los componentes desconectados.  
- **Brechas:** resalta los nodos más centrales (top 3) en naranja rojizo.

---

## 🧠 Tecnologías Utilizadas

- **Python 3.10+**
- **Tkinter** — interfaz gráfica interactiva.  
- **NetworkX** — modelado y análisis de grafos.  
- **Matplotlib** — renderizado visual del grafo.  
- **Collections / math** — cálculos de métricas.

---

## ⚙️ Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tuusuario/red-social-academica-avanzada.git
   cd red-social-academica-avanzada
