import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter.messagebox as messagebox

# List to store the images that need to be saved
images_to_save = []

# List to store the file paths of the images to be saved
images_to_save_paths = []

# Variable to store the watermark image
watermark_image = None

# Hexadecimal color codes for various colors
whitish_color = "#f0f0f0"
blue_color = "#293241"
blue_color_hover = "#1f2833"
red_color = "#ed6b4d"
red_color_hover = "#c9563b"

# Font style for Nunito with bold size 18
font_nunito_18_bold = ('Nunito', 18, 'bold')

# Font style for Nunito with size 10
font_nunito_10 = ('Nunito', 10)

# Font style for Playfair Display with size 14
font_playfair_display_14 = ("playfair display", 14)


def upload_watermark_image():
    """
    Opens a file dialog to select a watermark image file and assigns it to the 'watermark_image' variable.

    Returns:
        None
    """
    global watermark_image

    # File types for the file dialog
    file_type = [('Jpg Files', '*.jpg'), ('PNG Files', '*.png')]

    # Open the file dialog to select the watermark image file
    filename = filedialog.askopenfilenames(filetypes=file_type)

    # Update the text of the watermark image button to display the selected file name
    watermark_image_button.config(text=filename[0].split("/")[-1])

    # Open the selected image file and assign it to the 'watermark_image' variable
    watermark_image = Image.open(filename[0])


def upload_file():
    """
    Opens a file dialog to select multiple image files and processes each selected image.

    Returns:
        None
    """
    # Get watermark text from entry field
    watermark_text = watermark_entry.get()

    # Check if both watermark text and image are provided or not
    if watermark_text and watermark_image:
        messagebox.showerror("Error", "Please choose either a watermark text OR a watermark image.")
    elif not watermark_text and not watermark_image:
        messagebox.showerror("Error", "Please provide a watermark first.")
    else:
        # Create global variables to store images and their paths
        global images_to_save
        global images_to_save_paths

        images_to_save = []
        images_to_save_paths = []

        # Define file types for open file dialog
        file_types = [('Jpg Files', '*.jpg'), ('PNG Files', '*.png')]

        # Open file dialog to select multiple images
        filenames = filedialog.askopenfilenames(filetypes=file_types)

        # Get watermark location from variable
        watermark_location = watermark_location_var.get()

        col = 1
        row = 20

        # Process each selected image
        for f in filenames:
            # Open image
            img = Image.open(f)

            # Add watermark to image
            watermarked_img = add_watermark(img, watermark_text, watermark_location, watermark_image)

            # Resize watermarked image to fit in a label
            width, height = watermarked_img.size
            if width > height:
                width_new = 200
                height_new = width_new * height // width
            else:
                height_new = 200
                width_new = height_new * width // height
            watermarked_img_resized = img.resize((width_new, height_new))

            # Convert image to Tkinter format
            img_tk = ImageTk.PhotoImage(watermarked_img_resized)

            # Create label to display image
            e1 = tk.Label(frame)
            e1.grid(row=row, column=col, pady=10)
            e1.image = img_tk
            e1['image'] = img_tk

            # Update row and column for next image
            if col == 5:
                row += 1
                col = 1
            else:
                col += 1

            # Add watermarked image and its path to global variables
            images_to_save.append(watermarked_img)
            images_to_save_paths.append(f)

        # Enable the save button if there are images to save
        if len(images_to_save) > 0:
            b2.config(state=tk.NORMAL)


