@Loggable(LogLevel.DEBUG)
	private void getCategoriasBddDestacadas(List<MiIberdrolaExperienciasCategoria> categoriasBdd) {
		
		String nombreCategoriaDestacada = internacionalizacionService.obtenerDescLiteralAppLargo(ConstantesAPP.CATEGORIA_DESTACADA);
		String colorFondo = internacionalizacionService.obtenerDescLiteralAppLargo(ConstantesAPP.COLOR_FONDO_DESTACADO);
		
		List <MiIberdrolaExperienciasCategoria> categoriasBddDestacadas = categoriasBdd.stream()
                .filter(categoria -> nombreCategoriaDestacada.equals(categoria.getNombre())) //filtra para encontra que categoria es la destacada
                .map(categoria -> {
                	 boolean tieneAlianzaDestacada = categoria.getAlianzas().stream()
                			 .anyMatch(experiencia -> ConstantesAPP.SI.equals(experiencia.getDestacada())); // devuelve un booleancon el resultado de encontrar una alianza destacada
                	 categoria.setDestacados(tieneAlianzaDestacada); //Settea la categoria y cambia su atributo boolean destacado 
                	 categoria.getAlianzas().stream()
					 .limit(2)
                	 .forEach(experiencia -> {
                		 if (experiencia.getDestacada().equals(ConstantesAPP.SI)) { // Comprueba si alguna alianza es destacada y cambia su color de fondo 
                			 experiencia.setColorFondo(colorFondo);
                		 }
                	 });
                	 return categoria; //Devuelve la categoria ya preparada
                })
				.collect(Collectors.toList()); 
		
		LOGGER.info("AlianzasServiceImpl::getTodasExperiencias:: categorias totales obtenidas para el cliente "
				+ Objects.toString(categoriasBddDestacadas));

	}

			ResponseEntity<EsClienteEP> clienteEpResponse = null;
			EsClienteEP esclienteEp = null;
			LOGGER.info("OvcPromocionesAppEspServiceV2.getPromocionesGreenUp:: Llamamos a comprobarClienteEP para ver los datos del cliente EP");
			clienteEpResponse = msclibkService.comprobarClienteEP(datosUsuarioPromo.getCodCliente());
			esclienteEp = clienteEpResponse.getBody();
			
			List <PromocionesRegaloSeguro> listaRegaloSeguro = regaloSeguroMapper.getPromocionesRegaloSeguro();
			
			if (listaRegaloSeguro != null && !listaRegaloSeguro.isEmpty()) {
				LocalDateTime fechaActual = LocalDateTime.now();
				boolean existenRegalos = listaRegaloSeguro.stream()
						.anyMatch(promocion -> fechaActual.isAfter(promocion.getFechaFin().toInstant()
								.atZone(ZoneId.systemDefault())
								.toLocalDateTime()));
				if(ConstantesAPP.SI.equals(esclienteEp.getAdherible())&& existenRegalos) {
					
				}
				
			}
			
