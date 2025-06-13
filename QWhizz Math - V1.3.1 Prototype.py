# Date Created: 05/05/2025
# Author: Jack Compton
# Purpose: GUI application for Flow Computing that helps students with their mathematics.
# BEFORE USE: For windows, open Command Prompt and type "pip install customtkinter" then press enter. If or once installed, this program can be used.

import customtkinter as CTk
from tkinter import *
from tkinter import messagebox
import time, random

class Tools:
    # Constructor for the "Tools" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Home" class, for example, to be accessed from within the "Tools" class.
    def __init__(self, scoreboard_instance, completion_instance, quiz_instance, homepage_instance):
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


    # Method for saving details specific to the specified window.
    def save_details(self, window):
        global username, difficulty_num, questions
        if window == "Home":
            username = self.home.username_entry.get()           # Get the username entry widget value.
            difficulty_num = self.home.difficulty_slider.get()  # Get the difficulty slider value.
            questions = int(self.home.questions_slider.get())   # Get the questions slider value.
    

    # Method for resetting details specific to the specified window.
    def reset_details(self, origin):
        global username, difficulty, difficulty_num, questions
        if origin == "Completion":
            username = None
            difficulty = None
            difficulty_num = None
            questions = None


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
    def __init__(self):  
        # Disable the main window to prevent interaction with it while the about window is open.
        main_window.attributes("-disabled", True)
        
        # Create a top-level window (separate from the main window).
        self.about_window = Toplevel(main_window)
        self.about_window.title("About")
        self.about_window.columnconfigure(0, weight=0, minsize=300)
        self.about_window.resizable(False, False)
        self.about_window.update_idletasks()  # Process any pending events for the window before calculating the centre position later.
        
        # Centre the "About" window above the main window.
        x = main_window.winfo_x() + main_window.winfo_width() // 2 - self.about_window.winfo_width() // 2 - 50
        y = main_window.winfo_y() + main_window.winfo_height() // 2 - self.about_window.winfo_height() // 2 + 50
        self.about_window.geometry(f"+{x}+{y}")
        
        self.about_window.transient(main_window)  # Keep on top of parent window (main_window)
        self.about_window.lift()
        self.about_window.focus()

        # Add program details and a close button.
        CTk.CTkLabel(self.about_window, text="QWhizz Math\nVersion 1.3.1\n© 2025 Jack Compton", justify="center").grid(row=0, column=0, sticky=EW, padx=10, pady=(20,10))
        CTk.CTkButton(self.about_window, text="Close", command=self.close).grid(row=1, column=0, sticky=EW, padx=10, pady=10)

        # Override the window close (X) button behavior so that the main window is enabled again when the about window is closed using this button.
        self.about_window.protocol("WM_DELETE_WINDOW", self.close)

        # Bind the "esc" key to the "close" function so that the window can be closed by pressing "esc".
        self.about_window.bind("<Escape>", self.close)


    def close(self, event=None):  # Add "event" parameter to allow for "event" to be passed when the binded "esc" key is pressed (though the bind doesn't include an event).
        self.about_window.unbind("<Escape>")  # Unbind the "esc" key from the "close" function so that "esc" can be used for other purposes later.
        main_window.attributes("-disabled", False)  # Re-enable the main window so that it can be interacted.
        self.about_window.destroy()



