# Date Created: 05/05/2025
# Author: Jack Compton
# Purpose: GUI application for Flow Computing that helps students with their mathematics.

# BEFORE USE:
# Windows:  Open Command Prompt and run:
#           pip install customtkinter pillow fpdf2
#
# macOS:    Open Terminal and run:
#           brew install python-tk && pip install customtkinter pillow fpdf2
#
# Linux:    Open Terminal and run:
#           sudo apt install python3-tk && pip install customtkinter pillow fpdf2
#
# Once these packages are installed, the program is ready to use.

from tkinter import *
from tkinter import messagebox
import customtkinter as CTk
from AppData.CTkScrollableDropdown import *
from PIL import Image, ImageTk
from fpdf import FPDF
from fpdf.enums import TableCellFillMode
from fpdf.fonts import FontFace
from datetime import datetime
import json, time, random, os

class PDF(FPDF):
    def __init__(self):
        # Initialise the parent FPDF class and its attributes for page orientation and size.
        super().__init__(orientation="portrait", format="A4")  # "Super()" allows a subclass, in this case "PDF", to inherit methods and attributes from the parent class (superclass) "FPDF".
        self.set_auto_page_break(auto=True, margin=20)  # Automatically add a new page if content overflows.


    def header(self):
        # Add logo on the top left
        self.image("AppData\Images\qw_logo.png", 15, 7, 25)

        # Centered title image
        img_width = 70
        x_center = (self.w - img_width) / 2  # Calculate center x position.
        self.image("AppData\Images\scoreboard_logo.png", x=x_center, y=9, w=img_width)

        # Line break to move below header elements
        self.ln(20)


    def footer(self):
        self.set_y(-15)  # Move 1.5 cm from the bottom.
        self.set_font("helvetica", style="I", size=10)
        self.set_text_color("#75adf7")  # Set text colour to blue.
        # Print current date and time.
        current_datetime = datetime.now().strftime("%d %B %Y, %I:%M %p")  # Get current date and time.
        self.set_x(15)  # Align the left cell with the table's left-side X position, moved right by 15 mm.
        self.cell(0, 10, f"Generated on: {current_datetime}", align="L")  # Print current date and time on the left.
        # Print current page number and total pages.
        self.set_x(-20)  # Align the right cell with the table's right-side X position, moved left by 20 mm.
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="R")  # Print page number on the right. "{nb}" is a placeholder that gets replaced with the total page count by "alias_nb_pages()".


    def scoreboard_table(self, data, headings):
        # Position cursor before starting the table content
        self.set_y(32)
        self.set_font("helvetica", size=10)
        self.set_text_color("#000000")  # Set text colour to black
        self.set_draw_color("#6aa5db")  # Set draw (table border) colour to light blue
        self.set_line_width(0.25)

        # Style for heading row
        heading_style = FontFace(emphasis="BOLD", color=255, fill_color="#87bcf4")

        # Create a styled table using fpdf2's context manager
        with self.table(
            borders_layout="NO_HORIZONTAL_LINES",
            cell_fill_color=(224, 235, 255),  # Alternate cell colour for colour banding.
            cell_fill_mode=TableCellFillMode.ROWS,  # Fill alternate cells for colour banding.
            col_widths=(75, 290, 125, 120, 100, 100),  # Set column widths
            headings_style=heading_style,  # Apply heading style
            line_height=6,  # Set line height
            text_align=("CENTER", "LEFT", "CENTER", "CENTER", "CENTER", "CENTER"),  # Set text alignment for each column
            width=180,  # Set table width
        ) as table:
            # Create header cells
            heading_row = table.row()
            for i, heading in enumerate(headings):
                heading_row.cell(" " + heading if i == 1 else heading)  # Add left-side padding only to the "Username" column

            # Create each row of data from the scoreboard file
            for data_row in data:
                row = table.row()
                for i, datum in enumerate(data_row):
                    row.cell(" " + str(datum) if i == 1 else str(datum))  # Add left-side padding only to the "Username" column



