import os
import struct
import numpy as np
from collections import defaultdict

# VoxTiler - A tool for splitting MagicaVoxel files into smaller chunks and converting to OBJ

# Function to parse a MagicaVoxel file
def parse_vox_file(filename):
    with open(filename, 'rb') as f:
        # Read VOX header
        magic = f.read(4)
        if magic != b'VOX ':
            raise ValueError("Not a valid VOX file")
        
        version = struct.unpack('<I', f.read(4))[0]
        
        # Read MAIN chunk
        main_id = f.read(4)
        if main_id != b'MAIN':
            raise ValueError("MAIN chunk missing")
        
        main_content_size = struct.unpack('<I', f.read(4))[0]
        main_children_size = struct.unpack('<I', f.read(4))[0]
        
        # Initialize variables
        model_size = None
        voxels = []
        palette = None
        
        # Read chunks
        while True:
            try:
                chunk_id = f.read(4)
                if not chunk_id or len(chunk_id) < 4:
                    break
                
                chunk_content_size = struct.unpack('<I', f.read(4))[0]
                chunk_children_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'SIZE':
                    # Read model size
                    size_x, size_y, size_z = struct.unpack('<III', f.read(12))
                    model_size = (size_x, size_y, size_z)
                    print(f"Model dimensions: X={size_x}, Y={size_y}, Z={size_z}")
                
                elif chunk_id == b'XYZI':
                    # Read voxel data
                    num_voxels = struct.unpack('<I', f.read(4))[0]
                    for _ in range(num_voxels):
                        x, y, z, i = struct.unpack('<BBBB', f.read(4))
                        voxels.append((x, y, z, i))
                
                elif chunk_id == b'RGBA':
                    # Read color palette
                    palette = []
                    for _ in range(256):
                        r, g, b, a = struct.unpack('<BBBB', f.read(4))
                        palette.append((r, g, b, a))
                else:
                    # Skip other chunks
                    f.seek(chunk_content_size, 1)
            except Exception as e:
                print(f"Error reading chunk: {e}")
                break
        
        # If no palette was found, create a default palette
        if palette is None:
            palette = [(0, 0, 0, 0)]  # Index 0 is transparent
            for i in range(1, 256):
                palette.append((255, 255, 255, 255))  # All others white
        
        return model_size, voxels, palette

# Function to write a MagicaVoxel file
def write_vox_file(filename, size_x, size_y, size_z, voxels, palette):
    with open(filename, 'wb') as f:
        # VOX header
        f.write(b'VOX ')  # Magic number
        f.write(struct.pack('<I', 150))  # Version
        
        # MAIN chunk
        f.write(b'MAIN')
        f.write(struct.pack('<I', 0))  # Size of MAIN chunk content
        
        # Calculate the size of all child chunks
        children_size = (
            12 + 12 +                      # SIZE chunk
            12 + 4 + 4 * len(voxels) +     # XYZI chunk
            12 + 4 * 256                   # RGBA chunk
        )
        f.write(struct.pack('<I', children_size))  # Size of all child chunks
        
        # SIZE chunk
        f.write(b'SIZE')
        f.write(struct.pack('<I', 12))  # Size of SIZE chunk content
        f.write(struct.pack('<I', 0))   # No children
        f.write(struct.pack('<III', size_x, size_y, size_z))  # Model size
        
        # XYZI chunk
        f.write(b'XYZI')
        f.write(struct.pack('<I', 4 + 4 * len(voxels)))  # Size of XYZI chunk content
        f.write(struct.pack('<I', 0))   # No children
        f.write(struct.pack('<I', len(voxels)))  # Number of voxels
        
        # Write all voxels
        for x, y, z, i in voxels:
            f.write(struct.pack('<BBBB', x, y, z, i))
        
        # RGBA chunk
        f.write(b'RGBA')
        f.write(struct.pack('<I', 4 * 256))  # Size of RGBA chunk content
        f.write(struct.pack('<I', 0))   # No children
        
        # Write the palette
        for r, g, b, a in palette:
            f.write(struct.pack('<BBBB', r, g, b, a))

