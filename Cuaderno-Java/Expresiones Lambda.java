List<MiIberdrolaExperienciasCategoria> categoria = categorias.stream()
		.filter(c -> Integer.parseInt(c.getIdCategoria()) == peticion.getIdCategoria())
		.collect(Collectors.toList());


.map(
                		{
        					alianza.setColorFondo(colorFondo);
        					return alianza;
        				})
        		.collect(Collectors.toList());



		List <MiIberdrolaExperienciasCategoria> prueba1 = categoriasBdd.stream()
                .filter(categoria -> nombreCategoriaDestacada.equals(categoria.getNombre()))
				.filter(categoria -> categoria.getAlianzas().stream()
						.filter(experiencia -> ConstantesAPP.SI.equals(experiencia.getDestacada()))
            ).collect(Collectors.toList());