class Scoreboard:
    # Constructor for the "Scoreboard" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Home" class, for example, to be accessed from within the "Scoreboard" class.
    def __init__(self, tools_instance, completion_instance, quiz_instance, homepage_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.completion = completion_instance   # Store a reference to the "Completion" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.
        self.home = homepage_instance           # Store a reference to the "Home" class instance.


    def setup_scoreboard(self):
        # Set width for column 0 (1 total) in the main window. Positive weight means the column will expand to fill the available space.
        main_window.columnconfigure(0, weight=1, minsize=850)

        # Set up the menu bar.
        scoreboard_menubar = Menu(main_window)  # Create a new menu bar.

        file_menu = Menu(scoreboard_menubar, tearoff=0)
        scoreboard_menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Print Selected", accelerator="Ctrl+P")
        file_menu.add_command(label="Print All", accelerator="Ctrl+Shift+P")
        file_menu.add_command(label="Delete Selected", accelerator="Del")
        file_menu.add_command(label="Delete All", accelerator="Shift+Del")

        settings_menu = Menu(scoreboard_menubar, tearoff=0)
        scoreboard_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(scoreboard_menubar, tearoff=0)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, value=True)
        timer_settings.add_radiobutton(label="Disabled", variable=timer, value=False)

        help_menu = Menu(scoreboard_menubar, tearoff=0)
        scoreboard_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=About)

        main_window.config(menu=scoreboard_menubar)
        
        # Set up a content frame to place the main scoreboard top elements inside.
        top_frame1 = CTk.CTkFrame(main_window, fg_color="transparent")
        top_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,5))
        top_frame1._set_appearance_mode("light")

        # Set width for columns 0-2 (3 total) in top frame 1. Total minimum column width is 710px.
        top_frame1.columnconfigure(0, weight=1, minsize=300)
        top_frame1.columnconfigure(1, weight=0, minsize=205)
        top_frame1.columnconfigure(2, weight=0, minsize=205)

        # Create the buttons.
        CTk.CTkButton(top_frame1, text="Delete", width=200).grid(column=1, row=0, sticky=EW, padx=(0,5), pady=(0,5))
        CTk.CTkButton(top_frame1, text="Home", command=lambda: self.tools.clear_widget(self.home.setup_homepage, True, None, None, None), width=200).grid(column=2, row=0, sticky=EW, padx=(5,0), pady=(0,5))
        CTk.CTkButton(top_frame1, text="View Answers", width=200).grid(column=1, row=1, sticky=EW, padx=(0,5), pady=(5,0))
        CTk.CTkButton(top_frame1, text="Retry Quiz", width=200).grid(column=2, row=1, sticky=EW, padx=(5,0), pady=(5,0))

        # Set up a content frame to place the scores inside.
        content_frame1 = CTk.CTkFrame(main_window)
        content_frame1.grid(column=0, row=1, sticky=EW, padx=20, pady=(5,20))
        content_frame1._set_appearance_mode("light")

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
        CTk.CTkLabel(content_frame1, font=("Segoe UI", 14, "bold"), text="Ref #").grid(column=0, row=0, sticky=EW, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=("Segoe UI", 14, "bold"), text="Username").grid(column=1, row=0, sticky=W, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=("Segoe UI", 14, "bold"), text="Difficulty").grid(column=2, row=0, sticky=EW, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=("Segoe UI", 14, "bold"), text="Questions").grid(column=3, row=0, sticky=EW, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=("Segoe UI", 14, "bold"), text="Time").grid(column=4, row=0, sticky=EW, padx=5, pady=5)
        CTk.CTkLabel(content_frame1, font=("Segoe UI", 14, "bold"), text="Score").grid(column=5, row=0, sticky=EW, padx=5, pady=5)
        
        # Add each item in the list into its own row
        for index, details in enumerate(users):
            list_row = index + 1
            CTk.CTkLabel(content_frame1, font=("Segoe UI", 13), text=details[0]).grid(column=0, row=list_row, sticky=EW, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=("Segoe UI", 13), text=details[1]).grid(column=1, row=list_row, sticky=W, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=("Segoe UI", 13), text=details[2]).grid(column=2, row=list_row, sticky=EW, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=("Segoe UI", 13), text=details[3]).grid(column=3, row=list_row, sticky=EW, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=("Segoe UI", 13), text=details[4]).grid(column=4, row=list_row, sticky=EW, padx=5, pady=5)
            CTk.CTkLabel(content_frame1, font=("Segoe UI", 13), text=details[5]).grid(column=5, row=list_row, sticky=EW, padx=5, pady=5)



