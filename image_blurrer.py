import tkinter as tk
import numpy as np
import cv2
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageFilter, ImageDraw
from gaussian_blur import apply_gaussian_blur

current_file, current_image = None, None
last_image = []
polygon_points = []
blur_radius, remove_radius = 10, 3
image_height, image_width = None, None

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
            
            # max width and height
            max_width = 700
            max_height = 500

            orig_width, orig_height = image.size
            ratio = min(max_width / orig_width, max_height / orig_height)
            new_width = int(orig_width * ratio)
            new_height = int(orig_height * ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # resize with aspect ratio preserved
            image = image.resize((new_width, new_height))
            
            global image_height, image_width
            image_width, image_height = image.size
            
            global current_file, current_image
            current_file = file
            current_image = image
            
            # reset last image array
            last_image = []
            
            # display image in canvas
            display_image(image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")
    else: 
        messagebox.showerror("No Image Selected", "No Image Selected")
        
    file_btn.config(relief=tk.RAISED)
        
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
    
    last_image = []
    current_image, current_file = None, None
    
    file_btn.config(relief=tk.RAISED)

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
            
    file_btn.config(relief=tk.RAISED)
        

def show_file_menu(event):
    file_menu.post(event.x_root, event.y_root)
    
def set_blur_radius():
    global blur_radius
    value = simpledialog.askfloat('Blur Radius', "Enter blur radius (e.g., 5.0):", minvalue=0.0)
    if value is not None:
        blur_radius = value
    settings_btn.config(relief=tk.RAISED)
    
def set_remove_radius():
    global remove_radius
    value = simpledialog.askfloat('Remove Radius', "Enter remove radius (e.g., 5.0)", minvalue=0.0)
    if value is not None:
        remove_radius = value
    settings_btn.config(relief=tk.RAISED)

def show_settings_menu(event):
    settings_menu.post(event.x_root, event.y_root)
    
# function to allow add pixel points that users select to selection
def on_canvas_click(event):
    x, y = event.x, event.y
    polygon_points.append((x, y))
    image_canvas.create_oval(x-2, y-2, x+2, y+2, fill='red')
    
    # change button state
    if len(polygon_points) > 0:
        undo_btn.config(state='normal')
    
    if len(polygon_points) >= 3:
        blur_btn.config(state='normal')
        remove_btn.config(state='normal')
        
    # create polygon on canvas from user selection
    if len(polygon_points) > 1:
        image_canvas.create_line(polygon_points[-1], polygon_points[-2], fill='red')

# function to apply blur to user selection
def apply_polygon_blur():
    global current_image, polygon_points, blur_radius
    
    if not current_image or len(polygon_points) < 3:
        messagebox.showerror("Error", "You need to select at least 3 points.")
        return
    
    # create original and blurred images
    original = current_image.copy()
    
    blurred = apply_gaussian_blur(current_image, blur_radius)
    
    # create mask image to subtract blurred part from original
    mask = Image.new('L', current_image.size, 0)
    ImageDraw.Draw(mask).polygon(polygon_points, fill=255)
    
    # composite the two images using the mask
    result = Image.composite(blurred, original, mask)
    
    # update last image 
    last_image.append(current_image)
    
    # update current image and display
    current_image = result
    polygon_points = []
    image_canvas.delete("all")
    display_image(current_image)
    
    # change button state
    blur_btn.config(state='disabled')
    remove_btn.config(state='disabled')
    if not last_image: undo_btn.config(state='disabled')
    
# function to remove from user selection using content aware fill
def apply_polygon_remove():
    global current_image, polygon_points, remove_radius
    
    if not current_image or len(polygon_points) < 3:
        messagebox.showerror("Error", "You need to select at least 3 points.")
        return
    
    # convert PIL image to cv image
    cv_image = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
    
    # create mask
    mask = np.zeros((current_image.height, current_image.width), dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(polygon_points, dtype=np.int32)], 255)
    
    # perform removal
    inpainted = cv2.inpaint(cv_image, mask, inpaintRadius=remove_radius, flags=cv2.INPAINT_TELEA)
    
    # convert cv back to PIL image
    result = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
    
    # update last image
    last_image.append(current_image)
    
    # update current image and display
    current_image = result
    polygon_points = []
    image_canvas.delete('all')
    display_image(current_image)
    
    # change button state
    remove_btn.config(state='disabled')
    blur_btn.config(state='disabled')
    if not last_image: undo_btn.config(state="disabled")

# function to undo last selection or last blur/remove
def undo():
    global current_image, polygon_points
    
    if not current_image:
        messagebox.showerror("Error", "No Image Selected")
        return
    
    # selection
    if len(polygon_points) > 0:
        polygon_points = []
        image_canvas.delete("all")
        display_image(current_image)
        
    # image
    elif last_image:
        current_image = last_image.pop()
        display_image(current_image)
        
    # change button state
    if not last_image:
        undo_btn.config(state='disabled')
    
        
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

settings_btn = tk.Button(menu_bar, text='Settings')
settings_btn.pack(side='left', padx=5, pady=5)

settings_menu = tk.Menu(root, tearoff=0)
settings_menu.add_command(label='Blur Radius', command=set_blur_radius)
settings_menu.add_command(label='Remove Radius', command=set_remove_radius)

file_btn.bind("<Button-1>", show_file_menu)
settings_btn.bind("<Button-1>", show_settings_menu)

# buttons

blur_btn = tk.Button(menu_bar, text='Blur', state='disabled', bg='light blue', command=apply_polygon_blur)
blur_btn.pack(side='left', padx=5, pady=5)

remove_btn = tk.Button(menu_bar, text='Remove', state='disabled', bg='light green', command=apply_polygon_remove)
remove_btn.pack(side='left', padx=5, pady=5)

undo_btn = tk.Button(menu_bar, text='Undo', state='disabled', bg='red', command=undo)
undo_btn.pack(side='left', padx=5, pady=5)


# image editor

image_frame = tk.Frame(root, width=700, height=500)
image_frame.pack(pady=20)
image_frame.pack_propagate(False)

image_canvas = tk.Canvas(image_frame, width=700, height=500, bg="gray")
image_canvas.place(relx=0.5, rely=0.5, anchor="center")

image_canvas.bind("<Button-1>", on_canvas_click)


root.mainloop()