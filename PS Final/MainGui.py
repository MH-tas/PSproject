import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import math
import LZW_basic
import LZW_Grayscale  # Assuming LZW_Grayscale.py contains necessary functions for compressing and decompressing images


def select_file():
    global img_label, decompressed_text, selected_file_ext, selected_file_path, original_data  # Keep track of original data
    
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("BMP Image Files", "*.bmp")])
    
    if not file_path:
        return
    
    selected_file_path = file_path  # Save the selected file path here
    original_file_label.config(text=file_path)
    selected_file_ext = os.path.splitext(file_path)[1].lower()
    
    # Hide decompressed_text when a new file is selected
    decompressed_text.pack_forget()  # This will hide the decompressed text area
    
    if selected_file_ext == ".txt":
        with open(file_path, "rb") as f:
            original_data = f.read()  # Save the original data to calculate stats later
            original_text.pack()
            img_label.pack_forget()
            original_text.delete("1.0", tk.END)
            original_text.insert(tk.END, original_data[:500])  # Display first 500 bytes for preview
        # Reset statistics to "N/A" initially
        reset_statistics()
    
    elif selected_file_ext == ".bmp":
        image = Image.open(file_path)
        image.thumbnail((300, 300))
        img = ImageTk.PhotoImage(image)
        img_label.config(image=img)
        img_label.image = img
        img_label.pack()
        original_text.pack_forget()

    update_methods(selected_file_ext)

def reset_statistics():
    """Reset all statistics to N/A before processing."""
    entropy_label.config(text="Entropy: N/A")
    avg_code_length_label.config(text="Average Code Length: N/A")
    compression_ratio_label.config(text="Compression Ratio: N/A")
    input_size_label.config(text="Input Image Size: N/A")
    compressed_size_label.config(text="Compressed Image Size: N/A")
    diff_label.config(text="Difference: N/A")

def calculate_entropy(data):
    """Calculate entropy of the given data."""
    if len(data) == 0:
        return 0
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    entropy = 0
    for count in freq.values():
        prob = count / len(data)
        entropy -= prob * math.log2(prob)
    return entropy

def calculate_average_code_length(data):
    """Calculate the average code length."""
    return len(data) / len(set(data)) if len(set(data)) > 0 else 0

def update_methods(file_ext):
    methods_menu.delete(0, tk.END)  # Clear existing methods
    
    global selected_method
    selected_method = None  # Reset selection
    selected_method_label.config(text="Selected Method: None")

    # All levels (1 to 5) should be available for both .txt and .bmp
    available_methods = [
        "Level 1: Compression", "Level 1: Decompression",
        "Level 2: Compression", "Level 2: Decompression",
        "Level 3: Compression", "Level 3: Decompression",
        "Level 4: Compression", "Level 4: Decompression",
        "Level 5: Compression", "Level 5: Decompression"
    ]
    
    for method in available_methods:
        methods_menu.add_command(label=method, command=lambda m=method: select_method(m))  # Prevent error with lambda

def select_method(method):
    global selected_method
    selected_method = method
    selected_method_label.config(text=f"Selected Method: {method}")

def run_action():
    global selected_file_path, original_data  # Keep track of the original data
    
    # Ensure a method has been selected
    if not selected_method:
        messagebox.showerror("Error", "Please select a method before running.")
        return
    
    # Ensure a file has been selected
    if not selected_file_path:
        messagebox.showerror("Error", "Please select a file first.")
        return
    
    # Initialize compressed_data to None
    compressed_data = None
    
    # Perform compression or decompression based on the selected method
    if "Level 1: Compression" in selected_method:
        with open(selected_file_path, "r", encoding="utf-8") as f:
            data = f.read().strip()  # Read the content as text for Level 1
        compressed_data = LZW_basic.compress(data)  # Call the compression function for Level 1
        output_text = " ".join(map(str, compressed_data))  # Convert the list to a string

    elif "Level 1: Decompression" in selected_method:
        with open(selected_file_path, "r", encoding="utf-8") as f:
            data = f.read().strip()  # Read the content as text for Level 1
        try:
            compressed_data = list(map(int, data.split()))  # Convert string to integers
            output_text = LZW_basic.decompress(compressed_data)  # Call the decompression function for Level 1
        except ValueError:
            messagebox.showerror("Error", "Invalid compressed data format.")
            return

    elif "Level 2: Compression" in selected_method:
        # Level 2 Compression using LZW for grayscale images
        try:
            compressed_data = LZW_Grayscale.compress(selected_file_path)
            output_text = compressed_data
        except Exception as e:
            messagebox.showerror("Error", f"Error during compression: {str(e)}")
            return

    elif "Level 2: Decompression" in selected_method:
        try:
            decompressed_image = LZW_Grayscale.decompress(selected_file_path)
    
            # Hide decompressed text area when decompression occurs
            decompressed_text.pack_forget()  # This hides the decompressed text area

            # Create a frame inside the right_frame to hold the image
            image_frame = tk.Frame(right_frame, bg="#87CEEB")
            image_frame.pack(pady=10)  # Add some padding between "Processed File" label and image

            # Display the image in the new frame (under "Processed File")
            decompressed_image.thumbnail((300, 300))  # Resize to fit in the window
            img = ImageTk.PhotoImage(decompressed_image)

            img_label.config(image=img)
            img_label.image = img  # Keep a reference to the image to prevent it from being garbage collected
            img_label.pack(side=tk.RIGHT)  # Show the image in the 'Processed File' section

            # Now, show a message in the decompressed_text area instead of the image
            output_text = "Decompression Complete. Image shown below."

            # Show the decompressed output in the text area (not the image)
            decompressed_text.pack()  # Make sure the text box is visible after processing
            decompressed_text.delete("1.0", tk.END)  # Clear previous content
            decompressed_text.insert(tk.END, output_text)  # Insert the result message

        except Exception as e:
            messagebox.showerror("Error", f"Error during decompression: {str(e)}")



    else:
        messagebox.showerror("Error", "Unknown method selected.")
        return

    # Show the decompressed output in the text area
    decompressed_text.pack()  # Make sure the text box is visible after processing
    decompressed_text.delete("1.0", tk.END)  # Clear previous content
    decompressed_text.insert(tk.END, output_text)  # Insert the result message

    # Only calculate statistics if compressed_data was properly assigned
    if compressed_data is not None:
        calculate_and_display_statistics(original_data, compressed_data)

    messagebox.showinfo("Run", "Processing complete!")