class Completion:
    # Constructor for the "Completion" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Home" class, for example, to be accessed from within the "Completion" class.
    def __init__(self, tools_instance, scoreboard_instance, quiz_instance, homepage_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.scoreboard = scoreboard_instance   # Store a reference to the "Scoreboard" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.
        self.home = homepage_instance           # Store a reference to the "Home" class instance.


    def setup_completion(self):
        global username, difficulty, difficulty_num, questions, users
        
        existing_ref_numbers = [user[0] for user in users]  # Create a list of existing reference numbers from the "users" list.
        
        # Check if the maximum number of unique reference numbers has been reached.
        if len(existing_ref_numbers) >= 9000:  # Check if 9000 possible unique 4-digit ref numbers from 1000 to 9999 have been generated.
            messagebox.showwarning("Maximum Entries Reached", "No more unique reference numbers can be generated. Please delete old user scores to add new ones.")
            return  # Exit the procedure if no more reference numbers can be generated.

        while True:
            ref_number = random.randint(1000, 9999)  # Generate a random number from 1000 to 9999 and put this value into the "ref_number" variable.
            if ref_number not in existing_ref_numbers:  # Check that the generated reference number doesn't already exist.
                break
        
        self.final_score = f"{self.quiz.score}/{questions}"
        if timer.get() == True:
            self.time = self.quiz.total_time
        else:
            self.time = "Disabled"
        users.append([ref_number, username, difficulty, questions, self.time, self.final_score])  # Add the next user and their quiz details to the "users" list.
        
        # Set width for column 0 (1 total) in the main window. Setting the main window size before element creation ensures the window doesn't glitch between sizes.
        main_window.columnconfigure(0, weight=0, minsize=450)

        # Set up the menu bar.
        completion_menubar = Menu(main_window)  # Create a new menu bar.

        settings_menu = Menu(completion_menubar, tearoff=0)
        completion_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(completion_menubar, tearoff=0)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, command=lambda: self.tools.timer_config("Completion", "Enable"), value=True)
        timer_settings.add_radiobutton(label="Disabled", variable=timer, command=lambda: self.tools.timer_config("Completion", "Disable"), value=False)

        help_menu = Menu(completion_menubar, tearoff=0)
        completion_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=About)

        main_window.config(menu=completion_menubar)

        # Set up a content frame to place the main completion elements inside.
        completion_frame1 = CTk.CTkFrame(main_window)
        completion_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(10,5))
        completion_frame1._set_appearance_mode("light")

        # Set width for column 0 (1 total) in completion frame 1. Total minimum column width is 410px.
        completion_frame1.columnconfigure(0, weight=1, minsize=410)

        # Create the labels to be placed next to their relevant entry boxes.
        CTk.CTkLabel(completion_frame1, text="Quiz Complete!", font=("Segoe UI", 16, "bold")).grid(column=0, row=0, sticky=EW, padx=5, pady=(10,8))
        CTk.CTkLabel(completion_frame1, text=f"You scored a total of: {self.quiz.score}/{questions}", font=("Segoe UI", 14)).grid(column=0, row=1, sticky=EW, padx=5)
        CTk.CTkLabel(completion_frame1, text=f"Difficulty: {difficulty}", font=("Segoe UI", 14)).grid(column=0, row=2, sticky=EW, padx=5)
        self.total_time_lbl = CTk.CTkLabel(completion_frame1, text="", font=("Segoe UI", 14))  # Make an empty label for the timer until the state of the timer is determined (enabled/disabled).
        self.total_time_lbl.grid(column=0, row=3, sticky=EW, padx=5, pady=(0,10))
        if timer.get() == True:
            self.tools.timer_config("Completion", "Enable")
        if timer.get() == False:
            self.tools.timer_config("Completion", "Disable")

        # Create a frame to place the buttons inside.
        button_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        button_frame.grid(column=0, row=1, sticky=EW, padx=20, pady=(5,10))
        button_frame._set_appearance_mode("light")
        
        # Set width for columns 0-1 (2 total) in the answer frame. Total minimum column width is 410px.
        button_frame.columnconfigure(0, weight=1, minsize=205)
        button_frame.columnconfigure(1, weight=1, minsize=205)

        # Create the buttons.
        CTk.CTkButton(button_frame, text="View Answers", width=200).grid(column=0, row=0, sticky=EW, padx=(0,5), pady=(0,5))
        CTk.CTkButton(button_frame, text="Retry Quiz", width=200).grid(column=1, row=0, sticky=EW, padx=(5,0), pady=(0,5))
        CTk.CTkButton(button_frame, text="Scoreboard", command=lambda: self.quiz.reset_timer("Scoreboard", "Completion"), width=200).grid(column=0, row=1, sticky=EW, padx=(0,5), pady=(5,0))
        CTk.CTkButton(button_frame, text="Home", command=lambda: self.quiz.reset_timer("Home", "Completion"), width=200).grid(column=1, row=1, sticky=EW, padx=(5,0), pady=(5,0))



