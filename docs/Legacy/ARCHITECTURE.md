# ARCHITECTURE.md — Arquitectura del Sistema Candado / Signal Overlay

Este documento describe la arquitectura técnica propuesta para el sistema, integrada desde el inicio con la dimensión ética definida en `ETHICS.md`.

---

## 1. Componentes principales

1. **Extensión de Navegador (Cliente)**
   - Plataformas objetivo iniciales: navegadores basados en Chromium (Chrome, Edge, Brave).
   - Funciones:
     - Extraer URL, título y texto principal de la página.
     - Enviar solicitud al backend `/v1/verify`.
     - Mostrar el estado mediante un ícono/semáforo (🟢🟡⚪🔴).
     - Permitir ver el detalle: claims, evidencia, fuentes, fecha.

2. **API Backend (Servicio de Verificación)**
   - Implementación sugerida: FastAPI (Python) o Node.js/Express.
   - Endpoints clave:
     - `POST /v1/verify`: recibe `{url, title, text, locale}` y devuelve evaluación.
   - Incluye:
     - Orquestador Ético multi-IA.
     - Módulo de recolección de evidencia.
     - Módulo de fusión y decisión.
     - Capa de Auditoría Ética.

3. **Módulo de Fuentes y Evidencia**
   - Índices locales y conectores a:
     - fact-checkers,
     - organismos oficiales,
     - estudios y publicaciones reconocidas,
     - medios diversos (no solo mainstream).
   - Política abierta y documentada para agregar o ajustar fuentes.

4. **Orquestador Ético multi-IA**
   - Coordina consultas a múltiples modelos/servicios de IA.
   - Normaliza las respuestas a un formato estructurado.
   - Pasa toda salida por el Guardián Normativo antes de devolver resultado.

5. **Guardián Normativo**
   - Conjunto de reglas inmutables alineadas con `ETHICS.md`.
   - Revisa:
     - solicitudes peligrosas,
     - salidas de modelos,
     - decisiones del Fusor.
   - Tiene poder de bloquear, degradar o exigir abstención.

6. **Auditoría y Logs Éticos**
   - Registro append-only de:
     - decisiones críticas,
     - bloqueos por razones éticas,
     - casos de abstención.
   - Sin almacenar datos personales innecesarios.

---

## 2. Flujo general `/v1/verify`

1. **Extensión → Backend**
   - Envía:
     - `url`,
     - `title`,
     - `text` (limitado),
     - `locale`.

2. **Pre-check (Guardián Rápido)**
   - Detecta intentos de uso prohibido.
   - Si es riesgoso o viola principios → respuesta segura + registro.

3. **Recolección de Evidencia**
   - Sampling del contenido.
   - Búsqueda de fuentes relevantes (internas y externas).
   - Construcción del contexto para el análisis.

4. **Panel de IA (multi-model)**
   - IA1: extrae claims.
   - IA2: cruza claims vs fuentes.
   - IA3: evalúa riesgo potencial.
   - IA4: detecta sesgos/grietas.

5. **Fusor Ético**
   - Combina los resultados de las IA en un conjunto de claims evaluados.
   - Aplica reglas determinísticas para asignar un label global:

     - `respaldado` → 🟢
     - `en_debate` → 🟡
     - `especulativo` → ⚪
     - `contradicho` → 🔴

6. **Revisión del Guardián Normativo**
   - Verifica que la clasificación no viole principios éticos.
   - Puede ajustar (por ejemplo, bajar de `contradicho` a `en_debate` si se trata de ideas minoritarias sin daño directo).

7. **Respuesta a la Extensión**
   - JSON con:
     - `label`,
     - `score`,
     - resumen explicativo,
     - lista breve de claims y fuentes usadas,
     - `timestamp`,
     - `version`.

---

## 3. Extensión — Detalle mínimo sugerido

- `content_script.js`:
  - Extrae contenido principal de la página.
  - Envía mensaje al `service_worker` con payload.

- `service_worker.js`:
  - Gestiona cache local por URL.
  - Llama al backend.
  - Actualiza badge (✔ / ! / ? / ·) según label.

- `popup.html` + `popup.js`:
  - Muestra estado.
  - Lista claims y fuentes resumidas.
  - No expone datos sensibles.

---

## 4. Principios de implementación

- Mantener el código del Guardián Normativo separado y protegido.
- Documentar claramente las reglas del Fusor.
- Diseñar la integración con IA externas de forma intercambiable (no depender de un solo proveedor).
- Mantener repos iniciales privados hasta consolidar el modelo ético y técnico.
