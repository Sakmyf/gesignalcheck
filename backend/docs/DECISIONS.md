\# DECISIONS — Candado (MVP Local)



Propósito: registrar casos reales y la \*\*decisión\*\* que queremos que el sistema tome.

Esto guía ajustes de `site\_score()` y de las listas `EVENT\_HINTS / SPEC\_HINTS / ALERT\_HINTS`.



---



\## Cómo testear (paso a paso)

1\) Asegurate que el backend está corriendo (`Uvicorn running on 127.0.0.1:8787`).  

2\) En Chrome: `chrome://extensions` → \*\*Actualizar\*\* (para recargar la extensión).  

3\) Limpiar caché de la extensión si no ves cambios: abrir “service worker” → Consola →  

&nbsp;  `chrome.storage.local.clear()` y recargar la página bajo prueba.  

4\) Abrir la página → tocar el ícono \*\*Signal Overlay\*\* → anotar resultado.



---



\## Matriz de criterios (resumen)

\- \*\*+2\*\*: CUIT/CUIL o \*razón social\* / \*matrícula\*.  

\- \*\*+2\*\*: Dirección/ciudad real (“Ituzaingó”, “Buenos Aires”, “Avenida …”), teléfono.  

\- \*\*+1\*\*: Términos/Privacidad/Legales.  

\- \*\*+1\*\*: Email con dominio propio (no @gmail).  

\- \*\*+1\*\*: Frases de \*\*evento confirmado\*\* (fecha, lugar, “se realizará”, “entrada gratis”).  

\- \*\*−2\*\*: Condicional/predicción: “podría / sería / estaría por / rumor / trascendió”.  

\- \*\*−2\*\*: Alertas/denuncias (“estafa/falso/engaño/alerta”) sin respaldo claro.  

\- \*\*−3\*\*: Pedidos de dinero/datos sensibles (“depositá/transferí/CBU/clave token”) sin legales.



Mapeo a label global:

\- \*\*≥4\*\* → 🟢 Respaldado  

\- \*\*2–3\*\* → 🟡 En debate  

\- \*\*0–1\*\* → ⚪ Especulativo  

\- \*\*<0\*\* → 🔴 Contradicho



---



\## Casos de prueba (mínimo viable)



\### A. Oficiales / confiables

\- \*\*Caso\*\*: Boletín oficial, municipalidad, ministerio, Chequeado  

&nbsp; - \*\*Ejemplo URL\*\*: \*(anotá la real cuando pruebes)\*  

&nbsp; - \*\*Esperado\*\*: 🟢 \*Respaldado\*  

&nbsp; - \*\*Justificación\*\*: Dominio/organismo oficial o medio de verificación.  

&nbsp; - \*\*Notas\*\*: Si quedó 🟡, agregar palabra clave o ajustar regex de “boletín/municipio/ministerio”.



\### B. Evento confirmado (agenda, cultura, feria)

\- \*\*Caso\*\*: “Se realizará el sábado… entrada libre y gratuita… lugar y horario”  

&nbsp; - \*\*URL\*\*:  

&nbsp; - \*\*Esperado\*\*: 🟢 \*Respaldado\*  

&nbsp; - \*\*Señales que deben detonar\*\*: `se realizará`, `tendrá lugar`, `entrada gratis`, `fecha`, `lugar`.  

&nbsp; - \*\*Acción si falla\*\*: sumar la frase faltante a `EVENT\_HINTS` o subir +1 al score del bloque de eventos.



\### C. Comercial identificado (bajo riesgo)

\- \*\*Caso\*\*: Sitio de inmobiliaria/negocio con CUIT, dirección, legales  

&nbsp; - \*\*URL\*\*: `https://garnicainmuebles.com/...`  

&nbsp; - \*\*Esperado\*\*: 🟢 \*Respaldado\* (en laboratorio) o 🟡 si faltan señales.  

&nbsp; - \*\*Acción si falla\*\*: revisar que detecte CUIT/dirección/email dominio propio; ajustar regex.



\### D. Nota genérica de medio (no verificación)

\- \*\*Caso\*\*: Artículo periodístico normal sin fuentes sólidas visibles  

&nbsp; - \*\*URL\*\*:  

&nbsp; - \*\*Esperado\*\*: 🟡 \*En debate\*  