class Quiz:
    # Constructor for the "Quiz" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Home" class, for example, to be accessed from within the "Quiz" class.
    def __init__(self, tools_instance, scoreboard_instance, completion_instance, homepage_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
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
        self.completion.final_score = "0/0"     # Variable to store the final score, defaulting to "0/0".
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
        
        if command == "Home":
            self.reset_timer("Home", origin)


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
            if origin != None: self.tools.reset_details(origin)  # If the origin is not None (meaning an origin has been specified), reset the details. Origin is only specified for the completion page.
            self.question_no = 1
            self.score = 0
            if command == "Home":
                self.tools.clear_widget(self.home.setup_homepage, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the home page.
            elif command == "Scoreboard":
                self.tools.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the scoreboard page.


    def pause_quiz(self):
        self.stop_timer(None, None)
        self.pause_start_time = time.time()  # Record the real-world time for when the pause started.
        self.pause_btn.configure(command=self.unpause_quiz)
        
        # Create a pause overlay to visually block the quiz content until the quiz is unpaused.
        height = self.question_frame.winfo_height() + self.answer_frame.winfo_height() + 10  # Get the total height of both frames (question and answer frames), including the height of padding.
        self.pause_frame = CTk.CTkFrame(main_window)
        self.pause_frame.grid(column=0, row=2, rowspan=2, sticky=EW, padx=20, pady=(5,20))
        
        # Set width for column 0 (1 total) and row 0 (1 total) in the pause frame.
        self.pause_frame.columnconfigure(0, weight=0, minsize=410)
        self.pause_frame.rowconfigure(0, weight=0, minsize=height)

        CTk.CTkLabel(self.pause_frame, text="Quiz Paused", font=("Segoe UI", 20, "bold")).grid(column=0, row=0, columnspan=2, sticky=EW)
        

    def unpause_quiz(self):
        if self.pause_start_time != None:
            # Calculate how long the pause lasted and add it to the total paused duration.
            pause_duration = time.time() - self.pause_start_time
            self.total_paused_time += pause_duration
            self.pause_start_time = None  # Reset the pause start time tracker to be used again for the next pause.
        
        # Remove the pause overlay and restore the pause button to its original command, then start the timer again.
        self.pause_frame.destroy()
        self.pause_btn.configure(command=self.pause_quiz)
        self.start_timer()
        

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


    def update_timer(self):
        self.elapsed_time += 1
        self.timer_loop()


    def answer_management(self, answer):
        self.user_answers.append(answer)  # Append the user's answer to the list of all their answers.
        
        answer_index = len(self.user_answers) - 1  # Get the index of the most recent answer in the list, using "len()" to get the total number of items in the list.
        if self.user_answers[answer_index] == self.correct_answers[answer_index]:  # Check if the most recent answer matches the correct answer for the current question.
            self.score += 1
                
        if self.question_no < questions:
            self.question_no += 1
            self.question_no_lbl.configure(text=f"Question {self.question_no}/{questions}")  # Update the question number label.
        else:
            self.stop_timer(None, None)
            self.tools.clear_widget(self.completion.setup_completion, True, None, None, None)  # Clear all current widgets (passing "True" clears all widgets), then go to the completion page.


    # Procedure for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
    def setup_quiz(self):

        # Set width for column 0 (1 total) in the main window. Setting the main window size before element creation ensures the window doesn't glitch between sizes.
        main_window.columnconfigure(0, weight=0, minsize=450)

        # Set up the menu bar.
        quiz_menubar = Menu(main_window)  # Create a new menu bar.
        
        quiz_menu = Menu(quiz_menubar, tearoff=0)
        quiz_menubar.add_cascade(label="Quiz", menu=quiz_menu)
        quiz_menu.add_command(label="Restart Quiz", accelerator="Ctrl+R")
        quiz_menu.add_command(label="New Quiz", accelerator="Ctrl+N")
        quiz_menu.add_command(label="Exit Quiz", accelerator="Esc", command=lambda: self.stop_timer("Home", None))

        settings_menu = Menu(quiz_menubar, tearoff=0)
        quiz_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(quiz_menubar, tearoff=0)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, command=lambda: self.tools.timer_config("Quiz", "Enable"), value=True)        # Use lambda so that the method is called only when the radiobutton is clicked, rather than when it's defined.
        timer_settings.add_radiobutton(label="Disabled", variable=timer, command=lambda: self.tools.timer_config("Quiz", "Disable"), value=False)     # Use lambda so that the method is called only when the radiobutton is clicked, rather than when it's defined.

        help_menu = Menu(quiz_menubar, tearoff=0)
        quiz_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=About)

        main_window.config(menu=quiz_menubar)

        # Set up a content frame to place the top quiz elements inside.
        quiz_dtls_frame1 = CTk.CTkFrame(main_window)
        quiz_dtls_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,5))
        quiz_dtls_frame1._set_appearance_mode("light")
        
        # Set width for columns 0-2 (3 total) in quiz details frame 1. Total minimum column width is 410px.
        quiz_dtls_frame1.columnconfigure(0, weight=0, minsize=190)
        quiz_dtls_frame1.columnconfigure(1, weight=0, minsize=30)
        quiz_dtls_frame1.columnconfigure(2, weight=0, minsize=190)

        # Create the labels and pause button to be placed at the top of the quiz page.
        self.question_no_lbl = CTk.CTkLabel(quiz_dtls_frame1, text=f"Question: {self.question_no}/{questions}", font=("Segoe UI", 14, "bold"))
        self.question_no_lbl.grid(column=0, row=0, pady=10, sticky=NSEW)
        self.pause_btn = CTk.CTkButton(quiz_dtls_frame1, text="P", font=("Segoe UI", 14, "bold"), width=30, command=self.pause_quiz)
        self.pause_btn.grid(column=1, row=0, pady=10)
        self.timer_lbl = CTk.CTkLabel(quiz_dtls_frame1, text="", font=("Segoe UI", 14, "bold"))  # Make an empty label for the timer until the state of the timer is determined (enabled/disabled).
        self.timer_lbl.grid(column=2, row=0, pady=10, sticky=NSEW)
        if timer.get() == True:
            self.tools.timer_config("Quiz", "Enable")
        elif timer.get() == False:
            self.tools.timer_config("Quiz", "Disable")

        # Create a frame for the question label or question image.
        self.question_frame = CTk.CTkFrame(main_window)
        self.question_frame.grid(column=0, row=2, sticky=EW, padx=20, pady=5)
        
        # Set width for column 0 (1 total) and row 0 (1 total) in quiz details frame 1.
        self.question_frame.columnconfigure(0, weight=0, minsize=410)
        self.question_frame.rowconfigure(0, weight=0, minsize=205)
        
        # Create a label for the question text.
        question_lbl = CTk.CTkLabel(self.question_frame, text="It's looking a little empty...", font=("Segoe UI", 20, "bold"))
        question_lbl.grid(column=0, row=0)

        # Create a frame for the answer buttons
        self.answer_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        self.answer_frame.grid(column=0, row=3, sticky=EW, padx=20, pady=(5,20))
        
        # Set width for columns 0-1 (2 total) in the answer frame. Total minimum column width is 410px.
        self.answer_frame.columnconfigure(0, weight=0, minsize=205)
        self.answer_frame.columnconfigure(1, weight=0, minsize=205)
        
        # Create the answer values.
        answer_1 = "Yes"
        answer_2 = "No"
        answer_3 = "No"
        answer_4 = "No"
            
        self.correct_answers = ["A"] * questions

        # Create the answer buttons.
        btn_1 = CTk.CTkButton(self.answer_frame, text=f" A.    {answer_1}", font=("Segoe UI", 16, "bold"), command=lambda: self.answer_management("A"), anchor=W, width=200, height=40)
        btn_1.grid(column=0, row=0, padx=(0, 5), pady=(0,5))
        btn_2 = CTk.CTkButton(self.answer_frame, text=f" B.    {answer_2}", font=("Segoe UI", 16, "bold"), command=lambda: self.answer_management("B"), anchor=W, width=200, height=40)
        btn_2.grid(column=1, row=0, padx=(5, 0), pady=(0,5))
        btn_3 = CTk.CTkButton(self.answer_frame, text=f" C.    {answer_3}", font=("Segoe UI", 16, "bold"), command=lambda: self.answer_management("C"), anchor=W, width=200, height=40)
        btn_3.grid(column=0, row=1, padx=(0, 5), pady=(5,0))
        btn_4 = CTk.CTkButton(self.answer_frame, text=f" D.    {answer_4}", font=("Segoe UI", 16, "bold"), command=lambda: self.answer_management("D"), anchor=W, width=200, height=40)
        btn_4.grid(column=1, row=1, padx=(5, 0), pady=(5,0))

        self.start_timer()



