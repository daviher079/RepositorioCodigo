 @Select({
        "<script>",
        "SELECT COD_CAMPANIA, CARD_IMAGEN, CARD_LABEL, CARD_TITULO, CARD_DESCRIPCION, ",
        "CARD_TXT_VER, CARD_TXT_DESCUBRIR, CARD_ORDEN, IDIOMA, DETALLE_TITULO, ",
        "DETALLE_SUBTITULO, DETALLE_IMAGEN_CABECERA, DETALLE_IMAGEN, DETALLE_BUB_ACT_PICTO, ",
        "DETALLE_BUB_ACT_TIT, DETALLE_BUB_ACT_DESC ",
        "FROM SORTEOS_CAMPANIAS ",
        "WHERE COD_CAMPANIA IN ",
        "<foreach item='item' index='index' collection='codCampanias' open='(' separator=',' close=')'>",
        "#{item}",
        "</foreach>",
        "</script>"
    })
    @Results(id = "getSorteoCampanias", value = {
        @Result(property = "codCampania", column = "COD_CAMPANIA", jdbcType = JdbcType.VARCHAR),
        @Result(property = "cardImagen", column = "CARD_IMAGEN", jdbcType = JdbcType.VARCHAR),
        @Result(property = "cardLabel", column = "CARD_LABEL", jdbcType = JdbcType.VARCHAR),
        @Result(property = "cardTitulo", column = "CARD_TITULO", jdbcType = JdbcType.VARCHAR),
        @Result(property = "cardDescripcion", column = "CARD_DESCRIPCION", jdbcType = JdbcType.VARCHAR),
        @Result(property = "cardTxtVer", column = "CARD_TXT_VER", jdbcType = JdbcType.VARCHAR),
        @Result(property = "cardTxtDescubrir", column = "CARD_TXT_DESCUBRIR", jdbcType = JdbcType.VARCHAR),
        @Result(property = "cardOrden", column = "CARD_ORDEN", jdbcType = JdbcType.NUMERIC),
        @Result(property = "idioma", column = "IDIOMA", jdbcType = JdbcType.VARCHAR),
        @Result(property = "detalleTitulo", column = "DETALLE_TITULO", jdbcType = JdbcType.VARCHAR),
        @Result(property = "detalleSubtitulo", column = "DETALLE_SUBTITULO", jdbcType = JdbcType.VARCHAR),
        @Result(property = "detalleImagenCabecera", column = "DETALLE_IMAGEN_CABECERA", jdbcType = JdbcType.VARCHAR),
        @Result(property = "detalleImagen", column = "DETALLE_IMAGEN", jdbcType = JdbcType.VARCHAR),
        @Result(property = "detalleBubActPicto", column = "DETALLE_BUB_ACT_PICTO", jdbcType = JdbcType.VARCHAR),
        @Result(property = "detalleBubActTit", column = "DETALLE_BUB_ACT_TIT", jdbcType = JdbcType.VARCHAR),
        @Result(property = "detalleBubActDesc", column = "DETALLE_BUB_ACT_DESC", jdbcType = JdbcType.VARCHAR)
    })
    List<SorteoCampaniasDTO> getSorteoCampanias(@Param("codCampanias") List<String> codCampanias);

	

	 @Select({
 		"<script>",
		"SELECT SL.IDFAQ, SL.TITULOLEGAL AS TITULOLEGAL_SECCION, SL.URL, SL.IDIOMA, ", 
		"CF.TITULOLEGAL AS TITULOLEGAL_FAQ ",
		"FROM MAC.CAMPANIAS_SECCION_LEGAL SL ",
		"LEFT JOIN MAC.CAMPANIAS_FAQ CF ON SL.IDFAQ = CF.ID ", 
		"WHERE SL.IDIOMA = 'ES' AND SL.COD_CAMPANIA IN",
		"<foreach item='item' index='index' collection='codCampanias' open='(' separator=',' close=')'>",
		"#{item}",
		"</foreach>",
		"</script>"
	 })
	    @Results(value = {
	            @Result(property = "idFaq", column = "IDFAQ", jdbcType = JdbcType.VARCHAR),
	            @Result(property = "tituloLegalSeccionLegal", column = "TITULOLEGAL_SECCION", jdbcType = JdbcType.VARCHAR),
	            @Result(property = "tituloLegalFaq", column = "TITULOLEGAL_FAQ", jdbcType = JdbcType.VARCHAR),
	            @Result(property = "url", column = "URL", jdbcType = JdbcType.VARCHAR)
	    })
	    public List<CampaniasSeccionLegal> obtenerSeccionLegalCampanias(@Param("codCampanias") List<String> codCampanias);



