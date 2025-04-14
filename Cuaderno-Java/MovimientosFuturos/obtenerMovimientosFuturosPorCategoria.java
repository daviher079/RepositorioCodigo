@Override
	public MovimientosFuturosPorCatResponse obtenerMovimientosFuturosPorCategoria(int idCategoria, String codUsuario,
			String codCliente, List<ContratoListaVO> listaContratos,
			ListaReceptorSuministroSesionUsuario listaReceptores, HttpSession httpSession) {

		LOG.info("Iniciando obtenerMovimientosFuturosPorCategoria para idCategoria: {}" + idCategoria);

		FidCategoriasPrevisionSaldo categoria = obtenerCategoriaPorId(idCategoria);
		if (categoria == null) {
			LOG.info("La categoria con id {} no existe." + idCategoria);
			return null;
		}
		
		BeneficiosPorCompras beneficioPorCompra = obtenerBeneficiosPorCompras(categoria, codCliente);

		boolean incluirMovimientosFuturos = ConstantesAPP.SI.equalsIgnoreCase(categoria.getMovimientosFuturos());

		List<SaldoFuturoEnergyPack> listaSaldoFuturoEnergyPack = msclibkService.saldoFuturo(codCliente);
		if (listaSaldoFuturoEnergyPack == null) {
			LOG.info("No se encontraron movimientos futuros.");
		}

		List<CategoriasMFMapper> categoriasMFMapper = movimientosFuturosMapper.getCategorias();

		if (listaSaldoFuturoEnergyPack != null) {
			listaSaldoFuturoEnergyPack = filtrarMovimientosPorCategoria(idCategoria, categoriasMFMapper,
					listaSaldoFuturoEnergyPack);
			LOG.info("Lista de movimientos futuros filtrada y ordenada por codBeneficio: {}"
					+ listaSaldoFuturoEnergyPack);
		}

		Map<String, String> ordenAlias = obtenerAliasDireccion(listaContratos,
				obtenerAliasRS(codUsuario, codCliente, listaReceptores));
		LOG.info("Alias obtenidos para los contratos: {}" + ordenAlias);

		MovimientosFuturos resultado = new MovimientosFuturos();
		List<MovimientoFuturo> listaMovimientosFuturo = new ArrayList<>();
		HashMap<String, Double> codBeneficioImporte = new HashMap<>();
		double sumaTotal = 0;

		if (listaSaldoFuturoEnergyPack != null) {
			for (SaldoFuturoEnergyPack saldoFuturoEnergyPack : listaSaldoFuturoEnergyPack) {
				String codContrato = String.valueOf(saldoFuturoEnergyPack.getCodContrato());

				MovimientoFuturo movimientoFuturo = obtenerMovimientoFuturo(ordenAlias, saldoFuturoEnergyPack,
						codContrato);
				listaMovimientosFuturo.add(movimientoFuturo);

				if (saldoFuturoEnergyPack.getCodBeneficio() != null) {
					codBeneficioImporte.put(saldoFuturoEnergyPack.getCodBeneficio(),
							saldoFuturoEnergyPack.getImporteAnual());
					sumaTotal += saldoFuturoEnergyPack.getImporteAnual();
				}
			}
		}

		resultado.setMovimientosFuturo(listaMovimientosFuturo);

		List<CategoriasMovimientosFuturos> categoriasMovimientosFuturos = new ArrayList<>();
		List<DetalleContenidoTooltip> detalleContenidoTooltipList = new ArrayList<>();
		DecimalFormat df = new DecimalFormat("#.00");

		obtenerCategorias(categoriasMFMapper, codBeneficioImporte, df, categoriasMovimientosFuturos,
				detalleContenidoTooltipList);

		String importeTotalStr = null;
		if (idCategoria == 1) {
			String sumaTotalFormatted = df.format(sumaTotal).replace('.', ',') + ConstantesAPP.EURO;
			    if (sumaTotal == 0) {
		        importeTotalStr = "+0,00" + ConstantesAPP.EURO;
		    } else {
		        importeTotalStr = "+" + sumaTotalFormatted;
		    }
		}

		DetallePrevision detallePrevision = obtenerDetallePrevisionSegregadoPorCodBeneficio(codCliente, ordenAlias,
				idCategoria);

		return construirRespuesta(categoria, resultado, incluirMovimientosFuturos, importeTotalStr, detallePrevision, beneficioPorCompra);
	}







private MovimientosFuturosPorCatResponse construirRespuesta(FidCategoriasPrevisionSaldo categoria,
			MovimientosFuturos resultado, boolean incluirMovimientosFuturos, String importeTotalStr,
			DetallePrevision detallePrevision, BeneficiosPorCompras beneficiosPorCompras) {

		MovimientosFuturosPorCatResponse response = new MovimientosFuturosPorCatResponse();

		if (importeTotalStr != null && categoria.getId() == 1) {
			response.setImporteTotal(importeTotalStr);
		}

		response.setTitulo(categoria.getNombre());
		response.setSubtitulo(categoria.getSubtituloDetalle());

		response.setDetallePrevision(detallePrevision);

		if (incluirMovimientosFuturos) {
			response.setMovimientosFuturos(resultado.getMovimientosFuturo());
		} else {
			response.setMovimientosFuturos(null);
		}
		
		response.setBeneficiosPorCompras(beneficiosPorCompras);

		LOG.info("Finalizado obtenerMovimientosFuturosPorCategoria para idCategoria: {}" + categoria.getId());
		return response;
	}













