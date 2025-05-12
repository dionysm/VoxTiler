# VoxTiler Documentation

> [English Documentation](#english-documentation) | [Deutsche Dokumentation](#deutsche-dokumentation)

## English Documentation

### Overview

VoxTiler is a Python tool designed to process MagicaVoxel (.vox) files, split them into smaller chunks, and convert them to OBJ format for use in game engines. This documentation provides detailed information about the tool's functionality, usage, and technical implementation.

### Detailed Features

#### 1. VOX File Parsing
- Reads binary MagicaVoxel (.vox) files according to the official format
- Extracts model dimensions, voxel data, and color palette
- Handles different versions of the VOX format

#### 2. Flexible Splitting Options
- **Fixed Chunk Size**: Specify exact dimensions for output chunks (e.g., 16x16x10)
- **Division by Value**: Divide the model into a specific number of parts along each axis
- **Selective Splitting**: Choose which dimensions to split and which to keep intact
- **No Splitting**: Option to only convert formats without splitting

#### 3. Format Conversion
- **VOX Output**: Create valid MagicaVoxel files that maintain the original palette
- **OBJ Output**: Generate Wavefront OBJ files with corresponding MTL material definitions
  - Optimized mesh with only visible faces to reduce polygon count
  - Coordinate system adjusted for Godot compatibility (Y/Z swapped)
  - Complete materials with original colors from the voxel model

### Usage Guide

#### Basic Usage
1. Run the script: `python voxtiler.py`
2. Enter the path to your .vox file when prompted
3. Specify the output directory (default: "output_chunks")
4. Choose your splitting option:
   - Option 1: Fixed chunk size
   - Option 2: Division by value
   - Option 3: No splitting (only format conversion)
5. Choose your output format:
   - Option 1: MagicaVoxel (.vox)
   - Option 2: Wavefront OBJ (.obj)
   - Option 3: Both formats

#### Example: Splitting a Large Terrain

Imagine you have a large terrain model with dimensions 176x112x10 that is too big for your game engine to handle efficiently. You can split it into 16x16x10 chunks while preserving the full height:

1. Run the tool and input your .vox file
2. Choose Option 1 (Fixed chunk size)
3. Enter "16" for X, "16" for Y, and "0" for Z (or leave Z blank)
4. Choose your preferred output format

The tool will create multiple 16x16x10 chunks, named according to their position in the original model (e.g., chunk_x0_y0.vox, chunk_x0_y16.vox, etc.)

#### Using the OBJ Files in Godot

The OBJ files are specifically optimized for Godot:
1. Import the OBJ files into your Godot project
2. The MTL files will be automatically imported, preserving the colors
3. The coordinates are already adjusted for Godot's coordinate system

### Technical Details

#### VOX File Format

The tool parses the VOX format which consists of chunks:
- `VOX `: File identifier and version
- `MAIN`: Parent chunk containing all other chunks
- `SIZE`: Model dimensions
- `XYZI`: Voxel data with coordinates and color indices
- `RGBA`: Color palette with 256 RGBA colors

#### OBJ Optimization

The OBJ exporter uses several optimization techniques:
- Only creates faces for visible sides of voxels (adjacent to empty space)
- Separate material for each color in the palette
- Faces are oriented correctly for proper rendering

#### Performance Considerations

- For very large models (millions of voxels), the process may be memory-intensive
- The OBJ export creates separate faces for each visible voxel side, which may lead to large files
- Consider using LOD (Level of Detail) techniques for distant chunks in your game

---

## Deutsche Dokumentation

### Überblick

VoxTiler ist ein Python-Tool, das entwickelt wurde, um MagicaVoxel (.vox) Dateien zu verarbeiten, sie in kleinere Stücke zu teilen und sie in das OBJ-Format für die Verwendung in Game-Engines zu konvertieren. Diese Dokumentation bietet detaillierte Informationen über die Funktionalität, Verwendung und technische Implementierung des Tools.

### Detaillierte Funktionen

#### 1. VOX-Datei-Parsing
- Liest binäre MagicaVoxel (.vox) Dateien gemäß dem offiziellen Format
- Extrahiert Modellabmessungen, Voxeldaten und Farbpalette
- Unterstützt verschiedene Versionen des VOX-Formats

#### 2. Flexible Teilungsoptionen
- **Feste Chunk-Größe**: Genaue Abmessungen für Ausgabe-Chunks festlegen (z.B. 16x16x10)
- **Teilung durch Wert**: Teile das Modell in eine bestimmte Anzahl von Teilen entlang jeder Achse
- **Selektive Teilung**: Wähle, welche Dimensionen geteilt werden und welche intakt bleiben
- **Keine Teilung**: Option zur reinen Formatkonvertierung ohne Teilung

#### 3. Formatkonvertierung
- **VOX-Ausgabe**: Erstelle gültige MagicaVoxel-Dateien, die die Originalpalette beibehalten
- **OBJ-Ausgabe**: Erzeuge Wavefront OBJ-Dateien mit entsprechenden MTL-Materialdefinitionen
  - Optimiertes Mesh mit nur sichtbaren Flächen zur Reduzierung der Polygonanzahl
  - Angepasstes Koordinatensystem für Godot-Kompatibilität (Y/Z vertauscht)
  - Vollständige Materialien mit Originalfarben aus dem Voxel-Modell

### Nutzungsanleitung

#### Grundlegende Verwendung
1. Führe das Skript aus: `python voxtiler.py`
2. Gib den Pfad zu deiner .vox-Datei ein, wenn du dazu aufgefordert wirst
3. Gib das Ausgabeverzeichnis an (Standard: "output_chunks")
4. Wähle deine Teilungsoption:
   - Option 1: Feste Chunk-Größe
   - Option 2: Teilung durch Wert
   - Option 3: Keine Teilung (nur Formatkonvertierung)
5. Wähle dein Ausgabeformat:
   - Option 1: MagicaVoxel (.vox)
   - Option 2: Wavefront OBJ (.obj)
   - Option 3: Beide Formate

#### Beispiel: Aufteilen eines großen Terrains

Angenommen, du hast ein großes Terrainmodell mit den Abmessungen 176x112x10, das für deine Game-Engine zu groß ist, um es effizient zu verarbeiten. Du kannst es in 16x16x10 Chunks aufteilen und dabei die volle Höhe beibehalten:

1. Führe das Tool aus und gib deine .vox-Datei ein
2. Wähle Option 1 (Feste Chunk-Größe)
3. Gib "16" für X, "16" für Y und "0" für Z ein (oder lasse Z leer)
4. Wähle dein bevorzugtes Ausgabeformat

Das Tool erstellt mehrere 16x16x10 Chunks, die nach ihrer Position im Originalmodell benannt sind (z.B. chunk_x0_y0.vox, chunk_x0_y16.vox, usw.)

#### Verwendung der OBJ-Dateien in Godot

Die OBJ-Dateien sind speziell für Godot optimiert:
1. Importiere die OBJ-Dateien in dein Godot-Projekt
2. Die MTL-Dateien werden automatisch importiert und bewahren die Farben
3. Die Koordinaten sind bereits an Godots Koordinatensystem angepasst

### Technische Details

#### VOX-Dateiformat

Das Tool parst das VOX-Format, das aus Chunks besteht:
- `VOX `: Dateikennung und Version
- `MAIN`: Eltern-Chunk, der alle anderen Chunks enthält
- `SIZE`: Modellabmessungen
- `XYZI`: Voxeldaten mit Koordinaten und Farbindizes
- `RGBA`: Farbpalette mit 256 RGBA-Farben

#### OBJ-Optimierung

Der OBJ-Exporter verwendet mehrere Optimierungstechniken:
- Erstellt nur Flächen für sichtbare Seiten von Voxeln (angrenzend an leeren Raum)
- Separates Material für jede Farbe in der Palette
- Korrekt orientierte Flächen für eine ordnungsgemäße Rendering

#### Leistungsüberlegungen

- Für sehr große Modelle (Millionen von Voxeln) kann der Prozess speicherintensiv sein
- Der OBJ-Export erstellt separate Flächen für jede sichtbare Voxelseite, was zu großen Dateien führen kann
- Erwäge die Verwendung von LOD (Level of Detail)-Techniken für entfernte Chunks in deinem Spiel
