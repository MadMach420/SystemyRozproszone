package sr.serialization;

import sr.proto.AddressBookProtos.Person;

import java.io.FileOutputStream;
import java.io.IOException;

public class ProtoSerialization {

    public static void main(String[] args) {
        try {
            new ProtoSerialization().testProto();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }

    public void testProto() throws IOException {
        Person p1 =
                Person.newBuilder()
                        .setId(123456)
                        .setName("Włodzimierz Wróblewski")
                        .setEmail("wrobel@poczta.com")
                        .addPhones(
                                Person.PhoneNumber.newBuilder()
                                        .setNumber("+48-12-555-4321")
                                        .setType(Person.PhoneType.HOME))
                        .addPhones(
                                Person.PhoneNumber.newBuilder()
                                        .setNumber("+48-699-989-796")
                                        .setType(Person.PhoneType.MOBILE))
						.setNewMessage(Person.NewMessage.newBuilder()
                                .addExample(0.5).addExample(1.2).addExample(1.7))
						.build();

        byte[] p1ser = null;

        long n = 1000;
        System.out.println("Performing proto serialization " + n + " times...");
        for (long i = 0; i < n; i++) {
            p1ser = p1.toByteArray();
        }
        System.out.println("... finished.");

        //print data as hex values
        for (byte b : p1ser) {
            System.out.print(String.format("%02X", b));
        }

        //serialize again (only once) and write to a file
        FileOutputStream file = new FileOutputStream("person2.ser");
        file.write(p1.toByteArray());
        file.close();

    }
}
