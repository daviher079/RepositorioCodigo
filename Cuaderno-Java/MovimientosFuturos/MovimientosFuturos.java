package com.iberdrola.gestionesonline.model;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;

@Data
public class MovimientosFuturos {
	@JsonProperty("bannerInfo")
	private BannerInfo bannerInfo;

	@JsonProperty("movimientosFuturos")
	List<MovimientoFuturo> movimientosFuturo;
	
	@JsonProperty("antiguedadTitulo")
	private String antiguedadTitulo;
	
	@JsonProperty("antiguedadNegrita")
	private String antiguedadNegrita;
	
	@JsonProperty("antiguedadSubtitulo")
	private String antiguedadSubtitulo;
	
	@JsonProperty("antiguedadIcono")
	private String antiguedadIcono;
	
	@JsonProperty("bannerProximoNivel")
	private BannerProximoNivel bannerProximoNivel;
	
	@JsonProperty("detallePrevision")
	private DetallePrevision detallePrevision;
	
	@JsonProperty("categorias")
	private List<CategoriasMovimientosFuturos> categorias;

}