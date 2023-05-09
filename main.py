import os
# Install the requirements for this program if they aren't already installed.
# TODO uncomment the following line when done writing the program.
# os.system("pip3 install -r requirements.txt")

import tkinter
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from screeninfo import get_monitors

# ---------------- Global Variables ---------------- #

DEFAULT_IMAGE_PATH = "images/default-1-pexels-andy-vu-3244513.jpg"
DEFAULT_WATERMARK_PATH = "watermarks/default-watermark-1.png"

image_displayed = None
image_file = Image.open(DEFAULT_IMAGE_PATH)
watermark_file = Image.open(DEFAULT_WATERMARK_PATH)
watermark_scale = 0
watermark_opacity = 0

watermark_x = 0
watermark_y = 0

# 'watermarked_image' will be the working file, with 'image_file' being the original
watermarked_image = image_file
watermarked_image.paste(watermark_file)


# ---------------- Program Logic ---------------- #

def set_image_canvas_dimensions(picture: ImageTk.PhotoImage) -> list[int, int]:
    monitors_info = []

    # TODO Fix Proper Scaling of Input Images

    # Grab the width and height of any monitors on a computer
    for m in get_monitors():
        monitors_info.append([int(m.width), int(m.height)])

    # Look at the information on the smaller monitor
    monitor_info = sorted(monitors_info)[0]

    if monitor_info[0] > monitor_info[1]:
        if picture.width() > monitor_info[0]:
            monitor_info[0] = int(monitor_info[0] * monitor_info[0] / picture.width())
            monitor_info[1] = int(monitor_info[1] * monitor_info[0] / picture.height())
    else:
        if picture.height() > monitor_info[1]:
            monitor_info[0] = int(monitor_info[0] * monitor_info[1] / picture.width())
            monitor_info[1] = int(monitor_info[0] * monitor_info[1] / picture.width())
    return monitor_info


def update_screen(image_canvas: Canvas):
    global watermarked_image, image_displayed

    monitor_data = set_image_canvas_dimensions(ImageTk.PhotoImage(watermarked_image))
    canvas_width, canvas_height = monitor_data[0], monitor_data[1]
    image_canvas.config(width=canvas_width, height=canvas_height)

    image_displayed = ImageTk.PhotoImage(watermarked_image.resize((canvas_width, canvas_height)))
    image_canvas.create_image(0, 0, anchor=NW, image=image_displayed)


def change_image_file(input_image):
    global image_file
    image_file = Image.open(input_image)
    apply_watermark_to_image()


def change_watermark_file(input_image):
    global watermark_file
    watermark_file = Image.open(input_image)
    apply_watermark_to_image()


def browse_image_files():
    file = filedialog.askopenfile(initialdir="images/",
                                  title="Select Main Image File",
                                  filetypes=(("All Files", "*.*"), ("PNG Files", "*.png*"), ("JPG Files", "*.jpg*")))
    if file is not None:
        change_image_file(file.name)


def browse_watermark_files():
    file = filedialog.askopenfile(initialdir="watermarks/",
                                  title="Select Main Image File",
                                  filetypes=(("All Files", "*.*"), ("PNG Files", "*.png*"), ("JPG Files", "*.jpg*")))
    if file is not None:
        change_watermark_file(file.name)


def set_watermark_x(value):
    global watermark_x, image_file
    watermark_x = int(int(value) / 100 * image_file.width)
    apply_watermark_to_image()


def set_watermark_y(value):
    global watermark_y, image_file
    watermark_y = int(int(value) / 100 * image_file.height)
    apply_watermark_to_image()


def set_watermark_scale(value):
    global watermark_scale
    watermark_scale = int(value)
    print(watermark_scale)
    apply_watermark_to_image()


def set_watermark_opacity(value):
    global watermark_opacity
    watermark_opacity = int(value)
    print(watermark_opacity)
    apply_watermark_to_image()


def apply_watermark_to_image():
    global image_file, watermarked_image, watermark_file, watermark_scale, \
        watermark_opacity, watermark_x, watermark_y, canvas

    watermarked_image = image_file
    watermarked_image.paste(box=(watermark_x, watermark_y), im=watermark_file)

    update_screen(canvas)


def save_file():
    global watermarked_image
    file_name = filedialog.asksaveasfilename(initialdir="output/")
    watermarked_image.save(fp=file_name)


# ---------------- Tkinter GUI ---------------- #

# Create the Tkinter window
window = Tk()
window.title("Watermarking Application")
window.config(padx=50, pady=50, background="white")

# Add the images to the window
canvas = Canvas(border=10)
update_screen(canvas)
canvas.grid(column=0, row=0, columnspan=3, rowspan=2)

# Add file input buttons to the window
choose_image_button = Button(text="Select Image", command=browse_image_files)
choose_image_button.grid(column=0, row=2)

button_browse_watermarks = Button(text="Select Watermark", command=browse_watermark_files)
button_browse_watermarks.grid(column=1, row=2)

# Add save button to the window
watermark_button = Button(text="Create Watermarked Image", command=save_file)
watermark_button.grid(column=2, columnspan=3, row=2)

# Add slider scales to modify watermark values
scale_watermark_scale_label = Label(text="Watermark Scale")
scale_watermark_scale_label.grid(column=4, row=0)
scale_watermark_scale = Scale(orient=tkinter.VERTICAL, command=set_watermark_scale)
scale_watermark_scale.grid(column=4, row=1, rowspan=3)

place_watermark_scale_x_label = Label(text="Watermark Placement (x)")
place_watermark_scale_x_label.grid(column=5, row=0)
place_watermark_scale_x = Scale(orient=tkinter.VERTICAL, command=set_watermark_x)
place_watermark_scale_x.grid(column=5, row=1, rowspan=3)

place_watermark_scale_y_label = Label(text="Watermark Placement (y)")
place_watermark_scale_y_label.grid(column=6, row=0)
place_watermark_scale_y = Scale(orient=tkinter.VERTICAL, command=set_watermark_y)
place_watermark_scale_y.grid(column=6, row=1, rowspan=3)

opacity_scale_label = Label(text="Opacity Scale")
opacity_scale_label.grid(column=7, row=0)
opacity_scale = Scale(orient=tkinter.VERTICAL, command=set_watermark_opacity)
opacity_scale.grid(column=7, row=1, rowspan=3)

window.mainloop()
