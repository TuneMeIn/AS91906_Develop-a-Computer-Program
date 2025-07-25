# Date Created: 13/07/2025
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
from tkinter import ttk, messagebox, filedialog, font
import customtkinter as CTk
from AppData.CTkScrollableDropdown import *
from PIL import Image, ImageTk, ImageDraw
from fpdf import FPDF
from fpdf.enums import TableCellFillMode
from fpdf.fonts import FontFace
from datetime import datetime
import json, time, random, os, platform, subprocess, math

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
        self.button_pressed = False             # Flag variable to store whether a button is currently being pressed.


    # Method for clearing all widgets or clearing specified widgets (column, row).
    def clear_widget(self, procedure, all_widgets, element, column, row, command):
        if command != None: command()  # Go to the specified procedure from passed command if it is specified.
        if all_widgets == True and element == None:
            # Clear all page content.
            for widget in main_window.winfo_children():
                widget.destroy()
            if procedure != None: procedure()  # Go to the specified procedure from button command if it is specified.
        
        elif all_widgets == True and element != None:
            # Clear all content of the specified element.
            for widget in element.winfo_children():
                widget.destroy()
            if procedure != None: procedure()  # Go to the specified procedure from button command if it is specified.
        
        elif all_widgets == False:
            # Find all widgets in the specified row and column of a specified element.
            for widget in element.grid_slaves(column=column, row=row):
                widget.destroy()  # Destroy the widgets occupying the specified space.
            if procedure != None: procedure()  # Go to the specified procedure from button command if it is specified.


    # Method for handling mouse button 1 release events.
    def on_mbtn1_release(self, origin, element):
        if origin == "Scoreboard":
            if element == "Scrollbar":
                self.scoreboard.scrollbar.configure(button_color=BUTTON_FG, button_hover_color=BUTTON_HOVER)  # Change the scrollbar button colour back to a light blue when released.


    # Method for handling mouse button 1 click events.
    def on_mbtn1_click(self, origin, element):
        if origin == "Scoreboard":
            if element == "Scrollbar":
                self.scoreboard.scrollbar.configure(button_color=BUTTON_CLICKED, button_hover_color=BUTTON_CLICKED)  # Change the scrollbar button colour to a darker blue when clicked and/or held.


    # Method for handling the event of the mouse cursor leaving (hovering away from) a button.
    def on_ctkbutton_leave(self, button):
        self.cursor_over_button = False
        if self.button_pressed == False:
            button.configure(fg_color=BUTTON_FG)
        return


    # Method for handling the event of the mouse cursor entering (hovering over) a button.
    def on_ctkbutton_enter(self, button):
        self.cursor_over_button = True
        button.configure(fg_color=BUTTON_CLICKED) if self.button_pressed == True else button.configure(fg_color=BUTTON_HOVER)
        button.bind("<Leave>", lambda e: self.on_ctkbutton_leave(button))
        return
    

    # Method for handling the event of the left mouse button being released over a button.
    def on_ctkbutton_release(self, button, sizes, command):
        self.button_pressed = False
        
        # Ensure that when releasing the button, the forground colour is set to the hover colour if the mouse cursor is still hovering over the button, otherwise it is set to the original colour.
        if self.cursor_over_button == True:
            # Change the button colour back to its original colour and size (animated buttons only) when released.
            button.configure(fg_color=BUTTON_HOVER, width=sizes[0], height=sizes[1], font=(DEFAULT_FONT, sizes[2], "bold")) if sizes != None else button.configure(fg_color=BUTTON_HOVER)
        else:
            # Change the button colour back to its original colour and size (animated buttons only) when released.
            button.configure(fg_color=BUTTON_FG, width=sizes[0], height=sizes[1], font=(DEFAULT_FONT, sizes[2], "bold")) if sizes != None else button.configure(fg_color=BUTTON_FG)
        
        button.unbind("<ButtonRelease-1>")
        if command != None: command()
        return


    # Method for handling the event of a button being clicked (command is sent from the button rather than checking if the cursor specifically clicks on the button).
    def on_ctkbutton_click(self, button, sizes, command):  # Sizes is a list containing the width, height and font size of the button.
        self.cursor_over_button = True
        self.button_pressed = True
        
        # Change the button colour and size when clicked and/or held. Non-animated buttons will pass None as the "sizes" variable.
        button.configure(fg_color=BUTTON_CLICKED, width=sizes[0]*0.9, height=sizes[1]*0.9, font=(DEFAULT_FONT, sizes[2]*0.9, "bold")) if sizes != None else button.configure(fg_color=BUTTON_CLICKED)
        
        button.bind("<Leave>", lambda e: self.on_ctkbutton_leave(button))
        button.bind("<ButtonRelease-1>", lambda e: self.on_ctkbutton_release(button, sizes, command))
        return


    # Method for handling errors and preventing repeated code.
    def error_control(self, file_name, file_dir, file_data, control):
        global users, settings, timer, enable_trigonometry, enable_algebra, deletion_history_states
        
        # Temporary storage mode
        if control == "Temporary":
            if file_data == "users": users = []          # If the "file_data" variable is set to "users", make "users" as an empty list.
            elif file_data == "settings":
                settings = default_settings  # If the "file_data" variable is set to "settings", make "settings" store the default settings.
                timer.set(settings.get("enable_timer"))                               # Set the timer to the value stored in the "default_settings" dictionary.
                enable_trigonometry.set(settings.get("enable_trigonometry"))          # Set "enable_trigonometry" to the value stored in the "default_settings" dictionary.
                enable_algebra.set(settings.get("enable_algebra"))                    # Set "enable_algebra" to the value stored in the "default_settings" dictionary.
                deletion_history_states.set(settings.get("deletion_history_states"))  # Set the deletion history states to the value stored in the "default_settings" dictionary.
        return  # Exit the function after handling the error control for temporary storage mode.


    # Method for opening a specified file from within the program.
    def open_file(self, origin, file_dir, file_name):
        if origin == "Quiz" and quiz_paused == False: 
            self.quiz.pause_quiz()    # Pause the quiz if a file is opened from the "Quiz" window and the quiz is not already paused.

        if not os.path.exists(file_dir):
            messagebox.showwarning("File Not Found", f"The {file_name} file cannot be found. Please download the file from the GitHub repository and try again.")
            os.startfile("https://github.com/TuneMeIn/AS91906_Develop-a-Computer-Program")
            return

        try:
            os.startfile(file_dir)
        
        # Error control for instances such as the file being inaccessible or lacking the permission to read it.
        except IOError as io_error:
            messagebox.showwarning("File Error", f"An error occurred while reading the {file_name} file.\n\n{io_error}\n\n{file_dir}")  # Show an error message if the file cannot be read.
        
        # Error control for any other exceptions that may occur.
        except Exception as e:
            messagebox.showwarning("Unexpected Error", f"An unexpected error occurred while reading the {file_name} file.\n\n{e}\n\n{file_dir}")  # Show an error message if there is an unexpected error.

    
    # Procedure for loading the "users" and "settings" lists from the JSON files.
    def load_details(self, file_name, file_dir, file_data):
            global data_loaded, users, settings, timer, enable_trigonometry, enable_algebra, deletion_history_states
            self.loading_status = [None, None]  # Variable list to indicate if the file needs to be replaced, so that repeated file replacement code isn't used.

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
                    
                    error_type = None
                    for index, details in enumerate(users):
                        if len(details) != 7:  # Check if the number of elements for each entry is not 7.
                            error_type = 1
                            response2 = messagebox.askyesno("Invalid Data", f"The {file_name} file contains invalid data:\nEntry #{index+1} is invalid (expected 7 elements, got {len(details)}).\n\nWould you like to remove this entry?")                 
                        elif len(details[6]) != int(details[3]):  # Check if the number of saved questions is less than the recommended number of questions in any user's saved quiz.
                            error_type = 2
                            response2 = messagebox.askyesno("Invalid Data", f"The {file_name} file contains invalid data:\nEntry #{index+1} has an invalid list of saved questions (expected {details[3]} questions, got {len(details[6])}).\n\nWould you like to remove this entry?")
                        
                        if error_type != None:
                            if response2 == True:
                                # Remove invalid entries and update the scoreboard file.
                                users = [details for details in users if len(details) == 7] if error_type == 1 else [details for details in users if len(details[6]) == details[3]]
                                with open(file_dir, "w") as file:           # Open the JSON file in write mode ("w").
                                    json.dump(users, file, indent=4)        # Write the valid users to the JSON file.
                                    file.close()                            # Close the file after writing to it.
                                break
                            else:
                                messagebox.showwarning("Invalid Data", f"The program will run in temporary storage mode until the {file_name} file is fixed.\n\n{full_directory}")
                                users = [details for details in users if len(details) == 7] if error_type == 1 else [details for details in users if len(details[6]) == details[3]]  # Keep only the valid entries in memory.
                                break

                elif file_data == "settings":
                    if not isinstance(data, dict): # Check if the loaded data is a dictionary.
                        raise json.JSONDecodeError("Expected a dict", doc=str(data), pos=0)  # Raise an error if the loaded settings data is not a dictionary, simulating a JSON decode error.
                    
                    if "enable_timer" not in data or "enable_trigonometry" not in data or "enable_algebra" not in data or "deletion_history_states" not in data:
                        raise json.JSONDecodeError("Missing required keys in settings", doc=str(data), pos=0)
                    
                    settings.clear()    # Clear the list to prevent duplicate entries.
                    settings = data     # Modify the "settings" dictionary in place.
                    timer.set(settings.get("enable_timer", default_settings["enable_timer"]))                                          # Set the timer to the value stored in the "settings" dictionary, or the default value if not found.
                    enable_trigonometry.set(settings.get("enable_trigonometry", default_settings["enable_trigonometry"]))              # Set "enable_trigonometry" to the value stored in the "settings" dictionary, or the default value if not found.
                    enable_algebra.set(settings.get("enable_algebra", default_settings["enable_algebra"]))                             # Set "enable_algebra" to the value stored in the "settings" dictionary, or the default value if not found.
                    deletion_history_states.set(settings.get("deletion_history_states", default_settings["deletion_history_states"]))  # Set the deletion history states to the value stored in the "settings" dictionary, or the default value if not found.
                
                data_loaded = True      # Set the "data_loaded" variable to True, so that the program doesn't reload data again from the JSON file before it is accessed.
            
            # Error control for instances such as the JSON file having invalid data, having incorrect formatting, or being corrupted.
            except json.JSONDecodeError as JSONDecodeError:
                response3 = messagebox.askyesno("File Error", f"Failed to decode JSON data. The {file_name} file may be corrupted or improperly formatted. Do you want to replace it?\n\n{JSONDecodeError}\n\n{full_directory}")  # Show an error message if the JSON file cannot be decoded, asking the user if they want to replace the file.
                self.loading_status = ["Error", "Replace"] if response3 == True else ["Error", None]  # Set the loading status based on the user's choice, adding "Replace" to the second element of the list if the user wants to replace the file.
            
            # Error control for instances such as the file being inaccessible or lacking the permission to read it.
            except IOError as io_error:
                messagebox.showwarning("File Error", f"An error occurred while reading the {file_name} file, program will run in temporary storage mode.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be read.
                self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                data_loaded = False  # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
            
            # Error control for any other exceptions that may occur.
            except Exception as e:
                response3 = messagebox.askyesno("Unexpected Error", f"An unexpected error occurred while reading the {file_name} file. Do you want to replace it?\n\n{e}\n\n{full_directory}")  # Show an error message if there is an unexpected error.
                self.loading_status = ["Error", "Replace"] if response3 == True else ["Error", None]  # Set the loading status based on the user's choice, adding "Replace" to the second element of the list if the user wants to replace the file.
            
            if self.loading_status[0] == "Error" and self.loading_status[1] == "Replace":  # Check if there is a loading error and that the user chose to replace the file.
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
                self.loading_status = [None, None]  # Reset both values in the "loading_status" list to None.
                return
            
            elif self.loading_status[0] == "Error" and self.loading_status[1] == None:  # Check if there is a loading error and that the user did not choose to replace the file.
                messagebox.showwarning("Temporary Storage Mode", f"The program will run in temporary storage mode until the {file_name} file is replaced.\n\n{full_directory}")  # Show a warning message if the user does not want to create a new file.
                self.error_control(file_name, file_dir, file_data, "Temporary")  # Call the error control function to handle temporary storage mode, which will clear the "users" list and add the default values to the "settings" dictionary.
                data_loaded = False      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                self.loading_status = [None, None]  # Reset both values in the "loading_status" list to None.
                return


    # Function for validating user details and making sure there are no invalid entries inside any entry boxes.
    def validate_user_details(self):
        global overwrite_score, username
        overwrite_score = False
        warning_messages = []
        label = False
        invalid_entry = False
        adjust_entry = False
        
        # Clear any previous error labels by using the "clear_widget" method.
        self.clear_widget(None, False, self.home.home_frame1, 2, 0, None)  # Clear all current widgets in the home frame on column 2, row 0 (passing "False" means the program will rely on the specified element, column, and row to clear the widgets from).
        
        if username == "":  # Check if the username is empty.
            warning_messages.append("is required and cannot be left blank")  # Show a warning message if the username is empty.
            label = "Required"
            invalid_entry = True
            adjust_entry = ""

        else:
            if len(username) < 2:  # Check if the username is shorter than 2 characters.
                warning_messages.append("cannot be shorter than two characters")  # Show a warning message if the username is shorter than 3 characters.
                label = "Invalid Entry"
                invalid_entry = True
                adjust_entry = username

            if not any(char.isalpha() for char in username):  # Check if the username contains at least one alphabetical character.
                warning_messages.append("must contain at least one alphabetical character")  # Show a warning message if the username does not contain at least one alphabetical character.
                label = "Invalid Entry"
                invalid_entry = True
                adjust_entry = username

            if len(username) > 20:  # Check if the username is longer than 20 characters.
                warning_messages.append("cannot be longer than twenty characters.\n\nYour entry has been automatically shortened to twenty characters")  # Show a warning message if the username is longer than 20 characters.
                invalid_entry = True
                adjust_entry = username[:20]

            if " " in username:  # Check if the username contains any spaces.
                response1 = messagebox.askyesno("Invalid Entry", "Username cannot contain any spaces. Do you want to replace all spaces inside the username with underscores?")
                if response1 == True:
                    if invalid_entry != True: invalid_entry = False  # Allow the program to continue to the quiz only if no invalid entry is detected prior to replacing the spaces with underscores.
                    adjust_entry = username.replace(" ", "_")  # Replace the spaces inside the username with underscores.
                    username = adjust_entry
                else:
                    invalid_entry = True  # Prevent the program from continuing to the quiz after removing the spaces from the username, so the user can adjust the username to their liking.
                    adjust_entry = username.replace(" ", "")   # Remove the spaces from the username.

        if invalid_entry == True:
            if adjust_entry != False:
                if self.home.entry_type == "CTkEntry":
                    self.home.username_entry.insert(0, adjust_entry)
                elif self.home.entry_type == "CTkComboBox":
                    self.home.username_entry.set(adjust_entry)
            if label != False:
                CTk.CTkLabel(self.home.home_frame1, text=label, text_color="red", font=(DEFAULT_FONT, 12)).grid(column=2, row=0, sticky=W, padx=(5,0), pady=(20,0))
            if warning_messages != []:
                messagebox.showwarning("Invalid Entry", f"Username " + " and ".join(warning_messages) + ".")  # Show a warning message box if the username is invalid, combining multiple warning messages into a single message if applicable.
            warning_messages.clear()
            return "Invalid Entry"
        else:
            if adjust_entry != False:
                if self.home.entry_type == "CTkEntry":
                    self.home.username_entry.insert(0, adjust_entry)
                elif self.home.entry_type == "CTkComboBox":
                    self.home.username_entry.set(adjust_entry)
            # Check if a user already exists with the same username and difficulty in the "users" list.
            for user in users:
                if user[1].lower() == username.lower() and user[2] == difficulty:  # Use ".lower()" to ignore case sensitivity when comparing the existing usernames with the entered username by making them both lowercase.
                    response2 = messagebox.askyesno("Overwrite Score", "A score already exists for this username (case insensitive) and difficulty level. Continuing will replace this score with your final score after completion of the quiz. Are you sure you want to continue?", icon="warning")
                    if response2 == True:
                        overwrite_score = True
                        return "Valid Entry"
                    else:
                        return "Invalid Entry"
            return "Valid Entry"
            

    # Method for saving details specific to the specified window.
    def save_details(self, procedure, origin, scenario, file_dir):
        global ref_number, username, difficulty_num, question_amount, settings, data_loaded, enable_trigonometry, enable_algebra, use_trigonometry_questions, use_algebra_questions
        
        if origin == "Home":
            if scenario == "Temporary" or scenario == "Permanent":
                username = self.home.username_entry.get().strip()        # Get the username entry widget value and remove any leading or trailing spaces using ".strip()".
                difficulty_num = self.home.difficulty_slider.get()       # Get the difficulty slider value.
                question_amount = int(self.home.questions_slider.get())  # Get the questions slider value.
            
            if scenario == "Permanent":
                if users != []:  # Check if the "users" list is not empty.
                    existing_ref_numbers = [user[0] for user in users]  # Create a list of existing reference numbers from the "users" list.
                else:
                    existing_ref_numbers = []
                
                # Check if the maximum number of unique reference numbers has been reached.
                available_ref_numbers = list(set(range(1000, 1100)) - set(existing_ref_numbers)) if existing_ref_numbers else list(range(1000, 1100))  # Create a list of available reference numbers by subtracting the existing reference numbers from the list of all possible reference numbers.
                if not available_ref_numbers:  # Check if 100 possible unique 4-digit ref numbers from 1000 to 1099 have been generated.
                    messagebox.showwarning("Maximum Scores Reached", "No more unique reference numbers can be generated.\nPlease delete old user scores to add new ones.")
                    self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go back to the home page.
                    return
                else:
                    ref_number = random.choice(available_ref_numbers)
            
            if procedure == "Quiz":
                if self.validate_user_details()  == "Invalid Entry": return  # Run the "validate_user_details" function to ensure that the user details are valid before starting the quiz, otherwise return to home method.

                use_trigonometry_questions = enable_trigonometry.get()
                use_algebra_questions = enable_algebra.get()
                if use_trigonometry_questions == False and use_algebra_questions == False:
                    response1 = messagebox.askyesno("No Question Topics Selected", "The quiz cannot be started until a question topic is selected from the settings menu. Do you want to enable all question topics?", icon="warning")
                    if response1 == False: return
                    else:
                        enable_algebra.set(True)
                        enable_trigonometry.set(True)
                        try:
                            settings = {"enable_timer": timer.get(), "enable_trigonometry": enable_trigonometry.get(),"enable_algebra": enable_algebra.get(), "deletion_history_states": deletion_history_states.get()}
                            with open(file_dir, "w") as file:        # Open the file in write mode ("w"). If it doesn't exist, a new file will be created.
                                json.dump(settings, file, indent=4)  # Dump the entries from the "settings" list into the JSON file.
                                file.close()                         # Close the file after writing to it.
                            data_loaded = False                      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                        except IOError as io_error:                  # Error control for instances such as the file being inaccessible or lacking the permission to write to it.
                            messagebox.showerror("File Error", f"Failed to write to 'settings.json'. Check file permissions, disk space, and ensure the file is not in use.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be written to.
                            return
                        except Exception as e:                       # Error control for any other exceptions that may occur.
                            messagebox.showerror("Unexpected Error", f"An unexpected error occurred while writing to 'settings.json'.\n\n{e}\n\n{full_directory}")  # Show an error message if there is an unexpected error.
                            return
                self.clear_widget(lambda: self.quiz.setup_quiz(None), False, main_window, 1, 0, None)  # Clear all current widgets in the main window on column 1, row 0 (passing "False" means the program will rely on the specified element, column, and row to clear the widgets from), then go to the home page.
            elif procedure == "Scoreboard":
                self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the scoreboard page.
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
                try:
                    settings = {"enable_timer": timer.get(), "enable_trigonometry": enable_trigonometry.get(),"enable_algebra": enable_algebra.get(), "deletion_history_states": deletion_history_states.get()}
                    with open(file_dir, "w") as file:        # Open the file in write mode ("w"). If it doesn't exist, a new file will be created.
                        json.dump(settings, file, indent=4)  # Dump the entries from the "settings" list into the JSON file.
                        file.close()                         # Close the file after writing to it.
                    data_loaded = False                      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                except IOError as io_error:                  # Error control for instances such as the file being inaccessible or lacking the permission to write to it.
                    messagebox.showerror("File Error", f"Failed to write to 'settings.json'. Check file permissions, disk space, and ensure the file is not in use.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be written to.
                except Exception as e:                       # Error control for any other exceptions that may occur.
                    messagebox.showerror("Unexpected Error", f"An unexpected error occurred while writing to 'settings.json'.\n\n{e}\n\n{full_directory}")  # Show an error message if there is an unexpected error.

        elif origin == "Quiz":
            if procedure == "New Quiz":
                enable_algebra.set(True)
                enable_trigonometry.set(True)
                try:
                    settings = {"enable_timer": timer.get(), "enable_trigonometry": enable_trigonometry.get(),"enable_algebra": enable_algebra.get(), "deletion_history_states": deletion_history_states.get()}
                    with open(file_dir, "w") as file:        # Open the file in write mode ("w"). If it doesn't exist, a new file will be created.
                        json.dump(settings, file, indent=4)  # Dump the entries from the "settings" list into the JSON file.
                        file.close()                         # Close the file after writing to it.
                    data_loaded = False                      # Set the "data_loaded" variable to false, so that the program will reload data from the JSON file when it next needs to be accessed.
                except IOError as io_error:                  # Error control for instances such as the file being inaccessible or lacking the permission to write to it.
                    messagebox.showerror("File Error", f"Failed to write to 'settings.json'. Check file permissions, disk space, and ensure the file is not in use.\n\n{io_error}\n\n{full_directory}")  # Show an error message if the file cannot be written to.
                    return
                except Exception as e:                       # Error control for any other exceptions that may occur.
                    messagebox.showerror("Unexpected Error", f"An unexpected error occurred while writing to 'settings.json'.\n\n{e}\n\n{full_directory}")  # Show an error message if there is an unexpected error.
                    return


    # Method for printing details into a PDF.
    def print_details(self, selections):
        data = []
        
        if selections == "all" and data_loaded == False:  # Check if the data has been loaded from the JSON file only if all scores are being printed.
            self.load_details("scoreboard", SCOREBOARD_FILE_PATH, "users")
    
        if selections == "all":
            if users == []:  # Check if the "users" list is empty.
                response1 = messagebox.askyesno("No Scores Recorded", "There are no recorded scores to print. Would you still like to print out a blank scoreboard table?")
                if response1 == False:
                    return
            else:
                # Load all data from JSON file.
                with open("AppData\scoreboard.json", "r") as file:
                    data = json.load(file)  # Load the details from the JSON file into the "data" list.
                    data = [user[:6] for user in data]  # Trim each user record to include only the first 6 items (exluding the quiz saves).

        else:
            if selections != []:  # Check if the "selections" list is not empty.
                # Match the selected reference numbers in the treeview widget to the user reference numbers (user[0]) in the "users" list.
                # This creates a new list of users that match the selected user reference numbers so that only the selected users are printed on the scoreboard PDF.
                # "user[0]" is converted to a string to ensure that it matches the format used in the Treeview selection, which is passed as a string.
                data = [user[:6] for user in users if str(user[0]) in selections]  # If selections are provided, use them as the scoreboard data directly.
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
        
        if users == []:  # Check if the "users" list is empty.
            messagebox.showwarning("No Scores Recorded", "There are no recorded scores to delete.")
            return
        else:
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
                    self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets) to refresh the scoreboard page.
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
                        self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets) to refresh the scoreboard page.
                        messagebox.showinfo("Scores Deleted", f"The selected {words[0]} {words[1]} been deleted.")
                    else:
                        return
                else:
                    messagebox.showwarning("No Scores Selected", "Please select at least one score to delete.")
                    return
            self.reset_details("Scoreboard", None)  # Reset the "sel_reference_numbers" list in the Scoreboard class so that the list is ready for new selections.


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
        self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets) to refresh the scoreboard page.


    # Method for redoing the deletion of scores that were previously undone.
    def redo_delete(self):
        global users, history_stack, redo_stack

        # Check if the redo stack is empty.
        if not redo_stack:
            return  # If the redo stack is empty, do nothing and return.
        
        last_redo = redo_stack.pop()  # Retrieve the last deleted users from the redo stack.
        history_stack.append([(user, index) for user, index in last_redo])       # Store the last deleted users in the history stack for potential future undoing.
        # Delete users in reverse index order to avoid shifting issues.
        for user, index in sorted(last_redo, key=lambda x: x[1], reverse=True):  # Sort by the original index ("x[1]"), which refers to the second element ("1", being the index) in each (user, index) tuple, representing the user's original position.
            del users[index]  # Delete the user from the "users" list at the specified index.
        
        self.save_details(None, "Scoreboard", None, SCOREBOARD_FILE_PATH)
        self.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets) to refresh the scoreboard page.


    # Method for resetting details specific to the specified window.
    def reset_details(self, origin, action):
        global username, difficulty, difficulty_num, question_amount, question_details, temp_fake_answers
        if origin == "Completion" or origin == "Quiz" and action == "User Reset":
            username = None
            difficulty = None
            difficulty_num = None
            question_amount = None
            temp_fake_answers = []
            question_details.clear()
            self.quiz.quiz_save = []
        elif origin == "Scoreboard":
            self.scoreboard.sel_reference_numbers.clear()
        elif origin == "Quiz": 
                if action == "Restart" or action == "New":
                    self.quiz.score = 0
                    self.quiz.quiz_save = []
                
                if action == "New":
                    temp_fake_answers = []
                    question_details.clear()
                elif action == "Home" or action == "Scoreboard":
                    self.quiz.score = 0
                    temp_fake_answers = []
                    question_details.clear()
                    self.quiz.quiz_save = []
                
                if action != "Restart":  # Only reset these variables if the user is not restarting the quiz, otherwise restarting during a quiz retry or answer viewing mode will cause issues.
                    self.quiz.answer_viewing_active = False
                    self.quiz.retry_active = False

                self.quiz.current_index = 0
                self.quiz.question_no = 1


    # Method for unbinding specified key events from the main window.
    def unbind_keys(self, keys):
        # Unbind all key events from the main window.
        for key in keys:
            main_window.unbind(key)


    # Function for configuring the timer label state (enabled/disabled).
    # Unique identifiers are passed in "origin" to differentiate between the "Quiz" and "Completion" classes to manage their relevant timer labels.
    def timer_config(self, origin, command, procedure):
        if origin == "Quiz":
            if command == "Enable":
                return (f"Time: {self.quiz.time_string}")
            elif command == "Disable":
                return "Timer Disabled"
        
        elif origin == "Quiz Menubar":
            if self.quiz.answer_viewing_active == False:  # Only configure the timer label if not in answer viewing mode, since the timer is not available in that mode.
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
        self.about_window.geometry("320x157")  # Set the size of the "About" window, calculated by finding the size after the child elements have been added.
        self.about_window.resizable(False, False)
        self.about_window.update_idletasks()  # Process any pending events for the window to make sure the geometry info is up-to-date before calculating the centre position later.
        
        # Centre the "About" window above the main window.
        self.x = main_window.winfo_x() + main_window.winfo_width() // 2 - self.about_window.winfo_width() // 2
        self.y = main_window.winfo_y() + main_window.winfo_height() // 2 - self.about_window.winfo_height() // 2 + 56
        self.about_window.geometry(f"+{self.x}+{self.y}")
        self.about_window.transient(main_window)  # Keep on top of parent window (main_window).
        self.about_window.focus()  # Set focus to the "About" window so that it is ready for user interaction.

        # Create a frame inside the "About" window to hold the "about" details label.
        self.about_frame = CTk.CTkFrame(self.about_window, fg_color=FRAME_FG, corner_radius=10)
        self.about_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky=EW)
        self.about_frame.columnconfigure(0, weight=0, minsize=300)
        
        # Add program details and a close button.
        CTk.CTkLabel(self.about_frame, text=f"QWhizz Math\nVersion {APP_VERSION}\nMade by Jack Compton", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR, justify="center").grid(row=0, column=0, sticky=EW, padx=10, pady=(20))
        self.button_sizes = [300, 30, 14]  # Specify the sizing to be used for buttons (width, height, font size).
        self.close_button = CTk.CTkButton(self.about_window, text="Close", command=lambda: self.tools.on_ctkbutton_click(self.close_button, self.button_sizes, lambda: self.close()),
                                          width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.close_button.grid(row=1, column=0, padx=10, pady=(5,10))
        self.close_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.close_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
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
        global banners_loaded
        banners_loaded = False  # Reset the flag to indicate that the banners have not been loaded yet, so that going to the home or quiz page will reload them.

        # Setting the main window geometry (size) before element creation ensures the window doesn't glitch between sizes.
        if int(len(users)) > 8:
            main_window.geometry("868x411")  # Final size calculated based on the window size seen after the elements are all created, including the scrollbar when the users list is above 8.
        else:
            main_window.geometry("852x411")  # Final size calculated based on the window size seen after the elements are all created, excluding the scrollbar when the users list is at or below 8.
        
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
        question_settings = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=question_settings, label="Question Topics")
        question_settings.add_checkbutton(label="Trigonometry", variable=enable_trigonometry, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        question_settings.add_checkbutton(label="Algebra", variable=enable_algebra, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=history_settings, label="Score Deletion History States")
        history_settings.add_radiobutton(label="Disabled", variable=deletion_history_states, value=0, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="10", variable=deletion_history_states, value=10, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="25", variable=deletion_history_states, value=25, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="50", variable=deletion_history_states, value=50, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))

        help_menu = Menu(scoreboard_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        scoreboard_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=lambda: self.tools.open_file("Scoreboard", DOCUMENTATION_PATH, "readme.pdf"))
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
        self.button_sizes = [200, 30, 14]  # Specify the sizing to be used for buttons (width, height, font size).

        self.delete_button = CTk.CTkButton(top_frame1, text="Delete", command=lambda: self.tools.on_ctkbutton_click(self.delete_button, self.button_sizes, lambda: self.tools.delete_details(self.sel_reference_numbers)),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.delete_button.grid(column=1, row=0, padx=(0,5), pady=(0,5))
        self.delete_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.delete_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
        self.home_button = CTk.CTkButton(top_frame1, text="Home", command=lambda: self.tools.on_ctkbutton_click(self.home_button, self.button_sizes, lambda: self.tools.clear_widget(self.home.setup_homepage, True, None, None, None, self.tools.unbind_keys(self.binded_keys))),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.home_button.grid(column=2, row=0, padx=(5,0), pady=(0,5))
        self.home_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.home_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
        self.answers_button = CTk.CTkButton(top_frame1, text="View Answers", command=lambda: self.tools.on_ctkbutton_click(self.answers_button, self.button_sizes, lambda: self.quiz.review_quiz("View Answers", "Scoreboard", self.sel_reference_numbers)),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.answers_button.grid(column=1, row=1, padx=(0,5), pady=(5,0))
        self.answers_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.answers_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.

        self.retry_button = CTk.CTkButton(top_frame1, text="Retry Quiz", command=lambda: self.tools.on_ctkbutton_click(self.retry_button, self.button_sizes, lambda: self.quiz.review_quiz("Retry", "Scoreboard", self.sel_reference_numbers)),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.retry_button.grid(column=2, row=1, padx=(5,0), pady=(5,0))
        self.retry_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.retry_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.

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
        global ref_number, username, difficulty, question_amount, users, overwrite_score
        
        self.quiz.final_score = f"{self.quiz.score}/{question_amount}"
        if timer.get() == True:
            self.time = self.quiz.total_time
        else:
            self.time = "Disabled"
        if overwrite_score == True:
            # Check if a user already exists with the same username and difficulty in the "users" list.
            for index, user in enumerate(users):
                if user[1].lower() == username.lower() and user[2] == difficulty:  # Use ".lower()" to ignore case sensitivity when comparing the existing usernames with the entered username by making them both lowercase.
                    users[index] = [ref_number, username, difficulty, question_amount, self.time, self.quiz.final_score, self.quiz.quiz_save]  # Replace the existing user details with the new ones.
                    overwrite_score = False  # Reset the "overwrite_score" flag.
                    break
        else:
            users.append([ref_number, username, difficulty, question_amount, self.time, self.quiz.final_score, self.quiz.quiz_save])  # Add the next user and their quiz details to the "users" list.
        self.tools.save_details(None, "Completion", None, SCOREBOARD_FILE_PATH)  # Save the details to the JSON file.
        self.setup_completion()


    def setup_completion(self):
        global banners_loaded

        # Setting the main window geometry (size) before element creation ensures the window doesn't glitch between sizes.
        main_window.geometry("758x434")  # Final size calculated based on the window size seen after the elements are all created.
        
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
        question_settings = Menu(completion_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=question_settings, label="Question Topics")
        question_settings.add_checkbutton(label="Trigonometry", variable=enable_trigonometry, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        question_settings.add_checkbutton(label="Algebra", variable=enable_algebra, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings = Menu(completion_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=history_settings, label="Score Deletion History States")
        history_settings.add_radiobutton(label="Disabled", variable=deletion_history_states, value=0, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="10", variable=deletion_history_states, value=10, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="25", variable=deletion_history_states, value=25, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="50", variable=deletion_history_states, value=50, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))

        help_menu = Menu(completion_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        completion_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=lambda: self.tools.open_file("Completion", DOCUMENTATION_PATH, "readme.pdf"))
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Completion"))

        main_window.config(menu=completion_menubar)

        if banners_loaded == False:
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

            banners_loaded = True

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
        CTk.CTkLabel(completion_frame1, text="Quiz Complete!", font=(DEFAULT_FONT, 20, "bold"), text_color=FONT_COLOUR).grid(column=0, row=0, sticky=EW, padx=5, pady=(20,8))
        CTk.CTkLabel(completion_frame1, text=f"Total Score: {self.quiz.score}/{question_amount}", font=(SEMIBOLD_DEFAULT_FONT, 16), text_color=FONT_COLOUR).grid(column=0, row=1, sticky=EW, padx=5)
        CTk.CTkLabel(completion_frame1, text=f"Difficulty: {difficulty}", font=(SEMIBOLD_DEFAULT_FONT, 16), text_color=FONT_COLOUR).grid(column=0, row=2, sticky=EW, padx=5)
        self.total_time_lbl = CTk.CTkLabel(completion_frame1, text="", font=(SEMIBOLD_DEFAULT_FONT, 16), text_color=FONT_COLOUR)  # Make an empty label for the timer until the state of the timer is determined (enabled/disabled).
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
        self.button_sizes = [200, 30, 14]  # Specify the sizing to be used for buttons (width, height, font size).

        self.answers_button = CTk.CTkButton(button_frame, text="View Answers", command=lambda: self.tools.on_ctkbutton_click(self.answers_button, self.button_sizes, lambda: self.quiz.review_quiz("View Answers", "Completion", None)),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.answers_button.grid(column=0, row=0, padx=(0,5), pady=(0,5))
        self.answers_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.answers_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
        self.retry_button = CTk.CTkButton(button_frame, text="Retry Quiz", command=lambda: self.tools.on_ctkbutton_click(self.retry_button, self.button_sizes, lambda: self.quiz.review_quiz("Retry", "Completion", None)),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.retry_button.grid(column=1, row=0, padx=(5,0), pady=(0,5))
        self.retry_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.retry_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
        self.scoreboard_button = CTk.CTkButton(button_frame, text="Scoreboard", command=lambda: self.tools.on_ctkbutton_click(self.scoreboard_button, self.button_sizes, lambda: self.quiz.reset_timer("Scoreboard", "Completion")),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.scoreboard_button.grid(column=0, row=1, padx=(0,5), pady=(5,0))
        self.scoreboard_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.scoreboard_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
        self.home_button = CTk.CTkButton(button_frame, text="Home", command=lambda: self.tools.on_ctkbutton_click(self.home_button, self.button_sizes, lambda: self.quiz.reset_timer("Home", "Completion")),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=False, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.home_button.grid(column=1, row=1, padx=(5,0), pady=(5,0))
        self.home_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.home_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.



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
        self.answer_viewing_active = False      # Variable to store the state of the quiz (False indicating a standard quiz, True indicating that the user is viewing the answers), defaulting to False.
        self.retry_active = False               # Variable to store the state of the quiz (False indicating a standard quiz, True indicating a retried quiz), defaulting to False.
        self.active_topic = None                # Variable to store the active question topic (either trigonometry or algebra), defaulting to "None".
        self.elapsed_time = 0                   # Variable to store the elapsed time, defaulting to 0.
        self.calculated_elapsed_time = 0        # Variable to store the calculated elapsed time, defaulting to 0.
        self.quiz_start_time = None             # Variable to store the start time of the quiz, defaulting to None.
        self.pause_start_time = None            # Variable to store the start time of the quiz pause, defaulting to None.
        self.total_paused_time = 0              # Variable to store the total paused time, defaulting to 0.
        self.time_string = "00:00:00"           # Variable to store the formatted time string, defaulting to "00:00:00".
        self.total_time = "00:00:00"            # Variable to store the formatted total time, defaulting to "00:00:00".
        self.user_answers = []                  # Inalise a list to store the user's answers, defaulting to an empty list.
        self.quiz_save = []                     # Create empty list for completed quiz saves to be stored inside.
        self.final_score = "0/0"                # Variable to store the final score, defaulting to "0/0".
        self.score = 0                          # Variable to store the active score during the quiz, defaulting to 0.


    def exit_quiz(self, command, origin):
        if origin == "Quiz" and command == "Home" or command == "Scoreboard":
            paused_prior = quiz_paused  # Check if the quiz has been paused prior to pressing the exit button, meaning it shouldn't be paused twice and then unpaused.
            
            if self.answer_viewing_active == False:  # Only utilise the pause method if the user is not currently viewing the answers, since pausing isn't available on the answer viewing mode.
                if paused_prior == False: self.pause_quiz()

            # Ask the user if they're sure they want to exit the quiz, and inform them that all progress will be lost, only if they aren't in the answer viewing mode.
            response1 = messagebox.askyesno("Exit Quiz", "Are you sure you want to exit the quiz?" + ("\nAll progress will be lost." if self.answer_viewing_active == False else ""), icon="warning" if self.answer_viewing_active == False else "question")
            if response1 == True:
                self.stop_timer(command, origin)
            else:
                if self.answer_viewing_active == False:  # Only utilise the unpause method if the user is not currently viewing the answers, since pausing isn't available on the answer viewing mode.
                    if paused_prior == False: self.unpause_quiz()
                return
        

    def start_timer(self):
        self.timer_active = True
        # Only set the quiz start time on the first run of the timer loop (not after unpausing)
        if self.quiz_start_time == None:
            self.quiz_start_time = time.time()  # Record the current time as quiz start time.
        self.timer_loop()  # Start the timer update loop.


    def stop_timer(self, command, origin):
        global use_trigonometry_questions, use_algebra_questions
        self.timer_active = False
        # Cancel the "after" job if it is currently still running.
        if hasattr(self, "timer_job") and self.timer_job != None:
            self.timer_lbl.after_cancel(self.timer_job)
            self.timer_job = None

        if origin == "Quiz":
            if command == "Restart Quiz":
                if self.answer_viewing_active == False:  # Only provide a warning if the user is completing a standard quiz, since no progress would be lost by restarting in the answer viewing mode.
                    response1 = messagebox.askyesno("Restart Quiz", "Are you sure you want to restart the quiz?\nAll progress will be lost.", icon="warning")
                    if response1 == False: return
            if command == "New Quiz":
                if self.retry_active == True:
                    messagebox.showinfo("Cannot Start New Quiz", "A new quiz cannot be started because you are currently retrying an existing quiz. Please finish or exit the current quiz before starting a new one.")
                    return
                elif self.answer_viewing_active == True:
                    messagebox.showinfo("Cannot Start New Quiz", "A new quiz cannot be started because you are currently viewing the answers of an existing quiz. Please finish or exit the current quiz before starting a new one.")
                    return
                response1 = messagebox.askyesno("New Quiz", "Are you sure you want to start a new quiz?\nAll progress will be lost.", icon="warning")
                if response1 == False: return
                use_trigonometry_questions = enable_trigonometry.get()
                use_algebra_questions = enable_algebra.get()
                if use_trigonometry_questions == False and use_algebra_questions == False:
                    response1 = messagebox.askyesno("No Question Topics Selected", "A new quiz cannot be started until a question topic is selected from the settings menu. Do you want to enable all question topics?", icon="warning")
                    if response1 == False: return
                    else: self.tools.save_details("New Quiz", "Quiz", None, SETTINGS_FILE_PATH) 
            self.tools.unbind_keys(self.binded_keys)

        if command == "Home" or command == "Scoreboard" or command == "Restart Quiz" or command == "New Quiz":
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
            if origin == "Completion": self.tools.reset_details(origin, None)  # If the origin is from the completion page, reset the user details so that the home page doesn't remember the previous details.
            elif origin == "Quiz": self.tools.reset_details(origin, command)   # If the origin is from the quiz page, reset the quiz details so that starting a quiz later from the home page will use new questions.
            self.question_no = 1
            self.score = 0
            if command == "Home":
                self.tools.clear_widget(self.home.setup_homepage, False, main_window, 1, 0, None)  # Clear all current widgets in the main window on column 1, row 0 (passing "False" means the program will rely on the specified element, column, and row to clear the widgets from), then go to the home page.
            elif command == "Scoreboard":
                self.tools.reset_details("Quiz", "User Reset")  # Clear the quiz and user details (passing "Quiz" as the origin and "User Reset" as the action so that going home from the scoreboard won't reuse the user details of the viewed or retried quiz).
                self.tools.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the scoreboard page.
        elif command == "New Quiz":
            self.tools.reset_details("Quiz", "New")  # Pass "New" action so that all quiz details are cleared.
            self.tools.clear_widget(lambda: self.setup_quiz(None), False, main_window, 1, 0, None)
        elif command == "Restart Quiz":
            self.tools.reset_details("Quiz", "Restart")  # Pass "Restart" action so that the question details aren't cleared.
            self.tools.clear_widget(lambda: self.setup_quiz("Restart Quiz"), False, main_window, 1, 0, None)
        return


    def pause_quiz(self):
        global quiz_paused
        quiz_paused = True  # Set the flag to indicate that the quiz is paused.
        self.stop_timer(None, None)
        self.pause_start_time = time.time()  # Record the real-world time for when the pause started.
        self.pause_button.configure(command=lambda: self.tools.on_ctkbutton_click(self.pause_button, None, self.unpause_quiz), image=self.play_img)
        
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
        self.pause_button.configure(command=lambda: self.tools.on_ctkbutton_click(self.pause_button, None, self.pause_quiz), image=self.pause_img)
        self.start_timer()     


    # Method for either retrying a saved quiz or viewing the answers of a saved quiz.
    def review_quiz(self, mode, origin, selection):
        global overwrite_score, ref_number, username, difficulty, difficulty_num, question_amount, question_details
        if mode == "Retry":
            if origin == "Scoreboard":
                if users == []:
                    messagebox.showwarning("No Saved Quizzes Available", "There are no saved quizzes to retry.")
                    return
                else:
                    if len(selection) > 1:
                        messagebox.showwarning("Invalid Selection", "Please only select one saved quiz to retry.")
                        return
                    elif selection == []:
                        messagebox.showwarning("No Saved Quiz Selected", "Please select a saved quiz to retry.")
                        return

                    for i, user in enumerate(users):
                        if str(user[0]) == selection[0]:
                            index = i
                            break
                    
                    overwrite_score = True
                    self.retry_active = True
                    self.scoreboard.sel_reference_numbers.clear()  # Clear the selected reference numbers of the scoreboard's treeview widget to ensure a score has to be selected again before it can be managed when returning to the scoreboard.
                    self.score = 0
                    ref_number = users[index][0]
                    username = users[index][1]
                    difficulty = users[index][2]
                    difficulty_num = 0 if users[index][2] == "Easy" else 1 if users[index][2] == "Medium" else 2
                    question_amount = users[index][3]

                    # For each question in the saved quiz from the "users" list, append the 6 elements of the question to the "question_details" list (this excludes the original user answer [7th element]).
                    for question in users[index][6]:
                        question_details.append(question[:6])
                    
                    self.tools.clear_widget(lambda: self.setup_quiz("Retry Quiz"), True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the quiz page.
            
            elif origin == "Completion":
                overwrite_score = True
                self.retry_active = True
                self.quiz_save = []
                self.score = 0
                self.reset_timer(None, None)

                self.tools.clear_widget(lambda: self.setup_quiz("Retry Quiz"), False, main_window, 1, 0, None)  # Clear all current widgets in the main window on column 1, row 0 (passing "False" means the program will rely on the specified element, column, and row to clear the widgets from), then go to the quiz page.
        
        elif mode == "View Answers":
            if origin == "Scoreboard":
                if users == []:
                    messagebox.showwarning("No Saved Quizzes Available", "There are no saved quizzes to view the answers of.")
                    return
                else:  
                    if len(selection) > 1:
                        messagebox.showwarning("Invalid Selection", "Please only select one saved quiz to view the answers of.")
                        return
                    elif selection == []:
                        messagebox.showwarning("No Saved Quiz Selected", "Please select a saved quiz to view the answers of.")
                        return

                    for i, user in enumerate(users):
                        if str(user[0]) == selection[0]:
                            index = i
                            break
                    
                    self.answer_viewing_active = True
                    self.scoreboard.sel_reference_numbers.clear()  # Clear the selected reference numbers of the scoreboard's treeview widget to ensure a score has to be selected again before it can be managed when returning to the scoreboard.
                    self.all_answers = []
                    ref_number = users[index][0]
                    username = users[index][1]
                    difficulty = users[index][2]
                    difficulty_num = 0 if users[index][2] == "Easy" else 1 if users[index][2] == "Medium" else 2
                    question_amount = users[index][3]

                    # For each question in the saved quiz from the "users" list, append the 7 elements of the question to the "question_details" list (this includes the original user answer [7th element]).
                    for question in users[index][6]:
                        question_details.append(question[:7])
                        
                        # Create a list of the answers and shuffle them only once (as using the shuffle in "update_question" each time Next or Previous is pressed would result in the answers being arranged when going to the previous question).
                        answer_choices = [question[4]] + question[5]
                        random.shuffle(answer_choices)
                        self.all_answers.append(answer_choices)
                    
                    self.tools.clear_widget(lambda: self.setup_quiz("View Answers"), True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the quiz page.
            
            elif origin == "Completion":
                self.answer_viewing_active = True
                self.all_answers = []
                question_details = self.quiz_save  # Set the "question_details" list to the saved quiz questions and answers from the "quiz_save" list (this includes the original user answers [7th element]), so that the View Answers mode can be accessed from the Completion page to view the answers of the just-completed quiz.

                # Create a list of the answers and shuffle them only once (as using the shuffle in "update_question" each time Next or Previous is pressed would result in the answers being arranged when going to the previous question).
                for question in question_details:
                    answer_choices = [question[4]] + question[5]
                    random.shuffle(answer_choices)
                    self.all_answers.append(answer_choices)
                
                self.tools.clear_widget(lambda: self.setup_quiz("View Answers"), False, main_window, 1, 0, None)  # Clear all current widgets in the main window on column 1, row 0 (passing "False" means the program will rely on the specified element, column, and row to clear the widgets from), then go to the quiz page.


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


    # Method for setting up the algebra questions.
    def setup_algebra(self):
        self.inner_frame.rowconfigure(0, weight=0, minsize=55)
        self.inner_frame.rowconfigure(1, weight=0, minsize=50)
        self.inner_frame.rowconfigure(2, weight=0, minsize=60)

        self.active_topic = "Algebra"
        self.current_statement = question_details[self.current_index][2]  # Define the current statement individually for either topic, since the statement datatype is different for both topics.
        self.current_question = question_details[self.current_index][3]   # Define the current question individually for either topic, since the question datatype is different for both topics.

        # Create a label for the title text.
        self.title_lbl = CTk.CTkLabel(self.inner_frame, text=self.current_title, font=(DEFAULT_FONT, 22, "bold"), text_color=FONT_COLOUR)
        self.title_lbl.grid(column=0, row=0, sticky=N, pady=(15,0))

        # Create a label for the statement text regarding the question.
        self.statement_lbl = CTk.CTkLabel(self.inner_frame, text=self.current_statement, font=(SEMIBOLD_DEFAULT_FONT, 19), text_color=FONT_COLOUR)
        self.statement_lbl.grid(column=0, row=1, sticky=S, pady=(0,5))

        # Create a label for the question text.
        self.question_lbl = CTk.CTkLabel(self.inner_frame, text=self.current_question, font=(DEFAULT_FONT, 21, "bold"), text_color=FONT_COLOUR)
        self.question_lbl.grid(column=0, row=2, sticky=N)
        return


    # Method for setting up the trigonometry questions.
    def setup_trigonometry(self):
        self.inner_frame.rowconfigure(0, weight=0, minsize=165)
        self.inner_frame.rowconfigure(1, weight=0, minsize=0)
        self.inner_frame.rowconfigure(2, weight=0, minsize=0)

        self.active_topic = "Trigonometry"
        self.current_top_statement = question_details[self.current_index][2][0]     # Get the first value of the "question_statement" list within the "question_details" list.
        self.current_bottom_statement = question_details[self.current_index][2][1]  # Get the second value of the "question_statement" list within the "question_details" list.
        self.hypotenuse_value = question_details[self.current_index][3][0]  # Get the first value of the "question" list within the "question_details" list.
        self.left_value = question_details[self.current_index][3][1]        # Get the second value of the "question" list within the "question_details" list.
        self.bottom_value = question_details[self.current_index][3][2]      # Get the third value of the "question" list within the "question_details" list.
        self.angle_value = question_details[self.current_index][3][3]       # Get the fourth value of the "question" list within the "question_details" list.

        # Create a blank transparent image 200x160 px in size.
        image = Image.new("RGBA", (200, 160), (0, 0, 0, 0))  # "RGBA" for RBG with transparency (A for alpha - transparency level), using (0 (Red), 0 (Green), 0 (Blue), 0 (Alpha)) for transparent background colour.
        draw = ImageDraw.Draw(image)

        # Coordinates of the right-angled triangle (at bottom-left corner).
        # Triangle points: (x1, y1), (x2, y2), (x3, y3), with the zero point (0, 0) being the top left.
        # Vertical line is from (65, 120) to (65, 20), horizontal line is from (190, 120) to (65, 120), and a hypotenuse connecting the top of the vertical line to the end of the horizontal line.
        points = [(65, 120), (65, 20), (190, 120)]

        # Draw triangle using lines.
        draw.line([points[0], points[1]], fill="white", width=3)  # Draw a vertical line (opposite).
        draw.line([points[2], points[0]], fill="white", width=3)  # Draw a horizontal line (adjacent).
        draw.line([points[1], points[2]], fill="white", width=3)  # Draw a diagonal line (hypotenuse).

        # Define the points for the right-angle square, which tucks into the bottom-left corner of the triangle.
        square_size = 15
        square_points = [
            (points[0][0], points[0][1] - square_size),                # Move vertically up from the right-angle corner.
            (points[0][0] + square_size, points[0][1] - square_size),  # Move diagonally up-right.
            (points[0][0] + square_size, points[0][1])                 # Move horizontally right.
        ]

        # Draw the small square using two connected lines to represent the right-angle symbol.
        draw.line([square_points[0], square_points[1]], fill="white", width=3)  # Top side of the square (horizontal).
        draw.line([square_points[1], square_points[2]], fill="white", width=3)  # Right side of the square (vertical).

        # Load the triangle image.
        triangle_img = CTk.CTkImage(light_image=image, dark_image=image, size=(200, 160))

        # Create a label to display the image.
        self.triangle_lbl = CTk.CTkLabel(self.inner_frame, image=triangle_img, text=None)
        self.triangle_lbl.grid(row=0, column=0, sticky=E, padx=(0,20))

        # Create a label for the title text.
        self.title_lbl = CTk.CTkLabel(self.inner_frame, text=self.current_title, font=(DEFAULT_FONT, 17, "bold"), text_color=FONT_COLOUR, justify=LEFT)
        self.title_lbl.grid(column=0, row=0, sticky=NW, padx=(20,0), pady=(18,0))
        
        # Create labels for the statement text regarding the question, placing the top statement after the bottom statement so that the top statement appears above the bottom statement.
        # Having seperate labels for multiple lines allows for adjustment of the line height too.
        self.bottom_statement_lbl = CTk.CTkLabel(self.inner_frame, text=self.current_bottom_statement, font=(SEMIBOLD_DEFAULT_FONT, 17), text_color=FONT_COLOUR, justify=LEFT)
        self.bottom_statement_lbl.grid(column=0, row=0, sticky=SW, padx=(20,0), pady=(0,38))
        self.top_statement_lbl = CTk.CTkLabel(self.inner_frame, text=self.current_top_statement, font=(SEMIBOLD_DEFAULT_FONT, 17), text_color=FONT_COLOUR, justify=LEFT)
        self.top_statement_lbl.grid(column=0, row=0, sticky=SW, padx=(20,0), pady=(0,60))

        # Create a label for the triangle's hypotenuse length value.
        self.hypotenuse_length_lbl = CTk.CTkLabel(self.triangle_lbl, text=self.hypotenuse_value, font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR, anchor=W)
        self.hypotenuse_length_lbl.place(relx=0.645, rely=0.325, anchor=W)

        # Create a label for the triangle's left side length value.
        self.left_length_lbl = CTk.CTkLabel(self.triangle_lbl, text=self.left_value, font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR, anchor=E)
        self.left_length_lbl.place(relx=0.285, rely=0.45, anchor=E)

        # Create a label for the triangle's bottom side length value.
        self.bottom_length_lbl = CTk.CTkLabel(self.triangle_lbl, text=self.bottom_value, font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR)
        self.bottom_length_lbl.place(relx=0.625, rely=0.85, anchor=CENTER)

        # Create a label for the triangle's angle value.
        self.angle_value_lbl = CTk.CTkLabel(self.triangle_lbl, text=self.angle_value, font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR)
        self.angle_value_lbl.place(relx=0.678, rely=0.658, anchor=CENTER)
        return


    # Method for updating the question and answer options for the current question.
    def update_question(self):
        if self.answer_viewing_active == True:
            if self.question_no == 1:
                self.previous_button.configure(state="disabled", fg_color=BUTTON_FG)  # Disable the previous button for the first question since there is no previous question to go to. The "fg_color" is set to "BUTTON_FG" to reset the colour after hovering (which makes it darker).
                self.previous_button.unbind("<Enter>")  # Unbind the "Enter" event from the previous button so that it doesn't change to a darker colour when the mouse hovers over it while the button is disabled.
            else:
                self.previous_button.configure(state="normal")
                self.previous_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.previous_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.

            if self.question_no == len(question_details):
                self.next_button.configure(text="Finish")  # Change the next button text to "Finish" for the last question so that it's clearer to the user that they are on the final question.
            else:
                self.next_button.configure(text="Next")
        
        self.current_index = self.question_no - 1  # Remove 1 to correctly index from the "question_details" list (since lists start at index 0, but the question numbers start at 1).
        self.upcoming_topic = question_details[self.current_index][0]
        self.current_title = question_details[self.current_index][1]
        self.correct_answer = question_details[self.current_index][4]
        self.fake_answers = question_details[self.current_index][5]

        if self.active_topic == "Algebra" and self.upcoming_topic == "Trigonometry":  # Check if the current topic is algebra and the next topic is trigonometry, so that the previous algebra elements can be removed.
            self.title_lbl.destroy()
            self.statement_lbl.destroy()
            self.question_lbl.destroy()
            self.setup_trigonometry()

        elif self.active_topic == "Trigonometry" and self.upcoming_topic == "Algebra":  # Check if the current topic is trigonometry and the next topic is algebra, so that the previous trigonometry elements can be removed.
            self.title_lbl.destroy()
            self.top_statement_lbl.destroy()
            self.bottom_statement_lbl.destroy()
            self.triangle_lbl.destroy()
            self.hypotenuse_length_lbl.destroy()
            self.left_length_lbl.destroy()
            self.bottom_length_lbl.destroy()
            self.angle_value_lbl.destroy()
            self.setup_algebra()
        
        elif self.active_topic == "Algebra" and self.upcoming_topic == "Algebra":  # Check if the current topic is algebra and the next topic is algebra, meaning no elements need to be removed.
            self.current_statement = question_details[self.current_index][2]  # Define the current statement individually for either topic, since the statement datatype is different for both topics.
            self.current_question = question_details[self.current_index][3]   # Define the current question individually for either topic, since the question datatype is different for both topics.
            self.title_lbl.configure(text=self.current_title)
            self.statement_lbl.configure(text=self.current_statement)
            self.question_lbl.configure(text=self.current_question)
        
        elif self.active_topic == "Trigonometry" and self.upcoming_topic == "Trigonometry":  # Check if the current topic is trigonometry and the next topic is trigonometry, meaning no elements need to be removed.
            self.current_top_statement = question_details[self.current_index][2][0]     # Get the first value of the "question_statement" list within the "question_details" list.
            self.current_bottom_statement = question_details[self.current_index][2][1]  # Get the second value of the "question_statement" list within the "question_details" list.
            self.hypotenuse_value = question_details[self.current_index][3][0]  # Get the first value of the "question" list within the "question_details" list.
            self.left_value = question_details[self.current_index][3][1]        # Get the second value of the "question" list within the "question_details" list.
            self.bottom_value = question_details[self.current_index][3][2]      # Get the third value of the "question" list within the "question_details" list.
            self.angle_value = question_details[self.current_index][3][3]       # Get the fourth value of the "question" list within the "question_details" list.
            self.top_statement_lbl.configure(text=self.current_top_statement)
            self.bottom_statement_lbl.configure(text=self.current_bottom_statement)
            self.hypotenuse_length_lbl.configure(text=self.hypotenuse_value)
            self.left_length_lbl.configure(text=self.left_value)
            self.bottom_length_lbl.configure(text=self.bottom_value)
            self.angle_value_lbl.configure(text=self.angle_value)

        if self.answer_viewing_active == True:
            self.ans_button_1.configure(text=f" A.    {self.all_answers[self.current_index][0]}", fg_color=BUTTON_FG, border_width=0, text_color_disabled=DISABLED_FONT_COLOUR)
            for widget in self.ans_button_1.place_slaves():
                widget.place_forget()  # Clear any existing placed tick/cross images from button 1 for the next question so the new tick/cross image can be added later to the relevant button.
            self.answer_management(self.ans_button_1, self.all_answers[self.current_index][0])  # Send the button name and the answer to the answer management method so that the specific button (self.ans_button_1) will be highlighted if it contains the correct or user-chosen incorrect answer.
            
            self.ans_button_2.configure(text=f" B.    {self.all_answers[self.current_index][1]}", fg_color=BUTTON_FG, border_width=0, text_color_disabled=DISABLED_FONT_COLOUR)
            for widget in self.ans_button_2.place_slaves():
                widget.place_forget()  # Clear any existing placed tick/cross images from button 2 for the next question so the new tick/cross image can be added later to the relevant button.
            self.answer_management(self.ans_button_2, self.all_answers[self.current_index][1])  # Send the button name and the answer to the answer management method so that the specific button (self.ans_button_2) will be highlighted if it contains the correct or user-chosen incorrect answer.
            
            self.ans_button_3.configure(text=f" C.    {self.all_answers[self.current_index][2]}", fg_color=BUTTON_FG, border_width=0, text_color_disabled=DISABLED_FONT_COLOUR)
            for widget in self.ans_button_3.place_slaves():
                widget.place_forget()  # Clear any existing placed tick/cross images from button 3 for the next question so the new tick/cross image can be added later to the relevant button.
            self.answer_management(self.ans_button_3, self.all_answers[self.current_index][2])  # Send the button name and the answer to the answer management method so that the specific button (self.ans_button_3) will be highlighted if it contains the correct or user-chosen incorrect answer.
            
            self.ans_button_4.configure(text=f" D.    {self.all_answers[self.current_index][3]}", fg_color=BUTTON_FG, border_width=0, text_color_disabled=DISABLED_FONT_COLOUR)
            for widget in self.ans_button_4.place_slaves():
                widget.place_forget()  # Clear any existing placed tick/cross images from button 4 for the next question so the new tick/cross image can be added later to the relevant button.
            self.answer_management(self.ans_button_4, self.all_answers[self.current_index][3])  # Send the button name and the answer to the answer management method so that the specific button (self.ans_button_4) will be highlighted if it contains the correct or user-chosen incorrect answer.

        else:
            # Shuffle answer options and assign them to buttons
            answer_choices = [self.correct_answer] + self.fake_answers
            random.shuffle(answer_choices)

            self.ans_button_1.configure(text=f" A.    {answer_choices[0]}", command=lambda: self.tools.on_ctkbutton_click(self.ans_button_1, None, lambda: self.answer_management(self.ans_button_1, answer_choices[0])))
            self.ans_button_2.configure(text=f" B.    {answer_choices[1]}", command=lambda: self.tools.on_ctkbutton_click(self.ans_button_2, None, lambda: self.answer_management(self.ans_button_2, answer_choices[1])))
            self.ans_button_3.configure(text=f" C.    {answer_choices[2]}", command=lambda: self.tools.on_ctkbutton_click(self.ans_button_3, None, lambda: self.answer_management(self.ans_button_3, answer_choices[2])))
            self.ans_button_4.configure(text=f" D.    {answer_choices[3]}", command=lambda: self.tools.on_ctkbutton_click(self.ans_button_4, None, lambda: self.answer_management(self.ans_button_4, answer_choices[3])))


    # Method for managing the user's answer to the current question.
    def answer_management(self, button, answer):
        if self.answer_viewing_active == True:
            if button == self.previous_button:
                if self.question_no > 1:  # Go to the previous question by removing 1 from the question number and updating the question, only if the question number is greater than 1 (since the question numbers start at 1).
                    self.question_no -= 1
                    self.question_no_lbl.configure(text=f"Question {self.question_no}/{question_amount}")  # Update the question number label.
                    self.update_question()
            
            elif button == self.next_button:
                if self.question_no < question_amount:
                    self.question_no += 1
                    self.question_no_lbl.configure(text=f"Question {self.question_no}/{question_amount}")  # Update the question number label.
                    self.update_question()
                    
                else:
                    self.tools.reset_details("Completion", None)    # Clear the quiz and user details (passing "Completion" as the origin)
                    self.tools.reset_details("Quiz", "Scoreboard")  # Clear the extra quiz details (passing "Scoreboard" as the origin)
                    self.tools.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the scoreboard page.
        
            else:
                self.current_index = self.question_no - 1  # Remove 1 to correctly index from the "question_details" list (since lists start at index 0, but the question numbers start at 1).
                self.user_answer = question_details[self.current_index][6]

                self.tick_image = Image.open("AppData/Images/tick.png")  # Load the correct answer button image.
                self.tick_img = CTk.CTkImage(self.tick_image, size=(16, 17))  # Create a CTkImage object with the tick image to allow scaling to be used.

                self.cross_image = Image.open("AppData/Images/cross.png")  # Load the incorrect answer button image.
                self.cross_img = CTk.CTkImage(self.cross_image, size=(16, 17))  # Create a CTkImage object with the cross image to allow scaling to be used.

                # Check if the user answer was incorrect
                if self.user_answer != self.correct_answer:
                    # Highlight the correct answer button with green.
                    if answer == self.correct_answer:
                        button.configure(border_color="#00ea89", border_width=3, text_color_disabled=FONT_COLOUR)
                
                    # Highlight the user's incorrect answer button choice with red.
                    if answer == self.user_answer:
                        button.configure(fg_color="#f37272", text_color_disabled=FONT_COLOUR)
                        cross_lbl = CTk.CTkLabel(button, text=None, image=self.cross_img)
                        cross_lbl.place(relx=0.9, rely=0.5, anchor=E)
                
                # Check if the user answer was correct
                elif self.user_answer == self.correct_answer:
                    # Highlight the correct answer button with green.
                    if answer == self.correct_answer:
                        button.configure(fg_color="#00ea89", text_color_disabled=FONT_COLOUR)
                        tick_lbl = CTk.CTkLabel(button, text=None, image=self.tick_img)
                        tick_lbl.place(relx=0.9, rely=0.5, anchor=E)
        
        else:
            self.current_index = self.question_no - 1  # Remove 1 to correctly index from the "question_details" list (since lists start at index 0, but the question numbers start at 1).

            self.quiz_save.append([question_details[self.current_index][0],
                                question_details[self.current_index][1],
                                question_details[self.current_index][2],
                                question_details[self.current_index][3],
                                question_details[self.current_index][4],
                                question_details[self.current_index][5],
                                answer])
            
            if answer == self.correct_answer:  # Check if the most recent answer matches the correct answer for the current question.
                self.score += 1 
                    
            if self.question_no < question_amount:
                self.question_no += 1
                self.question_no_lbl.configure(text=f"Question {self.question_no}/{question_amount}")  # Update the question number label.
                self.update_question()

            else:
                self.stop_timer(None, "Quiz")
                self.tools.reset_details("Quiz", None)
                self.tools.clear_widget(self.completion.submit_details, False, main_window, 1, 0, None)  # Clear all current widgets in the main window on column 1, row 0 (passing "False" means the program will rely on the specified element, column, and row to clear the widgets from), then go to the completion page.
        return


    # Method for generating the hard mode questions.
    def hard_mode(self):
        global question_details, temp_fake_answers

        for i in range(question_amount):  # Loop through the number of questions to be generated.
            if use_trigonometry_questions == True and use_algebra_questions == False:
                question_topic = "Trigonometry"
            elif use_trigonometry_questions == False and use_algebra_questions == True:
                question_topic = "Algebra"
            else:
                question_topic = random.choice(["Trigonometry", "Algebra"])
            
            if question_topic == "Trigonometry":
                letter = "x"
                angle_deg = 40  # Angle in degrees.
                angle_rad = math.radians(angle_deg)  # Convert angle to radians to use in calculations.
                formatted_angle = f"{angle_deg}\u00B0"
                question_title = "Trigonometric\nRatios"

                question_type = random.randint(0, 2)  # Generate a random number between 0 and 2 for the question type, which determines what side of the triangle the number is placed on.
                side = "opposite" if question_type == 0 else "hypotenuse" if question_type == 1 else "adjacent"
                statement_s1 = "Find the length"  # Set the question statement for section 1 (top).
                statement_s2 = f"of the {side}:"  # Set the question statement for section 2 (bottom).
                question_statement = [statement_s1, statement_s2]  # Create a list of the question statement sections.

                # Question list order is [hypotenuse, left side, bottom side, angle].
                # Make the hypotenuse the known side of the triangle, and the left side (opposite) the unknown side.
                if question_type == 0:
                    number1 = random.randint(6, 24)                            # Generate a random number between 6 and 24 for the hypotenuse of the triangle. This number has a higher threshold since the hypotenuse is always the longest side in right-angled triangles.
                    question = [f"{number1} cm", letter, "", formatted_angle]  # Since there is no question, make the "question" a list with the values associated with the triangle.
                    answer = number1 * math.sin(angle_rad)                     # Calculate the left side (opposite) using the sine of the angle.
                # Make the bottom side (adjacent) the known side of the triangle, and the hypotenuse the unknown side.
                elif question_type == 1:
                    number1 = random.randint(4, 16)                            # Generate a random number between 4 and 16 for the left side of the triangle (opposite).
                    question = [letter, "", f"{number1} cm", formatted_angle]  # Since there is no question, make the "question" a list with the values associated with the triangle.
                    answer = number1 / math.cos(angle_rad)                     # Calculate the hypotenuse using the cosine of the angle.
                # Make the left side (opposite) the known side of the triangle, and the bottom side (adjacent) the unknown side.
                elif question_type == 2:
                    number1 = random.randint(4, 16)                            # Generate a random number between 4 and 16 for the bottom side of the triangle (adjacent).
                    question = ["", f"{number1} cm", letter, formatted_angle]  # Since there is no question, make the "question" a list with the values associated with the triangle.
                    answer = number1 / math.tan(angle_rad)                     # Calculate the bottom side (adjacent) using the tangent of the angle.

                formatted_answer = f"{str(int(answer)) if answer == int(answer) else '{:.2f}'.format(answer)} cm"  # Format the answer to 2 decimal places if it is a float (decimal number).

                temp_fake_answers = []
                while len(temp_fake_answers) < 3:  # Generate 3 fake answers for each question.
                    if answer == int(answer):  # Check if the answer is an integer.
                        offset = random.randint(1, 6)  # Generate a random offset between 1 and 6.
                    else:
                        offset = random.uniform(1, 6)  # Generate a random decimal offset between 1 and 6.
                    fake = answer + offset
                    formatted_fake = f"{str(int(fake)) if fake == int(fake) else '{:.2f}'.format(fake)} cm"  # Format the answer to 2 decimal places if it is a float (decimal number).
                    if formatted_fake != formatted_answer and formatted_fake not in temp_fake_answers:  # Check if the formatted fake answer is different from the correct answer and not already in the list of fake answers.
                        temp_fake_answers.append(formatted_fake)  # Append each formatted fake answer to the fake answers list.
            
            elif question_topic == "Algebra":
                letters = ["x", "y", "z", "a", "b", "c", "m", "n"]
                question_title = "Binomial Expansion"
                question_statement = "Expand the following:"
                
                # e.g. (x - 3)(x + 2) = ?.
                letter = random.choice(letters)
                number1 = random.choice([-1, 1]) * random.randint(1, 12)  # Generate a random number between 1 and 12, then multiply it by -1 or 1 to create a random number between -12 and 12.
                number2 = random.choice([-1, 1]) * random.randint(1, 12)  # Generate a random number between 1 and 12, then multiply it by -1 or 1 to create a random number between -12 and 12.
                # Create the question, using if statements to ensure that the number will have an addition sign if it isn't negative, or will have a negative sign if it is negative. ".removeprefix('-')" removes the original negative sign from the number if it is negative, so that a negative sign with spaces can be used instead.
                question = f"({letter}{' + ' if not str(number1).startswith('-') else ' - '}{str(number1).removeprefix('-') if str(number1).startswith('-') else number1})({letter}{' + ' if not str(number2).startswith('-') else ' - '}{str(number2).removeprefix('-') if str(number2).startswith('-') else number2}) = ?"
                
                section1 = f"{letter}\u00b2"  # Square the letter using the Unicode character for superscript 2 (\u00b2).
                section2 = number2 + number1  # Combine the like terms, e.g. 2x + 3x = 5x.
                section3 = number1 * number2  # Multiply the last terms, e.g. 2 * 3 = 6.

                # If section 2 is 0, make "formatted_section2" an empty string. If it's -1, use just a negative letter for "formatted_section2".
                # If it's 1, use just a positive letter for "formatted_section2". If it's not 0 or -1 or 1, use a positive sign with section 2 and the letter for "formatted_section2".
                # Finally, if section 2 is negative, use a negative sign with section 2 and the letter for "formatted_section2".
                formatted_section2 = f"" if section2 == 0 else f" - {letter}" if section2 == -1 else f" + {letter}" if section2 == 1 else f" + {section2}{letter}" if not str(section2).startswith("-") else f" - {str(section2).removeprefix('-')}{letter}"  # If section 2 is 1 or -1, use just the letter as the answer (this follows algebra rules where "1x" is the same as "x" and "-1x" is the same as "-x").
                formatted_section3 = f" + {section3}" if not str(section3).startswith("-") else f" - {str(section3).removeprefix('-')}"  # If section 3 isn't negative, use a positive sign with section 3 for "formatted_section3". If section 3 is negative, use a negative sign with section 3 for "formatted_section3".
                formatted_answer = f"{section1}{formatted_section2}{formatted_section3}"  # Combine the sections to create the answer.

                temp_fake_answers = []
                while len(temp_fake_answers) < 3:  # Generate 3 fake answers for each question.
                    offset1 = random.choice([-1, 1]) * random.randint(2, 10)  # Generate a random offset between 2 and 10, then multiply it by -1 or 1 to create a random number between -10 and 10.
                    offset2 = random.choice([-1, 1]) * random.randint(2, 10)  # Generate a random offset between 2 and 10, then multiply it by -1 or 1 to create a random number between -10 and 10.
                    fake1 = section2 + offset1  # Add the offset to section 2 to create a fake answer.
                    fake2 = section3 + offset2  # Add the offset to section 3 to create a fake answer.
                    
                    # If fake 1 is 0, make "formatted_fake1" an empty string. If it's -1, use just a negative letter for "formatted_fake1".
                    # If it's 1, use just a positive letter for "formatted_fake1". If it's not 0 or -1 or 1, use a positive sign with fake 1 and the letter for "formatted_fake1".
                    # Finally, if fake 1 is negative, use a negative sign with fake 1 and the letter for "formatted_fake1".
                    formatted_fake1 = f"" if fake1 == 0 else f" - {letter}" if fake1 == -1 else f" + {letter}" if fake1 == 1 else f" + {fake1}{letter}" if not str(fake1).startswith("-") else f" - {str(fake1).removeprefix('-')}{letter}"
                    formatted_fake2 = f"" if fake2 == 0 else f" + {fake2}" if not str(fake2).startswith("-") else f" - {str(fake2).removeprefix('-')}"
                    complete_fake = f"{section1}{formatted_fake1}{formatted_fake2}"

                    if complete_fake != formatted_answer and complete_fake not in temp_fake_answers:  # Check if the formatted fake answer is different from the correct answer and not already in the list of fake answers.
                        temp_fake_answers.append(complete_fake)  # Append each formatted fake answer to the fake answers list.

            # Append the question details to the question_details list.
            question_details.append([question_topic, question_title, question_statement, question, formatted_answer, temp_fake_answers])
        return
    

    # Method for generating the medium mode questions.
    def medium_mode(self):
        global question_details, temp_fake_answers

        for i in range(question_amount):  # Loop through the number of questions to be generated.
            if use_trigonometry_questions == True and use_algebra_questions == False:
                question_topic = "Trigonometry"
            elif use_trigonometry_questions == False and use_algebra_questions == True:
                question_topic = "Algebra"
            else:
                question_topic = random.choice(["Trigonometry", "Algebra"])
            
            if question_topic == "Trigonometry":
                letter = "x"
                question_title = "Pythagorean\nTheorem"

                question_type = random.randint(0, 2)  # Generate a random number between 0 and 2 for the question type, which determines what sides of the triangle the two numbers are placed on.
                side = "hypotenuse" if question_type == 0 else "adjacent" if question_type == 1 else "opposite"
                statement_s1 = "Find the length"  # Set the question statement for section 1 (top).
                statement_s2 = f"of the {side}:"  # Set the question statement for section 2 (bottom).
                question_statement = [statement_s1, statement_s2]  # Create a list of the question statement sections.

                # Question list order is [hypotenuse, left side, bottom side, angle(not used - set to None)].
                # Make the hypotenuse the unknown side of the triangle.
                if question_type == 0:
                    number1 = random.randint(2, 12)                        # Generate a random number between 2 and 12 for the left side of the triangle (opposite).
                    # Use "math.ceil" to round up the number to the nearest integer.
                    min_num2 = math.ceil(number1*1.1)                      # Ensure the minimum number for the bottom side (adjacent) is larger than the left side (opposite) by at least 1.1x.
                    number2 = random.randint(min_num2, min_num2+3)         # Generate a random number at least 1.1x larger than the left side, for the bottom side of the triangle (adjacent).
                    question = [letter, f"{number1} cm", f"{number2} cm", None]  # Since there is no question, make the "question" a list with the values associated with the triangle.
                    answer = math.sqrt(number1**2 + number2**2)            # Calculate the hypotenuse using Pythagorean theorem.
                # Make the bottom side (adjacent) the unknown side of the triangle.
                elif question_type == 1:
                    number1 = random.randint(2, 12)                        # Generate a random number between 2 and 12 for the left side of the triangle (opposite).
                    # Use "math.ceil" to round up the number to the nearest integer.
                    min_num2 = math.ceil(number1*1.1)                      # Ensure the minimum number for the hypotenuse (hypotenuse) is larger than the left side (opposite) by at least 1.1x.
                    number2 = random.randint(min_num2, min_num2+3)         # Generate a random number at least 1.1x larger than the left side, for the hypotenuse of the triangle.
                    question = [f"{number2} cm", f"{number1} cm", letter, None]  # Since there is no question, make the "question" a list with the values associated with the triangle.
                    answer = math.sqrt(number2**2 - number1**2)            # Calculate the bottom side (adjacent) using Pythagorean theorem.
                # Make the left side (opposite) the unknown side of the triangle.
                elif question_type == 2:
                    number1 = random.randint(2, 12)                        # Generate a random number between 2 and 12 for the bottom side of the triangle (adjacent).
                    # Use "math.ceil" to round up the number to the nearest integer.
                    min_num2 = math.ceil(number1*1.1)                      # Ensure the minimum number for the hypotenuse is larger than the bottom side (adjacent) by at least 1.1x.
                    number2 = random.randint(min_num2, min_num2+3)         # Generate a random number at least 1.1x larger than the bottom side, for the hypotenuse of the triangle.
                    question = [f"{number2} cm", letter, f"{number1} cm", None]  # Since there is no question, make the "question" a list with the values associated with the triangle.
                    answer = math.sqrt(number2**2 - number1**2)            # Calculate the left side (opposite) using Pythagorean theorem.

                formatted_answer = f"{str(int(answer)) if answer == int(answer) else '{:.2f}'.format(answer)} cm"  # Format the answer to 2 decimal places if it is a float (decimal number).

                temp_fake_answers = []
                while len(temp_fake_answers) < 3:  # Generate 3 fake answers for each question.
                    if answer == int(answer):  # Check if the answer is an integer.
                        offset = random.randint(1, 6)  # Generate a random offset between 1 and 6.
                    else:
                        offset = random.uniform(1, 6)  # Generate a random decimal offset between 1 and 6.
                    fake = answer + offset
                    formatted_fake = f"{str(int(fake)) if fake == int(fake) else '{:.2f}'.format(fake)} cm"  # Format the answer to 2 decimal places if it is a float (decimal number).
                    if formatted_fake != formatted_answer and formatted_fake not in temp_fake_answers:  # Check if the formatted fake answer is different from the correct answer and not already in the list of fake answers.
                        temp_fake_answers.append(formatted_fake)  # Append each formatted fake answer to the fake answers list.
            
            elif question_topic == "Algebra":
                letters = ['x', 'y', 'z', 'a', 'b', 'c', 'm', 'n']
                letter = random.choice(letters)
                question_title = "One Step Equations"
                question_statement = f"Solve for {letter}:"
                
                question_type = random.randint(0, 3)
                if question_type == 0:
                    # e.g. a - 2 = 4 >> a = 6.
                    number1 = random.randint(1, 20)  # Generate a random number between 1 and 20.
                    number2 = random.randint(1, 50)  # Generate a random number between 1 and 50.
                    question = f"{letter} - {number1} = {number2}"
                    answer = number2+number1
                elif question_type == 1:
                    # e.g. a + 2 = 4 >> a = 2.
                    number1 = random.randint(1, 20)  # Generate a random number between 1 and 20.
                    number2 = random.randint(1, 50)  # Generate a random number between 1 and 50.
                    question = f"{letter} + {number1} = {number2}"
                    answer = number2-number1
                elif question_type == 2:
                    # e.g. 2a = 4 >> a = 2.
                    number1 = random.randint(1, 10)  # Generate a random number between 1 and 10, since division is involved and a lower number will help maintain easiness.
                    number2 = random.randint(number1, number1+10)  # Ensure that the second number to divide is greater than the first number, by making the minimum value as "number1" and the maximum value as "number1" + 10.
                    question = f"{number1}{letter} = {number2}"
                    answer = number2/number1
                elif question_type == 3:
                    # e.g. a / 2 = 4 >> a = 8.
                    number1 = random.randint(1, 12)  # Generate a random number between 1 and 12, since multiplication is involved and a lower number will help maintain easiness.
                    number2 = random.randint(1, 12)  # Generate a random number between 1 and 12, since multiplication is involved and a lower number will help maintain easiness.
                    question = f"{letter} / {number1} = {number2}"
                    answer = number2*number1

                formatted_answer = str(int(answer)) if answer == int(answer) else "{:.2f}".format(answer)  # Format the answer to 2 decimal places if it is a float (decimal number).

                temp_fake_answers = []
                while len(temp_fake_answers) < 3:   # Generate 3 fake answers for each question.
                    if answer == int(answer):  # Check if the answer is an integer.
                        offset = random.choice([-1, 1]) * random.randint(1, 8)  # Generate a random offset between 2 and 10, then multiply it by -1 or 1 to create a random number between -10 and 10.
                    else:
                        offset = random.choice([-1, 1]) * random.uniform(1, 6)  # Generate a random decimal offset between 2 and 8, then multiply it by -1 or 1 to create a random number between -8 and 8.
                    fake = answer + offset
                    formatted_fake = str(int(fake)) if fake == int(fake) else "{:.2f}".format(fake)  # Format the answer to 2 decimal places if it is a float (decimal number).
                    if formatted_fake != formatted_answer and formatted_fake not in temp_fake_answers:  # Check if the formatted fake answer is different from the correct answer and not already in the list of fake answers.
                        temp_fake_answers.append(formatted_fake)  # Append each formatted fake answer to the fake answers list.

            # Append the question details to the question_details list.
            question_details.append([question_topic, question_title, question_statement, question, formatted_answer, temp_fake_answers])
        return


    # Method for generating the easy mode questions.
    def easy_mode(self):
        global question_details, temp_fake_answers

        for i in range(question_amount):  # Loop through the number of questions to be generated.
            if use_trigonometry_questions == True and use_algebra_questions == False:
                question_topic = "Trigonometry"
            elif use_trigonometry_questions == False and use_algebra_questions == True:
                question_topic = "Algebra"
            else:
                question_topic = random.choice(["Trigonometry", "Algebra"])

            if question_topic == "Trigonometry":
                question_title = "Area of Triangles"
                statement_s1 = "Find the area"     # Set the question statement for section 1 (top).
                statement_s2 = "of the triangle:"  # Set the question statement for section 2 (bottom).
                question_statement = [statement_s1, statement_s2]  # Create a list of the question statement sections.

                number1 = random.randint(2, 12)                        # Generate a random number between 2 and 12 for the left side of the triangle (opposite).
                # Use "math.ceil" to round up the number to the nearest integer.
                min_num2 = math.ceil(number1*1.1)                      # Ensure the minimum number for the bottom side (adjacent) is larger than the left side (opposite) by at least 1.1x.
                number2 = random.randint(min_num2, min_num2+3)         # Generate a random number at least 1.1x larger than the left side, for the adjacent side of the triangle.
                # Question list order is [hypotenuse (not used - set to None), left side, bottom side, angle (not used - set to None)].
                question = [None, f"{number1} cm", f"{number2} cm", None]  # Since there is no question, make the "question" a list with the values associated with the triangle.
                answer = (number1*number2)/2                           # Calculate the area of the triangle.

                formatted_answer = f"{str(int(answer)) if answer == int(answer) else '{:.2f}'.format(answer)} cm"  # Format the answer to 2 decimal places if it is a float (decimal number).

                temp_fake_answers = []
                while len(temp_fake_answers) < 3:   # Generate 3 fake answers for each question.
                    if answer == int(answer):  # Check if the answer is an integer.
                        offset = random.randint(1, 6)  # Generate a random offset between 1 and 6.
                    else:
                        offset = random.uniform(1, 6)  # Generate a random decimal offset between 1 and 6.
                    fake = answer + offset
                    formatted_fake = f"{str(int(fake)) if fake == int(fake) else '{:.2f}'.format(fake)} cm"  # Format the answer to 2 decimal places if it is a float (decimal number).
                    if formatted_fake != formatted_answer and formatted_fake not in temp_fake_answers:  # Check if the formatted fake answer is different from the correct answer and not already in the list of fake answers.
                        temp_fake_answers.append(formatted_fake)  # Append each formatted fake answer to the fake answers list.

            elif question_topic == "Algebra":
                letters = ["x", "y", "z", "a", "b", "c", "m", "n"]
                letter = random.choice(letters)
                question_title = "Like Terms"
                question_statement = "Simplify the following:"
                
                question_type = random.randint(0, 1)
                if question_type == 0:
                    # e.g. 2x - 4x - 6x = ?.
                    number1 = random.randint(1, 12)  # Generate a random number between 1 and 12.
                    number2 = random.randint(1, 12)  # Generate a random number between 1 and 12.
                    number3 = random.randint(1, 12)  # Generate a random number between 1 and 12.
                    question = f"{number1 if number1 != 1 else ''}{letter} - {number2 if number2 != 1 else ''}{letter} - {number3 if number3 != 1 else ''}{letter} = ?"  # If any numbers are 1 then only include the letter beside those numbers.
                    answer = number1-number2-number3
                elif question_type == 1:
                    # e.g. 2x + 4x + 6x = ?.
                    number1 = random.randint(1, 12)  # Generate a random number between 1 and 12.
                    number2 = random.randint(1, 12)  # Generate a random number between 1 and 12.
                    number3 = random.randint(1, 12)  # Generate a random number between 1 and 12.
                    question = f"{number1 if number1 != 1 else ''}{letter} + {number2 if number2 != 1 else ''}{letter} + {number3 if number3 != 1 else ''}{letter} = ?"  # If any numbers are 1 then only include the letter beside those numbers.
                    answer = number1+number2+number3

                # For instances where the answer is 1 or -1, use just the letter as the answer (this follows algebra rules where "1x" is the same as "x" and "-1x" is the same as "-x").
                if answer == 1:
                    formatted_answer = f"{letter}"
                elif answer == -1:
                    formatted_answer = f"-{letter}"
                else:
                    formatted_answer = f"{answer}{letter}"

                temp_fake_answers = []
                while len(temp_fake_answers) < 3:  # Generate 3 fake answers for each question.
                    offset = random.choice([-1, 1]) * random.randint(2, 10)  # Generate a random offset between 2 and 10, then multiply it by -1 or 1 to create a random number between -10 and 10.
                    fake = answer + offset
                    # If the fake answer is 1 or -1, use just the letter as the formatted fake answer (this follows algebra rules where "1x" is the same as "x" and "-1x" is the same as "-x").
                    # If it is 0, use just the number as the formatted fake answer. If it is not 1, -1, or 0, use the number and letter as the formatted fake answer.
                    formatted_fake = f"{letter}" if fake == 1 else f"-{letter}" if fake == -1 else f"{fake}" if fake == 0 else f"{fake}{letter}"
                    if formatted_fake != formatted_answer and formatted_fake not in temp_fake_answers:  # Check if the formatted fake answer is different from the correct answer and not already in the list of fake answers.
                        temp_fake_answers.append(formatted_fake)  # Append each formatted fake answer to the fake answers list.

            # Append the question details to the question_details list.
            question_details.append([question_topic, question_title, question_statement, question, formatted_answer, temp_fake_answers])
        return


    # Procedure for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
    def setup_quiz(self, scenario):
        global quiz_paused, banners_loaded
        quiz_paused = False  # Set the flag to indicate that the quiz is not paused.

        if scenario != "Restart Quiz" and scenario != "Retry Quiz" and scenario != "View Answers":  # Ensure that questions are not generated again when restarting or retrying the quiz.
            # Set the difficulty level of the quiz.
            if difficulty == "Easy":
                self.easy_mode()
            elif difficulty == "Medium":
                self.medium_mode()
            elif difficulty == "Hard":
                self.hard_mode()

        # Setting the main window geometry (size) before element creation ensures the window doesn't glitch between sizes.
        main_window.geometry("758x434")  # Final size calculated based on the window size seen after the elements are all created.

        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
        main_window.columnconfigure(0, weight=1, minsize=0)
        main_window.columnconfigure(1, weight=1, minsize=450)

        # Set up the menu bar.
        quiz_menubar = Menu(main_window)  # Create a new menu bar.
        
        quiz_menu = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        quiz_menubar.add_cascade(label="Quiz", menu=quiz_menu)
        quiz_menu.add_command(label="Restart Quiz", accelerator="Ctrl+R", command=lambda: self.stop_timer("Restart Quiz", "Quiz"))
        quiz_menu.add_command(label="New Quiz", accelerator="Ctrl+N", command=lambda: self.stop_timer("New Quiz", "Quiz"))
        quiz_menu.add_command(label="Exit Quiz", accelerator="Esc", command=lambda: self.exit_quiz("Scoreboard" if self.answer_viewing_active == True or self.retry_active == True else "Home", "Quiz"))  # If the user is currently viewing the answers or retrying a quiz, exiting the quiz goes to the scoreboard screen rather than the home screen. Exiting the normal quiz mode goes back to the home screen.

        settings_menu = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        quiz_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, command=lambda: self.tools.timer_config("Quiz Menubar", "Enable", self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH)), value=True)        # Use lambda so that the method is called only when the radiobutton is clicked, rather than when it's defined.
        timer_settings.add_radiobutton(label="Disabled", variable=timer, command=lambda: self.tools.timer_config("Quiz Menubar", "Disable", self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH)), value=False)     # Use lambda so that the method is called only when the radiobutton is clicked, rather than when it's defined.
        question_settings = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=question_settings, label="Question Topics")
        question_settings.add_checkbutton(label="Trigonometry", variable=enable_trigonometry, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        question_settings.add_checkbutton(label="Algebra", variable=enable_algebra, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=history_settings, label="Score Deletion History States")
        history_settings.add_radiobutton(label="Disabled", variable=deletion_history_states, value=0, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="10", variable=deletion_history_states, value=10, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="25", variable=deletion_history_states, value=25, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="50", variable=deletion_history_states, value=50, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))

        help_menu = Menu(quiz_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        quiz_menubar.add_cascade(label="Help", menu=help_menu)
        origin = "Quiz Answers" if self.answer_viewing_active == True else "Quiz"  # Documentation file opening command and about window utilises pause functionality when a quiz is active, so the origin needs to be something other than "Quiz" for this to not be used (since the answer viewing mode cannot be paused).
        help_menu.add_command(label="Documentation", command=lambda: self.tools.open_file(origin, DOCUMENTATION_PATH, "readme.pdf"))
        help_menu.add_command(label="About", command=lambda: self.about.setup_about(origin))

        main_window.config(menu=quiz_menubar)

        # Bind key shortcuts to perform actions.
        main_window.bind("<Control-r>", lambda e: self.stop_timer("Restart Quiz", "Quiz"))  # Bind Ctrl+R to restart the quiz.
        main_window.bind("<Control-n>", lambda e: self.stop_timer("New Quiz", "Quiz"))      # Bind Ctrl+N to start a new quiz.
        main_window.bind("<Escape>", lambda e: self.exit_quiz("Scoreboard" if self.answer_viewing_active == True or self.retry_active == True else "Home", "Quiz"))              # Bind Escape to exit the quiz and return to the home page.
        self.binded_keys = ["<Control-r>", "<Control-n>", "<Escape>"]                       # Create a list of binded keys to be used later for unbinding them when the user goes to a different page.

        if banners_loaded == False:
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

            banners_loaded = True

        # Set up the main content frame to place the main quiz frames and elements inside.
        self.main_content_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.main_content_frame.grid(column=1, row=0, sticky=EW, padx=35, pady=(24,25))

        # Set up a content frame to place the top quiz elements inside.
        quiz_dtls_frame1 = CTk.CTkFrame(self.main_content_frame, fg_color=FRAME_FG, corner_radius=10)
        quiz_dtls_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(0,5))
        
        if self.answer_viewing_active == True:
            # Set width for columns 0-2 (3 total) in quiz details frame 1. Total minimum column width is 410px.
            quiz_dtls_frame1.columnconfigure(0, weight=0, minsize=190)
            quiz_dtls_frame1.columnconfigure(1, weight=0, minsize=110)
            quiz_dtls_frame1.columnconfigure(2, weight=0, minsize=110)
            
            # Create the labels and pause button to be placed at the top of the quiz page.
            self.question_no_lbl = CTk.CTkLabel(quiz_dtls_frame1, text=f"Question: {self.question_no}/{question_amount}", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR)
            self.question_no_lbl.grid(column=0, row=0, pady=10, sticky=NSEW)
            
            self.reviewing_btn_sizes = [100, 30, 14]  # Specify the sizing to be used for buttons (width, height, font size).

            self.previous_button = CTk.CTkButton(quiz_dtls_frame1, text="Previous", command=lambda: self.tools.on_ctkbutton_click(self.previous_button, None, lambda: self.answer_management(self.previous_button, None)),
                                              width=self.reviewing_btn_sizes[0], height=self.reviewing_btn_sizes[1], corner_radius=7.5, fg_color=BUTTON_FG, hover=None, state="disabled", font=(DEFAULT_FONT, self.reviewing_btn_sizes[2], "bold"), text_color=FONT_COLOUR, text_color_disabled=DISABLED_FONT_COLOUR)
            self.previous_button.grid(column=1, row=0, padx=(0,10), pady=10)
            
            self.next_button = CTk.CTkButton(quiz_dtls_frame1, text="Next", command=lambda: self.tools.on_ctkbutton_click(self.next_button, None, lambda: self.answer_management(self.next_button, None)),
                                          width=self.reviewing_btn_sizes[0], height=self.reviewing_btn_sizes[1], corner_radius=7.5, fg_color=BUTTON_FG, hover=None, font=(DEFAULT_FONT, self.reviewing_btn_sizes[2], "bold"), text_color=FONT_COLOUR)
            self.next_button.grid(column=2, row=0, padx=(0,10), pady=10)
            self.next_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.next_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
        else:
            # Set width for columns 0-2 (3 total) in quiz details frame 1. Total minimum column width is 410px.
            quiz_dtls_frame1.columnconfigure(0, weight=0, minsize=185)
            quiz_dtls_frame1.columnconfigure(1, weight=0, minsize=40)
            quiz_dtls_frame1.columnconfigure(2, weight=0, minsize=185)

            self.pause_image = Image.open("AppData/Images/pause.png")  # Load the pause button image.
            self.pause_img = CTk.CTkImage(self.pause_image, size=(16, 17))  # Create a CTkImage object with the pause image to allow scaling to be used.

            self.play_image = Image.open("AppData/Images/play.png")  # Load the play button image.
            self.play_img = CTk.CTkImage(self.play_image, size=(16, 17))  # Create a CTkImage object with the play image to allow scaling to be used.

            # Create the labels and pause button to be placed at the top of the quiz page.
            self.question_no_lbl = CTk.CTkLabel(quiz_dtls_frame1, text=f"Question: {self.question_no}/{question_amount}", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR)
            self.question_no_lbl.grid(column=0, row=0, pady=10, sticky=NSEW)
            
            self.pause_btn_sizes = [40, 30, 14]  # Specify the sizing to be used for buttons (width, height, font size).

            self.pause_button = CTk.CTkButton(quiz_dtls_frame1, text=None, command=lambda: self.tools.on_ctkbutton_click(self.pause_button, None, self.pause_quiz),
                                              width=self.pause_btn_sizes[0], height=self.pause_btn_sizes[1], corner_radius=7.5, image=self.pause_img, fg_color=BUTTON_FG, hover=None, font=(DEFAULT_FONT, self.pause_btn_sizes[2], "bold"), text_color=FONT_COLOUR)
            self.pause_button.grid(column=1, row=0, pady=10)
            self.pause_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.pause_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
            
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

        self.inner_frame = CTk.CTkFrame(self.question_frame, fg_color="#78b0f4", corner_radius=10)
        self.inner_frame.grid(column=0, row=0, rowspan=2, padx=20)
        self.inner_frame.columnconfigure(0, weight=0, minsize=370)

        self.upcoming_topic = question_details[self.current_index][0]
        self.current_title = question_details[self.current_index][1]
        self.correct_answer = question_details[self.current_index][4]
        self.fake_answers = question_details[self.current_index][5]

        # Set up the main question GUI contents depending on the topic.
        if self.upcoming_topic == "Trigonometry":
            self.setup_trigonometry()
        elif self.upcoming_topic == "Algebra":
            self.setup_algebra()

        # Create a frame for the answer buttons
        self.answer_frame = CTk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.answer_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=(5,0))
        
        # Set width for columns 0-1 (2 total) in the answer frame. Total minimum column width is 410px.
        self.answer_frame.columnconfigure(0, weight=0, minsize=205)
        self.answer_frame.columnconfigure(1, weight=0, minsize=205)

        if self.answer_viewing_active == True:
            # Create the disabled answer buttons, which automatically send their value to answer management (using invoke) to identify what button displays the stored user answer and the correct answer.
            self.ans_button_1 = CTk.CTkButton(self.answer_frame, text=f" A.    {self.all_answers[self.current_index][0]}", font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR,
                                       anchor=W, width=200, height=40, corner_radius=10, fg_color=BUTTON_FG, hover=None, state="disabled", text_color_disabled=DISABLED_FONT_COLOUR)
            self.ans_button_1.grid(column=0, row=0, padx=(0, 5), pady=(0,5))
            self.answer_management(self.ans_button_1, self.all_answers[self.current_index][0])  # Send the button name and the answer to the answer management method so that the specific button (self.ans_button_1) will be highlighted if it contains the correct or user-chosen incorrect answer.
            
            self.ans_button_2 = CTk.CTkButton(self.answer_frame, text=f" B.    {self.all_answers[self.current_index][1]}", font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR,
                                       anchor=W, width=200, height=40, corner_radius=10, fg_color=BUTTON_FG, hover=None, state="disabled", text_color_disabled=DISABLED_FONT_COLOUR)
            self.ans_button_2.grid(column=1, row=0, padx=(5, 0), pady=(0,5))
            self.answer_management(self.ans_button_2, self.all_answers[self.current_index][1])  # Send the button name and the answer to the answer management method so that the specific button (self.ans_button_2) will be highlighted if it contains the correct or user-chosen incorrect answer.
            
            self.ans_button_3 = CTk.CTkButton(self.answer_frame, text=f" C.    {self.all_answers[self.current_index][2]}", font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR,
                                       anchor=W, width=200, height=40, corner_radius=10, fg_color=BUTTON_FG, hover=None, state="disabled", text_color_disabled=DISABLED_FONT_COLOUR)
            self.ans_button_3.grid(column=0, row=1, padx=(0, 5), pady=(5,0))
            self.answer_management(self.ans_button_3, self.all_answers[self.current_index][2])  # Send the button name and the answer to the answer management method so that the specific button (self.ans_button_3) will be highlighted if it contains the correct or user-chosen incorrect answer.
            
            self.ans_button_4 = CTk.CTkButton(self.answer_frame, text=f" D.    {self.all_answers[self.current_index][3]}", font=(DEFAULT_FONT, 16, "bold"), text_color=FONT_COLOUR,
                                       anchor=W, width=200, height=40, corner_radius=10, fg_color=BUTTON_FG, hover=None, state="disabled", text_color_disabled=DISABLED_FONT_COLOUR)
            self.ans_button_4.grid(column=1, row=1, padx=(5, 0), pady=(5,0))
            self.answer_management(self.ans_button_4, self.all_answers[self.current_index][3])  # Send the button name and the answer to the answer management method so that the specific button (self.ans_button_4) will be highlighted if it contains the correct or user-chosen incorrect answer.
        
        else:
            # Create a list of the answers and shuffle them.
            answer_choices = [self.correct_answer] + self.fake_answers
            random.shuffle(answer_choices)

            # Create the answer buttons.
            self.ans_btn_sizes = [200, 40, 16]  # Specify the sizing to be used for buttons (width, height, font size).

            self.ans_button_1 = CTk.CTkButton(self.answer_frame, text=f" A.    {answer_choices[0]}", command=lambda: self.tools.on_ctkbutton_click(self.ans_button_1, None, lambda: self.answer_management(self.ans_button_1, answer_choices[0])),
                                       anchor=W, width=self.ans_btn_sizes[0], height=self.ans_btn_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=None, font=(DEFAULT_FONT, self.ans_btn_sizes[2], "bold"), text_color=FONT_COLOUR)
            self.ans_button_1.grid(column=0, row=0, padx=(0, 5), pady=(0,5))
            self.ans_button_1.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.ans_button_1))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.

            self.ans_button_2 = CTk.CTkButton(self.answer_frame, text=f" B.    {answer_choices[1]}", command=lambda: self.tools.on_ctkbutton_click(self.ans_button_2, None, lambda: self.answer_management(self.ans_button_2, answer_choices[1])),
                                       anchor=W, width=self.ans_btn_sizes[0], height=self.ans_btn_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=None, font=(DEFAULT_FONT, self.ans_btn_sizes[2], "bold"), text_color=FONT_COLOUR)
            self.ans_button_2.grid(column=1, row=0, padx=(5, 0), pady=(0,5))
            self.ans_button_2.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.ans_button_2))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.

            self.ans_button_3 = CTk.CTkButton(self.answer_frame, text=f" C.    {answer_choices[2]}", command=lambda: self.tools.on_ctkbutton_click(self.ans_button_3, None, lambda: self.answer_management(self.ans_button_3, answer_choices[2])),
                                       anchor=W, width=self.ans_btn_sizes[0], height=self.ans_btn_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=None, font=(DEFAULT_FONT, self.ans_btn_sizes[2], "bold"), text_color=FONT_COLOUR)
            self.ans_button_3.grid(column=0, row=1, padx=(0, 5), pady=(5,0))
            self.ans_button_3.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.ans_button_3))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.

            self.ans_button_4 = CTk.CTkButton(self.answer_frame, text=f" D.    {answer_choices[3]}", command=lambda: self.tools.on_ctkbutton_click(self.ans_button_4, None, lambda: self.answer_management(self.ans_button_4, answer_choices[3])),
                                       anchor=W, width=self.ans_btn_sizes[0], height=self.ans_btn_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=None, font=(DEFAULT_FONT, self.ans_btn_sizes[2], "bold"), text_color=FONT_COLOUR)
            self.ans_button_4.grid(column=1, row=1, padx=(5, 0), pady=(5,0))
            self.ans_button_4.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.ans_button_4))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.

        if self.answer_viewing_active == False:
            self.start_timer()  # Only start the timer if answer viewing is not active (False), since the timer does not need to be used when viewing quiz answers.