class Home:
    # Constructor for the "Home" class, which takes an instance of the class names as a parameter and stores it in their unique attributes.
    # This allows attributes and methods defined in the "Quiz" class, for example, to be accessed from within the "Home" class.
    def __init__(self, tools_instance, scoreboard_instance, completion_instance, quiz_instance):
        self.tools = tools_instance             # Store a reference to the "Tools" class instance.
        self.scoreboard = scoreboard_instance   # Store a reference to the "Scoreboard" class instance.
        self.completion = completion_instance   # Store a reference to the "Completion" class instance.
        self.quiz = quiz_instance               # Store a reference to the "Quiz" class instance.


    # Procedure for updating the difficulty and question number labels based on the interpreted slider values.
    def slider_value_update(self, slider_id, value):
        global difficulty
        if slider_id == "S1":
            if value == 0:
                difficulty = "Easy"
            elif value == 1:
                difficulty = "Medium"
            else:
                difficulty = "Hard"
            self.difficulty_lbl.configure(text=difficulty)
        if slider_id == "S2":
            self.question_amnt_lbl.configure(text=f"{int(value)} Questions")


    # Procedure for setting up the UI elements consisting of images, labels, entry boxes, sliders (scales), and buttons.
    def setup_homepage(self):
        # Set width for column 0 (1 total) in the main window. Setting the main window size before element creation ensures the window doesn't glitch between sizes.
        main_window.columnconfigure(0, weight=0, minsize=450)

        # Set up the menu bar.
        home_menubar = Menu(main_window)

        settings_menu = Menu(home_menubar, tearoff=0)
        home_menubar.add_cascade(label="Settings", menu=settings_menu)
        timer_settings = Menu(home_menubar, tearoff=0)
        settings_menu.add_cascade(menu=timer_settings, label="Timer")
        timer_settings.add_radiobutton(label="Enabled", variable=timer, value=True)
        timer_settings.add_radiobutton(label="Disabled", variable=timer, value=False)

        help_menu = Menu(home_menubar, tearoff=0)
        home_menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About", command=About)

        main_window.config(menu=home_menubar)

        # Set up a content frame to place the main home elements inside.
        home_frame1 = CTk.CTkFrame(main_window)
        home_frame1.grid(column=0, row=0, sticky=EW, padx=20, pady=(20,5))
        home_frame1._set_appearance_mode("light")

        # Set width for columns 0-2 (3 total) in home frame 1. Total minimum column width is 410px.
        home_frame1.columnconfigure(0, weight=0, minsize=100)
        home_frame1.columnconfigure(1, weight=0, minsize=210)
        home_frame1.columnconfigure(2, weight=0, minsize=100)

        # Create the labels to be placed next to their relevant entry boxes.
        CTk.CTkLabel(home_frame1, text="Username").grid(column=0, row=0, sticky=E, padx=(0,5), pady=(10,0))
        CTk.CTkLabel(home_frame1, text="Difficulty").grid(column=0, row=1, sticky=E, padx=(0,5), pady=10)
        CTk.CTkLabel(home_frame1, text="Questions").grid(column=0, row=2, sticky=E, padx=(0,5), pady=(0,10))

        self.difficulty_lbl = CTk.CTkLabel(home_frame1, text="")      # Create an empty placeholder label to display the difficulty level.
        self.difficulty_lbl.grid(column=2, row=1, sticky=W, padx=(5,0), pady=10)
        self.question_amnt_lbl = CTk.CTkLabel(home_frame1, text="")   # Create an empty placeholder label to display the number of questions.
        self.question_amnt_lbl.grid(column=2, row=2, sticky=W, padx=(5,0), pady=(0,10))

        # Setup entry box and sliders (scales).
        self.username_entry = CTk.CTkEntry(home_frame1)
        self.username_entry.grid(column=1, row=0, padx=5, pady=(10,0), sticky=EW)
        self.difficulty_slider = CTk.CTkSlider(home_frame1, from_=0, to=2, number_of_steps=2, command=lambda value: self.slider_value_update("S1", value), orientation=HORIZONTAL)
        self.difficulty_slider.grid(column=1, row=1, padx=5, pady=10, sticky=EW)
        self.questions_slider = CTk.CTkSlider(home_frame1, from_=5, to=35, number_of_steps=30, command=lambda value: self.slider_value_update("S2", value), orientation=HORIZONTAL)
        self.questions_slider.grid(column=1, row=2, padx=5, pady=(0,10), sticky=EW)
        
        # Update the value of the entry box and the sliders (scales) with the previously recorded values (used for going from scoreboard back to homepage).
        if username != None:
            self.username_entry.insert(0, username)
        if difficulty_num != None:
            self.difficulty_slider.set(difficulty_num)
        if questions != None:
            self.questions_slider.set(questions)

        # Update the labels next to the sliders with their relevant values.
        self.slider_value_update("S1", self.difficulty_slider.get())
        self.slider_value_update("S2", self.questions_slider.get())

        # Create a frame to place the buttons inside.
        button_frame = CTk.CTkFrame(main_window, fg_color="transparent")
        button_frame.grid(column=0, row=1, sticky=EW, padx=20, pady=(5,20))
        button_frame._set_appearance_mode("light")
        
        # Set width for columns 0-1 (2 total) in the button frame. Total minimum column width is 410px.
        button_frame.columnconfigure(0, weight=0, minsize=205)
        button_frame.columnconfigure(1, weight=0, minsize=205)

        # Create the buttons.
        CTk.CTkButton(button_frame, text="Scoreboard", command=lambda: self.tools.clear_widget(self.scoreboard.setup_scoreboard, True, None, None, self.tools.save_details("Home")), width=200).grid(column=0, row=1, sticky=EW, padx=(0,5))
        CTk.CTkButton(button_frame, text="Start", command=lambda: self.tools.clear_widget(self.quiz.setup_quiz, True, None, None, self.tools.save_details("Home")), width=200).grid(column=1, row=1, sticky=EW, padx=(5,0))



