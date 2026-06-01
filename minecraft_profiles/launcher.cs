@'
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;

class MinecraftLauncher {
    static string mcDir = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), ".minecraft");
    static string javaHome = @"C:\Users\keeeensy\AppData\Local\Programs\Microsoft\jdk-25.0.3.9-hotspot";
    static string javaExe = Path.Combine(javaHome, "bin", "javaw.exe");
    static string libDir = Path.Combine(mcDir, "libraries");
    static string versionsDir = Path.Combine(mcDir, "versions");
    static string modsDir = Path.Combine(mcDir, "mods");
    static string assetsDir = Path.Combine(mcDir, "assets");
    static string nativesDir = Path.Combine(mcDir, "natives_tmp");
    static string clientJarPath;

    static string ResolveLib(string name) {
        // name format: group:artifact:version or group:artifact:version:classifier
        var parts = name.Split(':');
        string group = parts[0], artifact = parts[1], version = parts[2];
        string classifier = parts.Length > 3 ? "-" + parts[3] : "";
        string jarName = $"{artifact}-{version}{classifier}.jar";
        string path = group.Replace('.', Path.DirectorySeparatorChar);
        return Path.Combine(libDir, path, artifact, version, jarName);
    }

    static string ResolveClientJar() {
        // Find via index from version json
        string vanillaJson = Path.Combine(versionsDir, "26.1.2", "26.1.2.json");
        dynamic json = Newtonsoft.Json.JsonConvert.DeserializeObject(File.ReadAllText(vanillaJson));
        string sha1 = json.downloads.client.sha1;
        string objectsDir = Path.Combine(libDir, "v1", "objects");
        string subDir = sha1.Substring(0, 2);
        return Path.Combine(objectsDir, subDir, sha1, "client.jar");
    }

    static void ExtractNatives() {
        if (Directory.Exists(nativesDir)) Directory.Delete(nativesDir, true);
        Directory.CreateDirectory(nativesDir);
        
        string vanillaJson = Path.Combine(versionsDir, "26.1.2", "26.1.2.json");
        dynamic json = Newtonsoft.Json.JsonConvert.DeserializeObject(File.ReadAllText(vanillaJson));
        
        foreach (var lib in json.libraries) {
            string name = lib.name;
            if (!name.Contains("natives-windows")) continue;
            string jarPath = ResolveLib(name);
            if (!File.Exists(jarPath)) continue;
            using (var archive = ZipFile.OpenRead(jarPath)) {
                foreach (var entry in archive.Entries) {
                    if (entry.Name.EndsWith(".dll") || entry.Name.EndsWith(".so") || entry.Name.EndsWith(".dylib")) {
                        string target = Path.Combine(nativesDir, entry.Name);
                        try { entry.ExtractToFile(target, true); } catch { }
                    }
                }
            }
        }
    }

    static List<string> BuildClasspath() {
        var cp = new List<string>();
        // Client jar
        cp.Add(clientJarPath);
        
        // Vanilla libraries
        string vanillaJson = Path.Combine(versionsDir, "26.1.2", "26.1.2.json");
        dynamic vJson = Newtonsoft.Json.JsonConvert.DeserializeObject(File.ReadAllText(vanillaJson));
        foreach (var lib in vJson.libraries) {
            string name = lib.name;
            if (name.Contains("natives-")) continue; // skip native jars
            // Check rules - only include for Windows
            if (lib.rules != null) {
                bool allow = false;
                foreach (var rule in lib.rules) {
                    string action = rule.action;
                    if (rule.os != null && rule.os.name == "osx") { allow = action == "allow"; break; }
                    if (rule.os != null && rule.os.name == "linux") { allow = action == "allow"; break; }
                    if (rule.os != null && rule.os.name == "windows") { allow = action == "allow"; }
                    if (rule.os == null) allow = action == "allow";
                }
                if (!allow) continue;
            }
            string path = ResolveLib(name);
            if (File.Exists(path)) cp.Add(path);
        }

        // Fabric libraries
        string fabricJson = Path.Combine(versionsDir, "fabric-loader-0.19.2-26.1.2", "fabric-loader-0.19.2-26.1.2.json");
        dynamic fJson = Newtonsoft.Json.JsonConvert.DeserializeObject(File.ReadAllText(fabricJson));
        foreach (var lib in fJson.libraries) {
            string name = lib.name;
            if (name.Contains("natives-")) continue;
            if (lib.rules != null) {
                bool allow = false;
                foreach (var rule in lib.rules) {
                    string action = rule.action;
                    if (rule.os != null && rule.os.name == "osx") { allow = action == "allow"; break; }
                    if (rule.os != null && rule.os.name == "linux") { allow = action == "allow"; break; }
                    if (rule.os != null && rule.os.name == "windows") { allow = action == "allow"; }
                    if (rule.os == null) allow = action == "allow";
                }
                if (!allow) continue;
            }
            // If lib has artifact path, use it; otherwise resolve by name
            string path;
            if (lib.artifact != null && lib.artifact.path != null) {
                path = Path.Combine(libDir, (string)lib.artifact.path);
            } else {
                path = ResolveLib(name);
            }
            if (File.Exists(path)) cp.Add(path);
        }

        // Mod jars
        if (Directory.Exists(modsDir)) {
            foreach (var mod in Directory.GetFiles(modsDir, "*.jar")) {
                cp.Add(mod);
            }
        }

        return cp;
    }

    static void Main(string[] args) {
        clientJarPath = ResolveClientJar();
        if (!File.Exists(clientJarPath)) { Console.Error.WriteLine("Client jar not found"); return; }
        
        Console.WriteLine("Extracting natives...");
        ExtractNatives();
        
        Console.WriteLine("Building classpath...");
        var cp = BuildClasspath();
        string classpath = string.Join(";", cp);
        
        string gameDir = mcDir;
        string versionName = "fabric-loader-0.19.2-26.1.2";

        // JVM arguments
        var jvmArgs = new List<string> {
            $"-Djava.library.path={nativesDir}",
            $"-Djna.tmpdir={nativesDir}",
            $"-Dorg.lwjgl.system.SharedLibraryExtractPath={nativesDir}",
            $"-Dio.netty.native.workdir={nativesDir}",
            $"-Dminecraft.launcher.brand=opencode",
            $"-Dminecraft.launcher.version=1.0",
            $"-DFabricMcEmu= net.minecraft.client.main.Main ",
            "-Xss1M",
            "--sun-misc-unsafe-memory-access=allow",
            "--enable-native-access=ALL-UNNAMED",
            "-Xms2G",
            "-Xmx4G",
            "-XX:+UseCompactObjectHeaders",
            "-XX:+AlwaysPreTouch",
            "-XX:+UseStringDeduplication",
            "-XX:+UseZGC",
            $"-cp",
            $"{classpath}"
        };

        // Game arguments
        var gameArgs = new List<string> {
            "--username", "Keeeensyy",
            "--version", versionName,
            "--gameDir", gameDir,
            "--assetsDir", Path.Combine(assetsDir),
            "--assetIndex", "30",
            "--uuid", "00000000-0000-0000-0000-000000000000",
            "--accessToken", "0",
            "--clientId", "opencode",
            "--xuid", "",
            "--versionType", "release"
        };

        // Build command line
        var psi = new System.Diagnostics.ProcessStartInfo();
        psi.FileName = javaExe;
        psi.Arguments = string.Join(" ", jvmArgs.Select(a => a.Contains(" ") ? $"\"{a}\"" : a)) 
            + " net.fabricmc.loader.impl.launch.knot.KnotClient "
            + string.Join(" ", gameArgs.Select(a => a.Contains(" ") ? $"\"{a}\"" : a));
        psi.WorkingDirectory = gameDir;
        psi.UseShellExecute = false;
        
        Console.WriteLine("Launching Minecraft Fabric...");
        var proc = System.Diagnostics.Process.Start(psi);
        proc.WaitForExit();
        
        // Cleanup natives
        if (Directory.Exists(nativesDir)) Directory.Delete(nativesDir, true);
    }
}
'@