def add_watermark(image, watermark_text, watermark_location, watermark_image=None):
    """
    Adds a watermark to the given image.

    Args:
        image (PIL.Image.Image): The original image to add the watermark to.
        watermark_text (str): The text to use as the watermark.
        watermark_location (str): The location where the watermark should be placed. Possible values are 'top-left',
            'top-right', 'bottom-left', 'bottom-right', 'center'.
        watermark_image (PIL.Image.Image, optional): The image to use as the watermark. Defaults to None.

    Returns:
        PIL.Image.Image: The watermarked image.
    """
    # Create a copy of the original image
    watermarked_image = image.copy()

    # Get the position and anchor point for the watermark
    position, anchor = get_watermark_position(image.size, watermark_location)

    # Add text watermark if provided
    if watermark_text:
        # Create a transparent image with the same size as the original image
        watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))

        # Create a draw object to draw on the transparent image
        draw = ImageDraw.Draw(watermark)

        # Load a font for the watermark text
        font = ImageFont.truetype("fonts/Montserrat-Regular.otf", 100)

        # Draw the watermark text on the transparent image
        draw.text(position, watermark_text, fill=(255, 255, 255, 128), font=font, anchor=anchor)

        # Combine the original image and the transparent image with the watermark
        watermarked_image = Image.alpha_composite(image.convert('RGBA'), watermark)

    # Add image watermark if provided
    if watermark_image:
        width, height = watermark_image.size
        if anchor == "lt":
            watermark_position = position
        elif anchor == "lm":
            watermark_position = (position[0], position[1] - height // 2)
        elif anchor == "lb":
            watermark_position = (position[0], position[1] - height)
        elif anchor == "mt":
            watermark_position = (position[0] - width // 2, position[1])
        elif anchor == "mm":
            watermark_position = (position[0] - width // 2, position[1] - height // 2)
        elif anchor == "mb":
            watermark_position = (position[0] - width // 2, position[1] - height)
        elif anchor == "rt":
            watermark_position = (position[0] - width, position[1])
        elif anchor == "rm":
            watermark_position = (position[0] - width, position[1] - height // 2)
        elif anchor == "rb":
            watermark_position = (position[0] - width, position[1] - height)
        else:
            watermark_position = position

        # Convert the watermark image to RGBA format
        watermark = watermark_image.convert('RGBA')

        # Paste the watermark image onto the original image
        watermarked_image.paste(watermark, watermark_position, mask=watermark)

    return watermarked_image


def get_watermark_position(image_size, watermark_location):
    """
    Calculates the position and anchor point for the watermark based on the image size and desired location.

    Args:
        image_size (tuple): The size of the image in pixels.
        watermark_location (str): The desired location of the watermark.

    Returns:
        tuple: The position of the watermark in pixels and the anchor point for the watermark.
    """
    width, height = image_size
    x_pad = 10
    y_pad = 10

    if watermark_location == "top-left":
        position = (x_pad, y_pad)
        anchor = "lt"
    elif watermark_location == "middle-left":
        position = (x_pad, height // 2)
        anchor = "lm"
    elif watermark_location == "bottom-left":
        position = (x_pad, height - y_pad)
        anchor = "lb"
    elif watermark_location == "top-center":
        position = (width // 2, y_pad)
        anchor = "mt"
    elif watermark_location == "middle-center":
        position = (width // 2, height // 2)
        anchor = "mm"
    elif watermark_location == "bottom-center":
        position = (width // 2, height - y_pad)
        anchor = "mb"
    elif watermark_location == "top-right":
        position = (width - x_pad, y_pad)
        anchor = "rt"
    elif watermark_location == "middle-right":
        position = (width - x_pad, height // 2)
        anchor = "rm"
    elif watermark_location == "bottom-right":
        position = (width - x_pad, height - y_pad)
        anchor = "rb"
    else:
        position = (x_pad, y_pad)
        anchor = "lt"

    return position, anchor


def save():
    """
    Saves the watermarked images to a selected folder.

    Returns:
        None
    """
    folder_path = filedialog.askdirectory()
    if folder_path:
        for path in images_to_save_paths:
            index = images_to_save_paths.index(path)
            file_name = path.split("/")[-1]
            save_path = folder_path + "/ watermarked - " + file_name
            images_to_save[index].convert('RGB').save(save_path)

    messagebox.showinfo("Success", "All images saved with watermark")


def on_enter_blue(button):
    """
    Changes the background color of a button to blue when the mouse enters it.

    Args:
        button (tk.Button): The button to change the background color of.

    Returns:
        None
    """
    if button['state'] == tk.NORMAL:
        button.config(bg=blue_color_hover)


def on_leave_blue(button):
    """
    Changes the background color of a button back to its original color when the mouse leaves it.

    Args:
        button (tk.Button): The button to change the background color of.

    Returns:
        None
    """
    if button['state'] == tk.NORMAL:
        button.config(bg=blue_color)


def on_enter_red(button):
    """
    Changes the background color of a button to red when the mouse enters it.

    Args:
        button (tk.Button): The button to change the background color of.

    Returns:
        None
    """
    if button['state'] == tk.NORMAL:
        button.config(bg=red_color_hover)


def on_leave_red(button):
    """
    Changes the background color of a button back to its original color when the mouse leaves it.

    Args:
        button (tk.Button): The button to change the background color of.

    Returns:
        None
    """
    if button['state'] == tk.NORMAL:
        button.config(bg=red_color)


# ---------------------------- UI SETUP ------------------------------- #
# Set the window
# Create the main window
window = tk.Tk()

# Get the screen width and height
window_width = window.winfo_screenwidth()
window_height = window.winfo_screenheight()

# Set the window size to match the screen size
window.geometry("%dx%d" % (window_width, window_height))

# Set the window title
window.title('Watermark Wizard')

# Set the background color of the window
window.configure(bg=whitish_color)

# Create a frame to hold the widgets
frame = tk.Frame(window)

# Place the frame at the center of the window
frame.place(relx=0.5, rely=0.5, anchor="c")

# Add the logo image
logo_img = Image.open('logo.png')
logo_img_tk = ImageTk.PhotoImage(logo_img)
logo_label = tk.Label(frame, image=logo_img_tk, bg=whitish_color)
logo_label.grid(row=0, column=0, columnspan=8)

# Create a label for the watermark text
watermark_label = tk.Label(
    frame,
    text='Watermark Text:',
    bg=whitish_color,
    fg=blue_color,
    font=font_playfair_display_14
)
watermark_label.grid(row=1, column=1, pady=(30, 5))

# Create an entry field for the watermark text
watermark_entry = tk.Entry(frame)
watermark_entry.config(font=font_nunito_10)
watermark_entry.grid(row=2, column=1, pady=(5, 15))

# Create a label for the "or" text
watermark_label = tk.Label(
    frame,
    text='or',
    bg=whitish_color,
    fg=blue_color,
    font=font_playfair_display_14
)
watermark_label.grid(row=1, column=2, pady=(50, 5))

# Create a label for the watermark image
watermark_image_label = tk.Label(
    frame,
    text='Watermark Image:',
    bg=whitish_color,
    fg=blue_color,
    font=font_playfair_display_14
)
watermark_image_label.grid(row=1, column=3, pady=(30, 5))

# Create a button to upload the watermark image
watermark_image_button = tk.Button(
    frame,
    text='Upload Watermark Image',
    width=20,
    command=upload_watermark_image,
    bg=red_color,
    fg=whitish_color,
    font=font_nunito_10,
    relief='flat',
    compound='center',
)
watermark_image_button.grid(row=2, column=3, pady=(5, 15))
watermark_image_button.bind("<Enter>", lambda e: on_enter_red(watermark_image_button))
watermark_image_button.bind("<Leave>", lambda e: on_leave_red(watermark_image_button))

# Creating a label for the watermark location
watermark_location_label = tk.Label(
    frame,
    text='Watermark Location:',
    bg=whitish_color,
    fg=blue_color,
    font=font_playfair_display_14
)
watermark_location_label.grid(row=3, column=2, pady=(15, 5))

# Creating a variable to store the selected watermark location
watermark_location_var = tk.StringVar(frame)
watermark_location_var.set("top-left")

# Creating a dropdown menu for selecting the watermark location
watermark_location_menu = tk.OptionMenu(
    frame,
    watermark_location_var,
    "top-left", "middle-left", "bottom-left",
    "top-center", "middle-center", "bottom-center",
    "top-right", "middle-right", "bottom-right"
)
watermark_location_menu.config(font=('Nunito', 10))
watermark_location_menu.grid(row=4, column=2, pady=(5, 20))

# Creating a label for uploading files and displaying them
l1 = tk.Label(
    frame,
    text='Upload Files & Display',
    width=30,
    font=font_nunito_18_bold,
    bg=whitish_color,
    fg=blue_color
)
l1.grid(row=9, column=1, columnspan=4, pady=(25, 0))

# Creating a button for uploading images
b1 = tk.Button(
    frame,
    text='Upload Images',
    width=20,
    command=upload_file,
    bg=red_color,
    fg=whitish_color,
    font=font_nunito_10,
    relief='flat'
)
b1.grid(row=10, column=1, columnspan=4, pady=20)
b1.bind("<Enter>", lambda e: on_enter_red(b1))
b1.bind("<Leave>", lambda e: on_leave_red(b1))

# Creating a button for saving the changes
b2 = tk.Button(
    frame,
    text='Save',
    width=20,
    command=save,
    bg=blue_color,
    fg=whitish_color,
    font=font_nunito_10,
    relief='flat',
    state=tk.DISABLED
)
b2.grid(row=999, column=1, columnspan=4, pady=20)
b2.bind("<Enter>", lambda e: on_enter_blue(b2))
b2.bind("<Leave>", lambda e: on_leave_blue(b2))

# Running the main event loop for the GUI
window.mainloop()
