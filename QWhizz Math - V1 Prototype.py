# Date Created: 05/05/2025
# Author: Jack Compton
# Purpose: GUI application for Flow Computing that helps students with their mathematics

import customtkinter as CTk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk 


# Add the next user's quiz details to the list
def append_quiz_details():
    # Append each item to its own area of the list
    quiz_details.append([username.get(), difficulty.get(), questions.get()])
    # Clear the boxes
    username.delete(0, 'end')


def slider_value_update(slider_id, value):
    if slider_id == "S1":
        if value == 0:
            difficulty_label.configure(text="Easy  ")
        elif value == 1:
            difficulty_label.configure(text="Medium")
        else:
            difficulty_label.configure(text="Hard  ")
    if slider_id == "S2":
        question_no_label.configure(text=f"{int(value)} Questions")

# Function for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
def setup_elements():
    global username, difficulty, questions, difficulty_label, question_no_label, timer

    # Set up the menu bar
    menubar = Menu(main_window)

    filemenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Print Selected", accelerator="Ctrl+P")
    filemenu.add_command(label="Print All", accelerator="Ctrl+Shift+P")
    filemenu.add_command(label="Delete Selected", accelerator="Del")
    filemenu.add_command(label="Delete All", accelerator="Shift+Del")

    settingsmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settingsmenu)
    timer_settings = Menu(menubar, tearoff=0)
    settingsmenu.add_cascade(menu=timer_settings, label="Timer")
    # Create a "timer" BooleanVar to control the timer checkbutton state, with the default value being True, putting the checkbutton in an on state.
    timer = BooleanVar(value=True)
    timer_settings.add_radiobutton(label="Enabled", variable=timer, value=True)
    timer_settings.add_radiobutton(label="Disabled", variable=timer, value=False)

    helpmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="Documentation")
    helpmenu.add_command(label="About")

    main_window.config(menu=menubar)

    # Set up a content frame to place the main home elements inside
    content_frame1 = CTk.CTkFrame(main_window)
    content_frame1.grid(column=0, row=0, columnspan=2, sticky=EW, padx=10, pady=(10,5))
    content_frame1._set_appearance_mode("light")

    # Set width for columns 0-2 (3 total) in content frame 1.
    content_frame1.columnconfigure(0, weight=0, minsize=100)
    content_frame1.columnconfigure(1, weight=0, minsize=150)
    content_frame1.columnconfigure(2, weight=0, minsize=100)

    # Create the labels to be placed next to their relevant entry boxes.
    CTk.CTkLabel(content_frame1, text="Username").grid(column=0, row=0, sticky=E, padx=5, pady=(10,0))
    CTk.CTkLabel(content_frame1, text="Difficulty").grid(column=0, row=1, sticky=E, padx=5, pady=10)
    CTk.CTkLabel(content_frame1, text="Questions").grid(column=0, row=2, sticky=E, padx=5, pady=(0,10))
    
    difficulty_label = CTk.CTkLabel(content_frame1, text="", width=10)
    difficulty_label.grid(column=2, row=1, sticky=W, padx=5, pady=10)
    question_no_label = CTk.CTkLabel(content_frame1, text="", width=10)
    question_no_label.grid(column=2, row=2, sticky=W, padx=5, pady=(0,10))

    # Setup entry box and sliders (scales).
    username = CTk.CTkEntry(content_frame1)
    username.grid(column=1, row=0, padx=5, pady=(10,0), sticky=EW)
    difficulty = CTk.CTkSlider(content_frame1, from_=0, to=2, number_of_steps=2, command=lambda value: slider_value_update("S1", value), orientation=HORIZONTAL)
    difficulty.grid(column=1, row=1, padx=5, pady=10, sticky=EW)
    questions = CTk.CTkSlider(content_frame1, from_=5, to=35, number_of_steps=30, command=lambda value: slider_value_update("S2", value), orientation=HORIZONTAL)
    questions.grid(column=1, row=2, padx=5, pady=(0,10), sticky=EW)
    slider_value_update("S1", difficulty.get())
    slider_value_update("S2", questions.get())
    
    # Create the buttons
    CTk.CTkButton(main_window, text="Scoreboard", width=200).grid(column=0, row=1, sticky=EW, padx=(10,5), pady=(5, 10))
    CTk.CTkButton(main_window, text="Start", width=200).grid(column=1, row=1, sticky=EW, padx=(5,10), pady=(5,10))

# Main function for starting the program.
def main(): 
    # Start the primary GUI functions.
    setup_elements()

    main_window.mainloop()


#Initialise the main window.
main_window = CTk.CTk()
main_window.title("QWhizz Math")  # Set the title of the window.
#main_window.iconphoto(False, PhotoImage(file="Images/Pgm_icon.png"))  # Set the title bar icon.
main_window.resizable(False, False)         # Set the resizable property for height and width to False.
#main_window_bg = "#"                  # Set the background colour of the main window.
#main_window.configure(bg=main_window_bg)    # Configure the main window to use the background colour (value) of the "main_window_bg variable".
CTk.set_appearance_mode("light")

# Set width for columns 0-1 (2 total) in the main window.
main_window.columnconfigure(0, weight=0, minsize=215)
main_window.columnconfigure(1, weight=0, minsize=215)

# Initialise global lists and variables.
quiz_details = []           # Create empty list for user details so that their quiz results can be stored inside.
difficulty_list = ["Easy", "Medium", "Hard"]  # Create a list of the different difficulty levels.

# Run the main function.
main()