class Tools:
    # Constructor for the "Tools" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Home" class, for example, to be accessed from within the "Tools" class.
    def __init__(self, about_instance, scoreboard_instance, completion_instance, quiz_instance, homepage_instance):
        self.about = about_instance             # Store a reference to the "About" class instance.
        self.scoreboard = scoreboard_instance   # Store a reference to the "Scoreboard" class instance.
        self.completion = completion_instance   # Store a reference to the "Completion" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.
        self.home = homepage_instance           # Store a reference to the "Home" class instance.


    # Method for clearing all widgets or clearing specified widgets (column, row).
    def clear_widget(self, procedure, all_widgets, column, row, command):
        global username, difficulty_num, questions
        
        if command != None: command()  # Go to the specified procedure from passed command if it is specified.
        if all_widgets == True:
            # Clear all page content
            for widget in main_window.winfo_children():
                widget.destroy()
            if procedure != None: procedure()  # Go to the specified procedure from button command if it is specified.
        elif all_widgets == False:
            # Find all widgets in the specified row and column.
            for widget in main_window.grid_slaves(column=column, row=row):
                widget.destroy()  # Destroy the widgets occupying the specified space.


    # Function for loading the "users" list from the JSON file.
    def load_details(self):
            global data_loaded, users

            self.shortened_scoreboard_directory = "AppData/scoreboard.json"                              # Get the intended path of the scoreboard file to be loaded, storing it in "shortened_scoreboard_directory".
            self.full_scoreboard_directory = f"{os.path.dirname(os.path.abspath(__file__))}/AppData"     # Get the absolute intended path of the scoreboard file for debugging purposes when errors and warnings occur, storing it in "full_scoreboard_directory".
            
            # Check if the JSON file exists. If not, create it.
            if not os.path.exists(self.shortened_scoreboard_directory):   
                response1 = messagebox.askyesno("File Not Found", "The scoreboard file cannot be found. Do you want to create a new one?")
                if response1 == True:  # If the user chooses to create a new file, proceed.
                    try:
                        # Create a new JSON file with an empty list.
                        with open(self.shortened_scoreboard_directory, "w") as file:  # Create a new JSON file with an empty list if the file doesn't already exist.
                            json.dump([], file)                     # Write an empty list to the new JSON file.
                        users = []                                  # Make "users" as an empty list.
                        data_loaded = True                          # Set the "data_loaded" variable to True, so that the program doesn't reload data before printing.
                    except IOError as io_error:                     # Error control for instances such as the file being inaccessible or lacking the permission to read/write it.
                        messagebox.showerror("File Error", f"An error occurred while creating the scoreboard file, program will run in temporary storage mode.\n\n{io_error}\n\n{self.full_scoreboard_directory}")  # Show an error message if the file cannot be created.
                        users = []              # Make "users" as an empty list.
                        data_loaded = False     # Set the "data_loaded" variable to False, so that the program will attempt to reload data before printing.
                    return
                else:                           # If the user chooses not to create a new file, run the program in temporary storage mode.
                    messagebox.showwarning("Temporary Storage Mode", f"The program will run in temporary storage mode until the scoreboard file is created or replaced.\n\n{self.full_scoreboard_directory}")  # Show a warning message if the user does not want to create a new file.
                    users = []                  # Make "users" as an empty list.
                    data_loaded = False         # Set the "data_loaded" variable to False, so that the program will attempt to reload data before printing.
                    return
            
            # If the JSON file exists, try to load the data from it, and if the file isn't in JSON format, it will raise a JSONDecodeError. If there are any other errors, such as the file being inaccessible, it will raise an IOError.
            try:
                with open(self.shortened_scoreboard_directory, "r") as file:  # Open the JSON file in read mode ("r").
                    users.clear                             # Clear the list to prevent duplicate entries.
                    data = json.load(file)                  # Load the details from the JSON file into the "users" list.
                    if not isinstance(data, list):          # Check if the loaded data is a list.
                        raise json.JSONDecodeError("Expected a list", doc=str(data), pos=0)  # Raise an error if the loaded data is not a list, simulating a JSON decode error.
                    users = data                            # Assign the loaded data to the "users" list.
                    data_loaded = True                      # Set the "data_loaded" variable to True, so that the program doesn't reload data before printing.
            except json.JSONDecodeError:                    # Error control for instances such as the JSON file having invalid data, having incorrect formatting, or being corrupted.
                response2 = messagebox.askyesno("File Error", "Failed to decode JSON data. The scoreboard file may be corrupted or improperly formatted. Do you want to replace it?")  # Show an error message if the JSON file cannot be decoded, asking the user if they want to replace the file.
                if response2 == True:
                    try:
                        with open(self.shortened_scoreboard_directory, "w") as file:    # Open the shortened_scoreboard_directory file in write mode ("w").
                            json.dump([], file)                                         # Overwrite the JSON file with an empty list.
                        users = []                  # Make "users" as an empty list.
                        data_loaded = True          # Set the "data_loaded" variable to True, so that the program doesn't reload data before printing.
                        messagebox.showinfo("File Replaced", f"The JSON scoreboard file has been successfully replaced with an empty list.\n\n{self.full_scoreboard_directory}")
                    except IOError as io_error:     # Error control for instances such as the file being inaccessible or lacking the permission to read/write it.
                        messagebox.showerror("File Error", f"An error occurred while replacing the scoreboard file, program will run in temporary storage mode.\n\n{io_error}\n\n{self.full_scoreboard_directory}")  # Show an error message if the file cannot be replaced.
                        users = []                  # Make "users" as an empty list.
                        data_loaded = False         # Set the "data_loaded" variable to False, so that the program will attempt to reload data before printing.
                    except Exception as e:          # Error control for any other exceptions that may occur.
                        messagebox.showerror("Unexpected Error", f"An unexpected error occurred while replacing the scoreboard file, program will run in temporary storage mode.\n\n{e}\n\n{self.full_scoreboard_directory}")  # Show an error message if there is an unexpected error.
                        users = []                  # Make "users" as an empty list.
                        data_loaded = False         # Set the "data_loaded" variable to False, so that the program will attempt to reload data before printing.
                    return
                else:
                    users = []              # Make "users" as an empty list.
                    data_loaded = False     # Set the "data_loaded" variable to False, so that the program will attempt to reload data before printing.
                    return
            except IOError as io_error:     # Error control for instances such as the file being inaccessible or lacking the permission to read it.
                messagebox.showwarning("File Error", f"An error occurred while reading the scoreboard file, program will run in temporary storage mode.\n\n{io_error}\n\n{self.full_scoreboard_directory}")  # Show an error message if the file cannot be read.
                users = []                  # Make "users" as an empty list.
                data_loaded = False         # Set the "data_loaded" variable to False, so that the program will attempt to reload data before printing.
            except Exception as e:          # Error control for any other exceptions that may occur.
                messagebox.showerror("Unexpected Error", f"An unexpected error occurred while reading the scoreboard file, program will run in temporary storage mode.\n\n{e}\n\n{self.full_scoreboard_directory}")  # Show an error message if there is an unexpected error.
                users = []                  # Make "users" as an empty list.
                data_loaded = False         # Set the "data_loaded" variable to False, so that the program will attempt to reload data before printing.


    # Method for saving details specific to the specified window.
    def save_details(self, procedure, origin, scenario):
        global ref_number, username, difficulty_num, questions
        if origin == "Home":
            if scenario == "Temporary" or scenario == "Permanent":
                username = self.home.username_entry.get()           # Get the username entry widget value.
                difficulty_num = self.home.difficulty_slider.get()  # Get the difficulty slider value.
                questions = int(self.home.questions_slider.get())   # Get the questions slider value.
            
            if scenario == "Permanent":
                if users != []:  # Check if the "users" list is not empty.
                    existing_ref_numbers = [user[0] for user in users]  # Create a list of existing reference numbers from the "users" list.
                else:
                    existing_ref_numbers = []
                # Check if the maximum number of unique reference numbers has been reached.
                if len(existing_ref_numbers) >= 9000:  # Check if 9000 possible unique 4-digit ref numbers from 1000 to 9999 have been generated.
                    messagebox.showwarning("Maximum Scores Reached", "No more unique reference numbers can be generated.\nPlease delete old user scores to add new ones.")
                    self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go back to the home page.
                    return
                else:
                    while True:
                        ref_number = random.randint(1000, 9999)  # Generate a random number from 1000 to 9999 and put this value into the "ref_number" variable.
                        if ref_number not in existing_ref_numbers:  # Check that the generated reference number doesn't already exist.
                            break
            
            if procedure == "Quiz":
                self.clear_widget(self.quiz.setup_quiz, True, None, None, None)
            elif procedure == "Scoreboard":
                self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)
            else:
                return  # If the procedure is not "Quiz" or "Scoreboard", do nothing and return.

        elif origin == "Completion" or origin == "Scoreboard":
                global data_loaded
                try:
                    with open(self.shortened_scoreboard_directory, "w") as file:   # Open the "scoreboard.json" file in write mode ("w"). If it doesn't exist, a new file will be created.
                        json.dump(users, file, indent=4)    # Dump the entries from the "users" list into the JSON file.
                    data_loaded = False                     # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when printing.
                except IOError as io_error:                 # Error control for instances such as the file being inaccessible or lacking the permission to write to it.
                    messagebox.showerror("File Error", f"Failed to write to 'scoreboard.json'. Check file permissions, disk space, and ensure the file is not in use.\n\n{io_error}\n\n{self.full_scoreboard_directory}")  # Show an error message if the file cannot be written to.
                except Exception as e:                      # Error control for any other exceptions that may occur.
                    messagebox.showerror("Unexpected Error", f"An unexpected error occurred while writing to 'scoreboard.json'.\n\n{e}\n\n{self.full_scoreboard_directory}")  # Show an error message if there is an unexpected error.
    

    # Method for printing details into a PDF.
    def print_details(self, selection):
        self.full_pdf_directory = f"{os.path.dirname(os.path.abspath(__file__))}"  # Get the absolute intended path of the PDF scoreboard file for debugging purposes when errors and warnings occur, storing it in "full_pdf_directory".
        
        if not data_loaded:  # Check if the data has been loaded from the JSON file.
            self.load_details()
        
        if users == []:  # Check if the "users" list is empty.
            response = messagebox.askyesno("No Scores Recorded", "There are no recorded scores to print.\nWould you still like to print out a blank scoreboard table?")
            if response == False:
                return
        
        # Initialise PDF
        pdf = PDF()
        pdf.alias_nb_pages()  # Enable total page count placeholder
        pdf.add_page()        # Start with first page
        data = []

        # Define table headings
        headings = ["Ref #", "Username", "Difficulty", "Questions", "Time", "Score"]

        if selection == "all":
            # Load all data from JSON file
            with open("AppData\scoreboard.json", "r") as file:
                data = json.load(file)  # Load the details from the JSON file into the "data" list.

        # Generate the table on the PDF
        pdf.scoreboard_table(data, headings)

        try:
            # Save the PDF to file
            pdf.output("QWhizz Math Scoreboard.pdf")
            messagebox.showinfo("Print Successful", "The scoreboard has been successfully printed to 'QWhizz Math Scoreboard.pdf'.")
        except IOError as io_error:     # Error control for instances such as the file being inaccessible or lacking the permission to write to it.
            messagebox.showerror("File Error", f"Failed to write to 'QWhizz Math Scoreboard.pdf'. Check file permissions, disk space, and ensure the file is not in use.\n\n{io_error}\n\n{self.full_pdf_directory}")  # Show an error message if the file cannot be written to.
        except Exception as e:          # Error control for any other exceptions that may occur.
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred while writing to 'QWhizz Math Scoreboard.pdf'.\n\n{e}\n\n{self.full_pdf_directory}")  # Show an error message if there is an unexpected error.


    # Method for deleting details from the "users" list.
    def delete_details(self, selection):
        global users
        if users != []:  # Check if the "users" list is not empty.
                if selection == "all":
                    response = messagebox.askyesno("Delete All Scores", "Are you sure that you want to delete all recorded scores?")
                    if response == True:
                        users = []
                        self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)
                        messagebox.showinfo("Scores Deleted", "All recorded scores have been deleted.")
                        self.save_details(None, "Scoreboard", None)
                    else:
                        return
                else:
                    # Enumerate through the user details in the "users" list to find the matching reference number.
                    # "i" represents the index of the current user in the "users" list, and "user" is the current user.
                    for i, user in enumerate(users):
                        if user[0] == selection:            # Check if the reference number stored in the first element "[0]" of each "user" list entry matches the selected reference number.
                            del users[i]                    # If a match is found, delete the user score at index "i" from "users".
                            #if delkey_binded == True:       # If "delkey_binded" variable/flag is True, unbind the "del" key so that it doesn't work when no treeview item is selected.
                                #tree.unbind("<Delete>")
                            #delkey_binded = False           # Set "delkey_binded" variable/flag to False so program won't try to unbind the "del" key if it hasn't been binded already.
                    self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)
        else:
            messagebox.showwarning("No Scores Recorded", "There are no recorded scores to delete.")
            return


    # Method for resetting details specific to the specified window.
    def reset_details(self, origin):
        global username, difficulty, difficulty_num, questions
        if origin == "Completion":
            username = None
            difficulty = None
            difficulty_num = None
            questions = None


    # Method for unbinding specified key events from the main window.
    def unbind_keys(self, keys):
        # Unbind all key events from the main window.
        for key in keys:
            main_window.unbind(key)


    # Method for configuring the timer state (enabled/disabled).
    # Unique identifiers are passed in "origin" to differentiate between the "Quiz" and "Completion" classes to manage their relevant timer labels.
    def timer_config(self, origin, command):
        if origin == "Quiz":
            if command == "Enable":
                self.quiz.timer_lbl.configure(text=f"Time: {self.quiz.time_string}")
            if command == "Disable":
                self.quiz.timer_lbl.configure(text="Timer Disabled")
        if origin == "Completion":
            if command == "Enable":
                self.completion.total_time_lbl.configure(text=f"Total Time: {self.quiz.total_time}")
            if command == "Disable":
                self.completion.total_time_lbl.configure(text="Timer Disabled")