def calculate_and_display_statistics(original_data, compressed_data):
    """Calculate and display entropy, compression ratio, etc."""
    # Calculate statistics for original and processed data
    original_entropy = calculate_entropy(original_data)
    compressed_entropy = calculate_entropy(compressed_data)
    
    original_size = len(original_data)
    compressed_size = len(compressed_data)

    compression_ratio = compressed_size / original_size if original_size > 0 else 0
    diff = original_size - compressed_size
    
    # Display the calculated statistics
    entropy_label.config(text=f"Entropy (Original): {original_entropy:.4f} | (Compressed): {compressed_entropy:.4f}")
    avg_code_length_label.config(text=f"Average Code Length: {calculate_average_code_length(original_data):.4f}")
    compression_ratio_label.config(text=f"Compression Ratio: {compression_ratio:.4f}")
    input_size_label.config(text=f"Input File Size: {original_size} bytes")
    compressed_size_label.config(text=f"Compressed File Size: {compressed_size} bytes")
    diff_label.config(text=f"Size Difference: {diff} bytes")

def save_file():
    """Function to save the file with a given name in the specified directory."""
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("BMP Image Files", "*.bmp")], initialdir=r"C:\Users\90533\Desktop\PS Final")
    
    if save_path:
        # Get the output data from the decompressed_text (which contains the processed data)
        output_data = decompressed_text.get("1.0", tk.END).strip()  # Get the content from the decompressed text area
        
        if output_data:  # Ensure there is data to save
            # Save the processed data to the file
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(output_data)  # Write the decompressed/compressed data

            messagebox.showinfo("Saved", f"File saved as {save_path}")
        else:
            messagebox.showerror("Error", "No data to save. Please run a method first.")

root = tk.Tk()
root.title("File Compressor & Decompressor")
root.geometry("1000x600")
root.configure(bg="#87CEEB")

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open File", command=select_file)
menu_bar.add_cascade(label="File", menu=file_menu)

methods_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Methods", menu=methods_menu)
root.config(menu=menu_bar)

frame = tk.Frame(root, bg="#87CEEB")
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

left_frame = tk.Frame(frame, bg="#87CEEB")
left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(frame, bg="#87CEEB")
right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

original_file_label = tk.Label(left_frame, text="Original File:", bg="#87CEEB")
original_file_label.pack()

original_text = tk.Text(left_frame, height=15, width=40)
original_text.pack()

img_label = tk.Label(left_frame, bg="#87CEEB")
img_label.pack()

decompressed_file_label = tk.Label(right_frame, text="Processed File:", bg="#87CEEB")
decompressed_file_label.pack()

decompressed_text = tk.Text(right_frame, height=15, width=40)

selected_method_label = tk.Label(root, text="Selected Method: None", bg="#87CEEB")
selected_method_label.pack()

run_button = tk.Button(root, text="Run", bg="green", fg="white", font=("Arial", 16, "bold"), width=10, height=2, command=run_action)
run_button.place(relx=1.0, rely=1.0, anchor=tk.SE, x=-20, y=-20)

# New labels for the statistics at the bottom
entropy_label = tk.Label(root, text="Entropy: N/A", bg="#87CEEB")
entropy_label.pack()

avg_code_length_label = tk.Label(root, text="Average Code Length: N/A", bg="#87CEEB")
avg_code_length_label.pack()

compression_ratio_label = tk.Label(root, text="Compression Ratio: N/A", bg="#87CEEB")
compression_ratio_label.pack()

input_size_label = tk.Label(root, text="Input Image Size: N/A", bg="#87CEEB")
input_size_label.pack()

compressed_size_label = tk.Label(root, text="Compressed Image Size: N/A", bg="#87CEEB")
compressed_size_label.pack()

diff_label = tk.Label(root, text="Difference: N/A", bg="#87CEEB")
diff_label.pack()

# Save button with yellow color and functionality
save_button = tk.Button(root, text="Save", bg="yellow", fg="black", font=("Arial", 16, "bold"), width=10, height=2, command=save_file)
save_button.place(relx=1.0, rely=1.0, anchor=tk.SE, x=-180, y=-20)

root.mainloop()
