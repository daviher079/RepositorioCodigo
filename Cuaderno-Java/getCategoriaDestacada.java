private List<MiIberdrolaExperienciasCategoria> getCategoriasBddDestacadas(
			List<MiIberdrolaExperienciasCategoria> categoriasBdd) {
		List<MiIberdrolaExperienciasCategoria> salida = new ArrayList<>();
		String nombreCategoriaDestacada = internacionalizacionService.obtenerDescLiteralAppLargo("CATEGORIA_RESTAURANTES");
		String colorFondo = internacionalizacionService.obtenerDescLiteralAppLargo(ConstantesAPP.COLOR_FONDO_DESTACADO);
		
		/*List<MiIberdrolaExperienciasCategoria> categoriaBddDeestacada = categoriasBdd.stream()
                .filter(categoria -> categoria.getAlianzas().stream()
                        .anyMatch(experiencia -> ConstantesAPP.SI.equals(experiencia.getDestacada())))
                    .map(categoria ->{
                        // recorrr lista de alianzas
                            // set color (crear variable fuera del bucle)
                    }
                    )
                .collect(Collectors.toList());
                		List<MiIberdrolaExperienciasCategoria> categoriaBddDeestacada = categoriasBdd.stream()
                .filter(categoria -> nombreCategoriaDestacada.equals(categoria.getNombre()))
                .collect(Collectors.toList());
                *
                */
		
		
		
		/*for (MiIberdrolaExperienciasCategoria categoria: categoriasBddDestacadas) {
			categoria.setAlianzas(
					categoriasBddDestacadas.stream()
					 .flatMap(alianzas -> alianzas.getAlianzas().stream())          
			            .filter(alianza -> alianza.getDestacada().equals(ConstantesAPP.SI)) 
			            .collect(Collectors.toList())
					);
			
		}*/
		

		List <MiIberdrolaExperienciasCategoria> categoriasBddDestacadas = categoriasBdd.stream()
                .filter(categoria -> nombreCategoriaDestacada.equals(categoria.getNombre()))
                .map(categoria -> {
                	 boolean tieneAlianzaDestacada = categoria.getAlianzas().stream()
                			 .anyMatch(experiencia -> ConstantesAPP.SI.equals(experiencia.getDestacada()));
                	 categoria.setDestacado(tieneAlianzaDestacada);
                	 categoria.getAlianzas().stream()
                	 .map(experiencia -> {
                		 if (experiencia.getDestacada().equals(ConstantesAPP.SI)) {
                			 experiencia.setColorFondo(colorFondo);
                		 }
                		 return experiencia;	 
                	 })
                	 .collect(Collectors.toList());
                	 return categoria;
                })
				.collect(Collectors.toList()); 
		
		LOGGER.info("AlianzasServiceImpl::getTodasExperiencias:: categorias totales obtenidas para el cliente "
				+ Objects.toString(categoriasBddDestacadas));

		
		188386
		
		
                //.anyMatch(alianza -> ConstantesAPP.SI.equals(alianza.getDestacada())
		
		/*List<List<MiIberdrolaExperiencia>> prueba = categoriaBddDeestacada.stream()
				.map(categoria -> categoria.getAlianzas().stream()
						.map(alianza -> {
							alianza.setColorFondo(colorFondo);
							return alianza;
						})
						.collect(Collectors.toList()))
				.collect(Collectors.toList());
                
		/*List<MiIberdrolaExperienciasCategoria> categoriaBddDeestacada = categoriasBdd.stream()
                .filter(categoria -> categoria.getAlianzas().stream()
                        .anyMatch(experiencia -> ConstantesAPP.SI.equals(experiencia.getDestacada())))
                			.map(null)
                .collect(Collectors.toList());*/
		
		//salida.get(0).setNombre(nombreCategoriaDestacada);
		//crear en el dto destacada y setear a true
		
		//LOGGER.info("Categoria destacada :: "+ Object.toString(categoriaBddDeestacada));
		return salida;
	}