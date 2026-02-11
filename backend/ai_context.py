def build_prompt_v2(url: str, text: str) -> str:
    return f"""
Sos un sistema de análisis contextual de contenido web.
NO verificás si la información es verdadera o falsa.
NO juzgás intenciones ocultas.
NO determinás confiabilidad absoluta.

Tu objetivo es describir el CONTEXTO del contenido de forma neutral.

A partir de la URL y el contenido, devolvé un objeto JSON
con los siguientes campos EXACTOS.

Campos requeridos:

1) page_type
Elegí UNA sola categoría:
- news_editorial
- institutional
- ecommerce
- marketplace
- social_platform
- login_page
- personal_blog
- unknown

2) tone
Elegí UNO:
- neutral
- informative
- promotional
- opinionated
- emotional
- alarmist

3) authority_signals
Array de señales visibles de autoridad (o vacío).

4) caution_signals
Array de señales que sugieren leer con atención (o vacío).

5) recommendation
Elegí UNA:
- lectura_normal
- lectura_atenta
- lectura_con_cautela

Reglas:
- Respondé SOLO JSON válido.
- No agregues texto explicativo.
- Si hay duda, usá valores conservadores.

URL:
{url}

Contenido:
{text[:4000]}
"""
