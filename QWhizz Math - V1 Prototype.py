# Date Created: 05/05/2025
# Author: Jack Compton
# Purpose: GUI application for Flow Computing that helps students with their mathematics

from customtkinter import *
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk 


# Add the next user's quiz details to the list
def append_quiz_details():
    # Append each item to its own area of the list
    quiz_details.append([username.get(), difficulty.get(), questions.get()])
    # Clear the boxes
    username.delete(0, 'end')


# Function for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
def setup_elements():
    global username, difficulty, questions
    
    # Create the labels to be placed next to their relevant entry boxes.
    CTkLabel(main_window, text="Username").grid(column=0, row=0, sticky=E, padx=5, pady=5)
    CTkLabel(main_window, text="Difficulty").grid(column=0, row=1, sticky=E, padx=5, pady=5)
    CTkLabel(main_window, text="Questions").grid(column=0, row=2, sticky=E, padx=5, pady=5)
    
    # Setup entry box and sliders (scales).
    username = CTkEntry(main_window)
    username.grid(column=1, row=0, padx=5, sticky=EW)
    difficulty = CTkSlider(main_window, from_=0, to=2, number_of_steps=2, orientation=HORIZONTAL)
    difficulty.grid(column=1, row=1, padx=5, sticky=EW)
    questions = CTkSlider(main_window, from_=1, to=30, number_of_steps=29, orientation=HORIZONTAL)
    questions.grid(column=1, row=2, padx=5, sticky=EW)
    
    # Create the buttons
    CTkButton(main_window, text="Scoreboard", width=200).grid(column=0, row=3, sticky=EW, padx=5, pady=5)
    CTkButton(main_window, text="Start", width=200).grid(column=1, row=3, sticky=EW, padx=5, pady=5)

# Main function for starting the program.
def main(): 
    # Start the primary GUI functions.
    setup_elements()

    main_window.mainloop()


#Initialise the main window.
main_window = CTk()
main_window.title("QWhizz Math")  # Set the title of the window.
#main_window.iconphoto(False, PhotoImage(file="Images/Pgm_icon.png"))  # Set the title bar icon.
main_window.resizable(False, False)         # Set the resizable property for height and width to False.
#main_window_bg = "#"                  # Set the background colour of the main window.
#main_window.configure(bg=main_window_bg)    # Configure the main window to use the background colour (value) of the "main_window_bg variable".

# Set width for columns 0-1 (2 total) in the main window.
main_window.columnconfigure(0, weight=0, minsize=150)
main_window.columnconfigure(1, weight=0, minsize=150)

# Initialise global lists and variables.
quiz_details = []           # Create empty list for user details so that their quiz results can be stored inside.
difficulty_list = ["Easy", "Medium", "Hard"]  # Create a list of the different difficulty levels.

# Run the main function.
main()