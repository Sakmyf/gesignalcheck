@app.post("/v3/verify")
async def verify(
    data: VerifyRequest,
    x_extension_id: str = Header(None),
    db: Session = Depends(get_db)
):

    # -------------------------
    # VALIDACION EXTENSION
    # -------------------------

    if not x_extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    extension = db.query(Extension).filter(
        Extension.extension_id == x_extension_id.strip()
    ).first()

    if not extension:
        raise HTTPException(status_code=401, detail="Extensión no registrada")

    if not extension.is_active:
        raise HTTPException(status_code=403, detail="Extensión desactivada")

    if extension.analyses_limit > 0 and \
       extension.analyses_used >= extension.analyses_limit:
        raise HTTPException(status_code=403, detail="Límite de uso alcanzado")

    # -------------------------
    # VALIDACION TEXTO
    # -------------------------

    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    text = data.text
    url = data.url or ""

    # -------------------------
    # VERSIONADO
    # -------------------------

    content_hash = generate_content_hash(text)
    analysis_key = build_analysis_key(content_hash, ENGINE_VERSION)

    # -------------------------
    # CACHE CHECK
    # -------------------------

    existing_log = (
        db.query(AnalysisLog)
        .filter(AnalysisLog.analysis_key == analysis_key)
        .first()
    )

    if existing_log:
        return {
            "analysis": {
                "level": existing_log.level,
                "summary": "Resultado recuperado desde cache.",
                "indicators": [],
                "shown_indicators": 0,
                "note": "Este análisis ya había sido procesado anteriormente."
            },
            "meta": {
                "engine_version": existing_log.engine_version,
                "analysis_key": analysis_key,
                "cached": True
            }
        }

    # -------------------------
    # EJECUTAR ENGINE
    # -------------------------

    result = analyze_context(text, url)
    status_color, level = interpret_score(result.get("score", 0))

    # -------------------------
    # DETERMINAR SITE TYPE
    # -------------------------

    parsed = urlparse(url)
    site_type = parsed.netloc if parsed.netloc else "unknown"

    # -------------------------
    # GUARDAR LOG
    # -------------------------

    analysis_log = AnalysisLog(
        trust_score=result.get("quality_score", 0),
        rhetorical_score=0,
        narrative_score=0,
        absence_score=0,
        risk_index=result.get("score", 0),
        level=result.get("status"),
        premium_requested=False,
        engine_version=ENGINE_VERSION,
        analysis_key=analysis_key
    )

    db.add(analysis_log)

    # -------------------------
    # INCREMENTAR USO
    # -------------------------

    extension.analyses_used += 1

    db.commit()

    # -------------------------
    # INDICADORES
    # -------------------------

    indicators = [
        {
            "title": s,
            "explanation": "Señal estructural detectada durante el análisis contextual.",
            "orientation": "alerta" if status_color != "green" else "neutro"
        }
        for s in result.get("signals", [])[:5]
    ]

    # -------------------------
    # RESPUESTA FINAL
    # -------------------------

    return {
        "analysis": {
            "level": level,
            "summary": result.get("label"),
            "indicators": indicators,
            "shown_indicators": len(indicators),
            "note": "Se muestran las señales estructurales más relevantes para esta evaluación."
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "site_type": site_type,
            "content_hash": content_hash,
            "analysis_key": analysis_key,
            "premium_available": True,
            "disclaimer": "SignalCheck no determina veracidad. Ningún sistema automatizado reemplaza el juicio humano."
        }
    }