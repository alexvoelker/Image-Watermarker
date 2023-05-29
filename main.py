import os

# Install the requirements for this program if they aren't already installed.
os.system("pip3 install -r requirements.txt")

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
watermark_opacity = 0
watermark_scale = 0

# 'watermarked_image' will be the working file, with 'image_file' being the original
watermarked_image = image_file.copy()

watermark = Image.open(fp=WATERMARK_PATH)
watermarked_image.paste(watermark, (0, 0), watermark)
modified_watermark = None
canvas_id = None

# Initialize some tkinter global variables for use later
window = Tk()  # need the window here, so that we don't have a second window appear when declaring the scale globals
scale_watermark_scale = Scale()
scale_opacity_scale = Scale()
scale_place_watermark_x = Scale()
scale_place_watermark_y = Scale()


# ---------------- Program Logic ---------------- #
def get_watermarked_image_file():
    """Returns the watermarked image file object"""
    return watermarked_image


def find_suitable_image_dimensions(image: tuple[int, int], constraint_value: int,
                                   constraint_boundary: float = 0.95) -> tuple[int, int]:
    """Find image dimensions that would fit within a constraint value.
    Returns a tuple containing the calculated constrained values.

    :param image: The dimensions of an image, given as a tuple containing two integers
    :param constraint_value: The value that is used to scale the image dimensions by
    :param constraint_boundary: A value that modifies the constraint_value, creating a padding around the constraint_value (the default is 0.95).
    """
    # A suitable constraint is likely about 90% of the monitor's smaller dimension.
    constraint_value = constraint_boundary * constraint_value

    # Constrain the image by its larger dimension
    if image[0] > image[1]:
        constraint_factor = constraint_value / image[0]
    else:
        constraint_factor = constraint_value / image[1]

    # Find the new dimensions of the image when constrained by the constraint_factor
    constrained_x = int(image[0] * constraint_factor)
    constrained_y = int(image[1] * constraint_factor)

    constrained_dimensions = (constrained_x, constrained_y)
    return constrained_dimensions


def set_image_canvas_dimensions() -> tuple[int, int]:
    """Find image dimensions for the tkinter GUI that would fit in the smallest user's monitor."""
    picture = get_watermarked_image_file()
    monitors_info = []

    # Grab the width and height of any monitors on a computer
    for m in get_monitors():
        monitors_info.append([int(m.width), int(m.height)])

    # Look at the information on the smaller monitor
    monitor_info = sorted(monitors_info)[0]

    # Check to see if the smallest monitor's width is greater than its height
    if monitor_info[0] > monitor_info[1]:
        image_dimensions = find_suitable_image_dimensions(image=picture.size, constraint_value=monitor_info[1])
    else:
        # The smallest monitor's height is greater than it's width
        image_dimensions = find_suitable_image_dimensions(image=picture.size, constraint_value=monitor_info[0])
    return image_dimensions


def update_scale_lengths():
    """Increase the length of the Scales in the GUI."""
    global scale_watermark_scale, scale_opacity_scale, scale_place_watermark_x, scale_place_watermark_y
    length = set_image_canvas_dimensions()[1],
    scale_watermark_scale.config(length=length[0])
    scale_opacity_scale.config(length=length[0])
    scale_place_watermark_x.config(length=length[0])
    scale_place_watermark_y.config(length=length[0])


def update_screen(image_canvas: Canvas):
    """Swap the image that is currently in the GUI canvas element with a new image.

    :param image_canvas: The Canvas object to modify."""
    global watermarked_image, image_displayed, canvas_id

    # Since the main image is being changed, the scales to the side of it need to be updated also
    update_scale_lengths()

    monitor_data = set_image_canvas_dimensions()
    canvas_width, canvas_height = monitor_data[0], monitor_data[1]
    image_canvas.config(width=canvas_width, height=canvas_height)
    if canvas_id is not None:
        image_canvas.delete(canvas_id)

    image_displayed = ImageTk.PhotoImage(watermarked_image.resize((canvas_width, canvas_height)))
    canvas_id = image_canvas.create_image(0, 0, anchor=NW, image=image_displayed)


def change_image_file(input_image_path):
    """Change the image_file.

    :param input_image_path: The path of the new file."""

    global image_file
    image_file = Image.open(input_image_path)
    apply_watermark_to_image()


def get_watermark_file():
    """Return the watermark_file object as it appears in the filesystem. File is opened from the WATERMARK_PATH."""
    global WATERMARK_PATH
    watermark_file = Image.open(WATERMARK_PATH).convert("RGBA")
    return watermark_file


def change_watermark_file(input_image_path):
    """Change the WATERMARK_PATH and modified_watermark object. When changed, the screen is updated.

    :param input_image_path: The path of the new watermark file."""
    global WATERMARK_PATH, modified_watermark
    WATERMARK_PATH = input_image_path
    modified_watermark = get_watermark_file()
    apply_watermark_to_image()


