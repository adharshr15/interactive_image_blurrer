import tkinter as tk
import numpy as np
import cv2
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw

current_file, current_image = None, None
polygon_points = []

# function to display image as a canvas in the editor
def display_image(image): 
    image_tk = ImageTk.PhotoImage(image)
    image_canvas.image = image_tk
    image_canvas.create_image(0, 0, anchor='nw', image=image_tk)

# function to open and display an image in the editor
def open_file():
    file = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")]
    )
    
    if file:
        try:
            image = Image.open(file)
            
            # resize image to fit frame
            og_width, og_height = image.size
            width_to_height = og_height / og_width
            
            max_width = 700
            
            new_width = max_width
            new_height = int(new_width * width_to_height)
            
            image = image.resize((new_width, new_height))
            
            image_tk = ImageTk.PhotoImage(image)
            
            global current_file
            current_file = file
            
            global current_image
            current_image = image
            
            # display image in canvas
            display_image(image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")
    else: 
        messagebox.showerror("No Image Selected", "No Image Selected")
        
# function to save file 
def save_file():
    global current_file, current_image
    if current_file and current_image: 
        with open(current_file, "w") as file:
            try:
                current_image.save(current_file)
                messagebox.showinfo("Success", "Image saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")

# function to save file as   
def save_file_as():
    global current_file, current_image
    file = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("WebP", "*.webp")]
    )
    if file and current_image:
        try:
            current_image.save(file)
            current_file = file
            messagebox.showinfo("Success", "Image saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")
        

def show_file_menu(event):
    file_menu.post(event.x_root, event.y_root)
    
# function to allow add pixel points that users select to selection
def on_canvas_click(event):
    x, y = event.x, event.y
    polygon_points.append((x, y))
    image_canvas.create_oval(x-2, y-2, x+2, y+2, fill='red')
    
    # change button state
    if len(polygon_points) >= 3:
        blur_btn.config(state='normal')
        remove_btn.config(state='normal')
        
    # create polygon on canvas from user selection
    if len(polygon_points) > 1:
        image_canvas.create_line(polygon_points[-1], polygon_points[-2], fill='red')

# function to apply blur to user selection
def apply_polygon_blur():
    global current_image, polygon_points
    
    if not current_image or len(polygon_points) < 3:
        messagebox.showerror("Error", "You need to select at least 3 points.")
        return
    
    # create original and blurred images
    original = current_image.copy()
    blurred = current_image.filter(ImageFilter.GaussianBlur(radius=10))
    
    # create mask image to subtract blurred part from original
    mask = Image.new('L', current_image.size, 0)
    ImageDraw.Draw(mask).polygon(polygon_points, fill=255)
    
    # composite the two images using the mask
    result = Image.composite(blurred, original, mask)
    
    # update and display
    current_image = result
    polygon_points = []
    image_canvas.delete("all")
    display_image(current_image)
    
    # change button state
    blur_btn.config(state='disabled')
    remove_btn.config(state='disabled')
    
# function to remove from user selection using content aware fill
def apply_polygon_remove():
    global current_image, polygon_points
    
    if not current_image or len(polygon_points) < 3:
        messagebox.showerror("Error", "You need to select at least 3 points.")
        return
    
    # convert PIL image to cv image
    cv_image = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
    
    # create mask
    mask = np.zeros((current_image.height, current_image.width), dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(polygon_points, dtype=np.int32)], 255)
    
    # perform removal
    inpainted = cv2.inpaint(cv_image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    # convert cv back to PIL image
    result = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
    
    # update and display
    current_image = result
    polygon_points = []
    image_canvas.delete('all')
    display_image(current_image)
    
    # change button state
    remove_btn.config(state='disabled')
    blur_btn.config(state='disabled')


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

blur_btn = tk.Button(root, text='Blur', state='disabled', bg='light green', command=apply_polygon_blur)
blur_btn.pack(pady=10)

remove_btn = tk.Button(root, text='Remove', state='disabled', bg='light blue', command=apply_polygon_remove)
remove_btn.pack(pady=10)

# image editor

image_frame = tk.Frame(root, width=700, height=500)
image_frame.pack(pady=20)
image_frame.pack_propagate(False)

image_canvas = tk.Canvas(image_frame, width=700, height=500, bg="gray")
image_canvas.place(relx=0.5, rely=0.5, anchor="center")

image_canvas.bind("<Button-1>", on_canvas_click)



root.mainloop()