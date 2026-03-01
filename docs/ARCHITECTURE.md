# ARCHITECTURE.md — Arquitectura del Sistema Candado / Signal Overlay

Este documento describe la arquitectura técnica propuesta para el sistema, integrada desde el inicio con la dimensión ética definida en `ETHICS.md`.

El sistema no pretende reemplazar el criterio humano, sino asistirlo mediante indicadores estructurados de riesgo narrativo y evidencia contextual.

---

## 0. Principio estructural

SignalCheck es un sistema de análisis multicapa que distingue entre:

- Riesgo Narrativo
- Riesgo Factual
- Riesgo Científico
- Riesgo Comercial/Fraude

El color final es una síntesis.  
Las dimensiones internas pueden evolucionar independientemente.

---

## 1. Componentes principales

### 1. Extensión de Navegador (Cliente)

- Plataformas objetivo iniciales: navegadores basados en Chromium (Chrome, Edge, Brave).
- Funciones:
  - Extraer URL, título y texto principal de la página.
  - Enviar solicitud al backend `/v1/verify`.
  - Mostrar el estado mediante un ícono/semáforo (🟢🟡⚪🔴).
  - Permitir ver el detalle: claims, evidencia, fuentes, fecha.
  - Permitir selección de **modo de análisis**.

### 2. API Backend (Servicio de Verificación)

- Implementación sugerida: FastAPI (Python) o Node.js/Express.
- Endpoints clave:
  - `POST /v1/verify`: recibe `{url, title, text, locale, mode}` y devuelve evaluación.

Incluye:
- Orquestador Ético multi-IA.
- Módulo de recolección de evidencia.
- Módulo de fusión y decisión.
- Capa de Auditoría Ética.
- Motor de clasificación multidimensional.

### 3. Módulo de Fuentes y Evidencia

- Índices locales y conectores a:
  - fact-checkers,
  - organismos oficiales,
  - estudios y publicaciones reconocidas,
  - medios diversos (no solo mainstream),
  - registros comerciales y señales de legitimidad empresarial.

- Política abierta y documentada para agregar o ajustar fuentes.

### 4. Orquestador Ético multi-IA

- Coordina consultas a múltiples modelos/servicios de IA.
- Normaliza las respuestas a un formato estructurado.
- No delega la decisión final a ningún modelo individual.
- Pasa toda salida por el Guardián Normativo antes de devolver resultado.

### 5. Fusor Ético

- Combina resultados en múltiples dimensiones:
  - evidencia_strength
  - consensus
  - riesgo_potencial
  - tipo_de_contenido

- Aplica reglas determinísticas versionadas.
- Produce:
  - Label global
  - Score global
  - Subscores internos

### 6. Guardián Normativo

- Conjunto de reglas inmutables alineadas con `ETHICS.md`.
- Revisa:
  - solicitudes peligrosas,
  - salidas de modelos,
  - decisiones del Fusor.
- Puede:
  - bloquear,
  - degradar clasificación,
  - exigir abstención,
  - marcar “debate científico activo”.

### 7. Auditoría y Logs Éticos

- Registro append-only de:
  - decisiones críticas,
  - bloqueos por razones éticas,
  - abstenciones,
  - degradaciones de clasificación.

- Sin almacenar datos personales innecesarios.
- Basado en hashes y timestamps.

---

## 2. Modos de Análisis

El sistema podrá operar en distintos modos seleccionables por el usuario:

### 🧠 Modo Narrativo
Enfocado en:
- manipulación emocional,
- urgencia,
- polarización,
- promesas exageradas.

Ideal para análisis de redes sociales y noticias.

### 🧪 Modo Científico
Enfocado en:
- afirmaciones médicas,
- consenso científico,
- grado de evidencia,
- estado de debate.

No asume falsedad por ausencia de consenso.
Prioriza clasificación `en_debate` cuando corresponda.

### 💰 Modo Comercial / Fraude
Enfocado en:
- pedidos de dinero,
- promesas de ganancia rápida,
- ausencia de identificación legal,
- señales típicas de estafa.

### 🔎 Modo Integral (default)
Combina todas las dimensiones.

---

## 3. Flujo general `/v1/verify`

1. **Extensión → Backend**
   - Envía:
     - `url`,
     - `title`,
     - `text`,
     - `locale`,
     - `mode`.

2. **Pre-check (Guardián Rápido)**
   - Detecta intentos de uso prohibido.
   - Si es riesgoso o viola principios → respuesta segura + registro.

3. **Recolección de Evidencia**
   - Sampling del contenido.
   - Búsqueda de fuentes relevantes.
   - Construcción de contexto ampliado.

4. **Panel de IA (multi-model)**

   - IA1: extrae claims.
   - IA2: cruza claims vs fuentes.
   - IA3: evalúa riesgo potencial.
   - IA4: detecta sesgos o grietas.
   - IA5 (opcional): detecta estado de debate científico.

5. **Fusor Ético**

   Aplica reglas determinísticas:

   - `respaldado` → 🟢
   - `en_debate` → 🟡
   - `especulativo` → ⚪
   - `contradicho` → 🔴

6. **Revisión del Guardián Normativo**

   Puede ajustar:
   - contradicho → en_debate (si es minoritario sin daño directo).
   - respaldado → en_debate (si hay evidencia emergente contradictoria).

7. **Respuesta a la Extensión**

```json
{
  "label": "en_debate",
  "score": 0.47,
  "dimensions": {
    "narrative_risk": 0.62,
    "scientific_uncertainty": 0.71,
    "commercial_risk": 0.12
  },
  "summary": "...",
  "claims": [],
  "timestamp": "...",
  "version": "1.0.0"
}