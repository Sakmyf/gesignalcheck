\# Manejo de secretos (app pública)

\- Los clientes NO llevan secretos. Solo API\_KEY (identificador).

\- Tokens: JWT RS256 firmados por el backend (15 min).

\- Rotación: mantener 2 claves (KID actual y anterior). Rollover 24 h.

\- Custodia: privadas en servidor (KMS o .env), públicas expuestas en /jwks.json.

\- Revocación: cambiar KID => invalidar tokens nuevos; expiran los viejos en 15 min.



Procedimiento de clave:

1\) Generar nuevo par RSA (OpenSSL).

2\) Pegar privada en `.env` (JWT\_PRIVATE\_PEM) y pública en `JWT\_PUBLIC\_PEM`.

3\) Mover la anterior a `\_OLD` y ajustar KIDs.

4\) Reiniciar backend.