# Main function for starting the program.
def main(): 
    global main_window, users, timer_showing, timer, username, difficulty_num, questions
    
    main_window = Tk()                          # Initialise the main window. For scaling reasons, use a Tk window with CTk elements.
    main_window.title("QWhizz Math")            # Set the title of the window.
    main_window.resizable(False, False)         # Set the resizable property for height and width to False.
    CTk.set_appearance_mode("light")

    # Initialise global lists and variables.
    users = []                      # Create empty list for user details and their quiz results to be stored inside.
    timer_showing = None            # Initialise a flag to track whether the timer is being displayed or not.
    timer = BooleanVar(value=True)          # Create a "timer" BooleanVar global reference to control the timer checkbutton state, with the default value being True, putting the checkbutton in an on state.
    username = None                         # Initialise the username attribute as None.
    difficulty_num = None                   # Initialise the difficulty_num attribute as None.
    questions = None                        # Initialise the questions attribute as None.

    # Set up the class instances.
    # The classes (Tools, Scoreboard, Completion, Quiz, and Home) reference each other, so some instances are first given placeholder values (None) and are linked once the other necessary instances are created.
    # Ultimately, the class instances are linked together to allow access to each other's attributes and methods.
    tools = Tools(None, None, None, None)                                   # Create a "tools" instance of the "Tools" class so that the "Tools" class attributes and methods can be accessed within other classes once created. Temporarily pass "None" for all other class instances until they are created.
    scoreboard_page = Scoreboard(tools, None, None, None)                   # Create a "scoreboard_page" instance of the "Scoreboard" class and pass in the "tools" instance. Temporarily pass "None" for the "completion_page", "quiz_page", and "home_page" instances until they are created.
    completion_page = Completion(tools, scoreboard_page, None, None)        # Create a "completion_page" instance of the "Completion" class and pass in the "tools" and "scoreboard_page" instances. Temporarily pass "None" for the "quiz_page" and "home_page" instances until they are created.
    quiz_page = Quiz(tools, scoreboard_page, completion_page, None)         # Create a "quiz_page" instance of the "Quiz" class and pass in the "tools", "scoreboard_page", and "completion_page" instances. Temporarily pass "None" for the "home_page" instance until it is created.
    home_page = Home(tools, scoreboard_page, completion_page, quiz_page)    # Create a "home_page" instance of the "Home" class and pass in the "tools", "scoreboard_page", "completion_page", and "quiz_page" instances.
    
    # Link the remaining class instances to each other now that they are created.
    tools.scoreboard = scoreboard_page              # Link the "scoreboard_page" instance to the "tools" instance to allow access to "Scoreboard" class attributes and methods from within the "Tools" class.
    tools.completion = completion_page              # Link the "completion_page" instance to the "tools" instance to allow access to "Completion" class attributes and methods from within the "Tools" class.
    tools.quiz = quiz_page                          # Link the "quiz_page" instance to the "tools" instance to allow access to "Quiz" class attributes and methods from within the "Tools" class.
    tools.home = home_page                          # Link the "home_page" instance to the "tools" instance to allow access to "Home" class attributes and methods from within the "Tools" class.
    scoreboard_page.completion = completion_page    # Link the "completion_page" instance to the "scoreboard_page" instance to allow access to "Completion" class attributes and methods from within the "Scoreboard" class.
    scoreboard_page.quiz = quiz_page                # Link the "quiz_page" instance to the "scoreboard_page" instance to allow access to "Quiz" class attributes and methods from within the "Scoreboard" class.
    scoreboard_page.home = home_page                # Link the "home_page" instance to the "scoreboard_page" instance to allow access to "Home" class attributes and methods from within the "Scoreboard" class.
    completion_page.quiz = quiz_page                # Link the "quiz_page" instance to the "completion_page" instance to allow access to "Quiz" class attributes and methods from within the "Completion" class.
    completion_page.home = home_page                # Link the "home_page" instance to the "completion_page" instance to allow access to "Home" class attributes and methods from within the "Completion" class.
    quiz_page.home = home_page                      # Link the "home_page" instance to the "quiz_page" instance to allow access to "Home" class attributes and methods from within the "Quiz" class.

    # Call the "setup_homepage" method from the "home_page" class instance to set up the home page UI elements.
    home_page.setup_homepage()
    
    # Start the CTkinter event loop so that the GUI window stays open.
    main_window.mainloop()


# Run the main function.
main()