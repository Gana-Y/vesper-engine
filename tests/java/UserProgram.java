import java.util.Scanner;

public class UserProgram {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            System.out.println("Sum: " + (a + b));
        } else {
            System.out.println("Hello from Java Vesper");
        }
    }
}