class About:
    # Contstructor for the "About" class, which sets up the full window for the "About" page.
    def __init__(self, tools_instance, scoreboard_instance, completion_instance, quiz_instance, homepage_instance):  
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.scoreboard = scoreboard_instance   # Store a reference to the "Scoreboard" class instance.
        self.completion = completion_instance   # Store a reference to the "Completion" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.
        self.home = homepage_instance           # Store a reference to the "Home" class instance.


    def setup_about(self, origin):
        # Disable the main window to prevent interaction with it while the about window is open.
        main_window.attributes("-disabled", True)
        self.unpause_quiz = False  # Set the flag to indicate that the quiz should not be unpaused when the "About" window is closed.
        if origin == "Quiz" and quiz_paused == False: 
            self.quiz.pause_quiz()  # Pause the quiz if the "About" window is opened from the "Quiz" window.
            self.unpause_quiz = True  # Set the flag to indicate that the quiz should be unpaused when the "About" window is closed.
        
        # Create a top-level window (separate from the main window).
        self.about_window = Toplevel(main_window, bg=main_window_bg)
        self.about_window.title("About")
        self.about_window.columnconfigure(0, weight=0, minsize=300)
        self.about_window.resizable(False, False)
        self.about_window.update_idletasks()  # Process any pending events for the window before calculating the centre position later.
        
        # Centre the "About" window above the main window.
        x = main_window.winfo_x() + main_window.winfo_width() // 2 - self.about_window.winfo_width() // 2 - 60
        y = main_window.winfo_y() + main_window.winfo_height() // 2 - self.about_window.winfo_height() // 2 + 56
        self.about_window.geometry(f"+{x}+{y}")
        
        self.about_window.transient(main_window)  # Keep on top of parent window (main_window)
        self.about_window.lift()
        self.about_window.focus()

        # Create a frame inside the "About" window to hold the "about" details label.
        self.about_frame = CTk.CTkFrame(self.about_window, fg_color=frame_fg)
        self.about_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky=EW)
        self.about_frame.columnconfigure(0, weight=0, minsize=300)
        
        # Add program details and a close button.
        CTk.CTkLabel(self.about_frame, text="QWhizz Math\nVersion 1.3.1\nMade by Jack Compton", font=(default_font, 14, "bold"), text_color=font_colour, justify="center").grid(row=0, column=0, sticky=EW, padx=10, pady=(20))
        CTk.CTkButton(self.about_window, text="Close", command=lambda: self.close(), font=(default_font, 14, "bold"), height=30, fg_color=button_fg, hover_color=button_hover).grid(row=1, column=0, sticky=EW, padx=10, pady=(5,10))

        # Override the window close (X) button behavior so that the main window is enabled again when the about window is closed using this button.
        self.about_window.protocol("WM_DELETE_WINDOW", lambda: self.close())

        # Bind the "esc" key to the "close" function so that the window can be closed by pressing "esc".
        self.about_window.bind("<Escape>", lambda e: self.close())  # Prevent an argument error by using "e" after "lambda" to accept (but ignore) the event passed by bind, keeping close() parameterless.


    def close(self):  # Add "event" parameter to allow for "event" to be passed when the binded "esc" key is pressed (though the bind doesn't include an event).
        self.about_window.unbind("<Escape>")  # Unbind the "esc" key from the "close" function so that "esc" can be used for other purposes later.
        main_window.attributes("-disabled", False)  # Re-enable the main window so that it can be interacted.
        if self.unpause_quiz == True:
            self.quiz.unpause_quiz()    # Unpause the quiz if the "About" window was opened from the "Quiz" window and the quiz was previously running (not paused).
        self.unpause_quiz = False   # Reset the flag to indicate that the quiz should not be unpaused when the "About" window is closed.
        self.about_window.destroy()



