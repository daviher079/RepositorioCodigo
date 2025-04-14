 @Select({
        "<script>",
        "SELECT S.COD_CAMPANIA, S.CARD_IMAGEN, S.CARD_LABEL, S.CARD_TITULO, S.CARD_DESCRIPCION, ",
        "S.CARD_TXT_VER, S.CARD_TXT_DESCUBRIR, S.CARD_ORDEN, S.IDIOMA, S.DETALLE_TITULO, ",
        "S.DETALLE_SUBTITULO, S.DETALLE_IMAGEN_CABECERA, S.DETALLE_IMAGEN, S.DETALLE_BUB_ACT_PICTO, ",
        "S.DETALLE_BUB_ACT_TIT, S.DETALLE_BUB_ACT_DESC ",
        "FROM MAC.SORTEOS_CAMPANIAS S JOIN MAC.CAMPANIAS_SECCION_LEGAL C ON S.COD_CAMPANIA = C.COD_CAMPANIA ",
        "WHERE C.TITULOLEGAL = #{tituloLegal,jdbcType=VARCHAR} AND S.COD_CAMPANIA IN ",
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
        @Result(property = "detalleBubActDesc", column = "DETALLE_BUB_ACT_DESC", jdbcType = JdbcType.VARCHAR),
        @Result(property = "url", column = "URL", jdbcType = JdbcType.VARCHAR)
    })
    List<SorteoCampaniasDTO> getSorteoCampanias(@Param("codCampanias") List<String> codCampanias, @Param("tituloLegal") String tituloLegal);