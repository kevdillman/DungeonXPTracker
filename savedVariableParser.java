/*
    replaces savedVariableParser.py
    given a file path to a saved variable file of lua table data and output path for a csv:
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
import java.io.FileWriter;

public class savedVariableParser{

   // reformats dates to be easier to use during data processing steps
    private static String formatDate(String rawDate){
        // check that date field is populated
        if (rawDate == null || rawDate == "No Data"){
            return rawDate; // skip bad data
        }

        // extract year/month/day and time info
        // reformat to more typical layout
        try{
            String year = "20" + rawDate.substring(6, 8);
            String month = rawDate.substring(3, 5);
            String day = rawDate.substring(0, 2);
            String formattedDate = month + "/" + day + "/" + year + rawDate.substring(8);
            return formattedDate;
        }
        catch (Exception e){
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

        // reformat date time fields
        for (Map<String, String> run : result){
            run.put("startTime", formatDate(run.get("startTime")));
            run.put("endingTime", formatDate(run.get("endingTime")));
        }
        return result;
    }

    // writes passed data to a csv file specified in the passed output path
    private static void writeCSV(List<Map<String, String>> data, String outputPath){
        if (data.isEmpty()){
            System.out.println("No data to write.");
            return;
        }

        try (FileWriter writer = new FileWriter(outputPath)){
            // Collect all unique keys
            Set<String> headers = new LinkedHashSet<>();
            for (Map<String, String> row : data) {
                headers.addAll(row.keySet());
            }

            // Write header
            writer.write("rowCounter," + String.join(",", headers) + "\n");
            int rowCounter = 0;
            // Write rows
            for (Map<String, String> row : data){
                List<String> values = new ArrayList<>();

                for (String key : headers){
                    String value = row.getOrDefault(key, "");

                    // escape double quotes
                    values.add("\"" + value.replace("\"", "\"\"") + "\"");
                }

                writer.write("\"" + rowCounter + "\"," + String.join(",", values) + "\n");
                ++rowCounter;
            }
        }
        catch (IOException e){
            System.out.println("Error writing CSV: " + e.getMessage());
        }
    }

    // takes a path to a file and parses the contents of that file
    public static void main(String[] args){
        // check for arguments
        if(args.length == 0){
            System.out.println("No arguments");
            return;
        }

        // read filepath from passed argument
        String filePath = args[0];
        System.out.println("Reading file: " + filePath);

        // check that the file given exists and parses it's data
        try{
            String fileContents = Files.readString(Path.of(filePath));

            List<Map<String, String>> runs = parseDungeonData(fileContents);
            System.out.println("Parsed " + runs.size() + " dungeon runs.");

            // write the parsed data to a csv
            String accountName = args[1];
            String outputPath = "./dungeon_runs/" + accountName + "_dungeonDataJAVA.csv";
            writeCSV(runs, outputPath);
            System.out.println("CSV written to " + outputPath);
        }
        catch(IOException e){
            System.out.println("Error reading or writing file: " + e.getMessage());
        }
    }
}
