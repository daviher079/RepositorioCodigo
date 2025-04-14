@Loggable(LogLevel.DEBUG)
	private MovimientosFuturos obtenerMovimientosFuturos(String codUsuario, String codCliente, List<ContratoListaVO> listaCtoSesion,
			ListaReceptorSuministroSesionUsuario listaReceptoresSuministroDeUsuario,HttpSession httpSession) {

		String ultNivelFid = internacionalizacionService.obtenerDescLiteralAppLargo(ULTIMO_NIVEL_FIDELIZACION);
		
		String nivelFid = String.valueOf(httpSession.getAttribute(ConstantesAPP.NIVEL_FIDELIZACION)) ;
		LOG.info("obtenerMovimientosFuturos :: sesion :: nivelFidelizacion = "+Objects.toString(nivelFid));		
		
		String proximoNivelFidelizacion = String.valueOf(httpSession.getAttribute(ConstantesAPP.PROGRAMA_FIDELIZACION_PROXIMO_NIVEL)) ;	
		LOG.info("obtenerMovimientosFuturos :: sesion :: proximoNivelFidelizacion = "+ Objects.toString(proximoNivelFidelizacion));		
		
		int proximoNivelFidelizacionDiasRestantes = Integer.parseInt(httpSession.getAttribute(ConstantesAPP.PROGRAMA_FIDELIZACION_DIAS_RESTANTES).toString());	
		LOG.info("obtenerMovimientosFuturos :: sesion :: proximoNivelFidelizacionDiasRestantes = "+Objects.toString(proximoNivelFidelizacionDiasRestantes));	
		
		String iconoProxNivel = obtenerPicto(nivelFid);
		String nombreNivel = internacionalizacionService.obtenerDescLiteralAppLargo(ConstantesAPP.FIDELIZACION_NIVEL+ proximoNivelFidelizacion);
		String misDiasRestantes = internacionalizacionService.obtenerDescLiteralAppLargo(MI_DIAS_RESTANTES);
		int misdiasRes = Integer.parseInt(misDiasRestantes);
		String miIberdroaTitBannerProxNivel = internacionalizacionService.obtenerDescLiteralAppLargo(ConstantesAPP.MI_IBERDROLA_TIT_BANNER_PROX_NIVEL);
	
		LocalDate fechaHoy = LocalDate.now();
			
		LocalDate fechaEstimada = fechaHoy.plusDays(proximoNivelFidelizacionDiasRestantes);
		
		String tiempo = null;
		String tituloProxNivel = null;
		
		if (proximoNivelFidelizacionDiasRestantes < 30) {
			tiempo = proximoNivelFidelizacionDiasRestantes == 1
					? DIA
					: DIAS;
			
			tituloProxNivel = proximoNivelFidelizacionDiasRestantes == NumberUtils.INTEGER_ZERO || proximoNivelFidelizacionDiasRestantes > 90  
					? null 
					: MessageFormat.format( miIberdroaTitBannerProxNivel, proximoNivelFidelizacionDiasRestantes+ ConstantesAPP.SPACE + tiempo); 
			
		}else {
			float cantidadMeses = (float) proximoNivelFidelizacionDiasRestantes / 30;
			
			int meses = Math.round(cantidadMeses);
			
			tiempo = meses == 1
					? MES
					: MESES;
			
			tituloProxNivel = MessageFormat.format( miIberdroaTitBannerProxNivel, meses + ConstantesAPP.SPACE + tiempo); 	
		}
		
		if (proximoNivelFidelizacionDiasRestantes >= 105) {
			tituloProxNivel = null;
		}

		String textoNegrita = internacionalizacionService.obtenerDescLiteralAppLargo(MI_PROXIMO_NIVEL_NEGRITA );
		String descripcionProximoNivel = internacionalizacionService.obtenerDescLiteralAppLargo(MI_PROXIMO_NIVEL_DESCRICION );
		
		String proximoNivelDesc = MessageFormat.format(descripcionProximoNivel , nombreNivel);

		DateTimeFormatter formatter = DateTimeFormat.forPattern(ConstantesAPP.DATE_FORMAT);
		String fechaEstimadaFormateada = fechaEstimada.toString(formatter);
		
		String negrita =  MessageFormat.format(textoNegrita, fechaEstimadaFormateada);

		LOG.info(CLASE + "obtenerMovimientosFuturos :: INICIO");
		MovimientosFuturos salida = null;
		// 1. Llamar a msclibk para obtener datos del saldo del cliente
		List<SaldoFuturoEnergyPack> listaSaldoFuturoEnergyPack = msclibkService.saldoFuturo(codCliente);
		LOG.info(CLASE + "obtenerMovimientosFuturos :: listaSaldoFuturoEnergyPack = " + listaSaldoFuturoEnergyPack);
		if(listaSaldoFuturoEnergyPack != null) {
			// 2. Ordenar listaMovimientosFuturo por codBeneficio (de menor a mayor)
			Collections.sort(listaSaldoFuturoEnergyPack, Comparator.comparing(SaldoFuturoEnergyPack::getCodBeneficio));
			LOG.info(CLASE + "obtenerMovimientosFuturos :: listaSaldoFuturoEnergyPack se ha ordenado = " + listaSaldoFuturoEnergyPack.toString());
			// 3. Obtener el alias o la direccion de cada contrato
			Map<String, String> ordenAlias = obtenerAliasDireccion(listaCtoSesion, obtenerAliasRS(codUsuario, codCliente, listaReceptoresSuministroDeUsuario));
			// 4. Preparar la salida del servicio
			salida = new MovimientosFuturos();
			List<MovimientoFuturo> listaMovimientosFuturo = new ArrayList<>();
			HashMap<String, Double> codBeneficioImporte = new HashMap<>();
			for (SaldoFuturoEnergyPack saldoFuturoEnergyPack : listaSaldoFuturoEnergyPack) {
				String codContrato = ObjectUtils.toString(saldoFuturoEnergyPack.getCodContrato());				

				MovimientoFuturo movimientoFuturo = obtenerMovimientoFuturo(ordenAlias, saldoFuturoEnergyPack, codContrato);

				listaMovimientosFuturo.add(movimientoFuturo);
				
				codBeneficioImporte.put(saldoFuturoEnergyPack.getCodBeneficio(), saldoFuturoEnergyPack.getImporteAnual());
			}	
			
			List<CategoriasMFMapper> categoriasMFMapper = movimientosFuturosMapper.getCategorias();
			List<CategoriasMovimientosFuturos> categoriasMovimientosFuturos = new ArrayList<>();
			List<DetalleContenidoTooltip> detalleContenidoTooltipList = new ArrayList<>();
			DecimalFormat df = new DecimalFormat("#.00");
			
			this.obtenerCategorias(categoriasMFMapper, codBeneficioImporte, df, categoriasMovimientosFuturos, detalleContenidoTooltipList);
			
			ContenidoTooltip contenidoTooltip = new ContenidoTooltip();
			contenidoTooltip.setTitulo(internacionalizacionService.obtenerDescLiteralLargo(ConstantesAPP.MES_I18N_LITBACK, ConstantesAPP.PREV_SAL_TOOL_CONT_TIT));
			contenidoTooltip.setSubtitulo(internacionalizacionService.obtenerDescLiteralLargo(ConstantesAPP.MES_I18N_LITBACK, ConstantesAPP.PREV_SAL_TOOL_CONT_SUB));
			contenidoTooltip.setDetalle(detalleContenidoTooltipList);
			
			TooltipPrevisionSaldo tooltipPrevisionSaldo = new TooltipPrevisionSaldo();
			tooltipPrevisionSaldo.setTitulo(internacionalizacionService.obtenerDescLiteralLargo(ConstantesAPP.MES_I18N_LITBACK, ConstantesAPP.PREV_SAL_TOOLTIP_TIT));
			tooltipPrevisionSaldo.setContenido(contenidoTooltip); 
			
			salida.setMovimientosFuturo(listaMovimientosFuturo);
			salida.setAntiguedadIcono(internacionalizacionService.obtenerDescLiteralAppLargo("MES_EP_MOV_FUT_ANTIGUEDAD_ICONO_01"));
			salida.setAntiguedadNegrita(internacionalizacionService.obtenerDescLiteralAppLargo("MES_EP_MOV_FUT_ANTIGUEDAD_SUB_TIT_NEG_01"));
			salida.setAntiguedadSubtitulo(internacionalizacionService.obtenerDescLiteralAppLargo("MES_EP_MOV_FUT_ANTIGUEDAD_SUB_TIT_01"));
			salida.setAntiguedadTitulo(internacionalizacionService.obtenerDescLiteralAppLargo("MES_EP_MOV_FUT_ANTIGUEDAD_TIT_01"));
			salida.setDetallePrevision(obtenerDetallePrevision(codCliente, ordenAlias));
			salida.setCategorias(categoriasMovimientosFuturos);
			BannerInfo bannerInfo;
			BannerProximoNivel bannerProximoNivel;

			double sumaTotal = listaSaldoFuturoEnergyPack.stream()
					.mapToDouble(movimiento -> Double.valueOf(movimiento.getImporteAnual()))
					.sum();

			String sumaTotalFormatted = df.format(sumaTotal).replace('.', ',');
			String banerSaldo = sumaTotalFormatted;

			bannerInfo = setBanerInfo("+" + banerSaldo + ConstantesAPP.EURO, tooltipPrevisionSaldo);
			bannerProximoNivel = setbannerProximoNivel(misdiasRes, proximoNivelFidelizacionDiasRestantes, tituloProxNivel, iconoProxNivel, proximoNivelDesc, negrita, ultNivelFid, nivelFid);

			salida.setBannerInfo(bannerInfo);
			salida.setBannerProximoNivel(bannerProximoNivel);

		}

		LOG.info(CLASE + "obtenerMovimientosFuturos :: FIN");
		return salida;
	}