&nbsp; - \*\*Acción si dio 🟢\*\*: bajar peso de señales débiles; si dio ⚪, quizá sumar “autor/fecha/sección” como +1.



\### E. Opinión / blog / predicción

\- \*\*Caso\*\*: “Podría suceder… se evalúa… trascendió…”  

&nbsp; - \*\*URL\*\*:  

&nbsp; - \*\*Esperado\*\*: ⚪ \*Especulativo\*  

&nbsp; - \*\*Acción si quedó 🟡/🟢\*\*: agregar palabra faltante a `SPEC\_HINTS` o restar más puntos al condicional.



\### F. Alerta/denuncia sin respaldo

\- \*\*Caso\*\*: “Estafa/engaño/alerta” sin fuente, pide datos sensibles o dinero  

&nbsp; - \*\*URL\*\*:  

&nbsp; - \*\*Esperado\*\*: 🔴 \*Contradicho\* (o 🟡 si hay respaldo oficial linkeado)  

&nbsp; - \*\*Acción\*\*: endurecer el −3 de “depositá/CBU/clave token” cuando no existan legales visibles.



---



\## Ejemplos ya verificados (completá al probar)



\- \[ ] \*\*A1\*\* Boletín oficial \_\_\_\_\_\_\_\_\_\_ → \*\*Resultado actual:\*\* \_\_\_\_ → \*\*Esperado:\*\* 🟢 → \*\*Acción:\*\* \_\_\_\_\_\_  

\- \[ ] \*\*B1\*\* Evento cultural \_\_\_\_\_\_\_\_\_\_ → \*\*Resultado actual:\*\* \_\_\_\_ → \*\*Esperado:\*\* 🟢 → \*\*Acción:\*\* \_\_\_\_\_\_  

\- \[ ] \*\*C1\*\* Garnica Inmuebles (ficha/listado) → \*\*Resultado actual:\*\* \_\_\_\_ → \*\*Esperado:\*\* 🟢/🟡 → \*\*Acción:\*\* \_\_\_\_\_\_  

\- \[ ] \*\*D1\*\* Nota de diario genérica \_\_\_\_ → \*\*Resultado actual:\*\* \_\_\_\_ → \*\*Esperado:\*\* 🟡 → \*\*Acción:\*\* \_\_\_\_\_\_  

\- \[ ] \*\*E1\*\* Predicción/rumor \_\_\_\_\_\_\_\_\_ → \*\*Resultado actual:\*\* \_\_\_\_ → \*\*Esperado:\*\* ⚪ → \*\*Acción:\*\* \_\_\_\_\_\_  

\- \[ ] \*\*F1\*\* Alerta/estafa sin respaldo \_ → \*\*Resultado actual:\*\* \_\_\_\_ → \*\*Esperado:\*\* 🔴 → \*\*Acción:\*\* \_\_\_\_\_\_



---



\## Cambios propuestos (para tocar en `app.py`)



\- \*\*Regex nuevas\*\* a sumar en `site\_score()`:

&nbsp; - Positivas: `(?i)\\b(cuit|cuil|razón social|matr\[ií]cula)\\b`, `\\b(términos|privacidad|legales|política)\\b`, `\\bentrada (libre|gratis)\\b`, `\\bfecha|lugar|cronograma|se realizará|tendrá lugar\\b`

&nbsp; - Negativas: `\\bpodría|sería|estaría por|rumor|trascendió|proyecta\\b`, `\\bestafa|engaño|falso|fake|alerta\\b`, `\\bdepositá|transferí|clave token|cbu\\b`



\- \*\*Ajustes de puntos\*\* (anotar decisión):

&nbsp; - EVENT\_HINTS: \*\*+1 → +2\*\* ( ) / \*\*mantener +1\*\* ( )  

&nbsp; - Condicional: \*\*−2 → −3\*\* ( ) / \*\*mantener −2\*\* ( )  

&nbsp; - Pedidos sensibles sin legales: \*\*−3 → −4\*\* ( ) / \*\*mantener −3\*\* ( )



---



\## Changelog (últimas decisiones)

\- \*\*2025-11-13\*\*: Se introdujo score por señales y claims por oración (v0.0.4-mock).

\- \*\*YYYY-MM-DD\*\*: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



