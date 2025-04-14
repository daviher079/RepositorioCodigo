	@Loggable(LogLevel.DEBUG)
	public List<CondicionesLegales> listaCondicionesLegales(String pantalla) {
 
		List<CondicionesLegales> salidaDefinitiva = new ArrayList<>();
 
		Map<String, List<CondicionesLegalesDto>> mapNumCheck = condicionesLegalesAppMapper
				.getCondicionesLegalesApp(pantalla).stream()
				.collect(Collectors.groupingBy(CondicionesLegalesDto::getNumCheck));
 
		for (Entry<String, List<CondicionesLegalesDto>> entry : mapNumCheck.entrySet()) {
			CondicionesLegales cl = new CondicionesLegales();
			for (CondicionesLegalesDto condicionDto : entry.getValue()) {
 
				cl.setIdCondicionUrl(condicionDto.getIdCondicionUrl());
				cl.setIdCondicionesLegales(condicionDto.getIdCondicionesLegales());
				cl.setDescripcion(condicionDto.getDescripcion());
				cl.setTexto(condicionDto.getTexto());
				cl.setNumCheck(condicionDto.getNumCheck());
				cl.setHipervinculo(entry.getValue().stream().map(CondicionesLegalesDto::getHipervinculo)
						.collect(Collectors.toList()));
				cl.setUrl(entry.getValue().stream().map(CondicionesLegalesDto::getUrl).collect(Collectors.toList()));
				if (!salidaDefinitiva.contains(cl)) {
					salidaDefinitiva.add(cl);
				}
			}
		}
		return salidaDefinitiva;
	}