# Function to export voxel data as OBJ file
def export_voxels_to_obj(filename, voxels, palette, model_size):
    """
    Exports voxel data as OBJ file.
    
    Args:
        filename: Output filename
        voxels: List of (x, y, z, color_index) tuples
        palette: Color palette as list of (r, g, b, a) tuples
        model_size: Model size as (size_x, size_y, size_z) tuple
    """
    size_x, size_y, size_z = model_size
    
    # Create a 3D array to mark occupied voxels
    occupied = np.zeros((size_x, size_y, size_z), dtype=bool)
    colors = {}
    
    for x, y, z, i in voxels:
        if 0 <= x < size_x and 0 <= y < size_y and 0 <= z < size_z:
            occupied[x, y, z] = True
            colors[(x, y, z)] = i
    
    # Create OBJ and MTL files
    obj_filename = filename
    mtl_filename = os.path.splitext(filename)[0] + '.mtl'
    
    with open(obj_filename, 'w') as obj_file, open(mtl_filename, 'w') as mtl_file:
        # MTL reference in OBJ file
        obj_file.write(f"mtllib {os.path.basename(mtl_filename)}\n")
        
        # Write materials
        for i in range(1, 256):
            if i in [colors[pos] for pos in colors]:
                r, g, b, a = palette[i]
                if a > 0:  # Only visible colors
                    mtl_file.write(f"newmtl color_{i}\n")
                    mtl_file.write(f"Kd {r/255:.6f} {g/255:.6f} {b/255:.6f}\n")
                    mtl_file.write("Ka 0.000000 0.000000 0.000000\n")
                    mtl_file.write("Ks 0.000000 0.000000 0.000000\n")
                    mtl_file.write("d 1.000000\n")
                    mtl_file.write("illum 1\n\n")
        
        # Vertices and faces
        vertex_count = 0
        
        # Direction vectors for the 6 faces of a cube
        directions = [
            (1, 0, 0), (-1, 0, 0),  # X+ and X-
            (0, 1, 0), (0, -1, 0),  # Y+ and Y-
            (0, 0, 1), (0, 0, -1)   # Z+ and Z-
        ]
        
        # Vertices for each visible cube
        for x in range(size_x):
            for y in range(size_y):
                for z in range(size_z):
                    if not occupied[x, y, z]:
                        continue
                    
                    color_index = colors.get((x, y, z), 1)
                    
                    # Check each direction
                    for dx, dy, dz in directions:
                        nx, ny, nz = x + dx, y + dy, z + dz
                        
                        # If the neighbor is outside the model or empty, create a face
                        if nx < 0 or nx >= size_x or ny < 0 or ny >= size_y or nz < 0 or nz >= size_z or not occupied[nx, ny, nz]:
                            # Determine the 4 corners of the face
                            if dx == 1:  # X+
                                vertices = [
                                    (x+1, y, z), (x+1, y+1, z),
                                    (x+1, y+1, z+1), (x+1, y, z+1)
                                ]
                            elif dx == -1:  # X-
                                vertices = [
                                    (x, y+1, z), (x, y, z),
                                    (x, y, z+1), (x, y+1, z+1)
                                ]
                            elif dy == 1:  # Y+
                                vertices = [
                                    (x+1, y+1, z), (x, y+1, z),
                                    (x, y+1, z+1), (x+1, y+1, z+1)
                                ]
                            elif dy == -1:  # Y-
                                vertices = [
                                    (x, y, z), (x+1, y, z),
                                    (x+1, y, z+1), (x, y, z+1)
                                ]
                            elif dz == 1:  # Z+
                                vertices = [
                                    (x, y, z+1), (x+1, y, z+1),
                                    (x+1, y+1, z+1), (x, y+1, z+1)
                                ]
                            else:  # Z-
                                vertices = [
                                    (x+1, y, z), (x, y, z),
                                    (x, y+1, z), (x+1, y+1, z)
                                ]
                            
                            # Write the vertices
                            for vx, vy, vz in vertices:
                                obj_file.write(f"v {vx} {vz} {vy}\n")  # Swap Y and Z for Godot compatibility
                            
                            # Write the face with the corresponding material
                            obj_file.write(f"usemtl color_{color_index}\n")
                            obj_file.write(f"f {vertex_count+1} {vertex_count+2} {vertex_count+3} {vertex_count+4}\n")
                            vertex_count += 4

    print(f"OBJ and MTL saved as {obj_filename} and {mtl_filename}")

