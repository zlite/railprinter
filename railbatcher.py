import tkinter as tk
from tkinter import filedialog, messagebox

# Define the header and footer as multi-line string constants
GCODE_HEADER = """;FLAVOR:Marlin
;TIME:6666
;Filament used: 0m
;Layer height: 0.2
;MINX:2.14748e+06
;MINY:2.14748e+06
;MINZ:2.14748e+06
;MAXX:-2.14748e+06
;MAXY:-2.14748e+06
;MAXZ:-2.14748e+06

;Generated with Cura_SteamEngine 4.6.2
M104 S205
M105
M109 S205
M82 ;absolute extrusion mode
;---------- start gcode ----------
M2000 ;custom: set to line-mode
M888 P3 ;custom: current is p3d
;move header up 10mm
G1 Z10 F1000
G92 E0
G1 F200 E3
G92 E0
;---------------------------------
G92 E0
G92 E0
G1 F2400 E-7
;LAYER_COUNT:15
;LAYER:0
M107
M204 S100

G0 F12000 X99.28 Y332.613 Z0.2
;TYPE:WALL-INNER
G1 F3600 E0
"""

GCODE_FOOTER = """;TIME_ELAPSED:4717.883399
G1 F2400 E901.95044
M204 S200
M107
;----------- end gcode -----------
;move header up 10mm
G91
G0 Z10
G90
M104 S0
;retract the filament
G92 E1
G1 E-1 F300
;---------------------------------
M82 ;absolute extrusion mode
M104 S0
;End of Gcode
"""


def process_gcode_file(input_path, output_path):
    """
    Reads a G-code file, processes each layer, and writes to an output file,
    wrapping the content with a specific header and footer.

    A "layer" is defined as the set of G-code commands starting with a Z-axis 
    move (G0 or G1) up to the line just before the next Z-axis move.

    Args:
        input_path (str): The path to the source G-code file.
        output_path (str): The path to save the modified G-code file.
    """
    try:
        with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
            # First, write the specified header to the new file.
            outfile.write(GCODE_HEADER + "\n\n")

            layer_buffer = []
            lines = infile.readlines()

            for line in lines:
                # Clean the line to ignore comments and whitespace for accurate checking
                clean_line = line.split(';')[0].strip()

                # Check if the line represents a Z-axis move, which marks a new layer
                is_z_move = ('G0 ' in clean_line or 'G1 ' in clean_line) and ' Z' in clean_line

                if is_z_move:
                    # If we have a buffer, it means we've collected a full layer.
                    # Process and write it to the file before starting the new one.
                    if layer_buffer:
                        # Write the original layer content first
                        original_layer_content = "".join(layer_buffer)
                        outfile.write(original_layer_content)

                        # Now, write the 4 duplicates with their respective M118 and G92 commands
                        for i in range(1, 5):
                            distance = i * 200
                            outfile.write(f"M118 P0 Zone {distance}\n")
                            outfile.write("G92 E0\n")
                            outfile.write(original_layer_content)
                        
                        # Add the final "Zone 0" command at the end (without G92 E0)
                        outfile.write("M118 P0 Zone 0\n")

                    # Clear the buffer and start the new layer with the current Z-move line
                    layer_buffer = [line]
                else:
                    # If it's not a Z-move, just add the line to the current layer's buffer
                    layer_buffer.append(line)

            # After the loop, the final layer (and any end-script G-code) will be in the buffer.
            # We must process this final chunk.
            if layer_buffer:
                original_layer_content = "".join(layer_buffer)
                outfile.write(original_layer_content)

                # Write the 4 duplicates with their respective M118 and G92 commands
                for i in range(1, 5):
                    distance = i * 200
                    outfile.write(f"M118 P0 Zone {distance}\n")
                    outfile.write("G92 E0\n")
                    outfile.write(original_layer_content)
                
                # Add the final "Zone 0" command at the end (without G92 E0)
                outfile.write("M118 P0 Zone 0\n")
            
            # Finally, write the specified footer to the end of the file.
            outfile.write("\n" + GCODE_FOOTER)

    except Exception as e:
        messagebox.showerror("Processing Error", f"An error occurred: {e}")
        return False
    return True

class GCodeProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("G-code Layer Duplicator")
        self.root.geometry("500x250") # Set a default size for the window
        
        self.input_file_path = None

        # --- UI Elements ---

        # Main frame for content
        main_frame = tk.Frame(root, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input file selection
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_label = tk.Label(input_frame, text="Input G-code File:")
        input_label.pack(side=tk.LEFT, anchor='w')

        self.file_path_label = tk.Label(input_frame, text="No file selected", fg="grey", relief=tk.SUNKEN, padx=5)
        self.file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        browse_button = tk.Button(input_frame, text="Browse...", command=self.select_file)
        browse_button.pack(side=tk.RIGHT)
        
        # Process button
        self.process_button = tk.Button(main_frame, text="Process and Save As...", command=self.process_and_save, state=tk.DISABLED)
        self.process_button.pack(pady=20, ipady=5, fill=tk.X)

        # Status bar
        self.status_label = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def select_file(self):
        """Opens a file dialog to select a .gcode file."""
        path = filedialog.askopenfilename(
            title="Select a G-code file",
            filetypes=[("G-code files", "*.gcode"), ("All files", "*.*")]
        )
        if path:
            self.input_file_path = path
            # Display only the filename, not the full path
            filename = path.split('/')[-1]
            self.file_path_label.config(text=filename, fg="black")
            self.status_label.config(text=f"Loaded: {filename}")
            self.process_button.config(state=tk.NORMAL) # Enable the process button
        else:
            self.status_label.config(text="File selection cancelled.")

    def process_and_save(self):
        """Handles the logic for processing the file and saving the output."""
        if not self.input_file_path:
            messagebox.showwarning("No File", "Please select an input file first.")
            return

        # Suggest a default name for the output file
        original_filename = self.input_file_path.split('/')[-1]
        if '.' in original_filename:
            base, ext = original_filename.rsplit('.', 1)
            suggested_name = f"{base}_ZONED.{ext}"
        else:
            suggested_name = f"{original_filename}_ZONED"

        output_path = filedialog.asksaveasfilename(
            title="Save Processed G-code As...",
            initialfile=suggested_name,
            defaultextension=".gcode",
            filetypes=[("G-code files", "*.gcode"), ("All files", "*.*")]
        )

        if not output_path:
            self.status_label.config(text="Save operation cancelled.")
            return

        self.status_label.config(text="Processing... please wait.")
        self.root.update_idletasks() # Update the UI to show the message

        success = process_gcode_file(self.input_file_path, output_path)

        if success:
            self.status_label.config(text="Processing complete!")
            messagebox.showinfo("Success", f"File successfully processed and saved to:\n{output_path}")
        else:
            self.status_label.config(text="An error occurred during processing.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GCodeProcessorApp(root)
    root.mainloop()
