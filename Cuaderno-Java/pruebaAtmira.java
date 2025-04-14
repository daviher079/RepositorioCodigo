import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class Streams {
    public static void main(String args[]) {
        
        List<Integer> numeros = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20);
        //Pista. Los imports ya estan agregados
        
        //Prueba 1. Extraer los números pares
         List<Integer> pares = numeros.stream()
        .filter(num -> num % 2 == 0)
        .collect(Collectors.toList());
        System.out.println(pares);
        
        //Prueba 2. Recuperar únicamente el último registro de la lista
        int ultimo = numeros.stream().reduce(0 ,(first, second) -> second);
        System.out.println(ultimo);
        
        //Prueba 3. Extraer los números pares, multiplicarlos por 2 ordenando por orden descendiente y unicamente quedarnos con los 5 primeros.
        List<Integer> numMultiplicados = pares.stream()
        .map(num -> num * 2)
        .sorted((num1, num2) -> Integer.compare(num2, num1))
        .limit(5)
        .collect(Collectors.toList());
         System.out.println(numMultiplicados);
    }
}