class Home:
    # Constructor for the "Home" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Quiz" class, for example, to be accessed from within the "Home" class.
    def __init__(self, tools_instance, about_instance, scoreboard_instance, completion_instance, quiz_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.about = about_instance             # Store a reference to the "About" class instance.
        self.scoreboard = scoreboard_instance   # Store a reference to the "Scoreboard" class instance.
        self.completion = completion_instance   # Store a reference to the "Completion" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.


    # Function for processing slider values and returning a tuple containing the difficulty, color, and hover color, or the number of questions.
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
        global users, deiconify_reqd, banners_loaded

        # Setting the main window geometry (size) before element creation ensures the window doesn't glitch between sizes.
        main_window.geometry("758x434")  # Final size calculated based on the window size seen after the elements are all created.

        # Set width for columns 0-1 (2 total) in the main window. Positive weight means the column will expand to fill the available space.
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
        question_settings = Menu(home_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=question_settings, label="Question Topics")
        question_settings.add_checkbutton(label="Trigonometry", variable=enable_trigonometry, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        question_settings.add_checkbutton(label="Algebra", variable=enable_algebra, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings = Menu(home_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        settings_menu.add_cascade(menu=history_settings, label="Score Deletion History States")
        history_settings.add_radiobutton(label="Disabled", variable=deletion_history_states, value=0, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="10", variable=deletion_history_states, value=10, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="25", variable=deletion_history_states, value=25, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))
        history_settings.add_radiobutton(label="50", variable=deletion_history_states, value=50, command=lambda: self.tools.save_details(None, "Menubar", None, SETTINGS_FILE_PATH))

        help_menu = Menu(home_menubar, tearoff=0, activebackground=MENU_HOVER, activeforeground=MENU_ACTIVE_FG)
        home_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=lambda: self.tools.open_file("Home", DOCUMENTATION_PATH, "readme.pdf"))
        help_menu.add_command(label="About", command=lambda: self.about.setup_about("Home"))

        main_window.config(menu=home_menubar)

        if banners_loaded == False:
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

            banners_loaded = True

        # Set up the main content frame to place the main home frames and elements inside.
        self.main_content_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.main_content_frame.grid(column=1, row=0, sticky=EW, padx=35, pady=(0,20))

        # Logo creation
        logo_canvas = Canvas(self.main_content_frame, bg=MAIN_WINDOW_BG, bd=0, highlightthickness=0)  # Create a canvas for the banner image.
        logo_canvas.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,0))
        logo = Image.open("AppData/Images/logo.png")
        logo = ImageTk.PhotoImage(logo)
        logo_canvas.configure(width=410, height=logo.height()+5)  # Add 5 pixels to height to prevent image clipping on the bottom of image.
        logo_canvas.create_image(410 / 2, logo.height() / 2, anchor=CENTER, image=logo)  # Add the image to the canvas by calculating the x and y coordinates for centre position.
        logo_canvas.image = logo

        # Set up a content frame to place the main home elements inside.
        self.home_frame1 = CTk.CTkFrame(self.main_content_frame, fg_color=FRAME_FG, corner_radius=10)
        self.home_frame1.grid(column=0, row=1, sticky=EW, padx=20, pady=(20,5))

        # Set width for columns 0-2 (3 total) in home frame 1. Total minimum column width is 410px.
        self.home_frame1.columnconfigure(0, weight=0, minsize=100)
        self.home_frame1.columnconfigure(1, weight=0, minsize=210)
        self.home_frame1.columnconfigure(2, weight=0, minsize=100)

        # Create the labels to be placed next to their relevant entry boxes.
        CTk.CTkLabel(self.home_frame1, text="Username", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=0, sticky=E, padx=(0,5), pady=(20,0))
        CTk.CTkLabel(self.home_frame1, text="Difficulty", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=1, sticky=E, padx=(0,5), pady=15)
        CTk.CTkLabel(self.home_frame1, text="Questions", font=(DEFAULT_FONT, 14, "bold"), text_color=FONT_COLOUR).grid(column=0, row=2, sticky=E, padx=(0,5), pady=(0,20))

        self.difficulty_lbl = CTk.CTkLabel(self.home_frame1, text="", font=(DEFAULT_FONT, 12, "bold"), text_color=FONT_COLOUR)     # Create an empty placeholder label to display the difficulty level.
        self.difficulty_lbl.grid(column=2, row=1, sticky=W, padx=(5,0), pady=15)
        self.question_amnt_lbl = CTk.CTkLabel(self.home_frame1, text="", font=(DEFAULT_FONT, 12, "bold"), text_color=FONT_COLOUR)  # Create an empty placeholder label to display the number of questions.
        self.question_amnt_lbl.grid(column=2, row=2, sticky=W, padx=(5,0), pady=(0,20))

        # Set up the username entry, which is either an entry box if there are no usernames saved, or a combo box if there are usernames saved. This prevents the user from trying to open a combo box dropdown when there are no usernames saved.
        self.display_usernames = [user[1] for user in users]  # Get the usernames from the users list.
        self.processed = []  # Create an empty list to store one instance of each username, ensuring that there are no duplicates.
        # Create a list of usernames that are unique regardless of casing (e.g., "Jack" and "JACK" are treated as the same username - "jack"), using ".lower" so that all pr usernames are converted to lowercase.
        # Only the first occurrence of each lowercase name is included in "unique_display_usernames", as all lowercase versions are added to the "processed" list to find duplicates.
        self.unique_display_usernames = [name for name in self.display_usernames if not (name.lower() in self.processed or self.processed.append(name.lower()))]  # Usernames included in "unique_display_usernames" are ones that are not already in the "processed" list. If they aren't in the "processed" list, add them to the list to prevent future duplicates.

        if self.unique_display_usernames == []:  # Check if the usernames list is empty
            self.username_entry = CTk.CTkEntry(self.home_frame1, fg_color="#73ace0", border_color="#6aa5db", text_color=FONT_COLOUR, corner_radius=10)
            self.username_entry.insert(0, "")
            self.entry_type = "CTkEntry"
        else:
            # Setup combo box and sliders (scales).
            self.username_entry = CTk.CTkComboBox(self.home_frame1, fg_color="#73ace0", border_color="#6aa5db", button_color="#6aa5db", button_hover_color="#5997d5", text_color=FONT_COLOUR, corner_radius=10)
            self.username_entry.set("")
            self.entry_type = "CTkComboBox"
            # Attach the scrollable dropdown library to the username entry combo box.
            self.dropdown = CTkScrollableDropdown(self.username_entry, values=[""], justify="left", button_color="transparent", fg_color="#73ace0", bg_color=FRAME_FG, frame_border_color="#6aa5db", frame_corner_radius=10,
                                                  scrollbar_button_color="#5997d5", scrollbar_button_hover_color="#497caf", hover_color=MENU_HOVER, text_color=FONT_COLOUR, autocomplete=True)
            self.dropdown.configure(values=self.unique_display_usernames)  # Set the values of the combo box to the usernames of the users in the users list (user[1])
            # CTkScrollableDropdown library utilises "transient()" to stay on top, so after destroying the combo box (by going to a new page - Scoreboard or Quiz) and creating it again (going back to the Home page), the main window needs to be focused. 
            # If this isn't done, the focus will go back to the dropdown and prevent interaction with the combo box entry section, stopping users from being able to type inside it.
            main_window.focus_force()  # Focus the main window to ensure interaction with the combo box entry section.
        self.username_entry.grid(column=1, row=0, padx=5, pady=(20,0), sticky=EW)

        self.difficulty_slider = CTk.CTkSlider(self.home_frame1, from_=0, to=2, number_of_steps=2, command=lambda value: self.slider_label_update("S1", value), orientation=HORIZONTAL, fg_color="#73ace0", button_color="#4d97e8")
        self.difficulty_slider.grid(column=1, row=1, padx=5, pady=15, sticky=EW)
        self.questions_slider = CTk.CTkSlider(self.home_frame1, from_=5, to=35, number_of_steps=30, command=lambda value: self.slider_label_update("S2", value), orientation=HORIZONTAL, progress_color="#4d97e8", fg_color="#73ace0", button_color="#4d97e8", button_hover_color="#3b83c4")
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
        self.button_frame = CTk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.button_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=(5,20))
        
        # Set width for columns 0-1 (2 total) in the button frame. Total minimum column width is 410px.
        self.button_frame.columnconfigure(0, weight=0, minsize=205)
        self.button_frame.columnconfigure(1, weight=0, minsize=205)

        # Create the buttons.
        self.button_sizes = [200, 35, 14]  # Specify the sizing to be used for buttons (width, height, font size).

        self.scoreboard_button = CTk.CTkButton(self.button_frame, text="Scoreboard", command=lambda: self.tools.on_ctkbutton_click(self.scoreboard_button, self.button_sizes, lambda: self.tools.save_details("Scoreboard", "Home", "Temporary", None)),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=None, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.scoreboard_button.grid(column=0, row=1, padx=(0,5))
        self.scoreboard_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.scoreboard_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
        self.start_button = CTk.CTkButton(self.button_frame, text="Start", command=lambda: self.tools.on_ctkbutton_click(self.start_button, self.button_sizes, lambda:self.tools.save_details("Quiz", "Home", "Permanent", SETTINGS_FILE_PATH)),
                      width=self.button_sizes[0], height=self.button_sizes[1], corner_radius=10, fg_color=BUTTON_FG, hover=None, font=(DEFAULT_FONT, self.button_sizes[2], "bold"), text_color=FONT_COLOUR)
        self.start_button.grid(column=1, row=1, padx=(5,0))
        self.start_button.bind("<Enter>", lambda e: self.tools.on_ctkbutton_enter(self.start_button))  # Bind the "Enter" event to the "on_ctkbutton_enter" method so that the button changes to a darker colour when the mouse hovers over it.
        
        if deiconify_reqd == True:   # Check if deiconify is required, which is True when the main window is first created on program start. 
            main_window.deiconify()  # Show the main window after all elements are created to prevent flickering of the window before the UI is set up.
            deiconify_reqd = False   # Set the flag to False so that the main window is not deiconified again when the Home page is set up again.



# Main function for starting the program.
def main(): 
    global operating_system, APP_VERSION, main_window, deiconify_reqd, MAIN_WINDOW_BG, FRAME_FG, BUTTON_FG, BUTTON_HOVER, BUTTON_CLICKED, MENU_ACTIVE_FG, MENU_HOVER, FONT_COLOUR, DISABLED_FONT_COLOUR, DEFAULT_FONT, SEMIBOLD_DEFAULT_FONT  # Global variables and constants for the operating system and window UI elements/design.
    global full_directory, initial_pdf_directory, INITIAL_PDF_NAME, DOCUMENTATION_PATH, SCOREBOARD_FILE_PATH, SETTINGS_FILE_PATH  # Global variables and constants for the file paths of the general directories, JSON files, and the PDF scoreboard file.
    global users, overwrite_score, quiz_paused, banners_loaded, username, difficulty_num, question_amount, question_details, settings, default_settings, timer, enable_trigonometry, enable_algebra, deletion_history_states, history_stack, redo_stack, data_loaded  # Global lists and variables for data and flags

    # Get the operating system name to manage functionalities in the program with limited support for multiple operating systems.
    # When run on Linux, this will return "Linux". On macOS, this will return "Darwin". On Windows, this will return "Windows".
    operating_system = platform.system()

    # Set the version number of the program.
    APP_VERSION = "4.3.0"

    # Configure the main window and the variables used for UI element design.
    main_window = Tk()                              # Initialise the main window. For scaling reasons, use a Tk window instead of CTk.
    main_window.withdraw()                          # Hide the main window until all elements are created, preventing a flicker of the window before the UI is set up.
    deiconify_reqd = True                           # Initialise a flag to track whether the main window should be deiconified (shown) after all elements are created.
    CTk.deactivate_automatic_dpi_awareness()        # Deactivate the automatic DPI awareness of the CTk library, allowing it to work with Tkinter's DPI scaling. This resolves an issue with the custom combobox not scaling correctly.
    main_window.title("QWhizz Math")                # Set the title of the window.
    if os.path.exists("AppData/Images/icon.png"):   # Check if the icon file exists before setting it.
        main_window.iconphoto(False, PhotoImage(file="AppData/Images/icon.png"))  # Set the title bar icon.
    main_window.resizable(False, False)             # Set the program window's resizable property for height and width to False.
    
    # Colour hex code for UI elements
    MAIN_WINDOW_BG = "#d0ebfc"                  # Set the background colour to be used for the main window.
    FRAME_FG = "#87bcf4"                        # Set the foreground colour to be used for all frames.
    BUTTON_FG = "#5ba2ef"                       # Set the foreground colour to be used for all buttons.
    BUTTON_HOVER = "#4c93e3"                    # Set the hover colour to be used for all buttons.
    BUTTON_CLICKED = "#4989d8"                  # Set the clicked colour to be used for all buttons.
    MENU_ACTIVE_FG = "#FFFFFF"                  # Set the foreground colour to be used for active menu items.
    MENU_HOVER = "#a3cbf5"                      # Set the hover colour to be used for all menu items.
    FONT_COLOUR = "#FFFFFF"                     # Set the font colour to be used for all CTk elements.
    DISABLED_FONT_COLOUR = "#a3cbf5"            # Set the font colour to be used for all disabled CTk elements, such as buttons.
    
    # Default program font
    available_fonts = font.families()  # Get a list of available fonts on the system.
    DEFAULT_FONT = "Segoe UI" if "Segoe UI" in available_fonts else "TkDefaultFont"  # Use "Segoe UI" if available, otherwise use "TkDefaultFont" as a fallback.
    SEMIBOLD_DEFAULT_FONT = "Segoe UI Semibold" if "Segoe UI Semibold" in available_fonts else "Segoe UI" if "Segoe UI" in available_fonts else "TkDefaultFont"  # Use "Segoe UI Semibold" if available, otherwise use "Segoe UI" if available, otherwise use "TkDefaultFont" as a final fallback.

    # Setup the directories and paths for saving and loading data.
    full_directory = f"{os.path.dirname(os.path.abspath(__file__))}/AppData"  # Get the absolute intended path of the JSON files for debugging purposes when errors and warnings occur, storing it in "full_directory".
    initial_pdf_directory = f"{os.path.dirname(os.path.abspath(__file__))}"   # Get the absolute intended path of the PDF scoreboard file for debugging purposes when errors and warnings occur, storing it in "initial_pdf_directory".
    INITIAL_PDF_NAME = "QWhizz Math Scoreboard.pdf"                           # Set the file path for the scoreboard PDF file.
    DOCUMENTATION_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/readme.pdf"  # Set the file path for the documentation PDF file.
    SCOREBOARD_FILE_PATH = "AppData/scoreboard.json"  # Set the file path for the scoreboard JSON file.
    SETTINGS_FILE_PATH = "AppData/settings.json"      # Set the file path for the settings JSON file.

    # Initialise global lists and variables.
    users = []                              # Create empty list for user details and their quiz results to be stored inside.
    overwrite_score = True                  # Initialise a flag to track whether a score should be overwritten or not if a user already exists with the same username and difficulty.
    quiz_paused = False                     # Initialise a flag to track whether the quiz is paused or not.
    banners_loaded = False                  # Initialise a flag to track whether the banner images have been loaded or not, so that they aren't reloaded when switching between pages that both use the banenr images.
    username = None                         # Initialise the username attribute as None.
    difficulty_num = None                   # Initialise the difficulty_num attribute as None.
    question_amount = None                  # Initialise the question_amount attribute as None.
    question_details = []                   # Create empty list for question details to be stored inside.
    settings = []                           # Create empty list for settings to be stored inside.
    default_settings = {"enable_timer": True, "enable_trigonometry": True, "enable_algebra": True, "deletion_history_states": 10}  # Create a dictionary for default settings, with the "enable_timer", "enable_trigonometry", and "enable_algebra" keys set to True and the "deletion_history_states" (amount of deletion events that can be undone) key set to 10.
    timer = BooleanVar(value=default_settings["enable_timer"])                           # Create a "timer" BooleanVar global reference to control the timer checkbutton state, with the default value being dependent on the "enable_timer" key in the "default_settings" dictionary, setting the checkbutton in an on state.
    enable_trigonometry = BooleanVar(value=default_settings["enable_trigonometry"])      # Create an "enable_trigonometry" BooleanVar global reference to control the trigonometry checkbutton state, with the default value being dependent on the "enable_trigonometry" key in the "default_settings" dictionary, setting the checkbutton in an on state.
    enable_algebra = BooleanVar(value=default_settings["enable_algebra"])                # Create an "enabled_algebra" BooleanVar global reference to control the algebra checkbutton state, with the default value being dependent on the "enable_algebra" key in the "default_settings" dictionary, setting the checkbutton in an on state.
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

    # Load the data from the JSON files and setup the home page.
    tools.load_details("scoreboard", SCOREBOARD_FILE_PATH, "users")     # Load the user scores from the scoreboard.json file.
    tools.load_details("settings", SETTINGS_FILE_PATH, "settings")      # Load the settings from the settings.json file.
    main_window.configure(bg=MAIN_WINDOW_BG)                            # Configure the main window to use the background colour (value) of the "MAIN_WINDOW_BG variable".
    home_page.setup_homepage()                                          # Call the "setup_homepage" method from the "home_page" class instance to set up the home page UI elements.

    # Start the Tkinter event loop so that the GUI window stays open.
    main_window.mainloop()


# Run the program file only if the script is being run directly as the main program (not imported as a module).
if __name__ == "__main__":
    main()  # Run the main function.