class Scoreboard:
    # Constructor for the "Scoreboard" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Home" class, for example, to be accessed from within the "Scoreboard" class.
    def __init__(self, tools_instance, about_instance, completion_instance, quiz_instance, homepage_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.about = about_instance             # Store a reference to the "About" class instance.
        self.completion = completion_instance   # Store a reference to the "Completion" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.
        self.home = homepage_instance           # Store a reference to the "Home" class instance.
        self.selected_scores = None


    def setup_scoreboard(self):
        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        main_window.columnconfigure(0, weight=1, minsize=850)
        main_window.columnconfigure(1, weight=1, minsize=0)

        # Set up the menu bar.
        scoreboard_menubar = Menu(main_window)  # Create a new menu bar.

        file_menu = Menu(scoreboard_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        scoreboard_menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Print Selected", accelerator="Ctrl+P")
        file_menu.add_command(label="Print All", accelerator="Ctrl+Shift+P", command=lambda: self.tools.print_details("all"))
        file_menu.add_command(label="Delete Selected", accelerator="Del")
        file_menu.add_command(label="Delete All", accelerator="Shift+Del", command=lambda: self.tools.delete_details("all", "Scoreboard"))

        settings_menu = Menu(scoreboard_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        scoreboard_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(scoreboard_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, value=True)
        timer_settings.add_radiobutton(label="Disabled", variable=timer, value=False)

        help_menu = Menu(scoreboard_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        scoreboard_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Scoreboard"))

        main_window.config(menu=scoreboard_menubar)

        # Bind key shortcuts to perform actions.
        main_window.bind("<Control-Shift-P>", lambda e: self.tools.print_details("all"))
        main_window.bind("<Shift-Delete>", lambda e: self.tools.delete_details("all"))
        self.binded_keys = ["<Control-Shift-P>", "<Shift-Delete>"]
        
        # Set up a content frame to place the main scoreboard top elements inside.
        top_frame1 = CTk.CTkFrame(main_window, fg_color="transparent")
        top_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,5))

        # Set width for columns 0-2 (3 total) in top frame 1. Total minimum column width is 810px.
        top_frame1.columnconfigure(0, weight=0, minsize=400)
        top_frame1.columnconfigure(1, weight=0, minsize=205)
        top_frame1.columnconfigure(2, weight=0, minsize=205)

        # Logo creation
        total_height = 70  # Height for the canvas and vertical centre position is calculated by the height of two buttons + 10px padding.
        self.logo_canvas = Canvas(top_frame1, bg=main_window_bg, bd=0, highlightthickness=0, width=400, height=total_height)  # Create a canvas for the banner image.
        self.logo_canvas.grid(column=0, row=0, rowspan=2, sticky=EW)
        self.logo = Image.open("AppData/Images/logo_small.png")
        self.logo = ImageTk.PhotoImage(self.logo)
        self.logo_canvas.create_image(0, total_height / 2, anchor=W, image=self.logo)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        self.logo_canvas.image = self.logo

        # Create the buttons.
        CTk.CTkButton(top_frame1, text="Delete", font=(default_font, 14, "bold"), text_color=font_colour,
                      width=200, height=30, corner_radius=10, fg_color=button_fg, hover_color=button_hover).grid(column=1, row=0, sticky=EW, padx=(0,5), pady=(0,5))
        CTk.CTkButton(top_frame1, text="Home", font=(default_font, 14, "bold"), text_color=font_colour, command=lambda: self.tools.clear_widget(self.home.setup_homepage, True, None, None, self.tools.unbind_keys(self.binded_keys)),
                      width=200, height=30, corner_radius=10, fg_color=button_fg, hover_color=button_hover).grid(column=2, row=0, sticky=EW, padx=(5,0), pady=(0,5))
        CTk.CTkButton(top_frame1, text="View Answers", font=(default_font, 14, "bold"), text_color=font_colour,
                      width=200, height=30, corner_radius=10, fg_color=button_fg, hover_color=button_hover).grid(column=1, row=1, sticky=EW, padx=(0,5), pady=(5,0))
        CTk.CTkButton(top_frame1, text="Retry Quiz", font=(default_font, 14, "bold"), text_color=font_colour,
                      width=200, height=30, corner_radius=10, fg_color=button_fg, hover_color=button_hover).grid(column=2, row=1, sticky=EW, padx=(5,0), pady=(5,0))

        # Set up a content frame to place the scores inside.
        content_frame1 = CTk.CTkFrame(main_window, fg_color=frame_fg, corner_radius=10)
        content_frame1.grid(column=0, row=1, sticky=EW, padx=20, pady=(5,20))

        # Set width for columns 0-5 (6 total) in content frame 1. Total minimum column width is 810px.
        content_frame1.columnconfigure(0, weight=1, minsize=75)
        content_frame1.columnconfigure(1, weight=1, minsize=290)
        content_frame1.columnconfigure(2, weight=1, minsize=125)
        content_frame1.columnconfigure(3, weight=1, minsize=120)
        content_frame1.columnconfigure(4, weight=1, minsize=100)
        content_frame1.columnconfigure(5, weight=1, minsize=100)

        # Clear previous entries
        for widget in content_frame1.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:  # Checks if the widget is in a row larger than 0, which is where user details are displayed.
                widget.grid_forget()                # Remove the widget from the grid by forgetting it

        # Create the column headings
        CTk.CTkLabel(content_frame1, font=(default_font, 14, "bold"), text_color=font_colour, text="Ref #").grid(column=0, row=0, sticky=EW, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=(default_font, 14, "bold"), text_color=font_colour, text="Username").grid(column=1, row=0, sticky=W, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=(default_font, 14, "bold"), text_color=font_colour, text="Difficulty").grid(column=2, row=0, sticky=EW, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=(default_font, 14, "bold"), text_color=font_colour, text="Questions").grid(column=3, row=0, sticky=EW, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=(default_font, 14, "bold"), text_color=font_colour, text="Time").grid(column=4, row=0, sticky=EW, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=(default_font, 14, "bold"), text_color=font_colour, text="Score").grid(column=5, row=0, sticky=EW, padx=5, pady=5)
        
        # Add each item in the list into its own row
        for index, details in enumerate(users):
            list_row = index + 1
            CTk.CTkLabel(content_frame1, font=(default_font, 13), text_color=font_colour, text=details[0]).grid(column=0, row=list_row, sticky=EW, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=(default_font, 13), text_color=font_colour, text=details[1]).grid(column=1, row=list_row, sticky=W, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=(default_font, 13), text_color=font_colour, text=details[2]).grid(column=2, row=list_row, sticky=EW, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=(default_font, 13), text_color=font_colour, text=details[3]).grid(column=3, row=list_row, sticky=EW, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=(default_font, 13), text_color=font_colour, text=details[4]).grid(column=4, row=list_row, sticky=EW, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=(default_font, 13), text_color=font_colour, text=details[5]).grid(column=5, row=list_row, sticky=EW, padx=5, pady=5)



class Completion:
    # Constructor for the "Completion" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Home" class, for example, to be accessed from within the "Completion" class.
    def __init__(self, tools_instance, about_instance, scoreboard_instance, quiz_instance, homepage_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.about = about_instance             # Store a reference to the "About" class instance.
        self.scoreboard = scoreboard_instance   # Store a reference to the "Scoreboard" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.
        self.home = homepage_instance           # Store a reference to the "Home" class instance.


    # Method for submitting the quiz details to the "users" list and saving them to the JSON file (saving is done in the "save_details" method within the "Tools" class).
    def submit_details(self):
        global ref_number, username, difficulty, difficulty_num, questions, users
        
        self.quiz.final_score = f"{self.quiz.score}/{questions}"
        if timer.get() == True:
            self.time = self.quiz.total_time
        else:
            self.time = "Disabled"
        users.append([ref_number, username, difficulty, questions, self.time, self.quiz.final_score])  # Add the next user and their quiz details to the "users" list.
        self.tools.save_details(None, "Completion", None)  # Save the details to the JSON file.
        self.setup_completion()


    def setup_completion(self):
        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        main_window.columnconfigure(0, weight=1, minsize=0)
        main_window.columnconfigure(1, weight=1, minsize=450)

        # Set up the menu bar.
        completion_menubar = Menu(main_window)  # Create a new menu bar.

        settings_menu = Menu(completion_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        completion_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(completion_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, command=lambda: self.tools.timer_config("Completion", "Enable"), value=True)
        timer_settings.add_radiobutton(label="Disabled", variable=timer, command=lambda: self.tools.timer_config("Completion", "Disable"), value=False)

        help_menu = Menu(completion_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        completion_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Completion"))

        main_window.config(menu=completion_menubar)

        # Banner creation (left side)
        lbanner_canvas = Canvas(main_window, bg=main_window_bg, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        lbanner_canvas.grid(column=0, row=0, sticky=EW, padx=(10, 0))
        lbanner = Image.open("AppData/Images/lbanner.png")
        lbanner = ImageTk.PhotoImage(lbanner)
        lbanner_canvas.configure(width=lbanner.width()+2, height=lbanner.height())  # Add 2 pixels to width to prevent image clipping on the right of image.
        lbanner_canvas.create_image(lbanner.width() / 2, lbanner.height() / 2, anchor=CENTER, image=lbanner)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        lbanner_canvas.image = lbanner

        # Banner creation (right side)
        rbanner_canvas = Canvas(main_window, bg=main_window_bg, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        rbanner_canvas.grid(column=2, row=0, sticky=EW, padx=(0, 10))
        rbanner = Image.open("AppData/Images/rbanner.png")
        rbanner = ImageTk.PhotoImage(rbanner)
        rbanner_canvas.configure(width=rbanner.width()+2, height=rbanner.height())  # Add 2 pixels to width to prevent image clipping on the left of image.
        rbanner_canvas.create_image(rbanner.width() / 2, rbanner.height() / 2, anchor=CENTER, image=rbanner)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        rbanner_canvas.image = rbanner

        # Set up the main content frame to place the main completion frames and elements inside.
        self.main_content_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.main_content_frame.grid(column=1, row=0, sticky=EW, padx=35, pady=(0,20))

        # Logo creation
        self.logo_canvas = Canvas(self.main_content_frame, bg=main_window_bg, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        self.logo_canvas.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,0))
        self.logo = Image.open("AppData/Images/logo.png")
        self.logo = ImageTk.PhotoImage(self.logo)
        self.logo_canvas.configure(width=410, height=self.logo.height()+5)  # Add 5 pixels to height to prevent image clipping on the bottom of image.
        self.logo_canvas.create_image(410 / 2, self.logo.height() / 2, anchor=CENTER, image=self.logo)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        self.logo_canvas.image = self.logo

        # Set up a content frame to place the main completion elements inside.
        completion_frame1 = CTk.CTkFrame(self.main_content_frame, fg_color=frame_fg, corner_radius=10)
        completion_frame1.grid(column=0, row=1, sticky=EW, padx=20, pady=(20,5))

        # Set width for column 0 (1 total) in completion frame 1. Total minimum column width is 410px.
        completion_frame1.columnconfigure(0, weight=1, minsize=410)

        # Create the labels to be placed next to their relevant entry boxes.
        CTk.CTkLabel(completion_frame1, text="Quiz Complete!", font=(default_font, 18, "bold"), text_color=font_colour).grid(column=0, row=0, sticky=EW, padx=5, pady=(20,8))
        CTk.CTkLabel(completion_frame1, text=f"You scored a total of: {self.quiz.score}/{questions}", font=(default_font, 15), text_color=font_colour).grid(column=0, row=1, sticky=EW, padx=5)
        CTk.CTkLabel(completion_frame1, text=f"Difficulty: {difficulty}", font=(default_font, 15), text_color=font_colour).grid(column=0, row=2, sticky=EW, padx=5)
        self.total_time_lbl = CTk.CTkLabel(completion_frame1, text="", font=(default_font, 15), text_color=font_colour)  # Make an empty label for the timer until the state of the timer is determined (enabled/disabled).
        self.total_time_lbl.grid(column=0, row=3, sticky=EW, padx=5, pady=(0,20))
        if timer.get() == True:
            self.tools.timer_config("Completion", "Enable")
        if timer.get() == False:
            self.tools.timer_config("Completion", "Disable")

        # Create a frame to place the buttons inside.
        button_frame = CTk.CTkFrame(self.main_content_frame, fg_color="transparent")
        button_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=(5,0))
        
        # Set width for columns 0-1 (2 total) in the answer frame. Total minimum column width is 410px.
        button_frame.columnconfigure(0, weight=1, minsize=205)
        button_frame.columnconfigure(1, weight=1, minsize=205)

        # Create the buttons.
        CTk.CTkButton(button_frame, text="View Answers",
                      width=200, height=30, corner_radius=10, fg_color=button_fg, hover_color=button_hover, font=(default_font, 14, "bold"), text_color=font_colour).grid(column=0, row=0, sticky=EW, padx=(0,5), pady=(0,5))
        CTk.CTkButton(button_frame, text="Retry Quiz",
                      width=200, height=30, corner_radius=10, fg_color=button_fg, hover_color=button_hover, font=(default_font, 14, "bold"), text_color=font_colour).grid(column=1, row=0, sticky=EW, padx=(5,0), pady=(0,5))
        CTk.CTkButton(button_frame, text="Scoreboard", command=lambda: self.quiz.reset_timer("Scoreboard", "Completion"),
                      width=200, height=30, corner_radius=10, fg_color=button_fg, hover_color=button_hover, font=(default_font, 14, "bold"), text_color=font_colour).grid(column=0, row=1, sticky=EW, padx=(0,5), pady=(5,0))
        CTk.CTkButton(button_frame, text="Home", command=lambda: self.quiz.reset_timer("Home", "Completion"),
                      width=200, height=30, corner_radius=10, fg_color=button_fg, hover_color=button_hover, font=(default_font, 14, "bold"), text_color=font_colour).grid(column=1, row=1, sticky=EW, padx=(5,0), pady=(5,0))



class Quiz:
    # Constructor for the "Quiz" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Home" class, for example, to be accessed from within the "Quiz" class.
    def __init__(self, tools_instance, about_instance, scoreboard_instance, completion_instance, homepage_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.about = about_instance             # Store a reference to the "About" class instance.
        self.scoreboard = scoreboard_instance   # Store a reference to the "Scoreboard" class instance.
        self.completion = completion_instance   # Store a reference to the "Completion" class instance.
        self.home = homepage_instance           # Store a reference to the "Home" class instance.
        self.question_no = 1                    # Variable for keeping track of which question the user is on, with the default value being 1.
        self.timer_active = False               # Variable to store the state of the timer, defaulting to False (off).
        self.elapsed_time = 0                   # Variable to store the elapsed time, defaulting to 0.
        self.calculated_elapsed_time = 0        # Variable to store the calculated elapsed time, defaulting to 0.
        self.quiz_start_time = None             # Variable to store the start time of the quiz, defaulting to None.
        self.pause_start_time = None            # Variable to store the start time of the quiz pause, defaulting to None.
        self.total_paused_time = 0              # Variable to store the total paused time, defaulting to 0.
        self.time_string = "00:00:00"           # Variable to store the formatted time string, defaulting to "00:00:00".
        self.total_time = "00:00:00"            # Variable to store the formatted total time, defaulting to "00:00:00".
        self.user_answers = []                  # Inalise a list to store the user's answers, defaulting to an empty list.
        self.correct_answers = []               # Inalise a list to store the predefined correct answers, defaulting to an empty list.
        self.final_score = "0/0"     # Variable to store the final score, defaulting to "0/0".
        self.score = 0                          # Variable to store the active score during the quiz, defaulting to 0.


    def start_timer(self):
        self.timer_active = True
        # Only set the quiz start time on the first run of the timer loop (not after unpausing)
        if self.quiz_start_time == None:
            self.quiz_start_time = time.time()  # Record the current time as quiz start time.
        self.timer_loop()  # Start the timer update loop.


    def stop_timer(self, command, origin):
        self.timer_active = False
        # Cancel the "after" job if it is currently still running.
        if hasattr(self, "timer_job") and self.timer_job != None:
            self.timer_lbl.after_cancel(self.timer_job)
            self.timer_job = None
        
        if origin == "Quiz":
            self.tools.unbind_keys(self.binded_keys)

        if command == "Home":
            self.reset_timer(command, origin)
        elif command == "Quiz":
            self.reset_timer(command, origin)


    def reset_timer(self, command, origin):
        self.quiz_start_time = None
        self.pause_start_time = None
        self.total_paused_time = 0        
        self.elapsed_time = 0
        self.calculated_elapsed_time = 0
        self.time_string = "00:00:00"
        self.total_time = "00:00:00"

        if command == "Home" or command == "Scoreboard":
            self.user_answers.clear()
            if origin == "Completion": self.tools.reset_details(origin)  # If the origin is from the completion page, reset the user details so that the home page doesn't remember the previous details.
            self.question_no = 1
            self.score = 0
            if command == "Home":
                self.tools.clear_widget(self.home.setup_homepage, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the home page.
            elif command == "Scoreboard":
                self.tools.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the scoreboard page.
        elif command == "Quiz":
            self.tools.clear_widget(self.setup_quiz, True, None, None, None)


    def pause_quiz(self):
        global quiz_paused
        quiz_paused = True  # Set the flag to indicate that the quiz is paused.
        self.stop_timer(None, None)
        self.pause_start_time = time.time()  # Record the real-world time for when the pause started.
        self.pause_btn.configure(command=self.unpause_quiz)
        
        # Create a pause overlay to visually block the quiz content until the quiz is unpaused.
        height = self.question_frame.winfo_height() + self.answer_frame.winfo_height() + 10  # Get the total height of both frames (question and answer frames), including the height of padding.
        self.pause_frame = CTk.CTkFrame(self.main_content_frame, fg_color=frame_fg, corner_radius=10)
        self.pause_frame.grid(column=0, row=1, rowspan=2, sticky=EW, padx=20, pady=(5,0))
        
        # Set width for column 0 (1 total) and row 0 (1 total) in the pause frame.
        self.pause_frame.columnconfigure(0, weight=0, minsize=410)
        self.pause_frame.rowconfigure(0, weight=0, minsize=height)

        CTk.CTkLabel(self.pause_frame, text="Quiz Paused", font=(default_font, 20, "bold"), text_color=font_colour).grid(column=0, row=0, columnspan=2, sticky=EW)
        

    def unpause_quiz(self):
        global quiz_paused
        if self.pause_start_time != None:
            # Calculate how long the pause lasted and add it to the total paused duration.
            pause_duration = time.time() - self.pause_start_time
            self.total_paused_time += pause_duration
            self.pause_start_time = None  # Reset the pause start time tracker to be used again for the next pause.
        
        # Remove the pause overlay and restore the pause button to its original command, then start the timer again.
        self.pause_frame.destroy()
        quiz_paused = False  # Set the flag to indicate that the quiz is unpaused.
        self.pause_btn.configure(command=self.pause_quiz)
        self.start_timer()


    # Method for updating the elapsed time every second.
    # This method is called by the "after" job scheduled in the "timer_loop" method.
    def update_timer(self):
        self.elapsed_time += 1
        self.timer_loop()        


    # Method for running the timer loop, which updates the timer every second.
    # This method is called by the "start_timer" method to initiate the timer loop.
    def timer_loop(self):
        if self.timer_active == True:
            current_time = time.time()  # Get the current real-world time in seconds.
            
            # Calculate how long the quiz has been running in total and subtract all time spent paused.
            self.calculated_elapsed_time = int(current_time - self.quiz_start_time - self.total_paused_time)
            self.elapsed_time = self.calculated_elapsed_time

            # Format the total seconds into HH:MM:SS format
            # Divide total seconds by 3600 (as there are 3600 seconds in an hour) to get the number of full hours.
            hours = self.calculated_elapsed_time // 3600  # Floor division (//) divides and rounds down to the nearest whole number.
            
            # Modulo (%) by 3600 to remove full hours and get the remaining seconds.
            # Then divide the remaining seconds by 60 to get minutes as a whole number.
            minutes = (self.calculated_elapsed_time % 3600) // 60  # Modulo (%) divides and gives the remainder after division, then floor division (//) gives the full minutes.
            
            # Modulo (%) by 60 (as there are 60 seconds in a minute) to remove the full minutes and get the remaining seconds.
            seconds = self.calculated_elapsed_time % 60
            
            # Format the time as HH:MM:SS, padding with zeros instead of spaces (":0"), and with a minimum of 2 digits ("2") for each part.
            self.time_string = f"{hours:02}:{minutes:02}:{seconds:02}"  
            self.total_time = self.time_string

            # Update the label
            if timer.get() == True:
                self.timer_lbl.configure(text=f"Time: {self.time_string}")

            # Schedule the next increment and update after 1 second (1000 milliseconds).
            self.timer_job = self.timer_lbl.after(1000, self.update_timer)


    # Method for managing the user's answer to the current question.
    def answer_management(self, answer):
        self.user_answers.append(answer)  # Append the user's answer to the list of all their answers.
        
        answer_index = len(self.user_answers) - 1  # Get the index of the most recent answer in the list, using "len()" to get the total number of items in the list.
        if self.user_answers[answer_index] == self.correct_answers[answer_index]:  # Check if the most recent answer matches the correct answer for the current question.
            self.score += 1
                
        if self.question_no < questions:
            self.question_no += 1
            self.question_no_lbl.configure(text=f"Question {self.question_no}/{questions}")  # Update the question number label.
        else:
            self.stop_timer(None, "Quiz")
            self.tools.clear_widget(self.completion.submit_details, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the completion page.


    # Procedure for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
    def setup_quiz(self):
        global quiz_paused
        quiz_paused = False  # Set the flag to indicate that the quiz is not paused.

        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        main_window.columnconfigure(0, weight=1, minsize=0)
        main_window.columnconfigure(1, weight=1, minsize=450)

        # Set up the menu bar.
        quiz_menubar = Menu(main_window)  # Create a new menu bar.
        
        quiz_menu = Menu(quiz_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        quiz_menubar.add_cascade(label="Quiz", menu=quiz_menu)
        quiz_menu.add_command(label="Restart Quiz", accelerator="Ctrl+R")
        quiz_menu.add_command(label="New Quiz", accelerator="Ctrl+N", command=lambda: self.stop_timer("Quiz", "Quiz"))
        quiz_menu.add_command(label="Exit Quiz", accelerator="Esc", command=lambda: self.stop_timer("Home", "Quiz"))

        settings_menu = Menu(quiz_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        quiz_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(quiz_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, command=lambda: self.tools.timer_config("Quiz", "Enable"), value=True)        # Use lambda so that the method is called only when the radiobutton is clicked, rather than when it's defined.
        timer_settings.add_radiobutton(label="Disabled", variable=timer, command=lambda: self.tools.timer_config("Quiz", "Disable"), value=False)     # Use lambda so that the method is called only when the radiobutton is clicked, rather than when it's defined.

        help_menu = Menu(quiz_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        quiz_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Quiz"))

        main_window.config(menu=quiz_menubar)

        #main_window.bind("<Control-r>")
        main_window.bind("<Control-n>", lambda e: self.stop_timer("Quiz", "Quiz"))
        main_window.bind("<Escape>", lambda e: self.stop_timer("Home", "Quiz"))
        self.binded_keys = ["<Control-n>", "<Escape>"]

        # Banner creation (left side)
        lbanner_canvas = Canvas(main_window, bg=main_window_bg, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        lbanner_canvas.grid(column=0, row=0, sticky=EW, padx=(10, 0))
        lbanner = Image.open("AppData/Images/lbanner.png")
        lbanner = ImageTk.PhotoImage(lbanner)
        lbanner_canvas.configure(width=lbanner.width()+2, height=lbanner.height())  # Add 2 pixels to width to prevent image clipping on the right of image.
        lbanner_canvas.create_image(lbanner.width() / 2, lbanner.height() / 2, anchor=CENTER, image=lbanner)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        lbanner_canvas.image = lbanner

        # Banner creation (right side)
        rbanner_canvas = Canvas(main_window, bg=main_window_bg, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        rbanner_canvas.grid(column=2, row=0, sticky=EW, padx=(0, 10))
        rbanner = Image.open("AppData/Images/rbanner.png")
        rbanner = ImageTk.PhotoImage(rbanner)
        rbanner_canvas.configure(width=rbanner.width()+2, height=rbanner.height())  # Add 2 pixels to width to prevent image clipping on the left of image.
        rbanner_canvas.create_image(rbanner.width() / 2, rbanner.height() / 2, anchor=CENTER, image=rbanner)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        rbanner_canvas.image = rbanner

        # Set up the main content frame to place the main quiz frames and elements inside.
        self.main_content_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.main_content_frame.grid(column=1, row=0, sticky=EW, padx=35, pady=(24,25))

        # Set up a content frame to place the top quiz elements inside.
        quiz_dtls_frame1 = CTk.CTkFrame(self.main_content_frame, fg_color=frame_fg, corner_radius=10)
        quiz_dtls_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(0,5))
        
        # Set width for columns 0-2 (3 total) in quiz details frame 1. Total minimum column width is 410px.
        quiz_dtls_frame1.columnconfigure(0, weight=0, minsize=190)
        quiz_dtls_frame1.columnconfigure(1, weight=0, minsize=30)
        quiz_dtls_frame1.columnconfigure(2, weight=0, minsize=190)

        # Create the labels and pause button to be placed at the top of the quiz page.
        self.question_no_lbl = CTk.CTkLabel(quiz_dtls_frame1, text=f"Question: {self.question_no}/{questions}", font=(default_font, 14, "bold"), text_color=font_colour)
        self.question_no_lbl.grid(column=0, row=0, pady=10, sticky=NSEW)
        self.pause_btn = CTk.CTkButton(quiz_dtls_frame1, text="P", font=(default_font, 14, "bold"), text_color=font_colour, command=self.pause_quiz, width=30, height=30, corner_radius=7.5,  fg_color=button_fg, hover_color=button_hover)
        self.pause_btn.grid(column=1, row=0, pady=10)
        self.timer_lbl = CTk.CTkLabel(quiz_dtls_frame1, text="", font=(default_font, 14, "bold"), text_color=font_colour)  # Make an empty label for the timer until the state of the timer is determined (enabled/disabled).
        self.timer_lbl.grid(column=2, row=0, pady=10, sticky=NSEW)
        if timer.get() == True:
            self.tools.timer_config("Quiz", "Enable")
        elif timer.get() == False:
            self.tools.timer_config("Quiz", "Disable")

        # Create a frame for the question label or question image.
        self.question_frame = CTk.CTkFrame(self.main_content_frame, fg_color=frame_fg, corner_radius=10)
        self.question_frame.grid(column=0, row=1, sticky=EW, padx=20, pady=5)
        
        # Set width for column 0 (1 total) and row 0 (1 total) in quiz details frame 1.
        self.question_frame.columnconfigure(0, weight=0, minsize=410)
        self.question_frame.rowconfigure(0, weight=0, minsize=205)

        # Create a canvas for the question image.
        #question_canvas = CTk.CTkCanvas(question_frame, bd=0, highlightthickness=0)
        #question_canvas.grid(row=0, column=0, pady=10)
        
        # Create a label for the question text.
        question_lbl = CTk.CTkLabel(self.question_frame, text="It's looking a little empty...", font=(default_font, 20, "bold"), text_color=font_colour)
        question_lbl.grid(column=0, row=0)

        # Create a frame for the answer buttons
        self.answer_frame = CTk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.answer_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=(5,0))
        
        # Set width for columns 0-1 (2 total) in the answer frame. Total minimum column width is 410px.
        self.answer_frame.columnconfigure(0, weight=0, minsize=205)
        self.answer_frame.columnconfigure(1, weight=0, minsize=205)
        
        # Create the answer values.
        answer_1 = "Yes"
        answer_2 = "No"
        answer_3 = "No"
        answer_4 = "No"
        
        # Potential code for generating random answers.
        #for i in range(questions):
            #self.correct_answers = random.randint(1,10)
            #correct_btn = random.randint(1,4)
            #if correct_btn == 1:
                #self.correct_answers[i] = "A"
            #elif correct_btn == 2:
                #self.correct_answers[i] = "B"
            #elif correct_btn == 3:
                #self.correct_answers[i] = "C"
            #elif correct_btn == 4:
                #self.correct_answers[i] = "D"
            
        self.correct_answers = ["A"] * questions

        # Create the answer buttons.
        btn_1 = CTk.CTkButton(self.answer_frame, text=f" A.    {answer_1}", font=(default_font, 16, "bold"), text_color=font_colour, command=lambda: self.answer_management("A"), anchor=W, width=200, height=40, corner_radius=10, fg_color=button_fg, hover_color=button_hover)
        btn_1.grid(column=0, row=0, padx=(0, 5), pady=(0,5))
        btn_2 = CTk.CTkButton(self.answer_frame, text=f" B.    {answer_2}", font=(default_font, 16, "bold"), text_color=font_colour, command=lambda: self.answer_management("B"), anchor=W, width=200, height=40, corner_radius=10, fg_color=button_fg, hover_color=button_hover)
        btn_2.grid(column=1, row=0, padx=(5, 0), pady=(0,5))
        btn_3 = CTk.CTkButton(self.answer_frame, text=f" C.    {answer_3}", font=(default_font, 16, "bold"), text_color=font_colour, command=lambda: self.answer_management("C"), anchor=W, width=200, height=40, corner_radius=10, fg_color=button_fg, hover_color=button_hover)
        btn_3.grid(column=0, row=1, padx=(0, 5), pady=(5,0))
        btn_4 = CTk.CTkButton(self.answer_frame, text=f" D.    {answer_4}", font=(default_font, 16, "bold"), text_color=font_colour, command=lambda: self.answer_management("D"), anchor=W, width=200, height=40, corner_radius=10, fg_color=button_fg, hover_color=button_hover)
        btn_4.grid(column=1, row=1, padx=(5, 0), pady=(5,0))

        self.start_timer()



class Home:
    # Constructor for the "Home" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Quiz" class, for example, to be accessed from within the "Home" class.
    def __init__(self, tools_instance, about_instance, scoreboard_instance, completion_instance, quiz_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.about = about_instance             # Store a reference to the "About" class instance.
        self.scoreboard = scoreboard_instance   # Store a reference to the "Scoreboard" class instance.
        self.completion = completion_instance   # Store a reference to the "Completion" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.


    # Procedure for updating the difficulty and question number labels based on the interpreted slider values.
    def slider_value_update(self, slider_id, value):
        global difficulty
        if slider_id == "S1":
            if value == 0:
                difficulty = "Easy"
                color = "#9cffb1"
                hover_color = "#8bd894"
            elif value == 1:
                difficulty = "Medium"
                color = "#ffdf9f"
                hover_color = "#d8ba8b"
            else:
                difficulty = "Hard"
                color = "#f37272"
                hover_color = "#d36565"
            self.difficulty_lbl.configure(text=difficulty)
            self.difficulty_slider.configure(button_color=color, progress_color=color, button_hover_color=hover_color)
        if slider_id == "S2":
            self.question_amnt_lbl.configure(text=f"{int(value)} Questions")


    # Method to insert the chosen option from the autocomplete
    def insert_method(self, e):
        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, e)


    # Procedure for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
    def setup_homepage(self):
        global users

        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        # Setting the main window size before element creation ensures the window doesn't glitch between sizes.
        main_window.columnconfigure(0, weight=1, minsize=0)
        main_window.columnconfigure(1, weight=1, minsize=450)
        main_window.columnconfigure(2, weight=1, minsize=0)

        # Set up the menu bar.
        home_menubar = Menu(main_window)

        settings_menu = Menu(home_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        home_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(home_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, value=True)
        timer_settings.add_radiobutton(label="Disabled", variable=timer, value=False)

        help_menu = Menu(home_menubar, tearoff=0, activebackground=menu_hover, activeforeground=menu_active_fg)
        home_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Home"))

        main_window.config(menu=home_menubar)

        # Banner creation (left side)
        lbanner_canvas = Canvas(main_window, bg=main_window_bg, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        lbanner_canvas.grid(column=0, row=0, sticky=EW, padx=(10, 0), pady=27)
        lbanner = Image.open("AppData/Images/lbanner.png")
        lbanner = ImageTk.PhotoImage(lbanner)
        lbanner_canvas.configure(width=lbanner.width()+2, height=lbanner.height())  # Add 2 pixels to width to prevent image clipping on the right of image.
        lbanner_canvas.create_image(lbanner.width() / 2, lbanner.height() / 2, anchor=CENTER, image=lbanner)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        lbanner_canvas.image = lbanner

        # Banner creation (right side)
        rbanner_canvas = Canvas(main_window, bg=main_window_bg, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        rbanner_canvas.grid(column=2, row=0, sticky=EW, padx=(0, 10), pady=27)
        rbanner = Image.open("AppData/Images/rbanner.png")
        rbanner = ImageTk.PhotoImage(rbanner)
        rbanner_canvas.configure(width=rbanner.width()+2, height=rbanner.height())  # Add 2 pixels to width to prevent image clipping on the left of image.
        rbanner_canvas.create_image(rbanner.width() / 2, rbanner.height() / 2, anchor=CENTER, image=rbanner)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        rbanner_canvas.image = rbanner

        # Set up the main content frame to place the main home frames and elements inside.
        self.main_content_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.main_content_frame.grid(column=1, row=0, sticky=EW, padx=35, pady=(0,20))

        # Logo creation
        self.logo_canvas = Canvas(self.main_content_frame, bg=main_window_bg, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        self.logo_canvas.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,0))
        self.logo = Image.open("AppData/Images/logo.png")
        self.logo = ImageTk.PhotoImage(self.logo)
        self.logo_canvas.configure(width=410, height=self.logo.height()+5)  # Add 5 pixels to height to prevent image clipping on the bottom of image.
        self.logo_canvas.create_image(410 / 2, self.logo.height() / 2, anchor=CENTER, image=self.logo)  # Add the image to the canvas by calculating the x and y coordinates for center position.
        self.logo_canvas.image = self.logo

        # Set up a content frame to place the main home elements inside.
        home_frame1 = CTk.CTkFrame(self.main_content_frame, fg_color=frame_fg, corner_radius=10)
        home_frame1.grid(column=0, row=1, sticky=EW, padx=20, pady=(20,5))

        # Set width for columns 0-2 (3 total) in home frame 1. Total minimum column width is 410px.
        home_frame1.columnconfigure(0, weight=0, minsize=100)
        home_frame1.columnconfigure(1, weight=0, minsize=210)
        home_frame1.columnconfigure(2, weight=0, minsize=100)

        # Create the labels to be placed next to their relevant entry boxes.
        CTk.CTkLabel(home_frame1, text="Username", font=(default_font, 14, "bold"), text_color=font_colour).grid(column=0, row=0, sticky=E, padx=(0,5), pady=(20,0))
        CTk.CTkLabel(home_frame1, text="Difficulty", font=(default_font, 14, "bold"), text_color=font_colour).grid(column=0, row=1, sticky=E, padx=(0,5), pady=15)
        CTk.CTkLabel(home_frame1, text="Questions", font=(default_font, 14, "bold"), text_color=font_colour).grid(column=0, row=2, sticky=E, padx=(0,5), pady=(0,20))

        self.difficulty_lbl = CTk.CTkLabel(home_frame1, text="", font=(default_font, 12, "bold"), text_color=font_colour)      # Create an empty placeholder label to display the difficulty level.
        self.difficulty_lbl.grid(column=2, row=1, sticky=W, padx=(5,0), pady=15)
        self.question_amnt_lbl = CTk.CTkLabel(home_frame1, text="", font=(default_font, 12, "bold"), text_color=font_colour)   # Create an empty placeholder label to display the number of questions.
        self.question_amnt_lbl.grid(column=2, row=2, sticky=W, padx=(5,0), pady=(0,20))

        # Set up the username entry, which is either an entry box if there are no usernames saved, or a combo box if there are usernames saved. This prevents the user from trying to open a combo box dropdown when there are no usernames saved.
        usernames = [user[1] for user in users]
        if usernames == []:  # Check if the usernames list is empty
            self.username_entry = CTk.CTkEntry(home_frame1, fg_color="#73ace0", border_color="#6aa5db", text_color=font_colour, corner_radius=10)
            self.username_entry.insert(0, "")
            self.entry_type = "CTkEntry"
        else:
            # Setup combo box and sliders (scales).
            self.username_entry = CTk.CTkComboBox(home_frame1, fg_color="#73ace0", border_color="#6aa5db", button_color="#6aa5db", button_hover_color="#5997d5", text_color=font_colour, corner_radius=10)
            self.username_entry.set("")
            self.entry_type = "CTkComboBox"
            # Attach the scrollable dropdown library to the username entry combo box.
            self.dropdown = CTkScrollableDropdown(self.username_entry, values=[""], justify="left", button_color="transparent", fg_color="#73ace0", bg_color=frame_fg, frame_border_color="#6aa5db", frame_corner_radius=10,
                                                  scrollbar_button_color="#5997d5", scrollbar_button_hover_color="#497caf", hover_color=menu_hover, text_color=font_colour, autocomplete=True)
            self.dropdown.configure(values=usernames)  # Set the values of the combo box to the usernames of the users in the users list (user[1])
            main_window.focus_force()  # CTkScrollableDropdown library utilises "transient()" to stay on top, so after destroying the combo box (by going to a new page - Scoreboard or Quiz) and creating it again (going back to the Home page), the main window needs to be focused. 
                                        # If this isn't done, the focus will go back to the dropdown and prevent interaction with the combo box entry section, stopping users from being able to type inside it.
        self.username_entry.grid(column=1, row=0, padx=5, pady=(20,0), sticky=EW)

        self.difficulty_slider = CTk.CTkSlider(home_frame1, from_=0, to=2, number_of_steps=2, command=lambda value: self.slider_value_update("S1", value), orientation=HORIZONTAL, fg_color="#73ace0", button_color="#4d97e8")
        self.difficulty_slider.grid(column=1, row=1, padx=5, pady=15, sticky=EW)
        self.questions_slider = CTk.CTkSlider(home_frame1, from_=5, to=35, number_of_steps=30, command=lambda value: self.slider_value_update("S2", value), orientation=HORIZONTAL, progress_color="#4d97e8", fg_color="#73ace0", button_color="#4d97e8", button_hover_color="#3b83c4")
        self.questions_slider.grid(column=1, row=2, padx=5, pady=(0,20), sticky=EW)
        
        # Update the value of the entry box and the sliders (scales) with the previously recorded values (used for going from scoreboard back to homepage).
        if username != None:
            if self.entry_type == "CTkEntry":  # Check if the username entry is an entry box, as combo boxes don't support the "insert" method but entry boxes do.
                self.username_entry.insert(0, username)
            elif self.entry_type == "CTkComboBox":  # Check if the username entry is a combo box, as entry boxes don't support the "set" method but combo boxes do.
                self.username_entry.set(username)
        if difficulty_num != None:
            self.difficulty_slider.set(difficulty_num)
        if questions != None:
            self.questions_slider.set(questions)

        # Update the labels next to the sliders with their relevant values.
        self.slider_value_update("S1", self.difficulty_slider.get())
        self.slider_value_update("S2", self.questions_slider.get())

        # Create a frame to place the buttons inside.
        button_frame = CTk.CTkFrame(self.main_content_frame, fg_color="transparent")
        button_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=(5,20))
        
        # Set width for columns 0-1 (2 total) in the button frame. Total minimum column width is 410px.
        button_frame.columnconfigure(0, weight=0, minsize=205)
        button_frame.columnconfigure(1, weight=0, minsize=205)

        # Create the buttons.
        CTk.CTkButton(button_frame, text="Scoreboard", command=lambda: self.tools.save_details("Scoreboard", "Home", "Temporary"),
                      width=200, height=35, corner_radius=10, fg_color=button_fg, hover_color=button_hover, font=(default_font, 14, "bold"), text_color=font_colour).grid(column=0, row=1, sticky=EW, padx=(0,5))
        CTk.CTkButton(button_frame, text="Start", command=lambda:self.tools.save_details("Quiz", "Home", "Permanent"),
                      width=200, height=35, corner_radius=10, fg_color=button_fg, hover_color=button_hover, font=(default_font, 14, "bold"), text_color=font_colour).grid(column=1, row=1, sticky=EW, padx=(5,0))



# Main function for starting the program.
def main(): 
    global main_window,main_window_bg, frame_fg, button_fg, button_hover, menu_active_fg, menu_hover, font_colour, default_font, users, data_loaded, quiz_paused, timer_showing, timer, username, difficulty_num, questions
    
    main_window = Tk()                          # Initialise the main window. For scaling reasons, use a Tk window with CTk elements.
    CTk.deactivate_automatic_dpi_awareness()    #  Deactivate the automatic DPI awareness of the CTk library, allowing it to work with Tkinter's DPI scaling. This resolves an issue with the custom combobox not scaling correctly.
    main_window.title("QWhizz Math")            # Set the title of the window.
    main_window.iconphoto(False, PhotoImage(file="AppData/Images/icon.png"))  # Set the title bar icon.
    main_window.resizable(False, False)         # Set the resizable property for height and width to False.
    main_window_bg = "#d0ebfc"                  # Set the background colour to be used for the main window.
    frame_fg = "#87bcf4"                        # Set the foreground colour to be used for all frames.
    button_fg = "#5ba2ef"                       # Set the foreground colour to be used for all buttons.
    button_hover = "#4989ce"                    # Set the hover colour to be used for all buttons.
    menu_active_fg = "#FFFFFF"                  # Set the foreground colour to be used for active menu items.
    menu_hover = "#a3cbf5"                      # Set the hover colour to be used for all menu items.
    font_colour = "#FFFFFF"                     # Set the font colour to be used for all CTk elements.
    default_font = "Segoe UI"                   # Set the default font to be used for all CTk elements.
    main_window.configure(bg=main_window_bg)    # Configure the main window to use the background colour (value) of the "main_window_bg variable".

    # Initialise global lists and variables.
    users = []                              # Create empty list for user details and their quiz results to be stored inside.
    data_loaded = False                     # Initialise a flag to track whether the JSON file data has been loaded, setting it to False so that the program will attempt to reload data from the file before displaying the scoreboard.
    quiz_paused = False                     # Initialise a flag to track whether the quiz is paused or not.
    timer_showing = None                    # Initialise a flag to track whether the timer is being displayed or not.
    timer = BooleanVar(value=True)          # Create a "timer" BooleanVar global reference to control the timer checkbutton state, with the default value being True, putting the checkbutton in an on state.
    username = None                         # Initialise the username attribute as None.
    difficulty_num = None                   # Initialise the difficulty_num attribute as None.
    questions = None                        # Initialise the questions attribute as None.

    # Set up the class instances.
    # The classes (Tools, Scoreboard, Completion, Quiz, and Home) reference each other, so some instances are first given placeholder values (None) and are linked once the other necessary instances are created.
    # Ultimately, the class instances are linked together to allow access to each other's attributes and methods.
    tools = Tools(None, None, None, None, None)                                         # Create a "tools" instance of the "Tools" class so that the "Tools" class attributes and methods can be accessed within other classes once created. Temporarily pass "None" for all other class instances until they are created.
    about_window = About(tools, None, None, None, None)                                 # Create an "about_window" instance of the "About" class and pass in the "tools" instance. Temporarily pass "None" for the "scoreboard_page", "completion_page", "quiz_page", and "home_page" instances until they are created.
    scoreboard_page = Scoreboard(tools, about_window, None, None, None)                 # Create a "scoreboard_page" instance of the "Scoreboard" class and pass in the "tools" instance. Temporarily pass "None" for the "completion_page", "quiz_page", and "home_page" instances until they are created.
    completion_page = Completion(tools, about_window, scoreboard_page, None, None)      # Create a "completion_page" instance of the "Completion" class and pass in the "tools" and "scoreboard_page" instances. Temporarily pass "None" for the "quiz_page" and "home_page" instances until they are created.
    quiz_page = Quiz(tools, about_window, scoreboard_page, completion_page, None)       # Create a "quiz_page" instance of the "Quiz" class and pass in the "tools", "scoreboard_page", and "completion_page" instances. Temporarily pass "None" for the "home_page" instance until it is created.
    home_page = Home(tools, about_window, scoreboard_page, completion_page, quiz_page)  # Create a "home_page" instance of the "Home" class and pass in the "tools", "scoreboard_page", "completion_page", and "quiz_page" instances.
    
    # Link the remaining class instances to each other now that they are created.
    tools.about = about_window                      # Link the "about_window" instance to the "tools" instance to allow access to "About" class attributes and methods from within the "Tools" class.
    tools.scoreboard = scoreboard_page              # Link the "scoreboard_page" instance to the "tools" instance to allow access to "Scoreboard" class attributes and methods from within the "Tools" class.
    tools.completion = completion_page              # Link the "completion_page" instance to the "tools" instance to allow access to "Completion" class attributes and methods from within the "Tools" class.
    tools.quiz = quiz_page                          # Link the "quiz_page" instance to the "tools" instance to allow access to "Quiz" class attributes and methods from within the "Tools" class.
    tools.home = home_page                          # Link the "home_page" instance to the "tools" instance to allow access to "Home" class attributes and methods from within the "Tools" class.
    about_window.scoreboard = scoreboard_page       # Link the "scoreboard_page" instance to the "about_window" instance to allow access to "Scoreboard" class attributes and methods from within the "About" class.
    about_window.completion = completion_page       # Link the "completion_page" instance to the "about_window" instance to allow access to "Completion" class attributes and methods from within the "About" class.
    about_window.quiz = quiz_page                   # Link the "quiz_page" instance to the "about_window" instance to allow access to "Quiz" class attributes and methods from within the "About" class.
    about_window.home = home_page                   # Link the "home_page" instance to the "about_window" instance to allow access to "Home" class attributes and methods from within the "About" class.
    scoreboard_page.completion = completion_page    # Link the "completion_page" instance to the "scoreboard_page" instance to allow access to "Completion" class attributes and methods from within the "Scoreboard" class.
    scoreboard_page.quiz = quiz_page                # Link the "quiz_page" instance to the "scoreboard_page" instance to allow access to "Quiz" class attributes and methods from within the "Scoreboard" class.
    scoreboard_page.home = home_page                # Link the "home_page" instance to the "scoreboard_page" instance to allow access to "Home" class attributes and methods from within the "Scoreboard" class.
    completion_page.quiz = quiz_page                # Link the "quiz_page" instance to the "completion_page" instance to allow access to "Quiz" class attributes and methods from within the "Completion" class.
    completion_page.home = home_page                # Link the "home_page" instance to the "completion_page" instance to allow access to "Home" class attributes and methods from within the "Completion" class.
    quiz_page.home = home_page                      # Link the "home_page" instance to the "quiz_page" instance to allow access to "Home" class attributes and methods from within the "Quiz" class.

    # Call the "setup_homepage" method from the "home_page" class instance to set up the home page UI elements.
    home_page.setup_homepage()
    tools.load_details()

    # Start the CTkinter event loop so that the GUI window stays open.
    main_window.mainloop()


# Run the main function.
main()