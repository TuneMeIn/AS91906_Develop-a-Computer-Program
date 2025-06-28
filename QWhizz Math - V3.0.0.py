# Date Created: 25/06/2025
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
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import customtkinter as CTk
from AppData.CTkScrollableDropdown import *
from PIL import Image, ImageTk
from fpdf import FPDF
from fpdf.enums import TableCellFillMode
from fpdf.fonts import FontFace
from datetime import datetime
import json, time, random, os, platform, subprocess, string

class PDF(FPDF):
    def __init__(self):
        # Initialise the parent FPDF class and its attributes for page orientation and size.
        super().__init__(orientation="portrait", format="A4")  # "Super()" allows a subclass, in this case "PDF", to inherit methods and attributes from the parent class (superclass) "FPDF".
        self.set_auto_page_break(auto=True, margin=20)         # Automatically add a new page if content overflows.


    def header(self):
        # Add logo on the top left
        self.image("AppData\Images\qw_logo.png", 15, 7, 25)

        # Centred title image
        img_width = 70
        x_center = (self.w - img_width) / 2  # Calculate centre x position.
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
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="R")      # Print page number on the right. "{nb}" is a placeholder that gets replaced with the total page count by "alias_nb_pages()".


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
            cell_fill_color=(224, 235, 255),           # Alternate cell colour for colour banding.
            cell_fill_mode=TableCellFillMode.ROWS,     # Fill alternate cells for colour banding.
            col_widths=(75, 290, 125, 120, 100, 100),  # Set column widths
            headings_style=heading_style,              # Apply heading style
            line_height=6,                             # Set line height
            text_align=("CENTER", "LEFT", "CENTER", "CENTER", "CENTER", "CENTER"),  # Set text alignment for each column
            width=180,                                 # Set table width
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
        global username, difficulty_num, question_amount
        
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


    # Method for handling mouse button 1 click events.
    def on_mbtn1_click(self, origin, element):
        if origin == "Scoreboard":
            if element == "Scrollbar":
                self.scoreboard.scrollbar.configure(button_color=BUTTON_CLICKED, button_hover_color=BUTTON_CLICKED)  # Change the scrollbar button colour to a darker blue when clicked and/or held.


    # Method for handling mouse button 1 release events.
    def on_mbtn1_release(self, origin, element):
        if origin == "Scoreboard":
            if element == "Scrollbar":
                self.scoreboard.scrollbar.configure(button_color=BUTTON_FG, button_hover_color=BUTTON_HOVER)  # Change the scrollbar button colour back to a light blue when released.


    # Method for handling errors and preventing repeated code.
    def error_control(self, file_name, file_dir, file_data, control):
        global users, settings, timer, deletion_history_states
        
        # Temporary storage mode
        if control == "Temporary":
            if file_data == "users": users = []          # If the "file_data" variable is set to "users", make "users" as an empty list.
            elif file_data == "settings":
                settings = default_settings              # If the "file_data" variable is set to "settings", make "settings" store the default settings.
                timer.set(settings.get("enable_timer"))  # Set the timer to the value stored in the "default_settings" dictionary.
                deletion_history_states.set(settings.get("deletion_history_states"))  # Set the deletion history states to the value stored in the "default_settings" dictionary.
        return  # Exit the function after handling the error control for temporary storage mode.

    
    # Function for loading the "users" and "settings" lists from the JSON files.
    def load_details(self, file_name, file_dir, file_data):
            global data_loaded, users, settings, timer, deletion_history_states
            
            # Check if the JSON file exists. If not, create it.
            if not os.path.exists(file_dir):   
                response1 = messagebox.askyesno("File Not Found", f"The {file_name} file cannot be found. Do you want to create a new one?")
                if response1 == True:  # If the user chooses to create a new file, proceed.
                    try:
                        # Create a new JSON file with an empty list.
                        with open(file_dir, "w") as file:   # Create a new JSON file with an empty list if the file doesn't already exist.
                            if file_data == "users": json.dump([], file)                               # Write an empty list to the new JSON file.
                            elif file_data == "settings": json.dump(default_settings, file, indent=4)  # Write an empty list to the new JSON file.
                            file.close()    # Close the file after writing to it.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = True  # Set the "data_loaded" variable to True, so that the program doesn't reload data again from the JSON file before it is accessed.

                    # Error control for instances such as the file being inaccessible or lacking the permission to read/write it.
                    except IOError as io_error:
                        messagebox.showerror("File Error", f"An error occurred while creating the {file_name} file, program will run in temporary storage mode.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be created.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = False  # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.

                    # Error control for any other errors.
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred while creating the {file_name} file, program will run in temporary storage mode.\n\n{e}\n\n{full_directory}")  # Show an error message if the file cannot be created due to an unexpected error.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = False  # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                    return

                # If the user chooses not to create a new file, run the program in temporary storage mode.
                else:
                    messagebox.showwarning("Temporary Storage Mode", f"The program will run in temporary storage mode until the {file_name} file is created or replaced.\n\n{full_directory}")  # Show a warning message if the user does not want to create a new file.
                    self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                    data_loaded = False      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                    return

            # If the JSON file exists, try to load the data from it, and if the file isn't in JSON format, it will raise a JSONDecodeError. If there are any other errors, such as the file being inaccessible, it will raise an IOError.
            try:
                with open(file_dir, "r") as file:  # Open the JSON file in read mode ("r").
                    data = json.load(file)         # Load the details from the JSON file into the "users" list.

                if file_data == "users":
                    if not isinstance(data, list):  # Check if the loaded data is a list.
                        raise json.JSONDecodeError("Expected a list", doc=str(data), pos=0)  # Raise an error if the loaded scoreboard data is not a list, simulating a JSON decode error.
                    users.clear()  # Clear the list to prevent duplicate entries.
                    users = data   # Assign the loaded data to the "users" list.
                    
                    # Check all entries to make sure they each contain 6 elements.
                    for i, details in enumerate(users):
                        if len(details) < 6:
                            response2 = messagebox.askyesno("Invalid Data", f"The {file_name} file contains invalid data. Entry #{i+1} is incomplete (expected 6 elements, got {len(details)}).\nWould you like to remove this entry?")
                            if response2:
                                # Remove invalid entries and update the scoreboard file.
                                valid_users = [details for details in users if len(details) == 6]
                                with open(file_dir, "w") as file:           # Open the JSON file in write mode ("w").
                                    json.dump(valid_users, file, indent=4)  # Write the valid users to the JSON file.
                                    file.close()                            # Close the file after writing to it.
                                break
                            else:
                                messagebox.showwarning("Invalid Data", f"The program will run in temporary storage mode until the {file_name} file is fixed.\n\n{full_directory}")
                                users = [details for details in users if len(details) == 6]  # Keep only the valid entries in memory.
                                break

                elif file_data == "settings":
                    if not isinstance(data, dict): # Check if the loaded data is a dictionary.
                        raise json.JSONDecodeError("Expected a dict", doc=str(data), pos=0)  # Raise an error if the loaded settings data is not a dictionary, simulating a JSON decode error.
                    
                    if "enable_timer" not in data or "deletion_history_states" not in data:
                        raise json.JSONDecodeError("Missing required keys in settings", doc=str(data), pos=0)
                    
                    settings.clear()    # Clear the list to prevent duplicate entries.
                    settings = data     # Modify the "settings" dictionary in place.
                    timer.set(settings.get("enable_timer", default_settings["enable_timer"]))  # Set the timer to the value stored in the "settings" dictionary, or the default value if not found.
                    deletion_history_states.set(settings.get("deletion_history_states", default_settings["deletion_history_states"]))  # Set the deletion history states to the value stored in the "settings" dictionary, or the default value if not found.
                
                data_loaded = True      # Set the "data_loaded" variable to True, so that the program doesn't reload data again from the JSON file before it is accessed.
            
            # Error control for instances such as the JSON file having invalid data, having incorrect formatting, or being corrupted.
            except json.JSONDecodeError as JSONDecodeError:
                response3 = messagebox.askyesno("File Error", f"Failed to decode JSON data. The {file_name} file may be corrupted or improperly formatted. Do you want to replace it?\n\n{JSONDecodeError}\n\n{full_directory}")  # Show an error message if the JSON file cannot be decoded, asking the user if they want to replace the file.
                if response3 == True:
                    try:
                        with open(file_dir, "w") as file:  # Open the shortened_directory file in write mode ("w").
                            if file_data == "users": json.dump([], file)                                # Write an empty list to the new JSON file.
                            elif file_data == "settings": json.dump(default_settings, file, indent=4)   # Write an empty list to the new JSON file.
                            file.close()    # Close the file after writing to it.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = True  # Set the "data_loaded" variable to True, so that the program doesn't reload data again from the JSON file before it is accessed.
                        messagebox.showinfo("File Replaced", f"The JSON {file_name} file has been successfully replaced and restored to defaults.\n\n{full_directory}")
                    
                    # Error control for instances such as the file being inaccessible or lacking the permission to read/write it.
                    except IOError as io_error:
                        messagebox.showerror("File Error", f"An error occurred while replacing the {file_name} file, program will run in temporary storage mode.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be replaced.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = False  # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                    
                    # Error control for any other exceptions that may occur.
                    except Exception as e:                                  
                        messagebox.showerror("Unexpected Error", f"An unexpected error occurred while replacing the {file_name} file, program will run in temporary storage mode.\n\n{e}\n\n{full_directory}")  # Show an error message if there is an unexpected error.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = False  # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                    return
                else:
                    messagebox.showwarning("Temporary Storage Mode", f"The program will run in temporary storage mode until the {file_name} file is created or replaced.\n\n{full_directory}")  # Show a warning message if the user does not want to create a new file.
                    self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                    data_loaded = False      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                    return
            
            # Error control for instances such as the file being inaccessible or lacking the permission to read it.
            except IOError as io_error:
                messagebox.showwarning("File Error", f"An error occurred while reading the {file_name} file, program will run in temporary storage mode.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be read.
                self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                data_loaded = False  # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
            
            # Error control for any other exceptions that may occur.
            except Exception as e:
                response3 = messagebox.askyesno("Unexpected Error", f"An unexpected error occurred while reading the {file_name} file. Do you want to replace it?")  # Show an error message if there is an unexpected error.
                if response3 == True:
                    try:
                        with open(file_dir, "w") as file:  # Open the shortened_directory file in write mode ("w").
                            if file_data == "users": json.dump([], file)                                # Write an empty list to the new JSON file.
                            elif file_data == "settings": json.dump(default_settings, file, indent=4)   # Write an empty list to the new JSON file.
                            file.close()    # Close the file after writing to it.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = True  # Set the "data_loaded" variable to True, so that the program doesn't reload data again from the JSON file before it is accessed.
                        messagebox.showinfo("File Replaced", f"The JSON {file_name} file has been successfully replaced and restored to defaults.\n\n{full_directory}")
                    
                    # Error control for instances such as the file being inaccessible or lacking the permission to read/write it.
                    except IOError as io_error:
                        messagebox.showerror("File Error", f"An error occurred while replacing the {file_name} file, program will run in temporary storage mode.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be replaced.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = False  # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                    
                    # Error control for any other exceptions that may occur.
                    except Exception as e:
                        messagebox.showerror("Unexpected Error", f"An unexpected error occurred while replacing the {file_name} file, program will run in temporary storage mode.\n\n{e}\n\n{full_directory}")  # Show an error message if there is an unexpected error.
                        self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                        data_loaded = False  # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                    return
                else:
                    messagebox.showwarning("Temporary Storage Mode", f"The program will run in temporary storage mode until the {file_name} file is created or replaced.\n\n{full_directory}")  # Show a warning message if the user does not want to create a new file.
                    self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                    data_loaded = False      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                    return


    # Method for saving details specific to the specified window.
    def save_details(self, procedure, origin, scenario, file_dir):
        global ref_number, username, difficulty_num, question_amount, data_loaded
        
        if origin == "Home":
            if scenario == "Temporary" or scenario == "Permanent":
                username = self.home.username_entry.get()                # Get the username entry widget value.
                difficulty_num = self.home.difficulty_slider.get()       # Get the difficulty slider value.
                question_amount = int(self.home.questions_slider.get())  # Get the questions slider value.
            
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
                        ref_number = random.randint(1000, 9999)     # Generate a random number from 1000 to 9999 and put this value into the "ref_number" variable.
                        if ref_number not in existing_ref_numbers:  # Check that the generated reference number doesn't already exist.
                            break
            
            if procedure == "Quiz":
                self.clear_widget(self.quiz.setup_quiz, True, None, None, None)
            elif procedure == "Scoreboard":
                self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)
            else:
                return  # If the procedure is not "Quiz" or "Scoreboard", do nothing and return.

        elif origin == "Completion" or origin == "Scoreboard":
                try:
                    with open(file_dir, "w") as file:        # Open the file in write mode ("w"). If it doesn't exist, a new file will be created.
                        json.dump(users, file, indent=4)     # Dump the entries from the "users" list into the JSON file.
                        file.close()                         # Close the file after writing to it.
                    data_loaded = False                      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                except IOError as io_error:                  # Error control for instances such as the file being inaccessible or lacking the permission to write to it.
                    messagebox.showerror("File Error", f"Failed to write to 'scoreboard.json'. Check file permissions, disk space, and ensure the file is not in use.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be written to.
                except Exception as e:                       # Error control for any other exceptions that may occur.
                    messagebox.showerror("Unexpected Error", f"An unexpected error occurred while writing to 'scoreboard.json'.\n\n{e}\n\n{full_directory}")  # Show an error message if there is an unexpected error.
        
        elif origin == "Menubar":
                global settings
                try:
                    settings = {"enable_timer": timer.get(), "deletion_history_states": deletion_history_states.get()}
                    with open(file_dir, "w") as file:        # Open the file in write mode ("w"). If it doesn't exist, a new file will be created.
                        json.dump(settings, file, indent=4)  # Dump the entries from the "users" list into the JSON file.
                        file.close()                         # Close the file after writing to it.
                    data_loaded = False                      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                except IOError as io_error:                  # Error control for instances such as the file being inaccessible or lacking the permission to write to it.
                    messagebox.showerror("File Error", f"Failed to write to 'settings.json'. Check file permissions, disk space, and ensure the file is not in use.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be written to.
                except Exception as e:                       # Error control for any other exceptions that may occur.
                    messagebox.showerror("Unexpected Error", f"An unexpected error occurred while writing to 'settings.json'.\n\n{e}\n\n{full_directory}")  # Show an error message if there is an unexpected error.


    # Method for printing details into a PDF.
    def print_details(self, selections):
        data = []
        
        if selections == "all" and data_loaded == False:  # Check if the data has been loaded from the JSON file only if all scores are being printed.
            self.load_details("scoreboard", SCOREBOARD_FILE_PATH, "users")
    
        if selections == "all":
            if users == []:  # Check if the "users" list is empty.
                response1 = messagebox.askyesno("No Scores Recorded", "There are no recorded scores to print.\nWould you still like to print out a blank scoreboard table?")
                if response1 == False:
                    return
            else:
                # Load all data from JSON file.
                with open("AppData\scoreboard.json", "r") as file:
                    data = json.load(file)  # Load the details from the JSON file into the "data" list.
        else:
            if selections != []:  # Check if the "selections" list is not empty.
                # Match the selected reference numbers in the treeview widget to the user reference numbers (user[0]) in the "users" list.
                # This creates a new list of users that match the selected user reference numbers so that only the selected users are printed on the scoreboard PDF.
                # "user[0]" is converted to a string to ensure that it matches the format used in the Treeview selection, which is passed as a string.
                data = [user for user in users if str(user[0]) in selections]  # If selections are provided, use them as the scoreboard data directly.
            else:
                messagebox.showwarning("No Scores Selected", "Please select at least one score to print.")
                return
        self.scoreboard.tree.selection_set("")  # Clear the current selection in the Treeview widget.
        self.reset_details("Scoreboard", None)  # Reset the "sel_reference_numbers" list in the Scoreboard class so that the list is ready for new selections.
        
        # Initialise PDF.
        pdf = PDF()
        pdf.alias_nb_pages()  # Enable total page count placeholder.
        pdf.add_page()        # Start with first page.

        # Define table headings.
        headings = ["Ref #", "Username", "Difficulty", "Questions", "Time", "Score"]

        # Generate the table on the PDF.
        pdf.scoreboard_table(data, headings)

        try:
            # Ask the user where they would like to save the PDF file.
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialdir=initial_pdf_directory, initialfile=INITIAL_PDF_NAME, filetypes=[("PDF files", "*.pdf")], title="Save Scoreboard As")
            saved_file_name = os.path.basename(file_path)  # Get the name of the saved file using "os.path.basename", which would be any characters after the last slash (/) in the file path.

            # If the user chose a location, save the PDF to that location.
            if file_path:
                pdf.output(file_path)  # Save the PDF to the specified file path.
                words = "scoreboard has" if selections == "all" else "selected score has" if len(selections) == 1 else "selected scores have"  # Determine whether to use "scoreboard has", "selected score has", or "selected scores have" in the message box based on the number of selected items.
                messagebox.showinfo("Print Successful", f"The {words} been successfully printed to '{saved_file_name}'.\n\n{file_path}")
            
                # Ask the user if they want to print the PDF.
                response2 = messagebox.askyesno("Send PDF to Printer", "Would you like to send the PDF to a printer now?")
                # If the user chooses to send the PDF to a printer, proceed with printing.
                if response2 == True:
                    try:
                        if operating_system == "Windows":                  # Check if the operating system is Windows.
                            os.startfile(file_path, "print")               # Send the PDF file to the default printer.
                        elif operating_system == "Linux":                  # Check if the operating system is Linux.
                            subprocess.run(["lp", file_path], check=True)  # Use the "lp" command to send the PDF file to the default printer.
                        elif operating_system == "Darwin":                 # Check if the operating system is macOS.
                            subprocess.run(["lp", file_path], check=True)  # Use the "lp" command to send the PDF file to the default printer.
                        else:
                            messagebox.showwarning("Unsupported OS", f"Your operating system ({operating_system}) is not supported for printing. Please print the PDF file manually.\n\n{file_path}")  # Show a warning message if the operating system is not supported for printing.
                    except Exception as e:
                        messagebox.showerror("Printing Error", f"An error occurred while printing the PDF file.\n\n{e}\n\n{file_path}")  # Show an error message if there is an error while printing the PDF file.
            else:
                return
        
        # Error control for instances such as the file being inaccessible or lacking the permission to write to it.
        except IOError as io_error:
            messagebox.showerror("File Error", f"Failed to write to 'QWhizz Math Scoreboard.pdf'. Check file permissions, disk space, and ensure the file is not in use.\n\n{io_error}\n\n{file_path}")  # Show an error message if the file cannot be written to.
        
        # Error control for any other exceptions that may occur.
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred while writing to 'QWhizz Math Scoreboard.pdf'.\n\n{e}\n\n{file_path}")  # Show an error message if there is an unexpected error.


    # Method for deleting details from the "users" list.
    def delete_details(self, selections):
        global users
        users_to_delete = []  # Create an empty list to store users to delete.
        
        if users != []:  # Check if the "users" list is not empty.
                if selections == "all":
                    response = messagebox.askyesno("Delete All Scores", "Are you sure that you want to delete all recorded scores?")
                    if response == True:
                        if deletion_history_states.get() > 0:  # Check if the "deletion_history_states" variable is greater than 0, which means that the deletion history is enabled.
                            # Store all users with their indices in the "history_stack" list.
                            history_stack.append([(user, i) for i, user in enumerate(users)])
                            # Trim the stack to the specified history limit in the "deletion_history_states" variable if the amount of stacked scores exceeds the set amount of history states.
                            if len(history_stack) > deletion_history_states.get():
                                history_stack.pop(0)  # Remove the last entry from the stack (corresponding to the oldest score, which has an index of 0) if the stack exceeds the history limit.

                        users = []
                        redo_stack.clear()  # Clear the "redo_stack" list to prevent any redo actions directly after deletion.
                        self.save_details(None, "Scoreboard", None, SCOREBOARD_FILE_PATH)
                        self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)
                        messagebox.showinfo("Scores Deleted", "All recorded scores have been deleted.")
                    else:
                        return
                else:
                    if selections != []:  # Check if the "selections" list is not empty.
                        words = ["scores", "have"] if len(selections) > 1 else ["score", "has"]  # Determine whether to use "scores" and "have", or "score" and "has" in the message boxes based on the number of selected items.
                        response = messagebox.askyesno("Delete Selected Scores", f"Are you sure that you want to delete the selected {words[0]}?")
                        if response == True:
                            # Find the users to delete and record their original index positions
                            users_to_delete = []
                            for index, user in enumerate(users):
                                if str(user[0]) in selections:
                                    users_to_delete.append((user, index))  # Store (user, index) in the "users_to_delete" list
                            
                            # Store all selected users with their indices in the "history_stack" list.
                            if deletion_history_states.get() > 0:             # Check if the "deletion_history_states" variable is greater than 0, which means that the deletion history is enabled.
                                history_stack.append(users_to_delete.copy())  # Use .copy() to append a snapshot of the current users_to_delete list, ensuring that future modifications to the original list (like clearing it) do not affect the stored history stack.
                            
                            # Trim the stack to the specified history limit in the "deletion_history_states" variable if the amount of stacked scores exceeds the set amount of history states.
                            if len(history_stack) > deletion_history_states.get():
                                history_stack.pop(0)  # Remove the last entry from the stack (corresponding to the oldest score, which has an index of 0) if the stack exceeds the history limit.

                            # Delete users in reverse index order to avoid shifting issues.
                            # "users_to_delete" is a list of tuples in the form (user, index), where "index" is the user's position in the "users" list.
                            # Sorting this list by index in descending order ensures that when items are deleted, the positions of earlier items in the list are not affected.
                            # If deletions were done in ascending order, deleting an item would shift the indices of the items that follow it, leading to incorrect deletions if more than one item is deleted at once.
                            for user, index in sorted(users_to_delete, key=lambda x: x[1], reverse=True):  # Sort by the original index ("x[1]"), which refers to the second element ("1", being the index) in each (user, index) tuple, representing the user's original position.
                                del users[index]     # Delete the user from the "users" list at the specified index.
                            redo_stack.clear()       # Clear the "redo_stack" list to prevent any redo actions directly after deletion.
                            users_to_delete.clear()  # Clear the list of users to delete.
                            
                            self.save_details(None, "Scoreboard", None, SCOREBOARD_FILE_PATH)
                            self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)
                            messagebox.showinfo("Scores Deleted", f"The selected {words[0]} {words[1]} been deleted.")
                        else:
                            return
                    else:
                        messagebox.showwarning("No Scores Selected", "Please select at least one score to delete.")
                        return
                self.reset_details("Scoreboard", None)  # Reset the "sel_reference_numbers" list in the Scoreboard class so that the list is ready for new selections.
        else:
            messagebox.showwarning("No Scores Recorded", "There are no recorded scores to delete.")
            return


    # Method for undoing the deletion of scores.
    def undo_delete(self):
        global users, history_stack
        
        # Check if the history stack is empty.
        if not history_stack:  
            return  # If the stack is empty, do nothing and return.
        
        last_deleted = history_stack.pop()  # Retrieve the last deleted users from the history stack.
        redo_stack.append([(user, index) for user, index in last_deleted])  # Store the last deleted users in the redo stack for potential future redoing.
        for user, index in last_deleted:  # Reinsert each user at their original index.
            users.insert(index, user)
        
        self.save_details(None, "Scoreboard", None, SCOREBOARD_FILE_PATH)
        self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)


    # Method for redoing the deletion of scores that were previously undone.
    def redo_delete(self):
        global users, history_stack, redo_stack

        # Check if the redo stack is empty.
        if not redo_stack:
            return  # If the redo stack is empty, do nothing and return.
        
        last_redo = redo_stack.pop()  # Retrieve the last deleted users from the redo stack.
        history_stack.append([(user, index) for user, index in last_redo])    # Store the last deleted users in the history stack for potential future undoing.
        # Delete users in reverse index order to avoid shifting issues.
        for i, index in sorted(last_redo, key=lambda x: x[1], reverse=True):  # Sort by the original index ("x[1]"), which refers to the second element ("1", being the index) in each (user, index) tuple, representing the user's original position.
            del users[index]  # Delete the user from the "users" list at the specified index.
        
        self.save_details(None, "Scoreboard", None, SCOREBOARD_FILE_PATH)
        self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)


    # Method for resetting details specific to the specified window.
    def reset_details(self, origin, action):
        global username, difficulty, difficulty_num, question_amount, question_details, fake_answers
        if origin == "Completion":
            username = None
            difficulty = None
            difficulty_num = None
            question_amount = None
        elif origin == "Scoreboard":
            self.scoreboard.sel_reference_numbers.clear()
        elif origin == "Quiz":
                if action != "Restart":  # Only clear the question details if the action is not "Restart", since restarting the quiz requires the question details to be retained.
                    question_details.clear()
                    fake_answers.clear()
                if action == "Restart" or action == "New":
                    self.quiz.score = 0
                self.quiz.current_index = 0
                self.quiz.question_no = 1
                self.quiz.user_answers.clear()



    # Method for unbinding specified key events from the main window.
    def unbind_keys(self, keys):
        # Unbind all key events from the main window.
        for key in keys:
            main_window.unbind(key)


    # Method for configuring the timer label state (enabled/disabled).
    # Unique identifiers are passed in "origin" to differentiate between the "Quiz" and "Completion" classes to manage their relevant timer labels.
    def timer_config(self, origin, command, procedure):
        if origin == "Quiz":
            if command == "Enable":
                return (f"Time: {self.quiz.time_string}")
            elif command == "Disable":
                return "Timer Disabled"
        
        elif origin == "Quiz Menubar":
            if command == "Enable":
                self.quiz.timer_lbl.configure(text=f"Time: {self.quiz.time_string}")
            elif command == "Disable":
                self.quiz.timer_lbl.configure(text="Timer Disabled")
            if procedure != None: procedure()

        elif origin == "Completion":
            if command == "Enable":
                return (f"Total Time: {self.quiz.total_time}")
            elif command == "Disable":
                return "Timer Disabled"



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
        self.unpause_quiz = False     # Set the flag to indicate that the quiz should not be unpaused when the "About" window is closed.
        if origin == "Quiz" and quiz_paused == False: 
            self.quiz.pause_quiz()    # Pause the quiz if the "About" window is opened from the "Quiz" window.
            self.unpause_quiz = True  # Set the flag to indicate that the quiz should be unpaused when the "About" window is closed.
        
        # Create a top-level window (separate from the main window).
        self.about_window = Toplevel(main_window, bg=MAIN_WINDOW_BG)
        self.about_window.withdraw()  # Withdraw the window so that it is not shown immediately.
        if os.path.exists("AppData/Images/icon.png"):  # Check if the icon file exists before setting it.
            self.about_window.iconphoto(False, PhotoImage(file="AppData/Images/icon.png"))  # Set the title bar icon for the "About" window.
        self.about_window.title("About")
        self.about_window.columnconfigure(0, weight=0, minsize=300)
        self.about_window.resizable(False, False)
        self.about_window.update_idletasks()  # Process any pending events for the window to make sure the geometry info is up-to-date before calculating the centre position later.
        
        # Centre the "About" window above the main window.
        self.x = main_window.winfo_x() + main_window.winfo_width() // 2 - self.about_window.winfo_width() // 2 - 60
        self.y = main_window.winfo_y() + main_window.winfo_height() // 2 - self.about_window.winfo_height() // 2 + 56
        self.about_window.geometry(f"+{self.x}+{self.y}")
        self.about_window.transient(main_window)  # Keep on top of parent window (main_window)
        self.about_window.focus()  # Set focus to the "About" window so that it is ready for user interaction.

        # Create a frame inside the "About" window to hold the "about" details label.
        self.about_frame = CTk.CTkFrame(self.about_window, fg_color=FRAME_FG, corner_radius=10)
        self.about_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky=EW)
        self.about_frame.columnconfigure(0, weight=0, minsize=300)
        
        # Add program details and a close button.
        CTk.CTkLabel(self.about_frame, text=f"QWhizz Math\nVersion {APP_VERSION}\nMade by Jack Compton", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR, justify="center").grid(row=0, column=0, sticky=EW, padx=10, pady=(20))
        CTk.CTkButton(self.about_window, text="Close", command=lambda: self.close(), font=(DEFAULT_FONT, 14, "bold"), height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER).grid(row=1, column=0, sticky=EW, padx=10, pady=(5,10))
        
        # Show the "About" window after setting its position and size and adding its contents. This prevents the window from flickering when it is created and shown.
        self.about_window.deiconify()

        # Override the window close (X) button behavior so that the main window is enabled again when the about window is closed using this button.
        self.about_window.protocol("WM_DELETE_WINDOW", lambda: self.close())

        # Bind the "esc" key to the "close" function so that the window can be closed by pressing "esc".
        self.about_window.bind("<Escape>", lambda e: self.close())  # Prevent an argument error by using "e" after "lambda" to accept (but ignore) the event passed by bind, keeping close() parameterless.


    def close(self):  # Add "event" parameter to allow for "event" to be passed when the binded "esc" key is pressed (though the bind doesn't include an event).
        self.about_window.unbind("<Escape>")        # Unbind the "esc" key from the "close" function so that "esc" can be used for other purposes later.
        main_window.attributes("-disabled", False)  # Re-enable the main window so that it can be interacted.
        if self.unpause_quiz == True:
            self.quiz.unpause_quiz()  # Unpause the quiz if the "About" window was opened from the "Quiz" window and the quiz was previously running (not paused).
        self.unpause_quiz = False     # Reset the flag to indicate that the quiz should not be unpaused when the "About" window is closed.
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
        self.sel_reference_numbers = []         # Create a new list to store the selected reference numbers from the treeview widget.


    # Function for handling the treeview items being selected or unselected ("<<TreeviewSelect>>" event is generated for both).
    def on_item_selected(self, event):
        selected_items = self.tree.selection()
        self.sel_reference_numbers = []  # Clear the "sel_reference_numbers" list to ensure it only contains the currently selected items.
        
        # If items are selected, i.e. at least one item is selected in the treeview, then proceed to get the reference numbers of the selected items.
        if selected_items:
            # Loop through each selected item in the treeview.
            for item_id in selected_items:
                sel_ref_number = str(self.tree.item(item_id, "values")[0])  # Get the reference number of the selected item.
                self.sel_reference_numbers.append(sel_ref_number)           # Append the selected reference number to the "sel_reference_numbers" list.


    def setup_scoreboard(self):
        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        main_window.columnconfigure(0, weight=1, minsize=850)
        main_window.columnconfigure(1, weight=1, minsize=0)

        # Set up the menu bar.
        scoreboard_menubar = Menu(main_window)  # Create a new menu bar.

        file_menu = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        scoreboard_menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Print Selected", accelerator="Ctrl+P", command=lambda: self.tools.print_details(self.sel_reference_numbers))
        file_menu.add_command(label="Print All", accelerator="Ctrl+Shift+P", command=lambda: self.tools.print_details("all"))
        file_menu.add_command(label="Delete Selected", accelerator="Del", command=lambda: self.tools.delete_details(self.sel_reference_numbers))
        file_menu.add_command(label="Delete All", accelerator="Shift+Del", command=lambda: self.tools.delete_details("all"))

        edit_menu = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        scoreboard_menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo Delete", accelerator="Ctrl+Z", command=lambda: self.tools.undo_delete())
        edit_menu.add_command(label="Redo Delete", accelerator="Ctrl+Shift+Z", command=lambda: self.tools.redo_delete())

        settings_menu = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        scoreboard_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, value=True, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        timer_settings.add_radiobutton(label="Disabled", variable=timer, value=False, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=history_settings, label="Score Deletion History States")
        history_settings.add_radiobutton(label="Disabled", variable=deletion_history_states, value=0, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="10", variable=deletion_history_states, value=10, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="25", variable=deletion_history_states, value=25, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="50", variable=deletion_history_states, value=50, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))

        help_menu = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        scoreboard_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Scoreboard"))

        main_window.config(menu=scoreboard_menubar)

        # Bind key shortcuts to perform actions.
        main_window.bind("<Control-p>", lambda e: self.tools.print_details(self.sel_reference_numbers))  # Bind the "Ctrl+P" key to the "print_details" function so that the selected receipts can be printed.
        main_window.bind("<Control-Shift-P>", lambda e: self.tools.print_details("all"))                 # Bind the "Ctrl+Shift+P" key to the "print_details" function so that all receipts can be printed.
        main_window.bind("<Delete>", lambda e: self.tools.delete_details(self.sel_reference_numbers))    # Bind the "del" key to the "delete_details" function so that the selected receipts can be deleted.
        main_window.bind("<Shift-Delete>", lambda e: self.tools.delete_details("all"))                   # Bind the "Shift+del" key to the "delete_details" function so that all receipts can be deleted.
        main_window.bind("<Control-z>", lambda e: self.tools.undo_delete())                              # Bind the "Ctrl+Z" key to the "undo_delete" function so that the last deletion can be undone.
        main_window.bind("<Control-Shift-Z>", lambda e: self.tools.redo_delete())                        # Bind the "Ctrl+Shift+Z" key to the "redo_delete" function so that the last deletion can be redone if it was previously undone.
        self.binded_keys = ["<Control-p>", "<Control-Shift-P>", "<Delete>", "<Shift-Delete>", "<Control-z>", "<Control-Shift-Z>"]  # Create a list of binded keys to be used later for unbinding them when the user goes back to the home page.
        
        # Set up a content frame to place the main scoreboard top elements inside.
        top_frame1 = CTk.CTkFrame(main_window, fg_color="transparent")
        top_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,5))

        # Set width for columns 0-2 (3 total) in top frame 1. Total minimum column width is 810px.
        top_frame1.columnconfigure(0, weight=0, minsize=400)
        top_frame1.columnconfigure(1, weight=0, minsize=205)
        top_frame1.columnconfigure(2, weight=0, minsize=205)

        # Logo creation
        total_height = 70  # Height for the canvas and vertical centre position is calculated by the height of two buttons (60px) + 10px padding.
        self.logo_canvas = Canvas(top_frame1, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0, width=400, height=total_height)  # Create a canvas for the banner image.
        self.logo_canvas.grid(column=0, row=0, rowspan=2, sticky=EW)
        self.logo = Image.open("AppData/Images/logo_small.png")
        self.logo = ImageTk.PhotoImage(self.logo)
        self.logo_canvas.create_image(0, total_height / 2, anchor=W, image=self.logo)  # Add the image to the canvas by calculating the x and y coordinates for centre-left position.
        self.logo_canvas.image = self.logo

        # Create the buttons.
        CTk.CTkButton(top_frame1, text="Delete", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR, command=lambda: self.tools.delete_details(self.sel_reference_numbers),
                      width=200, height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER).grid(column=1, row=0, sticky=EW, padx=(0,5), pady=(0,5))
        CTk.CTkButton(top_frame1, text="Home", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR, command=lambda: self.tools.clear_widget(self.home.setup_homepage, True, None, None, self.tools.unbind_keys(self.binded_keys)),
                      width=200, height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER).grid(column=2, row=0, sticky=EW, padx=(5,0), pady=(0,5))
        CTk.CTkButton(top_frame1, text="View Answers", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR,
                      width=200, height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER).grid(column=1, row=1, sticky=EW, padx=(0,5), pady=(5,0))
        CTk.CTkButton(top_frame1, text="Retry Quiz", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR,
                      width=200, height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER).grid(column=2, row=1, sticky=EW, padx=(5,0), pady=(5,0))

        # Reload the user scores from the scoreboard.json file.
        self.tools.load_details("scoreboard", SCOREBOARD_FILE_PATH, "users")

        # Create a frame to hold the Treeview and scrollbar.
        tree_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        tree_frame.grid(column=0, row=1, sticky=EW, padx=20, pady=(5,20))

        treestyle = ttk.Style()
        treestyle.theme_use("default")

        # Configure the Treeview style for the headings.
        treestyle.configure("custom.Treeview.Heading",
                            background=BUTTON_FG,           # Background colour of the treeview headings.
                            foreground="white",             # Text colour of the treeview headings.
                            font=("Segoe UI", 10,"bold"),   # Font style of the treeview heading text.
                            padding=(0, 5, 0 ,5),           # Vertical padding of 5 px above and below the text in the treeview headings. 
                            relief="flat")                  # Set the relief to "ridge" to give the header less of a button-look.

        # Configure the Treeview style for the field section.
        treestyle.configure("custom.Treeview",
                            background=FRAME_FG,            # Background colour of the treeview field entries.
                            foreground="white",             # Text colour of the treeview headings.
                            fieldbackground=FRAME_FG,       # Main background colour of the treeview field.
                            rowheight=30,                   # Height of the treeview headings.
                            bordercolor=BUTTON_FG,          # Border colour of the treeview field.
                            borderwidth=1,                  # Border width of the treeview field.
                            relief="flat",                  # Set the relief to "flat" to give the field a flat apperanance.
                            font=("Segoe UI", 10))          # Font style of the treeview field text.

        # Change entry selection colour using ".map()" for dynamic styling of the "selected" state.
        treestyle.map("Treeview",
                    background=[("selected", "#78b0f4")])  # Selection background colour of the treeview field entries.

        # Change the highlight colour for the headers when the mouse hovers over them.
        treestyle.map("custom.Treeview.Heading",
                    background=[("active", BUTTON_FG)],     # Background colour of the treeview headings when hovered over.
                    foreground=[("active", "white")])       # Text colour of the treeview headings when hovered over.


        # Create a Treeview widget to display the customer receipts.
        columns = ("Ref #", "Username", "Difficulty", "Questions", "Time", "Score")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="custom.Treeview", height=8, selectmode="extended")
        
        # Define the Treeview column headings.
        for col in columns:
            if col == "Username":
                self.tree.heading(col, text=col, anchor=W)
            else:
                self.tree.heading(col, text=col, anchor=CENTER)
        
        # Set individual Treeview column widths. Total width of the Treeview is 810 pixels.
        column_widths = {
            "Ref #": 75,
            "Username": 290,
            "Difficulty": 125,
            "Questions": 120,
            "Time": 100,
            "Score": 100
        }

        # Configure the Treeview columns.
        for col in columns:
            if col == "Username":
                self.tree.column(col, anchor=W, width=column_widths[col])
            else:
                self.tree.column(col, anchor=CENTER, width=column_widths[col])

        try:
            # Add each item in the list into the Treeview.
            for index, details in enumerate(users):
                index += 1  # Increment the index by 1 each time t
                self.tree.insert("", "end", values=(details[0], details[1], details[2], details[3], details[4], details[5]))
        except IndexError as index_error:  # Error control for instances such as the "users" list being empty.
            messagebox.showerror("Invalid Data", f"The saved JSON data is invalid or incomplete.\nPlease check the file for missing fields.\n\n{index_error}\n\n{full_directory}")
            return  # Return from the method if an IndexError occurs, preventing further execution.

        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)  # Bind the treeview item selection event to the "on_item_selected" method.
        self.tree.bind("<Motion>", "break")  # Prevent the treeview columns from being manually resized by the user by breaking the motion event.

        # Create a vertical scrollbar for the Treeview if the list is higher than 8 entries.
        if int(len(users)) > 8:
            self.scrollbar = CTk.CTkScrollbar(tree_frame, orientation="vertical", command=self.tree.yview, height=10, button_color=BUTTON_FG, button_hover_color=BUTTON_HOVER)
            self.tree.configure(yscrollcommand=self.scrollbar.set)
            self.scrollbar.pack(side=RIGHT, fill=Y)  # Position the scrollbar inside the frame by using ".pack()".
            self.scrollbar.bind("<Button-1>", lambda e: self.tools.on_mbtn1_click("Scoreboard", "Scrollbar"))           # Bind the left mouse button click event to the "on_mbtn1_click" method in the "Tools" class, so that the color stays dim while clicked.
            self.scrollbar.bind("<ButtonRelease-1>", lambda e: self.tools.on_mbtn1_release("Scoreboard", "Scrollbar"))  # Bind the left mouse button release event to the "on_mbtn1_release" method in the "Tools" class, so that the color returns to normal when released.

        # Position the Treeview inside the frame by using ".pack()".
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Make sure the frame resizes properly by setting the weight to 1.
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)



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
        global ref_number, username, difficulty, difficulty_num, question_amount, users
        
        self.quiz.final_score = f"{self.quiz.score}/{question_amount}"
        if timer.get() == True:
            self.time = self.quiz.total_time
        else:
            self.time = "Disabled"
        users.append([ref_number, username, difficulty, question_amount, self.time, self.quiz.final_score])  # Add the next user and their quiz details to the "users" list.
        self.tools.save_details(None, "Completion", None, SCOREBOARD_FILE_PATH)  # Save the details to the JSON file.
        self.setup_completion()


    def setup_completion(self):
        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        main_window.columnconfigure(0, weight=1, minsize=0)
        main_window.columnconfigure(1, weight=1, minsize=450)

        # Set up the menu bar.
        completion_menubar = Menu(main_window)  # Create a new menu bar.

        settings_menu = Menu(completion_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        completion_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(completion_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH), value=True)
        timer_settings.add_radiobutton(label="Disabled", variable=timer, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH), value=False)
        history_settings = Menu(completion_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=history_settings, label="Score Deletion History States")
        history_settings.add_radiobutton(label="Disabled", variable=deletion_history_states, value=0, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="10", variable=deletion_history_states, value=10, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="25", variable=deletion_history_states, value=25, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="50", variable=deletion_history_states, value=50, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))

        help_menu = Menu(completion_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        completion_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Completion"))

        main_window.config(menu=completion_menubar)

        # Banner creation (left side)
        lbanner_canvas = Canvas(main_window, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        lbanner_canvas.grid(column=0, row=0, sticky=EW, padx=(20, 0))
        lbanner = Image.open("AppData/Images/lbanner.png")
        lbanner = ImageTk.PhotoImage(lbanner)
        lbanner_canvas.configure(width=lbanner.width()+2, height=lbanner.height())  # Add 2 pixels to width to prevent image clipping on the right of image.
        lbanner_canvas.create_image(lbanner.width() / 2, lbanner.height() / 2, anchor=CENTER, image=lbanner)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        lbanner_canvas.image = lbanner

        # Banner creation (right side)
        rbanner_canvas = Canvas(main_window, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        rbanner_canvas.grid(column=2, row=0, sticky=EW, padx=(0, 20))
        rbanner = Image.open("AppData/Images/rbanner.png")
        rbanner = ImageTk.PhotoImage(rbanner)
        rbanner_canvas.configure(width=rbanner.width()+2, height=rbanner.height())  # Add 2 pixels to width to prevent image clipping on the left of image.
        rbanner_canvas.create_image(rbanner.width() / 2, rbanner.height() / 2, anchor=CENTER, image=rbanner)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        rbanner_canvas.image = rbanner

        # Set up the main content frame to place the main completion frames and elements inside.
        self.main_content_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.main_content_frame.grid(column=1, row=0, sticky=EW, padx=35, pady=(0,20))

        # Logo creation
        self.logo_canvas = Canvas(self.main_content_frame, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        self.logo_canvas.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,0))
        self.logo = Image.open("AppData/Images/logo.png")
        self.logo = ImageTk.PhotoImage(self.logo)
        self.logo_canvas.configure(width=410, height=self.logo.height()+5)  # Add 5 pixels to height to prevent image clipping on the bottom of image.
        self.logo_canvas.create_image(410 / 2, self.logo.height() / 2, anchor=CENTER, image=self.logo)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        self.logo_canvas.image = self.logo

        # Set up a content frame to place the main completion elements inside.
        completion_frame1 = CTk.CTkFrame(self.main_content_frame, fg_color=FRAME_FG, corner_radius=10)
        completion_frame1.grid(column=0, row=1, sticky=EW, padx=20, pady=(20,5))

        # Set width for column 0 (1 total) in completion frame 1. Total minimum column width is 410px.
        completion_frame1.columnconfigure(0, weight=1, minsize=410)

        # Create the labels to be placed next to their relevant entry boxes.
        CTk.CTkLabel(completion_frame1, text="Quiz Complete!", font=(DEFAULT_FONT, 18, "bold"), text_color=FONT_COLOUR).grid(column=0, row=0, sticky=EW, padx=5, pady=(20,8))
        CTk.CTkLabel(completion_frame1, text=f"You scored a total of: {self.quiz.score}/{question_amount}", font=(DEFAULT_FONT, 15), text_color=FONT_COLOUR).grid(column=0, row=1, sticky=EW, padx=5)
        CTk.CTkLabel(completion_frame1, text=f"Difficulty: {difficulty}", font=(DEFAULT_FONT, 15), text_color=FONT_COLOUR).grid(column=0, row=2, sticky=EW, padx=5)
        self.total_time_lbl = CTk.CTkLabel(completion_frame1, text="", font=(DEFAULT_FONT, 15), text_color=FONT_COLOUR)  # Make an empty label for the timer until the state of the timer is determined (enabled/disabled).
        self.total_time_lbl.grid(column=0, row=3, sticky=EW, padx=5, pady=(0,20))
        if timer.get() == True:
            self.total_time_lbl.configure(text=self.tools.timer_config("Completion", "Enable", None))  # Use the "timer_config" function to update the label text relative to the state of the timer.
        if timer.get() == False:
            self.total_time_lbl.configure(text=self.tools.timer_config("Completion", "Disable", None))  # Use the "timer_config" function to update the label text relative to the state of the timer.

        # Create a frame to place the buttons inside.
        button_frame = CTk.CTkFrame(self.main_content_frame, fg_color="transparent")
        button_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=(5,0))
        
        # Set width for columns 0-1 (2 total) in the answer frame. Total minimum column width is 410px.
        button_frame.columnconfigure(0, weight=1, minsize=205)
        button_frame.columnconfigure(1, weight=1, minsize=205)

        # Create the buttons.
        CTk.CTkButton(button_frame, text="View Answers",
                      width=200, height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER, font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=0, sticky=EW, padx=(0,5), pady=(0,5))
        CTk.CTkButton(button_frame, text="Retry Quiz",
                      width=200, height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER, font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=1, row=0, sticky=EW, padx=(5,0), pady=(0,5))
        CTk.CTkButton(button_frame, text="Scoreboard", command=lambda: self.quiz.reset_timer("Scoreboard", "Completion"),
                      width=200, height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER, font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=1, sticky=EW, padx=(0,5), pady=(5,0))
        CTk.CTkButton(button_frame, text="Home", command=lambda: self.quiz.reset_timer("Home", "Completion"),
                      width=200, height=30, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER, font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=1, row=1, sticky=EW, padx=(5,0), pady=(5,0))



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
        self.current_index = 0                  # Variable to store the index of the current question, defaulting to 0.
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
        self.final_score = "0/0"                # Variable to store the final score, defaulting to "0/0".
        self.score = 0                          # Variable to store the active score during the quiz, defaulting to 0.


    def exit_quiz(self, command, origin):
        if origin == "Quiz" and command == "Home":
            paused_prior = quiz_paused  # Check if the quiz has been paused prior to pressing the exit button, meaning it shouldn't be paused twice and then unpaused.
            if paused_prior == False: self.pause_quiz()
            response1 = messagebox.askyesno("Exit Quiz", "Are you sure you want to exit the quiz?\nAll progress will be lost.", icon="warning")
            if response1 == True:
                self.stop_timer(command, origin)
            else:
                if paused_prior == False: self.unpause_quiz()
                return
        

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

        if command == "Home" or command == "Restart Quiz" or command == "New Quiz":
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
            if origin == "Completion": self.tools.reset_details(origin, None)  # If the origin is from the completion page, reset the user details so that the home page doesn't remember the previous details.
            elif origin == "Quiz": self.tools.reset_details(origin, None)  # If the origin is from the quiz page, reset the quiz details so that starting the quiz later will use new questions.
            self.question_no = 1
            self.score = 0
            if command == "Home":
                self.tools.clear_widget(self.home.setup_homepage, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the home page.
            elif command == "Scoreboard":
                self.tools.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the scoreboard page.
        elif command == "New Quiz":
            self.tools.reset_details("Quiz", "New")  # Pass "None" action so that all quiz details are cleared.
            self.tools.clear_widget(self.setup_quiz, True, None, None, None)
        elif command == "Restart Quiz":
            self.tools.reset_details("Quiz", "Restart")  # Pass "restart" action so that the question details aren't cleared.
            self.tools.clear_widget(self.setup_quiz, True, None, None, None)


    def pause_quiz(self):
        global quiz_paused
        quiz_paused = True  # Set the flag to indicate that the quiz is paused.
        self.stop_timer(None, None)
        self.pause_start_time = time.time()  # Record the real-world time for when the pause started.
        self.pause_btn.configure(command=self.unpause_quiz, image=self.play_img)
        
        # Create a pause overlay to visually block the quiz content until the quiz is unpaused.
        height = self.question_frame.winfo_height() + self.answer_frame.winfo_height() + 10  # Get the total height of both frames (question and answer frames), including the height of padding.
        self.pause_frame = CTk.CTkFrame(self.main_content_frame, fg_color=FRAME_FG, corner_radius=10)
        self.pause_frame.grid(column=0, row=1, rowspan=2, sticky=EW, padx=20, pady=(5,0))
        
        # Set width for column 0 (1 total) and row 0 (1 total) in the pause frame.
        self.pause_frame.columnconfigure(0, weight=0, minsize=410)
        self.pause_frame.rowconfigure(0, weight=0, minsize=height)

        CTk.CTkLabel(self.pause_frame, text="Quiz Paused", font=(DEFAULT_FONT, 20, "bold"), text_color=FONT_COLOUR).grid(column=0, row=0, columnspan=2, sticky=EW)
        

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
        self.pause_btn.configure(command=self.pause_quiz, image=self.pause_img)
        self.start_timer()     


    # Method for running the timer loop, which updates the elapsed time and timer label every second.
    # This method is called by the "start_timer" method to initiate the timer loop.
    def timer_loop(self):
        if self.timer_active == True:
            current_time = time.time()  # Get the current real-world time in seconds.
            
            # Calculate how long the quiz has been running in total and subtract all time spent paused.
            self.calculated_elapsed_time = int(current_time - self.quiz_start_time - self.total_paused_time)

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
            self.timer_job = self.timer_lbl.after(1000, self.timer_loop)


    # Method for updating the question and answer options for the current question.
    def update_question(self):
        self.current_index = self.question_no - 1  # Remove 1 to correctly index from the lists (as lists start at index 0, but the question numbers start at 1).
        self.current_title = question_details[self.current_index][0]
        self.current_statement = question_details[self.current_index][1]
        self.current_question = question_details[self.current_index][2]
        self.correct_answer = question_details[self.current_index][3]
        self.fake_answers = question_details[self.current_index][4]

        # Shuffle answer options and assign them to buttons
        answer_choices = [self.correct_answer] + self.fake_answers
        random.shuffle(answer_choices)

        self.statement_lbl.configure(text=self.current_statement)
        self.question_lbl.configure(text=self.current_question)

        self.btn_1.configure(text=f" A.    {answer_choices[0]}", command=lambda: self.answer_management(answer_choices[0]))
        self.btn_2.configure(text=f" B.    {answer_choices[1]}", command=lambda: self.answer_management(answer_choices[1]))
        self.btn_3.configure(text=f" C.    {answer_choices[2]}", command=lambda: self.answer_management(answer_choices[2]))
        self.btn_4.configure(text=f" D.    {answer_choices[3]}", command=lambda: self.answer_management(answer_choices[3]))


    # Method for managing the user's answer to the current question.
    def answer_management(self, answer):
        self.user_answers.append(answer)  # Append the user's answer to the list of all their answers.
        
        if answer == self.correct_answer:  # Check if the most recent answer matches the correct answer for the current question.
            self.score += 1 
                
        if self.question_no < question_amount:
            self.question_no += 1
            self.question_no_lbl.configure(text=f"Question {self.question_no}/{question_amount}")  # Update the question number label.
            self.update_question()

        else:
            self.stop_timer(None, "Quiz")
            self.tools.reset_details("Quiz", None)
            self.tools.clear_widget(self.completion.submit_details, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the completion page.


    def hard_mode(self):
        return
    

    def medium_mode(self):
        return
    

    def easy_mode(self):
        global question_details, fake_answers
        #question_topic = random.randint(0, 1)
        question_topic = 1  # For testing, use just the one step equation algebra question type.
        if question_topic == 0:  # If the random number is 0, then the question topic is triangle area.
            return
        elif question_topic == 1:  # If the random number is 1, then the question topic is one step equation algebra.
            for i in range(question_amount):
                letters = ['x', 'y', 'z', 'a', 'b', 'c', 'm', 'n']
                letter1 = random.choice(letters)
                question_title = "One Step Equations"
                question_statement = f"Solve for {letter1}:"
                
                question_type = random.randint(0, 3)
                if question_type == 0:
                    # e.g. a - 2 = 4 >> a = 6
                    number1 = random.randint(1, 20)
                    number2 = random.randint(1, 50)
                    question = f"{letter1} - {number1} = {number2}"
                    answer = number2+number1
                elif question_type == 1:
                    # e.g. a + 2 = 4 >> a = 2
                    number1 = random.randint(1, 20)
                    number2 = random.randint(1, 50)
                    question = f"{letter1} + {number1} = {number2}"
                    answer = number2-number1
                elif question_type == 2:
                    # e.g. 2a = 4 >> a = 2
                    number1 = random.randint(1, 10)
                    number2 = random.randint(number1, number1+10)  # Ensure that the second number is greater than the first number, by making the minimum value as "number1" and the maximum value as "number1" + 50.
                    question = f"{number1}{letter1} = {number2}"
                    answer = number2/number1
                elif question_type == 3:
                    # e.g. a / 2 = 4 >> a = 8
                    number1 = random.randint(1, 12)
                    number2 = random.randint(1, 12)
                    question = f"{letter1} / {number1} = {number2}"
                    answer = number2*number1

                formatted_answer = str(int(answer)) if answer == int(answer) else "{:.2f}".format(answer)  # Format the answer to 2 decimal places if it is a float (decimal number).

                fake_answers = []
                while len(fake_answers) < 3:  # Generate 3 fake answers for each question.
                    offset = random.choice([-1, 1]) * random.randint(2, 10)  # Generate a random offset between -2 or 2 and -20 or 20.
                    distractor = answer + offset
                    formatted_fake = str(int(distractor)) if distractor == int(distractor) else "{:.2f}".format(distractor)  # Format the answer to 2 decimal places if it is a float (decimal number).
                    if formatted_fake != formatted_answer and formatted_fake not in fake_answers:  # Check if the formatted fake answer is different from the correct answer and not already in the list of fake answers.
                        fake_answers.append(formatted_fake)  # Append each formatted fake answer to the fake answers list.

                # Append the question details to the question_details list.
                question_details.append([question_title, question_statement, question, formatted_answer, fake_answers])
        return


    # Procedure for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
    def setup_quiz(self):
        global quiz_paused
        quiz_paused = False  # Set the flag to indicate that the quiz is not paused.

        # Set the difficulty level of the quiz.
        if difficulty == "Easy":
            self.easy_mode()
        elif difficulty == "Medium":
            self.easy_mode()  # Use easy mode till medium mode is implemented
        elif difficulty == "Hard":
            self.easy_mode()  # Use easy mode till hard mode is implemented

        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        main_window.columnconfigure(0, weight=1, minsize=0)
        main_window.columnconfigure(1, weight=1, minsize=450)

        # Set up the menu bar.
        quiz_menubar = Menu(main_window)  # Create a new menu bar.
        
        quiz_menu = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        quiz_menubar.add_cascade(label="Quiz", menu=quiz_menu)
        quiz_menu.add_command(label="Restart Quiz", accelerator="Ctrl+R", command=lambda: self.stop_timer("Restart Quiz", "Quiz"))
        quiz_menu.add_command(label="New Quiz", accelerator="Ctrl+N", command=lambda: self.stop_timer("New Quiz", "Quiz"))
        quiz_menu.add_command(label="Exit Quiz", accelerator="Esc", command=lambda: self.exit_quiz("Home", "Quiz"))

        settings_menu = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        quiz_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, command=lambda: self.tools.timer_config("Quiz Menubar", "Enable", self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH)), value=True)        # Use lambda so that the method is called only when the radiobutton is clicked, rather than when it's defined.
        timer_settings.add_radiobutton(label="Disabled", variable=timer, command=lambda: self.tools.timer_config("Quiz Menubar", "Disable", self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH)), value=False)     # Use lambda so that the method is called only when the radiobutton is clicked, rather than when it's defined.
        history_settings = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=history_settings, label="Score Deletion History States")
        history_settings.add_radiobutton(label="Disabled", variable=deletion_history_states, value=0, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="10", variable=deletion_history_states, value=10, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="25", variable=deletion_history_states, value=25, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="50", variable=deletion_history_states, value=50, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))

        help_menu = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        quiz_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Quiz"))

        main_window.config(menu=quiz_menubar)

        # Bind key shortcuts to perform actions.
        main_window.bind("<Control-r>", lambda e: self.stop_timer("Restart Quiz", "Quiz"))  # Bind Ctrl+R to restart the quiz.
        main_window.bind("<Control-n>", lambda e: self.stop_timer("New Quiz", "Quiz"))      # Bind Ctrl+N to start a new quiz.
        main_window.bind("<Escape>", lambda e: self.exit_quiz("Home", "Quiz"))              # Bind Escape to exit the quiz and return to the home page.
        self.binded_keys = ["<Control-r>", "<Control-n>", "<Escape>"]                       # Create a list of binded keys to be used later for unbinding them when the user goes to a different page.

        # Banner creation (left side)
        lbanner_canvas = Canvas(main_window, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        lbanner_canvas.grid(column=0, row=0, sticky=EW, padx=(20, 0))
        lbanner = Image.open("AppData/Images/lbanner.png")
        lbanner = ImageTk.PhotoImage(lbanner)
        lbanner_canvas.configure(width=lbanner.width()+2, height=lbanner.height())  # Add 2 pixels to width to prevent image clipping on the right of image.
        lbanner_canvas.create_image(lbanner.width() / 2, lbanner.height() / 2, anchor=CENTER, image=lbanner)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        lbanner_canvas.image = lbanner

        # Banner creation (right side)
        rbanner_canvas = Canvas(main_window, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        rbanner_canvas.grid(column=2, row=0, sticky=EW, padx=(0, 20))
        rbanner = Image.open("AppData/Images/rbanner.png")
        rbanner = ImageTk.PhotoImage(rbanner)
        rbanner_canvas.configure(width=rbanner.width()+2, height=rbanner.height())  # Add 2 pixels to width to prevent image clipping on the left of image.
        rbanner_canvas.create_image(rbanner.width() / 2, rbanner.height() / 2, anchor=CENTER, image=rbanner)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        rbanner_canvas.image = rbanner

        # Set up the main content frame to place the main quiz frames and elements inside.
        self.main_content_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.main_content_frame.grid(column=1, row=0, sticky=EW, padx=35, pady=(24,25))

        # Set up a content frame to place the top quiz elements inside.
        quiz_dtls_frame1 = CTk.CTkFrame(self.main_content_frame, fg_color=FRAME_FG, corner_radius=10)
        quiz_dtls_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(0,5))
        
        # Set width for columns 0-2 (3 total) in quiz details frame 1. Total minimum column width is 410px.
        quiz_dtls_frame1.columnconfigure(0, weight=0, minsize=185)
        quiz_dtls_frame1.columnconfigure(1, weight=0, minsize=40)
        quiz_dtls_frame1.columnconfigure(2, weight=0, minsize=185)

        main_window.button_image_1 = Image.open("AppData/Images/pause.png")  # Load the pause button image.
        self.pause_image = main_window.button_image_1  # Assign the loaded image to a variable for use in the pause button.
        self.pause_img = CTk.CTkImage(self.pause_image, size=(16, 17))  # Create a CTkImage object with the pause image to allow scaling to be used.

        main_window.button_image_2 = Image.open("AppData/Images/play.png")  # Load the pause button image.
        self.play_image = main_window.button_image_2  # Assign the loaded image to a variable for use in the pause button.
        self.play_img = CTk.CTkImage(self.play_image, size=(16, 17))  # Create a CTkImage object with the pause image to allow scaling to be used.

        # Create the labels and pause button to be placed at the top of the quiz page.
        self.question_no_lbl = CTk.CTkLabel(quiz_dtls_frame1, text=f"Question: {self.question_no}/{question_amount}", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR)
        self.question_no_lbl.grid(column=0, row=0, pady=10, sticky=NSEW)
        self.pause_btn = CTk.CTkButton(quiz_dtls_frame1, text=None, font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR, command=self.pause_quiz, width=40, height=30, corner_radius=7.5, image=self.pause_img, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER)
        self.pause_btn.grid(column=1, row=0, pady=10)
        self.timer_lbl = CTk.CTkLabel(quiz_dtls_frame1, text="", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR)  # Make an empty label for the timer until the state of the timer is determined (enabled/disabled).
        self.timer_lbl.grid(column=2, row=0, pady=10, sticky=NSEW)
        if timer.get() == True:
            self.timer_lbl.configure(text=self.tools.timer_config("Quiz", "Enable", None))
        elif timer.get() == False:
            self.timer_lbl.configure(text=self.tools.timer_config("Quiz", "Disable", None))

        # Create a frame for the question label or question image.
        self.question_frame = CTk.CTkFrame(self.main_content_frame, fg_color=FRAME_FG, corner_radius=10)
        self.question_frame.grid(column=0, row=1, sticky=EW, padx=20, pady=5)
        
        # Set width for column 0 (1 total) and row 0 (1 total) in quiz details frame 1.
        self.question_frame.columnconfigure(0, weight=0, minsize=410)
        self.question_frame.rowconfigure(0, weight=0, minsize=50)
        self.question_frame.rowconfigure(1, weight=0, minsize=155)

        self.current_title = question_details[self.current_index][0]
        self.current_statement = question_details[self.current_index][1]
        self.current_question = question_details[self.current_index][2]
        self.correct_answer = question_details[self.current_index][3]
        self.fake_answers = question_details[self.current_index][4]

        # Create a label for the title text.
        self.title_lbl = CTk.CTkLabel(self.question_frame, text=self.current_title, font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR)
        self.title_lbl.grid(column=0, row=0, sticky=S, padx=20)

        # Create a canvas for question images.
        #self.question_canvas = CTk.CTkCanvas(self.question_frame, bd=0, highlightthickness=0)
        #self.question_canvas.grid(row=1, column=0, padx=20)
        
        self.inner_frame = CTk.CTkFrame(self.question_frame, fg_color="#78b0f4", corner_radius=10)
        self.inner_frame.grid(column=0, row=1, padx=20)
        self.inner_frame.columnconfigure(0, weight=0, minsize=370)
        self.inner_frame.rowconfigure(0, weight=0, minsize=55)
        self.inner_frame.rowconfigure(1, weight=0, minsize=60)

        # Create a label for the statement text regarding the question.
        self.statement_lbl = CTk.CTkLabel(self.inner_frame, text=self.current_statement, font=(DEFAULT_FONT, 20, "bold"), text_color=FONT_COLOUR, pady=0)
        self.statement_lbl.grid(column=0, row=0, padx=20)

        # Create a label for the question text.
        self.question_lbl = CTk.CTkLabel(self.inner_frame, text=self.current_question, font=(DEFAULT_FONT, 22, "bold"), text_color=FONT_COLOUR, pady=0)
        self.question_lbl.grid(column=0, row=1, pady=(0,15))

        # Create a frame for the answer buttons
        self.answer_frame = CTk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.answer_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=(5,0))
        
        # Set width for columns 0-1 (2 total) in the answer frame. Total minimum column width is 410px.
        self.answer_frame.columnconfigure(0, weight=0, minsize=205)
        self.answer_frame.columnconfigure(1, weight=0, minsize=205)
        
        # Create a list of the answers and shuffle them.
        answer_choices = [self.correct_answer] + self.fake_answers
        random.shuffle(answer_choices)

        # Create the answer buttons.
        self.btn_1 = CTk.CTkButton(self.answer_frame, text=f" A.    {answer_choices[0]}", font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR, command=lambda: self.answer_management(answer_choices[0]), anchor=W, width=200, height=40, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER)
        self.btn_1.grid(column=0, row=0, padx=(0, 5), pady=(0,5))
        self.btn_2 = CTk.CTkButton(self.answer_frame, text=f" B.    {answer_choices[1]}", font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR, command=lambda: self.answer_management(answer_choices[1]), anchor=W, width=200, height=40, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER)
        self.btn_2.grid(column=1, row=0, padx=(5, 0), pady=(0,5))
        self.btn_3 = CTk.CTkButton(self.answer_frame, text=f" C.    {answer_choices[2]}", font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR, command=lambda: self.answer_management(answer_choices[2]), anchor=W, width=200, height=40, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER)
        self.btn_3.grid(column=0, row=1, padx=(0, 5), pady=(5,0))
        self.btn_4 = CTk.CTkButton(self.answer_frame, text=f" D.    {answer_choices[3]}", font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR, command=lambda: self.answer_management(answer_choices[3]), anchor=W, width=200, height=40, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER)
        self.btn_4.grid(column=1, row=1, padx=(5, 0), pady=(5,0))

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


    # Method for processing slider values and returning a tuple containing the difficulty, color, and hover color, or the number of questions.
    def process_slider_value(self, slider_id, value):
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
            return ([difficulty, color, hover_color])
        if slider_id == "S2":
            return (f"{int(value)} Questions")

    
    # Method for updating the difficulty label, difficulty slider, and question amount label based on slider values processed by the "process_slider_value" function.
    def slider_label_update(self, slider_id, value):
        if slider_id == "S1":
                self.difficulty_lbl.configure(text=self.process_slider_value(slider_id, value)[0])
                self.difficulty_slider.configure(button_color=self.process_slider_value(slider_id, value)[1], 
                                                 progress_color=self.process_slider_value(slider_id, value)[1], 
                                                 button_hover_color=self.process_slider_value(slider_id, value)[2])
        if slider_id == "S2":
            self.question_amnt_lbl.configure(text=self.process_slider_value(slider_id, value))


    # Method to insert the chosen option from the autocomplete
    def insert_method(self, e):
        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, e)


    # Procedure for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
    def setup_homepage(self):
        global users, deiconify_reqd

        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        # Setting the main window size before element creation ensures the window doesn't glitch between sizes.
        main_window.columnconfigure(0, weight=1, minsize=0)
        main_window.columnconfigure(1, weight=1, minsize=450)
        main_window.columnconfigure(2, weight=1, minsize=0)

        # Set up the menu bar.
        home_menubar = Menu(main_window)

        settings_menu = Menu(home_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        home_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(home_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, value=True, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        timer_settings.add_radiobutton(label="Disabled", variable=timer, value=False, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings = Menu(home_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=history_settings, label="Score Deletion History States")
        history_settings.add_radiobutton(label="Disabled", variable=deletion_history_states, value=0, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="10", variable=deletion_history_states, value=10, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="25", variable=deletion_history_states, value=25, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="50", variable=deletion_history_states, value=50, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))

        help_menu = Menu(home_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        home_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Home"))

        main_window.config(menu=home_menubar)

        # Banner creation (left side)
        lbanner_canvas = Canvas(main_window, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        lbanner_canvas.grid(column=0, row=0, sticky=EW, padx=(20, 0), pady=27)
        lbanner = Image.open("AppData/Images/lbanner.png")
        lbanner = ImageTk.PhotoImage(lbanner)
        lbanner_canvas.configure(width=lbanner.width()+2, height=lbanner.height())  # Add 2 pixels to width to prevent image clipping on the right of image.
        lbanner_canvas.create_image(lbanner.width() / 2, lbanner.height() / 2, anchor=CENTER, image=lbanner)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        lbanner_canvas.image = lbanner

        # Banner creation (right side)
        rbanner_canvas = Canvas(main_window, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        rbanner_canvas.grid(column=2, row=0, sticky=EW, padx=(0, 20), pady=27)
        rbanner = Image.open("AppData/Images/rbanner.png")
        rbanner = ImageTk.PhotoImage(rbanner)
        rbanner_canvas.configure(width=rbanner.width()+2, height=rbanner.height())  # Add 2 pixels to width to prevent image clipping on the left of image.
        rbanner_canvas.create_image(rbanner.width() / 2, rbanner.height() / 2, anchor=CENTER, image=rbanner)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        rbanner_canvas.image = rbanner

        # Set up the main content frame to place the main home frames and elements inside.
        self.main_content_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.main_content_frame.grid(column=1, row=0, sticky=EW, padx=35, pady=(0,20))

        # Logo creation
        self.logo_canvas = Canvas(self.main_content_frame, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        self.logo_canvas.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,0))
        self.logo = Image.open("AppData/Images/logo.png")
        self.logo = ImageTk.PhotoImage(self.logo)
        self.logo_canvas.configure(width=410, height=self.logo.height()+5)  # Add 5 pixels to height to prevent image clipping on the bottom of image.
        self.logo_canvas.create_image(410 / 2, self.logo.height() / 2, anchor=CENTER, image=self.logo)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        self.logo_canvas.image = self.logo

        # Set up a content frame to place the main home elements inside.
        home_frame1 = CTk.CTkFrame(self.main_content_frame, fg_color=FRAME_FG, corner_radius=10)
        home_frame1.grid(column=0, row=1, sticky=EW, padx=20, pady=(20,5))

        # Set width for columns 0-2 (3 total) in home frame 1. Total minimum column width is 410px.
        home_frame1.columnconfigure(0, weight=0, minsize=100)
        home_frame1.columnconfigure(1, weight=0, minsize=210)
        home_frame1.columnconfigure(2, weight=0, minsize=100)

        # Create the labels to be placed next to their relevant entry boxes.
        CTk.CTkLabel(home_frame1, text="Username", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=0, sticky=E, padx=(0,5), pady=(20,0))
        CTk.CTkLabel(home_frame1, text="Difficulty", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=1, sticky=E, padx=(0,5), pady=15)
        CTk.CTkLabel(home_frame1, text="Questions", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=2, sticky=E, padx=(0,5), pady=(0,20))

        self.difficulty_lbl = CTk.CTkLabel(home_frame1, text="", font=(DEFAULT_FONT, 12, "bold"), text_color=FONT_COLOUR)     # Create an empty placeholder label to display the difficulty level.
        self.difficulty_lbl.grid(column=2, row=1, sticky=W, padx=(5,0), pady=15)
        self.question_amnt_lbl = CTk.CTkLabel(home_frame1, text="", font=(DEFAULT_FONT, 12, "bold"), text_color=FONT_COLOUR)  # Create an empty placeholder label to display the number of questions.
        self.question_amnt_lbl.grid(column=2, row=2, sticky=W, padx=(5,0), pady=(0,20))

        # Set up the username entry, which is either an entry box if there are no usernames saved, or a combo box if there are usernames saved. This prevents the user from trying to open a combo box dropdown when there are no usernames saved.
        usernames = [user[1] for user in users]
        if usernames == []:  # Check if the usernames list is empty
            self.username_entry = CTk.CTkEntry(home_frame1, fg_color="#73ace0", border_color="#6aa5db", text_color=FONT_COLOUR, corner_radius=10)
            self.username_entry.insert(0, "")
            self.entry_type = "CTkEntry"
        else:
            # Setup combo box and sliders (scales).
            self.username_entry = CTk.CTkComboBox(home_frame1, fg_color="#73ace0", border_color="#6aa5db", button_color="#6aa5db", button_hover_color="#5997d5", text_color=FONT_COLOUR, corner_radius=10)
            self.username_entry.set("")
            self.entry_type = "CTkComboBox"
            # Attach the scrollable dropdown library to the username entry combo box.
            self.dropdown = CTkScrollableDropdown(self.username_entry, values=[""], justify="left", button_color="transparent", fg_color="#73ace0", bg_color=FRAME_FG, frame_border_color="#6aa5db", frame_corner_radius=10,
                                                  scrollbar_button_color="#5997d5", scrollbar_button_hover_color="#497caf", hover_color=MENU_HOVER, text_color=FONT_COLOUR, autocomplete=True)
            self.dropdown.configure(values=usernames)  # Set the values of the combo box to the usernames of the users in the users list (user[1])
            # CTkScrollableDropdown library utilises "transient()" to stay on top, so after destroying the combo box (by going to a new page - Scoreboard or Quiz) and creating it again (going back to the Home page), the main window needs to be focused. 
            # If this isn't done, the focus will go back to the dropdown and prevent interaction with the combo box entry section, stopping users from being able to type inside it.
            main_window.focus_force()  # Focus the main window to ensure interaction with the combo box entry section.
        self.username_entry.grid(column=1, row=0, padx=5, pady=(20,0), sticky=EW)

        self.difficulty_slider = CTk.CTkSlider(home_frame1, from_=0, to=2, number_of_steps=2, command=lambda value: self.slider_label_update("S1", value), orientation=HORIZONTAL, fg_color="#73ace0", button_color="#4d97e8")
        self.difficulty_slider.grid(column=1, row=1, padx=5, pady=15, sticky=EW)
        self.questions_slider = CTk.CTkSlider(home_frame1, from_=5, to=35, number_of_steps=30, command=lambda value: self.slider_label_update("S2", value), orientation=HORIZONTAL, progress_color="#4d97e8", fg_color="#73ace0", button_color="#4d97e8", button_hover_color="#3b83c4")
        self.questions_slider.grid(column=1, row=2, padx=5, pady=(0,20), sticky=EW)
        
        # Update the value of the entry box and the sliders (scales) with the previously recorded values (used for going from scoreboard back to homepage).
        if username != None:
            if self.entry_type == "CTkEntry":  # Check if the username entry is an entry box, as combo boxes don't support the "insert" method but entry boxes do.
                self.username_entry.insert(0, username)
            elif self.entry_type == "CTkComboBox":  # Check if the username entry is a combo box, as entry boxes don't support the "set" method but combo boxes do.
                self.username_entry.set(username)
        if difficulty_num != None:
            self.difficulty_slider.set(difficulty_num)
        if question_amount != None:
            self.questions_slider.set(question_amount)

        # Update the labels next to the sliders with their relevant values.
        self.slider_label_update("S1", self.difficulty_slider.get())
        self.slider_label_update("S2", self.questions_slider.get())

        # Create a frame to place the buttons inside.
        button_frame = CTk.CTkFrame(self.main_content_frame, fg_color="transparent")
        button_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=(5,20))
        
        # Set width for columns 0-1 (2 total) in the button frame. Total minimum column width is 410px.
        button_frame.columnconfigure(0, weight=0, minsize=205)
        button_frame.columnconfigure(1, weight=0, minsize=205)

        # Create the buttons.
        CTk.CTkButton(button_frame, text="Scoreboard", command=lambda: self.tools.save_details("Scoreboard", "Home", "Temporary", None),
                      width=200, height=35, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER, font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=1, sticky=EW, padx=(0,5))
        CTk.CTkButton(button_frame, text="Start", command=lambda:self.tools.save_details("Quiz", "Home", "Permanent", None),
                      width=200, height=35, corner_radius=10, fg_color=BUTTON_FG, hover_color=BUTTON_HOVER, font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=1, row=1, sticky=EW, padx=(5,0))
        
        if deiconify_reqd == True:   # Check if deiconify is required, which is True when the main window is first created on program start. 
            main_window.deiconify()  # Show the main window after all elements are created to prevent flickering of the window before the UI is set up.
            deiconify_reqd = False   # Set the flag to False so that the main window is not deiconified again when the Home page is set up again.



# Main function for starting the program.
def main(): 
    global operating_system, APP_VERSION, main_window, deiconify_reqd, MAIN_WINDOW_BG, FRAME_FG, BUTTON_FG, BUTTON_HOVER, BUTTON_CLICKED, MENU_ACTIVE_FG, MENU_HOVER, FONT_COLOUR, DEFAULT_FONT  # Global variables and constants for the operating system and window UI elements/design.
    global full_directory, initial_pdf_directory, INITIAL_PDF_NAME, SCOREBOARD_FILE_PATH, SETTINGS_FILE_PATH  # Global variables and constants for the file paths of the general directories, JSON files, and the PDF scoreboard file.
    global users, quiz_paused, username, difficulty_num, question_amount, question_details, settings, default_settings, timer, deletion_history_states, history_stack, redo_stack, data_loaded  # Global lists and variables for data and flags

    # Get the operating system name to manage functionalities in the program with limited support for multiple operating systems.
    # When run on Linux, this will return "Linux". On macOS, this will return "Darwin". On Windows, this will return "Windows".
    operating_system = platform.system()

    # Set the version number of the program.
    APP_VERSION = "3.0.0"

    # Configure the main window and the variables used for UI element design.
    main_window = Tk()                              # Initialise the main window. For scaling reasons, use a Tk window instead of CTk.
    main_window.withdraw()                          # Hide the main window until all elements are created, preventing a flicker of the window before the UI is set up.
    deiconify_reqd = True                           # Initialise a flag to track whether the main window should be deiconified (shown) after all elements are created.
    CTk.deactivate_automatic_dpi_awareness()        # Deactivate the automatic DPI awareness of the CTk library, allowing it to work with Tkinter's DPI scaling. This resolves an issue with the custom combobox not scaling correctly.
    main_window.title("QWhizz Math")                # Set the title of the window.
    if os.path.exists("AppData/Images/icon.png"):   # Check if the icon file exists before setting it.
        main_window.iconphoto(False, PhotoImage(file="AppData/Images/icon.png"))  # Set the title bar icon.
    main_window.resizable(False, False)         # Set the resizable property for height and width to False.
    
    # Colour hex code for UI elements
    MAIN_WINDOW_BG = "#d0ebfc"                  # Set the background colour to be used for the main window.
    FRAME_FG = "#87bcf4"                        # Set the foreground colour to be used for all frames.
    BUTTON_FG = "#5ba2ef"                       # Set the foreground colour to be used for all buttons.
    BUTTON_HOVER = "#4c93e3"                    # Set the hover colour to be used for all buttons.
    BUTTON_CLICKED = "#4989d8"                  # Set the clicked colour to be used for all buttons.
    MENU_ACTIVE_FG = "#FFFFFF"                  # Set the foreground colour to be used for active menu items.
    MENU_HOVER = "#a3cbf5"                      # Set the hover colour to be used for all menu items.
    FONT_COLOUR = "#FFFFFF"                     # Set the font colour to be used for all CTk elements.
    
    # Default program font
    DEFAULT_FONT = "Segoe UI"                   # Set the default font to be used for all CTk elements.

    # Setup the directories and paths for saving and loading data.
    full_directory = f"{os.path.dirname(os.path.abspath(__file__))}/AppData"  # Get the absolute intended path of the JSON files for debugging purposes when errors and warnings occur, storing it in "full_directory".
    initial_pdf_directory = f"{os.path.dirname(os.path.abspath(__file__))}"      # Get the absolute intended path of the PDF scoreboard file for debugging purposes when errors and warnings occur, storing it in "initial_pdf_directory".
    INITIAL_PDF_NAME = "QWhizz Math Scoreboard.pdf"      # Set the file path for the scoreboard PDF file.
    SCOREBOARD_FILE_PATH = "AppData/scoreboard.json"  # Set the file path for the scoreboard JSON file.
    SETTINGS_FILE_PATH = "AppData/settings.json"      # Set the file path for the settings JSON file.

    # Initialise global lists and variables.
    users = []                              # Create empty list for user details and their quiz results to be stored inside.
    quiz_paused = False                     # Initialise a flag to track whether the quiz is paused or not.
    username = None                         # Initialise the username attribute as None.
    difficulty_num = None                   # Initialise the difficulty_num attribute as None.
    question_amount = None                  # Initialise the question_amount attribute as None.
    question_details = []                   # Create empty list for question details to be stored inside.
    settings = []                           # Create empty list for settings to be stored inside.
    default_settings = {"enable_timer": True, "deletion_history_states": 10}             # Create a dictionary for default settings, with the "enable_timer" key set to True and the "deletion_history_states" (amount of deletion events that can be undone) key set to 10. This will be used to store the default settings for the program.
    timer = BooleanVar(value=default_settings["enable_timer"])                           # Create a "timer" BooleanVar global reference to control the timer checkbutton state, with the default value being dependent on the "enable_timer" key in the "default_settings" dictionary, setting the checkbutton in an on state.
    deletion_history_states = IntVar(value=default_settings["deletion_history_states"])  # Create a "deletion_history_states" IntVar global reference to control the deletion history states checkbutton state, with the default value being dependent on the "deletion_history_states" key in the "default_settings" dictionary, setting the "10" checkbutton in an on state.
    history_stack = []                      # Create an empty list stack to store deleted scores, used for undo functionality.
    redo_stack = []                         # Create an empty list stack to store undone deletions, used for redo functionality.
    data_loaded = False                     # Initialise a flag to track whether the JSON file data has been loaded, setting it to False so that the program will attempt to reload data from the file before displaying the scoreboard.

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

    # Load the data from the JSON files and start the home page.
    tools.load_details("scoreboard", SCOREBOARD_FILE_PATH, "users")     # Load the user scores from the scoreboard.json file.
    tools.load_details("settings", SETTINGS_FILE_PATH, "settings")      # Load the settings from the settings.json file.
    main_window.configure(bg=MAIN_WINDOW_BG)                            # Configure the main window to use the background colour (value) of the "MAIN_WINDOW_BG variable".
    home_page.setup_homepage()                                          # Call the "setup_homepage" method from the "home_page" class instance to set up the home page UI elements.

    # Start the CTkinter event loop so that the GUI window stays open.
    main_window.mainloop()


# Run the program file only if the script is being run directly as the main program (not imported as a module).
if __name__ == "__main__":
    main()  # Run the main function.