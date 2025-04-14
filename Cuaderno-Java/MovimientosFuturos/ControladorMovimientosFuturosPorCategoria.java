@POST
	@ApiOperation(value = "getMovimientosFuturosPorCategoria", notes = "Obtiene los movimientos futuros por categor�a")
	@ApiResponses({ 
	    @ApiResponse(code = 200, message = "OK"),
	    @ApiResponse(code = 418, message = "ERROR", response = MsgConfirmacion.class) 
	})
	@Path("/getMovimientosFuturosPorCategoria")
	@PostMapping(value = "/getMovimientosFuturosPorCategoria", produces = "application/json", headers = "Accept=application/json")
	public MovimientosFuturosPorCatResponse getMovimientosFuturosPorCategoria(
	        @RequestBody MovimientosFuturosPorCategoriaRequest request, HttpSession httpSession) {

	    LOGGER.info("MovimientosFuturosController :: getMovimientosFuturosPorCategoria :: INICIO");

	    MovimientosFuturosPorCatResponse salida = null;
	    try {
	        String codUsuario = sesionUsuario.getLoggedUser().getCodUsuario();
	        String codCliente = sesionUsuario.getClienteSEL().getCodCliente();
	        List<ContratoListaVO> listaContratos = sesionUsuario.getListaContratos();
	        ListaReceptorSuministroSesionUsuario listaReceptores = sesionUsuario.getListaReceptoresDeSuministroConAliasEstadoNoBaja();

	        salida = service.obtenerMovimientosFuturosPorCategoria(
	            request.getIdCategoria(), codUsuario, codCliente, listaContratos, listaReceptores, httpSession
	        );

	        if (salida == null) {
	            LOGGER.error("MovimientosFuturosController::getMovimientosFuturosPorCategoria:: No se encontraron movimientos futuros para la categor�a");
	            sendMsg(ERR_GEN_TIT, ERR_GEN, MsgConfirmacionLevel.ERROR, datoClaveApp);
	        }
	    } catch (Exception e) {
	        LOGGER.error("MovimientosFuturosController::getMovimientosFuturosPorCategoria:: Ha ocurrido un error -> ", e);
	        sendMsg(ERR_GEN_TIT, ERR_GEN, MsgConfirmacionLevel.ERROR, datoClaveApp);
	    }

	    LOGGER.info("MovimientosFuturosController :: getMovimientosFuturosPorCategoria :: FIN");
	    return salida;
	}