def browse_image_files():
    """Select a new image file from the filesystem."""
    file = filedialog.askopenfile(initialdir="images/",
                                  title="Select Main Image File",
                                  filetypes=(("All Files", "*.*"), ("PNG Files", "*.png*"), ("JPG Files", "*.jpg*")))
    if file is not None:
        change_image_file(file.name)


def browse_watermark_files():
    """Select a new watermark file from the filesystem."""
    file = filedialog.askopenfile(initialdir="watermarks/",
                                  title="Select Main Image File",
                                  filetypes=(("All Files", "*.*"), ("PNG Files", "*.png*"), ("JPG Files", "*.jpg*")))
    if file is not None:
        change_watermark_file(file.name)


def set_watermark_x(value):
    """Set the x-value for the watermark in the image"""
    global watermark_x, image_file
    watermark_x = int(int(value) / 100 * image_file.width)
    apply_watermark_to_image()


def set_watermark_y(value):
    """Set the y-value for the watermark in the image"""
    global watermark_y, image_file
    watermark_y = int(int(value) / 100 * image_file.height)
    apply_watermark_to_image()


def modify_watermark(fix_white_background=False):
    """Modify the watermark in some way based on the watermark_scale and watermark_opacity global variables

    :param fix_white_background: Boolean input. If true, the program will attempt to fix the watermark by setting all white pixels to full transparency"""
    global modified_watermark, watermark_scale, watermark_opacity
    modified_watermark = get_watermark_file()

    if watermark_scale > 0:
        # Change size of watermark image
        scaled_dimensions = (int(modified_watermark.width * watermark_scale / 50),
                             int(modified_watermark.height * watermark_scale / 50))
        modified_watermark = modified_watermark.resize(scaled_dimensions)

    if watermark_opacity > 0:
        # Apply opacity to watermark
        opaque_image = [(pixel[0], pixel[1], pixel[2], watermark_opacity) if pixel[3] != 0 else
                        (pixel[0], pixel[1], pixel[2], 0) for pixel in modified_watermark.getdata()]
        modified_watermark.putdata(opaque_image)

    if fix_white_background:
        # Change all white pixels to be fully transparent
        transparent_background_image = [(pixel[0], pixel[1], pixel[2], 0) if pixel[:3] == (255, 255, 255) else
                                        pixel for pixel in modified_watermark.getdata()]
        modified_watermark.putdata(transparent_background_image)

    return modified_watermark


def apply_watermark_to_image():
    """Apply the watermark image object to the main image using global settings of watermark_x, watermark_y and watermark_opacity."""
    global image_file, watermarked_image, modified_watermark, watermark_x, watermark_y, watermark_opacity, canvas
    if modified_watermark is None:
        modified_watermark = modify_watermark()

    image_background = image_file.copy()

    if watermark_opacity != 0:
        # If the opacity level has been changed
        watermarked_image = Image.new("RGBA", image_background.size)
        watermarked_image = Image.alpha_composite(watermarked_image, image_background.convert("RGBA"))
    else:
        # If the opacity level hasn't been changed
        watermarked_image = image_background

    watermarked_image.paste(modified_watermark, (watermark_x, watermark_y), modified_watermark)
    update_screen(canvas)


def set_watermark_scale(value):
    """Set the value that the watermark will be scaled by on the image. The image is then modified to reflect the change.

    :param value: the integer value to scale the image by."""
    global watermark_scale
    watermark_scale = int(value)
    modify_watermark()
    apply_watermark_to_image()


def set_watermark_opacity(value):
    """Set the value of the watermark's opacity in the image. The image is then modified to reflect the change.

    :param value: the integer value to set the opacity level to."""
    global watermark_opacity
    watermark_opacity = int(value)
    modify_watermark()
    apply_watermark_to_image()


def fix_watermark_background():
    """Attempt to fix the background opacity of the watermark image. After the watermark is modified, it's applied to
    the image. """
    modify_watermark(fix_white_background=True)
    apply_watermark_to_image()


def save_file():
    """Save the watermarked image to the filesystem."""
    global watermarked_image
    file_name = filedialog.asksaveasfilename(initialdir="output/", defaultextension=".png")
    if len(file_name) > 0:
        watermarked_image.save(fp=file_name)
        print(f"File Saved at: {file_name}")


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

button_fix_watermark_background = Button(text="Fix Watermark Background?", command=fix_watermark_background)
button_fix_watermark_background.grid(column=2, row=3)

# Add save button to the window
watermark_button = Button(text="Save Watermarked Image", command=save_file)
watermark_button.grid(column=3, columnspan=3, row=3)

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
                           length=set_image_canvas_dimensions()[1],
                           to=255)
scale_opacity_scale.grid(column=7, row=1, rowspan=3)

window.mainloop()
