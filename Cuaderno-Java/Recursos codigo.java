
public class Main {
    public static void main(String[] args) throws Exception {
        
        LocalDateTime fechaHoy = LocalDateTime.now();
        LocalDateTime fechaLista = LocalDateTime.parse("2025-10-09T16:06:07").minusDays(30);
        
        System.out.println(fechaHoy);
        System.out.println(fechaLista);
        
         if (fechaHoy.isAfter(fechaLista)) {
            System.out.println("La fecha y hora " + fechaLista + " es inferior (más reciente) a 30 días desde ahora.");
        } else {
            System.out.println("La fecha y hora " + fechaLista + " es superior (más antigua) a 30 días desde ahora.");
        }
        
    }
}


LocalDateTime fechaHoy = LocalDateTime.now();
        
        LocalDateTime fechaLista = LocalDateTime.parse("2025-10-09T16:06:07").minusDays(30);
        
        System.out.println(fechaHoy);
        System.out.println(fechaLista);
        
        long diferenciaDias = ChronoUnit.DAYS.between(fechaHoy, fechaLista);
        System.out.println(diferenciaDias);


if(!CollectionUtils.isEmpty(desgloseSaldofuturo)) 
import com.iberdrola.gestionesonline.model.Tooltip.ResumenMovimientosSaldo;




String nombreCategoriaDestacada = internacionalizacionService.obtenerDescLiteralAppLargo("CATEGORIA_RESTAURANTES");
		String colorFondo = internacionalizacionService.obtenerDescLiteralAppLargo(ConstantesAPP.COLOR_FONDO_DESTACADO);
		
		List <MiIberdrolaExperienciasCategoria> categoriasBddDestacadas = categoriasBdd.stream()
                .filter(categoria -> nombreCategoriaDestacada.equals(categoria.getNombre())) //filtra para encontra que categoria es la destacada
                .map(categoria -> {
                	 boolean tieneAlianzaDestacada = categoria.getAlianzas().stream()
                			 .anyMatch(experiencia -> ConstantesAPP.SI.equals(experiencia.getDestacada())); // devuelve un booleancon el resultado de encontrar una alianza destacada
                	 categoria.setDestacado(tieneAlianzaDestacada); //Settea la categoria y cambia su atributo boolean destacado 
                	 categoria.getAlianzas().stream()
                	 .map(experiencia -> {
                		 if (experiencia.getDestacada().equals(ConstantesAPP.SI)) { // Comprueba si alguna alianza es destacada y cambia su color de fondo 
                			 experiencia.setColorFondo(colorFondo);
                		 }
                		 return experiencia;	 
                	 })
                	 .collect(Collectors.toList());
                	 return categoria; //Devuelve la categoria ya preparada
                })
				.collect(Collectors.toList()); 



                   