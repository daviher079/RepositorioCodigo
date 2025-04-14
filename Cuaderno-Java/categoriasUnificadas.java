private List<MiIberdrolaExperienciasCategoria> getCategoriasUnificadas(
	        List<MiIberdrolaExperienciasCategoria> categoriasVD,
	        List<MiIberdrolaExperienciasCategoria> categoriasBdd) {
	    LOGGER.info("AlianzasServiceImpl::getCategoriasUnificadas:: Iniciando la unificacion de categorias");

	    List<MiIberdrolaExperienciasCategoria> response = new ArrayList<>();
	    Map<String, MiIberdrolaExperienciasCategoria> categoriasMap = new LinkedHashMap<>();

	    for (MiIberdrolaExperienciasCategoria categoriaVD : categoriasVD) {
	        categoriasMap.put(categoriaVD.getIdCategoria(), categoriaVD);
	        LOGGER.info("Categoria anadida desde VipDistrict: {}"+ categoriaVD.getNombre());
	    }

	    for (MiIberdrolaExperienciasCategoria categoriaBdd : categoriasBdd) {
	        if (!categoriasMap.containsKey(categoriaBdd.getIdCategoria())) {
	            categoriasMap.put(categoriaBdd.getIdCategoria(), categoriaBdd);
	            LOGGER.info("Categoria anadida desde BBDD: {}"+ categoriaBdd.getNombre());
	        } else {
	            LOGGER.info("Categoria {} ya cubierta por VipDistrict. Se omiten las alianzas de BBDD."+ categoriaBdd.getNombre());
	        }
	    }

	    response.addAll(categoriasMap.values());
	    LOGGER.info("Unificacion de categorias completada. Total categorias: {}"+ response.size());

	    return response;
	}


	campanias.getCodCampaniasDto().stream().anyMatch(
					campania -> Boolean.TRUE.equals(campania.isCampActiva())
					)