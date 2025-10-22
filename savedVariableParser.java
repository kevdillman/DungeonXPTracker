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
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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

   // reformats dates to be easier to use during data processing steps
   private static String formatDate(String rawDate){

    // check that date field is populated
    if (rawDate == null || rawDate == "No Data"){
        return rawDate; // skip bad data
    }

    // extract year/month/day and time info
    // reformat to more typical layout
    try {
        String year = "20" + rawDate.substring(6, 8);
        String month = rawDate.substring(3, 5);
        String day = rawDate.substring(0, 2);
        String formattedDate = month + "/" + day + "/" + year + rawDate.substring(8);
        return formattedDate;
    } catch (Exception e) {
        return rawDate; // fallback if malformed
    }
}


    // parse Lua-style data
    private static List<Map<String, String>> parseDungeonData(String fileData){
        List<Map<String, String>> result = new ArrayList<>();

        // isolate ["dungeons"] section
        Pattern dungeonsSectionPattern = Pattern.compile("\\[\"dungeons\"\\]\\s*=\\s*\\{(.*)\\}\\s*,?\\s*\\}", Pattern.DOTALL);
        Matcher dungeonSectionMatcher = dungeonsSectionPattern.matcher(fileData);

        if (!dungeonSectionMatcher.find()){
            System.out.println("No [\"dungeons\"] section found!");
            return result;
        }

        // fill string with unprocessed dungeon data
        String dungeonsBlock = dungeonSectionMatcher.group(1);

        // extract each individual dungeon run block
        Pattern dungeonPattern = Pattern.compile("\\{(.*?)\\}", Pattern.DOTALL);
        Matcher matcher = dungeonPattern.matcher(dungeonsBlock);

        // build list with all dungeon run data found
        while (matcher.find()){
            String block = matcher.group(1);
            Map<String, String> dungeonRun = new HashMap<>();

            // find key/value pairs like ["key"] = "value"
            Pattern keyValuePattern = Pattern.compile("\\[\"(.*?)\"\\]\\s*=\\s*\"?(.*?)\"?(,|$)");
            Matcher keyValueMatcher = keyValuePattern.matcher(block);

            while (keyValueMatcher.find()){
                String key = keyValueMatcher.group(1);
                String value = keyValueMatcher.group(2);
                dungeonRun.put(key, value);
            }

            if (!dungeonRun.isEmpty()){
                result.add(dungeonRun);
            }
        }

        // build the set of all found keys
        Set<String> allKeys = new HashSet<>();
        for (Map<String, String> run : result){
            allKeys.addAll(run.keySet());
        }

        // normalize all runs to contain same keys and fill
        // any missing entries with No Data
        for (Map<String, String> run : result){
            for (String key : allKeys){
                if (!run.containsKey(key)){
                    run.put(key, "No Data");
                }
            }
        }

        return result;
    }

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
            //System.out.println("\nFile contents (first 500 chars):");
            //System.out.println(fileContents.substring(0, Math.min(fileContents.length(), 500)));

            List<Map<String, String>> runs = parseDungeonData(fileContents);
            System.out.println("Parsed " + runs.size() + " dungeon runs.");
            System.out.println("List contents:");
            for (int i = 0; i < 5; ++i){
                System.out.println(runs.get(i));
            }
            System.out.println(runs.get((runs.size())-1));
        }
        catch (IOException e) {
            System.out.println("Error reading file: " + e.getMessage());
        }
    }
}
