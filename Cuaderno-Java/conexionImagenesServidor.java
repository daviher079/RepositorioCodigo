URL url = new URL(prepararUrl(urlImagen, "-small"));
	            /*HttpURLConnection connection = (HttpURLConnection) url.openConnection();

	            
	            connection.setRequestMethod("GET");
	            //connection.setRequestProperty("Authorization", ssoToken);
	            connection.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");
	            //connection.setRequestProperty("Accept", "image/jpeg");
	            connection.setConnectTimeout(5000); 
	            connection.setReadTimeout(5000);
	            
	            int responseCode = connection.getResponseCode();*/
				
				URLConnection connection = url.openConnection();
	            connection.setConnectTimeout(5000); 
	            connection.setReadTimeout(5000);    
	            connection.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");

	            
	            connection.connect();
	            String contentType = connection.getContentType();
	            LOG.debug("getPermission " + connection.getPermission().toString() + " contentType " + contentType);