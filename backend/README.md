> Documento base del proyecto SignalCheck.  

> A partir de esta versión, todo cambio se versiona.

\# 🧠 SignalCheck

\## Documento Base — v1.0 (Estado Congelado)



\# 🧠 SignalCheck — Documento Base v1.0



\*\*Estado congelado del MVP\*\*



> Este documento deja constancia del estado funcional, conceptual y de producto de SignalCheck.

> A partir de aquí, todo cambio se versiona. No se re-discute.



---



\## 1. Propósito del proyecto



SignalCheck es una herramienta de asistencia a la lectura crítica de información online. Su objetivo es \*\*detectar y explicar señales estructurales y discursivas\*\* que puedan indicar falta de respaldo, posible manipulación o necesidad de verificación adicional.



SignalCheck \*\*no determina verdades\*\* ni reemplaza el criterio humano.



---



\## 2. Qué hace



\* Analiza contenido visible de una página web

\* Detecta señales observables y explicables

\* Calcula un estado interpretativo

\* Presenta el resultado de forma clara al usuario

\* Funciona en tiempo real mediante extensión de navegador



\## 3. Qué NO hace



\* No afirma si algo es verdadero o falso

\* No verifica hechos en bases oficiales

\* No censura ni bloquea contenido

\* No toma posición ideológica o política



> SignalCheck asiste. No decide.



---



\## 4. Arquitectura (estado técnico)



\### Backend



\* Framework: FastAPI

\* Endpoints activos: `/`, `/health`, `/v1/verify`

\* Motor de reglas operativo

\* CORS, rate limit y parsing correctos

\* Documentación Swagger disponible



\### Infraestructura



\* Deployment activo en Railway

\* Servicio estable, sin crashes

\* Logs limpios



\### Extensión Chrome



\* Manifest V3 correcto

\* Popup funcional

\* Comunicación completa: popup → service worker → backend → popup

\* Estados visuales operativos



---



\## 5. Lenguaje oficial de estados (v1)



\### 🟢 Respaldado



El contenido presenta señales claras de respaldo y contexto.



\### 🟡 Requiere lectura crítica



El contenido presenta señales mixtas o falta información clave para evaluarlo con confianza.



\### 🔴 Información cuestionable



El contenido presenta señales fuertes de posible manipulación, distorsión o desinformación.



> SignalCheck no evalúa intenciones ni ideologías. Evalúa señales.



---



\## 6. Señales detectables (v1)



\### Fuente



\* S1: Fuente no periodística

\* S2: Autor no identificable



\### Respaldo



\* S3: Afirmación relevante sin evidencia

\* S4: Afirmación extraordinaria sin prueba



\### Contexto



\* S5: Falta de contexto temporal

\* S6: Falta de contexto situacional



\### Lenguaje



\* S7: Lenguaje emocional intenso

\* S8: Lenguaje confrontativo o identitario



\### Manipulación



\* S9: Manipulación deliberada del texto

\* S10: Titular amplificado



\### Trazabilidad



\* S11: Ausencia total de referencias

\* S12: Llamado implícito a reaccionar



---



\## 7. Scoring interno (v1)



\### Pesos



\* Señales leves: +1

\* Señales fuertes: +3



\### Umbrales



\* 🟢 0–2

\* 🟡 3–6

\* 🔴 ≥7



\*\*Regla especial:\*\*

Dos o más señales fuertes ⇒ 🔴 directo



---



\## 8. Explicabilidad en UI



El sistema muestra:



1\. Estado principal

2\. Subtítulo explicativo

3\. Hasta 5 señales detectadas

4\. Mensaje aclaratorio final



Lenguaje claro, neutral y no acusatorio.



---



\## 9. Caso ejemplo público



Publicación en red social con afirmaciones de alto impacto sin respaldo verificable.



Resultado: 🔴 Información cuestionable



Motivo:



\* Fuente no periodística

\* Afirmaciones extraordinarias sin evidencia

\* Lenguaje emocional intenso

\* Manipulación del texto

\* Ausencia total de referencias



---



\## 10. Principio rector



> Cuanto más fuerte es una afirmación, mayor debe ser su respaldo visible.



---



\## 11. Estado del documento



\* Versión: v1.0

\* Estado: Congelado

\* Uso: Referencia base para desarrollo, publicación y comunicación



---



✔ Acta de estado del proyecto registrada