# Main program with user options
def main():
    # Input file and output directory
    input_vox = input("Path to input file (.vox): ") or "input.vox"
    output_dir = input("Path to output directory (default: output_chunks): ") or "output_chunks"
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse file
    try:
        model_size, voxels, palette = parse_vox_file(input_vox)
        orig_size_x, orig_size_y, orig_size_z = model_size
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # User options for splitting
    print("\n=== Splitting Options ===")
    print("1: Fixed chunk size for each dimension")
    print("2: Divide by a value")
    print("3: No splitting (format conversion only)")
    option = input("Choose an option (1-3): ") or "1"
    
    # Initialize variables for chunk sizes and splitting
    chunk_size_x = orig_size_x
    chunk_size_y = orig_size_y
    chunk_size_z = orig_size_z
    divide_x = True
    divide_y = True
    divide_z = True
    
    if option == "1":
        # Fixed chunk size
        print("\nEnter the chunk size for each dimension (0 for no splitting):")
        chunk_size_x_input = input(f"X chunk size (currently {orig_size_x}): ")
        chunk_size_y_input = input(f"Y chunk size (currently {orig_size_y}): ")
        chunk_size_z_input = input(f"Z chunk size (currently {orig_size_z}): ")
        
        if chunk_size_x_input and chunk_size_x_input != "0":
            chunk_size_x = int(chunk_size_x_input)
        else:
            divide_x = False
            
        if chunk_size_y_input and chunk_size_y_input != "0":
            chunk_size_y = int(chunk_size_y_input)
        else:
            divide_y = False
            
        if chunk_size_z_input and chunk_size_z_input != "0":
            chunk_size_z = int(chunk_size_z_input)
        else:
            divide_z = False
    
    elif option == "2":
        # Divide by a value
        print("\nEnter the divider for each dimension (0 or empty for no splitting):")
        divider_x = input(f"X divider (currently {orig_size_x}): ")
        divider_y = input(f"Y divider (currently {orig_size_y}): ")
        divider_z = input(f"Z divider (currently {orig_size_z}): ")
        
        if divider_x and divider_x != "0":
            chunk_size_x = orig_size_x // int(divider_x)
        else:
            divide_x = False
            
        if divider_y and divider_y != "0":
            chunk_size_y = orig_size_y // int(divider_y)
        else:
            divide_y = False
            
        if divider_z and divider_z != "0":
            chunk_size_z = orig_size_z // int(divider_z)
        else:
            divide_z = False
    
    elif option == "3":
        # No splitting
        divide_x = divide_y = divide_z = False
    
    # Choose output format
    print("\n=== Output Format ===")
    print("1: MagicaVoxel (.vox)")
    print("2: Wavefront OBJ (.obj)")
    print("3: Both formats")
    format_option = input("Choose a format (1-3): ") or "1"
    
    export_vox = format_option in ["1", "3"]
    export_obj = format_option in ["2", "3"]
    
    # If no splitting was chosen, export the entire model
    if not (divide_x or divide_y or divide_z):
        base_filename = os.path.splitext(os.path.basename(input_vox))[0]
        output_base = os.path.join(output_dir, base_filename)
        
        if export_vox:
            output_vox = output_base + ".vox"
            write_vox_file(output_vox, orig_size_x, orig_size_y, orig_size_z, voxels, palette)
            print(f"Voxel model saved as {output_vox}")
        
        if export_obj:
            output_obj = output_base + ".obj"
            export_voxels_to_obj(output_obj, voxels, palette, model_size)
            print(f"OBJ model saved as {output_obj}")
        
        return
    
    # Otherwise, split the model into chunks
    chunks = defaultdict(list)
    
    # Group voxels into chunks
    for x, y, z, i in voxels:
        # Determine which chunk this voxel belongs to
        chunk_indices = [0, 0, 0]
        
        if divide_x:
            chunk_indices[0] = x // chunk_size_x
        if divide_y:
            chunk_indices[1] = y // chunk_size_y
        if divide_z:
            chunk_indices[2] = z // chunk_size_z
        
        chunk_key = tuple(chunk_indices)
        
        # Calculate the relative coordinates within the chunk
        rel_x = x % chunk_size_x if divide_x else x
        rel_y = y % chunk_size_y if divide_y else y
        rel_z = z % chunk_size_z if divide_z else z
        
        chunks[chunk_key].append((rel_x, rel_y, rel_z, i))
    
    # Save each chunk group as a separate file
    for chunk_key, chunk_voxels in chunks.items():
        chunk_x, chunk_y, chunk_z = chunk_key
        
        # Filename based on chunk position
        if divide_x and divide_y and divide_z:
            filename_base = f"chunk_x{chunk_x*chunk_size_x}_y{chunk_y*chunk_size_y}_z{chunk_z*chunk_size_z}"
        elif divide_x and divide_y:
            filename_base = f"chunk_x{chunk_x*chunk_size_x}_y{chunk_y*chunk_size_y}"
        elif divide_x and divide_z:
            filename_base = f"chunk_x{chunk_x*chunk_size_x}_z{chunk_z*chunk_size_z}"
        elif divide_y and divide_z:
            filename_base = f"chunk_y{chunk_y*chunk_size_y}_z{chunk_z*chunk_size_z}"
        elif divide_x:
            filename_base = f"chunk_x{chunk_x*chunk_size_x}"
        elif divide_y:
            filename_base = f"chunk_y{chunk_y*chunk_size_y}"
        elif divide_z:
            filename_base = f"chunk_z{chunk_z*chunk_size_z}"
        
        # Size of the current chunk
        output_size_x = chunk_size_x if divide_x else orig_size_x
        output_size_y = chunk_size_y if divide_y else orig_size_y
        output_size_z = chunk_size_z if divide_z else orig_size_z
        
        # Save VOX file
        if export_vox:
            vox_filename = os.path.join(output_dir, filename_base + ".vox")
            write_vox_file(vox_filename, output_size_x, output_size_y, output_size_z, chunk_voxels, palette)
            print(f"Saved: {vox_filename} with {len(chunk_voxels)} voxels, size: {output_size_x}x{output_size_y}x{output_size_z}")
        
        # Save OBJ file
        if export_obj:
            obj_filename = os.path.join(output_dir, filename_base + ".obj")
            export_voxels_to_obj(obj_filename, chunk_voxels, palette, (output_size_x, output_size_y, output_size_z))
    
    print("All chunks successfully saved!")

if __name__ == "__main__":
    main()
