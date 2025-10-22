/*
    replaces savedVariableParser.py
    -takes a file path to a saved variable file of lua table data
    -will:
        -find all data tags in file
        -build structured data from parsed data
        -output a csv file of the parsed data
*/

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class savedVariableParser{

    /*public List<Map<String, String>> parse(String luaData) {
        List<Map<String, String>> tables = new ArrayList<>();

        int tableStart = luaData.indexOf('{');
        while (tableStart != -1) {
            int tableEnd = luaData.indexOf('}', tableStart);
            if (tableEnd == -1) break;

            String tableText = luaData.substring(tableStart, tableEnd + 1);
            Map<String, String> table = parseTable(tableText);
            if (!table.isEmpty()) {
                tables.add(table);
            }

            tableStart = luaData.indexOf('{', tableEnd);
        }

        return tables;
    }

    private Map<String, String> parseTable(String tableText) {
        Map<String, String> table = new HashMap<>();

        Pattern pattern = Pattern.compile("\\[\"(.*?)\"\\]\\s*=\\s*\"?(.*?)\"?,");
        Matcher matcher = pattern.matcher(tableText);

        while (matcher.find()) {
            String key = matcher.group(1);
            String value = matcher.group(2);
            table.put(key, value);
        }

        return table;
    }*/

    // takes a path to a file and parses the contents of that file
    public static void main(String[] args) {
        // check for arguments
        if(args.length == 0){
            System.out.println("No arguments");
            return;
        }

        // read filepath from passed argument
        String filePath = args[0];
        System.out.println("Reading file: " + filePath);

        // check that the file given exists and prints first 500 characters
        try{
            String fileContents = Files.readString(Path.of(filePath));
            System.out.println("\nFile contents (first 500 chars):");
            System.out.println(fileContents.substring(0, Math.min(fileContents.length(), 500)));
        }
        catch (IOException e) {
            System.out.println("Error reading file: " + e.getMessage());
        }
    }
}
