import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os


def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_msg = "This application was created by Erol Can and Memo in September 2023."
    tk.Label(about_window, text=about_msg, padx=10, pady=10).pack()
    tk.Button(about_window, text="Close", command=about_window.destroy).pack(pady=10)
    about_window.resizable(False, False)
    

def image_to_ascii(image_path, width, aspect_ratio):
    # Open the image
    image = Image.open(image_path)
    
    # Define the ASCII characters
    ASCII_CHARS = "@%#*+=-:. "
    
    # Resize the image
    height = image.size[1]
    new_height = int(aspect_ratio * width)
    
    # Failsafe for large requests
    if new_height * width > 300000:  # for instance, this checks if total number of pixels exceeds 300k
        messagebox.showerror("Error", "Requested size is too large. Please reduce the resolution or aspect ratio.")
        return ""
    
    resized_image = image.resize((width, new_height))
    
    # Convert the image to grayscale
    grayscale_image = resized_image.convert("L")
    
    # Convert pixels to ASCII
    pixels = grayscale_image.getdata()
    ascii_str = ""
    for pixel_value in pixels:
        index = pixel_value // 25
        index = min(index, len(ASCII_CHARS) - 1)  # Failsafe to ensure index doesn't exceed the length
        ascii_str += ASCII_CHARS[index]
    img_width = grayscale_image.width
    ascii_str_len = len(ascii_str)
    ascii_img = ""
    for i in range(0, ascii_str_len, img_width):
        ascii_img += ascii_str[i:i+img_width] + "\n"
    
    return ascii_img

def load_image():
    global file_path
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    # Display image
    img = Image.open(file_path)
    img.thumbnail((100, 100))
    img = ImageTk.PhotoImage(img)
    img_label.config(image=img)
    img_label.image = img

    # Display image details with name limited to 30 characters
    img_name = os.path.basename(file_path)
    if len(img_name) > 20:
        img_name = img_name[:17] + '...'
    img_size = os.path.getsize(file_path) / 1024  # KB
    if img_size < 1024:
        size_str = f"{img_size:.2f} KB"
    else:
        size_str = f"{img_size / 1024:.2f} MB"
    width, height = Image.open(file_path).size
    aspect = height / width
    details_label.config(text=f"Name: {img_name}\nSize: {size_str}\nResolution: {width}x{height}\nAspect Ratio: {aspect:.2f}")
    
    # Set the optimal aspect ratio on the slider
    optimal_value = calculate_optimal_slider_value(aspect)
    aspect_ratio_slider.set(optimal_value)
    
def convert_image():
    if not file_path:
        return
    
    resolution = resolution_slider.get()
    aspect_ratio = aspect_ratio_slider.get() / 100  # Dividing by 100 to get the actual aspect ratio
    
    ascii_art = image_to_ascii(file_path, resolution, aspect_ratio)
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, ascii_art)

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(text_widget.get("1.0", tk.END))
    
def calculate_optimal_slider_value(aspect_ratio):
    # Given points for linear interpolation
    x1, y1 = 0.67, 30
    x2, y2 = 1.51, 70

    # Calculate the optimal slider value based on the aspect ratio using linear interpolation
    slider_value = y1 + ((aspect_ratio - x1) * (y2 - y1)) / (x2 - x1)
    
    # Ensure that the slider value is within bounds
    return max(10, min(200, int(slider_value)))

# Create the main window
root = tk.Tk()
root.title("Image to ASCII Converter")

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Import Image", command=load_image)
file_menu.add_command(label="Close", command=root.destroy)

about_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="About", menu=about_menu)
about_menu.add_command(label="About", command=show_about)

# Import image button
load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.place(x=20, y=15)

# Image and details labels
img_label = tk.Label(root)
img_label.place(x=20, y=50)
details_label = tk.Label(root, anchor=tk.W, justify=tk.LEFT)
details_label.place(x=120, y=50)

# Sliders for aspect ratio and resolution
tk.Label(root, text="Resolution:").place(x=300, y=20)
resolution_slider = tk.Scale(root, from_=30, to=300, orient=tk.HORIZONTAL)
resolution_slider.set(200)
resolution_slider.place(x=414, y=20, width=200, height=60)

tk.Label(root, text="Aspect Ratio (x0.01):").place(x=300, y=65)
aspect_ratio_slider = tk.Scale(root, from_=10, to=100, orient=tk.HORIZONTAL)
aspect_ratio_slider.set(30)
aspect_ratio_slider.place(x=414, y=65, width=200, height=60)

# Convert button
convert_button = tk.Button(root, text="Convert", command=convert_image)
convert_button.place(x=240, y=150, width=120, height=30)

# Text widget for ASCII art and clipboard button
text_widget = tk.Text(root, wrap=tk.WORD, font=("Courier", 3))
text_widget.place(x=10, y=190, width=604, height=300)


clipboard_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
clipboard_button.place(x=240, y=500, width=120, height=30)

file_path = None


root.geometry('624x540')
root.resizable(False, False)  # Disable window resizing
root.mainloop()

