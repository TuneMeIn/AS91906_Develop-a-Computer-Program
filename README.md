# AS91906 Develop a Computer Program
This project is a GUI application for Flow Computing to help students with their mathematics.

# [Versions](https://github.com/TuneMeIn/AS91906_Develop-a-Computer-Program/commits/main/)
### Version 1
* __Ver 1.0.0 - 05/05/2025__ - Initial preview release of program.  
* __Ver 1.1.0 - 08/05/2025 - Minor UI Update:__ Overhauled the UI elements of the program.  
* __Ver 1.2.0 - 15/05/2025 - Minor Functionality Update:__ Added a large amount of functionality to the program, including classes for Tools, About, Completion, Quiz, and Home.  
* __Ver 1.3.0 - 19/05/2025 - Minor Functionality Update:__ Added class for Scoreboard, and updates/improvements to other program functionalities.  
* __Ver 1.4.0 - 19/05/2025 - Minor Functionality Update:__ Implemented a pause timer feature for the quiz, improved the timer accuracy when paused and unpaused, and implemented other patches.
* __Ver 1.4.1 - 22/06/2025 - Quick Patch Update:__ Adjusted the "About" window details to fix inaccuracies.

### Version 2
* __Ver 2.0.0 - 17/06/2025__ - Initial release of version 2 for the QWhizz Math program. This release contains a large improvement to the functionality and UI design, including JSON storage for saving scores.  
* __Ver 2.1.0 - 18/06/2025 - Minor Functionality Update:__ In this version, another JSON storage file has been introduced in order to save program settings, which currently just contains the preference for the timer being enabled or disabled. The file management has also been made more robust and efficient to adapt to future updates.
* __Ver 2.2.0 - 19/06/2025 - Minor Functionality & UI Update:__ Added a dynamic image for the pause button to improve user experience. Also tidied up the timer loop method and added a check to make sure the program only runs if the script is being run directly as the main program (not imported as a module).
* __Ver 2.3.0 - 19/06/2025 - Minor Functionality Update:__ This version includes the ability to send the printed PDF file to a printer, with operating system detection to allow support for printing on Windows, Linux, and macOS operating systems.
* __Ver 2.4.0 - 22/06/2025 - Minor Functionality Update:__ In this version, a treeview widget has been introduced to select individual scores on the scoreboard to manage them (i.e print, delete, etc.). The file management has also been made significantly tidier on the backend and more robust in terms of the program's ability to handle file errors. Optimisations have also been made to prevent window flickering when starting the program.
* __Ver 2.5.0 - 22/06/2025 - Minor Functionality Update:__ In this version, the program now has the capability to store history logs of deleted users, so that a deletion of a user score on the treeview scoreboard widget can be undone and/or redone. The number of deletion history states saved can be configured to the user's preference from "Disabled" to 50 saves.
* __Ver 2.6.0 - 23/06/2025 - Minor Functionality Update:__ This version includes minor changes, such as changing certain variables to constants, updating two procedures to work as functions to improve program structure, and making the statement within the message box clearer for confirming that a PDF file has been generated.
* __Ver 2.7.0 - 24/06/2025 - Minor Functionality Update:__ This version includes more minor changes, alongside a new way to save a scoreboard PDF file, which provides the user with an OS-default system of saving files to their preferred directory through apps such as Explorer on Windows, rather than the program simply saving the file to the program's root directory.

### Version 3
* __Ver 3.0.0 - 28/06/2025__ - Initial release of version 3 for the QWhizz Math program. This release contains the first preview of question generation, with the easy difficulty question generation functionality being half complete. It currently contains one step algebra equations, and is yet to include area of triangle questions.