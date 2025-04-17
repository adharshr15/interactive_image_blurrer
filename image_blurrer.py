import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

current_file = None

def open_file():
    file = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")]
    )
    
    if file:
        try:
            image = Image.open(file)
            
            og_width, og_height = image.size
            width_to_height = og_height / og_width
            
            max_width = 700
            
            new_width = max_width
            new_height = int(new_width * width_to_height)
            
            image = image.resize((new_width, new_height))
            
            image_tk = ImageTk.PhotoImage(image)
            
            image_label.config(image=image_tk)
            image_label.image = image_tk
            
            global current_file
            current_file = file
        except:
            return
    
def save_file():
    return
    
def save_file_as():
    return

def show_file_menu(event):
    file_menu.post(event.x_root, event.y_root)

root = tk.Tk()
root.title("Image Blurrer")
root.geometry("800x600")

# menu bar

menu_bar = tk.Frame(root)
menu_bar.pack(side="top", fill="x")

file_btn = tk.Button(menu_bar, text='File')
file_btn.pack(side="left", padx=5, pady=5)

file_menu = tk.Menu(root, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_file_as)

file_btn.bind("<Button-1>", show_file_menu)

# image editor

image_frame = tk.Frame(root, width=700, height=500)
image_frame.pack(pady=20)
image_frame.pack_propagate(False)

image_label = tk.Label(image_frame)
image_label.place(relx=0.5, rely=0.5, anchor="center")


root.mainloop()