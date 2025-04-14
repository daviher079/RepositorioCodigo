
	@Loggable(LogLevel.DEBUG)
	public String calcularColor(String urlImagen) {
		String color = "";
		
		try {
			if(StringUtils.isNotBlank(urlImagen)) {
					urlImagen = cambiarTamanio(urlImagen, ConstantesAPP.SIZE_IMAGE_SMALL);
					
		            /*
		             * && !(urlImagen.contains(ConstantesAPP.IBERDROLA) || urlImagen.contains(ConstantesAPP.VIPDISTRICT)) 
		             * HttpURLConnection connection = (HttpURLConnection) url.openConnection();

		            
		            connection.setRequestMethod("GET");
		            //connection.setRequestProperty("Authorization", ssoToken);
		            connection.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");
		            //connection.setRequestProperty("Accept", "image/jpeg");
		            connection.setConnectTimeout(5000); 
		            connection.setReadTimeout(5000);
		            
		            int responseCode = connection.getResponseCode();*/
		            BufferedImage imagen = ImageIO.read(new ByteArrayInputStream(getImagen(urlImagen)));
					
					//BufferedImage imagen = ImageIO.read(new URL(prepararUrl(urlImagen, "-small")));
				
				int primerPixel = imagen.getRGB(0, 0);
				Color colorPixel = new Color(primerPixel);
				color = colorFormatoHexadecimal(colorPixel);
			}else {
				color = colorFormatoHexadecimal(Color.WHITE);
			}
		} catch (IOException e) {
			e.printStackTrace();
		} 
		
		return color;
	}
	
	@Loggable(LogLevel.DEBUG)
	private String colorFormatoHexadecimal(Color colorPixel) {
		return String.format(ConstantesAPP.FORMATO_HEXADECIMAL, colorPixel.getRed(), colorPixel.getGreen(), colorPixel.getBlue());
	}
	
	
	@Loggable(LogLevel.DEBUG)
	private String cambiarTamanio(String urlImagen, String size) {
		if(StringUtils.isNotBlank(urlImagen)) {
			int ultimoPunto = urlImagen.lastIndexOf('.');
			urlImagen = urlImagen.substring(0, ultimoPunto) + size + urlImagen.substring(ultimoPunto);
		}
		return urlImagen;
	}
	
	@Loggable(LogLevel.DEBUG)
	private HttpHeaders getCustomHeaders() {
		LOG.info("VipDistrictServiceImpl::getCustomHeaders INI");

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Accept", MediaType.APPLICATION_JSON_VALUE);
        headers.add(ConstantesAPP.AUTHORIZATION, ConstantesAPP.BEARER + bearerToken);
		
        LOG.info("VipDistrictServiceImpl::getCustomHeaders FIN");
        
        return headers;
	}
	
	
	@Loggable(LogLevel.DEBUG)
	public byte[] getImagen(String urlImagen) {
		
		HttpHeaders headers = getCustomHeaders();
		
		HttpEntity<String> entity = new HttpEntity<>(PARAMETERS, headers);

		ResponseEntity<byte[]> response = null;
		try {
			LOG.debug("VipDistrictServiceImpl.getOfertas :: Llamando a VipDistrict :: URL: " + urlImagen);
			response = restTemplate.exchange(urlImagen, HttpMethod.GET, entity, byte[].class);
		} catch (HttpStatusCodeException ex) {
			loggerErrorVipDistrict(urlImagen, ex);
			throw ex;
		}
		
		return response.getBody();
	}
	
	private void loggerErrorVipDistrict(String url, HttpStatusCodeException ex) {
		LOG.error("Error llamando a VipDistrict :: URL:  " + url + " :: Exception: " + Objects.toString(ex) );
		LOG.error("VipDistrict HTTP Error :: " + ex.getStatusCode());
	}