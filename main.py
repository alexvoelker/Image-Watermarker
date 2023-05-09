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
WATERMARK_PATH = "watermarks/default-watermark-1.png"

image_displayed = None
image_file = Image.open(fp=DEFAULT_IMAGE_PATH)

watermark_x = 0
watermark_y = 0

# 'watermarked_image' will be the working file, with 'image_file' being the original
watermarked_image = image_file.copy()
watermarked_image.paste(Image.open(fp=WATERMARK_PATH))
modified_watermark = None

# Initialize some tkinter global variables for use later
window = Tk()  # need the window here, so that we don't have a second window appear when declaring the scale globals
scale_watermark_scale = Scale()
scale_opacity_scale = Scale()
scale_place_watermark_x = Scale()
scale_place_watermark_y = Scale()


# ---------------- Program Logic ---------------- #
def get_watermarked_image_file():
    return watermarked_image


def set_image_canvas_dimensions() -> list[int, int]:
    picture = ImageTk.PhotoImage(get_watermarked_image_file())
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


def update_scale_lengths():
    global scale_watermark_scale, scale_opacity_scale, scale_place_watermark_x, scale_place_watermark_y
    length = set_image_canvas_dimensions()[1],
    scale_watermark_scale.config(length=length[0])
    scale_opacity_scale.config(length=length[0])
    scale_place_watermark_x.config(length=length[0])
    scale_place_watermark_y.config(length=length[0])


def update_screen(image_canvas: Canvas):
    global watermarked_image, image_displayed

    update_scale_lengths()

    monitor_data = set_image_canvas_dimensions()
    canvas_width, canvas_height = monitor_data[0], monitor_data[1]
    image_canvas.config(width=canvas_width, height=canvas_height)

    image_displayed = ImageTk.PhotoImage(watermarked_image.resize((canvas_width, canvas_height)))
    image_canvas.create_image(0, 0, anchor=NW, image=image_displayed)


def change_image_file(input_image_path):
    global image_file
    image_file = Image.open(input_image_path)
    apply_watermark_to_image()


def get_watermark_file():
    global WATERMARK_PATH
    watermark_file = Image.open(WATERMARK_PATH)
    return watermark_file


def change_watermark_file(input_image_path):
    global WATERMARK_PATH, modified_watermark
    WATERMARK_PATH = input_image_path
    modified_watermark = get_watermark_file()
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


def modify_watermark(watermark_scale=None, watermark_opacity=None):
    global modified_watermark
    modified_watermark = get_watermark_file()

    if watermark_scale is not None and watermark_scale > 0:
        scaled_dimensions = (int(modified_watermark.width * watermark_scale / 50),
                             int(modified_watermark.height * watermark_scale / 50))
        modified_watermark = modified_watermark.resize(scaled_dimensions)

    if watermark_opacity is not None and watermark_opacity != 0:
        modified_watermark.putalpha(int(watermark_opacity / 100 * 255))

    modified_watermark.save(fp="output/watermark_edit.png")

    apply_watermark_to_image()


def set_watermark_scale(value):
    modify_watermark(watermark_scale=int(value))


def set_watermark_opacity(value):
    # TODO fix the opacity of images not showing
    modify_watermark(watermark_opacity=int(value))


def apply_watermark_to_image():
    global image_file, watermarked_image, modified_watermark, watermark_x, watermark_y, canvas
    if modified_watermark is None:
        modified_watermark = get_watermark_file()
    watermarked_image = image_file.copy()
    watermarked_image.paste(box=(watermark_x, watermark_y), im=modified_watermark)
    update_screen(canvas)


def save_file():
    global watermarked_image
    file_name = filedialog.asksaveasfilename(initialdir="output/")
    watermarked_image.save(fp=file_name)


# ---------------- Tkinter GUI ---------------- #

# Create the Tkinter window
window.title("Watermarking Application")
window.config(padx=50, pady=50, background="white")

# Add the images to the window
canvas = Canvas(border=10)
update_screen(canvas)
canvas.grid(column=0, row=1, columnspan=3, rowspan=2)

# Add file input buttons to the window
choose_image_button = Button(text="Select Image", command=browse_image_files)
choose_image_button.grid(column=0, row=3)

button_browse_watermarks = Button(text="Select Watermark", command=browse_watermark_files)
button_browse_watermarks.grid(column=1, row=3)

# Add save button to the window
watermark_button = Button(text="Create Watermarked Image", command=save_file)
watermark_button.grid(column=2, columnspan=3, row=3)

# Add slider scales to modify watermark values
label_watermark_scale = Label(text="Watermark Scale")
label_watermark_scale.grid(column=4, row=0)
scale_watermark_scale.config(orient=tkinter.VERTICAL,
                             command=set_watermark_scale,
                             length=set_image_canvas_dimensions()[1],
                             to=250)
scale_watermark_scale.grid(column=4, row=1, rowspan=3)

label_place_watermark_x = Label(text="Watermark Placement (x)")
label_place_watermark_x.grid(column=5, row=0)
scale_place_watermark_x.config(orient=tkinter.VERTICAL,
                               command=set_watermark_x,
                               length=set_image_canvas_dimensions()[1])
scale_place_watermark_x.grid(column=5, row=1, rowspan=3)

label_place_watermark_y = Label(text="Watermark Placement (y)")
label_place_watermark_y.grid(column=6, row=0)
scale_place_watermark_y.config(orient=tkinter.VERTICAL,
                               command=set_watermark_y,
                               length=set_image_canvas_dimensions()[1])
scale_place_watermark_y.grid(column=6, row=1, rowspan=3)

label_opacity_scale = Label(text="Opacity Scale")
label_opacity_scale.grid(column=7, row=0)
scale_opacity_scale.config(orient=tkinter.VERTICAL,
                           command=set_watermark_opacity,
                           length=set_image_canvas_dimensions()[1])
scale_opacity_scale.grid(column=7, row=1, rowspan=3)

window.mainloop()
