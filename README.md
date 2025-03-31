# university-virtual-assistant
gpt powered virtual assistant helping students managing calendar, deadlines and events

Currently the application is working on VSCode 2019 2.9.2, please use the specified version to avoidfuture issues.

The project uses flask as web service and sqlite3 for database

First run pip install -r requirements.txt to get all the dependencies in specified version

The project first needs an openai api key which can be retrieved from https://openai.com/api/, the key can be input in config.json in settings folder

Then run main.py in VSCode

Project currently has 2 pages, the authentication page and chat page for communicating with assistant

For authentication, uses functions stored in the back-end folder as "database.py" which executes self explanatory functions

For assistant, uses functions stored in the back-end folder as "assistant_funct.py", for now it handles more of the events in the database

sort_events was used for displaying in the web page in order of the time and date, and get_specific_event was used to retrieve the actual index in the database other than visually displayed in the webpage
extract_details was used to collect informations from provided inputs, currently the application does not support dynamic input, however supports in a pattern like:
    "can you help me create an event on april 4th at 2pm that i have my brother's birthday",
    "please add into the calendar that i have a company meeting at 16:00 on april 20th",
    "change the event at number 4 to 6pm at grandma's house",
    "can you change the 2nd event name to lucy's party and set it to 7pm",
    "can you delete the first event",
    "please delete number 5 event",
    "add an event on april 4th that i have to be at my mom's house at 7pm"

The assistant uses model "gpt-4o-mini"
In case of thread cannot be appended, replace thread_id in config.json to "firstrun"

- future updates will be about accepting dynamic inputs, changes events name and work on other tables of the database

Summary of the libraries and their purposes:

spaCy (3.8.4) – NLP library for processing and analyzing text.

en-core-web-sm (3.8.0) – Small English language model for spaCy.

Flask (2.1.3) – Lightweight web framework for building APIs and web applications.

Flask[async] (3.8.1) – Asynchronous version of Flask for handling async tasks.

Dateparser (1.2.1) – Parses natural language dates (e.g., "tomorrow" or "next Friday").

OpenAI (1.54.3) – API client for integrating OpenAI models (e.g., GPT).

Flask-CORS (5.0.1) – Handles Cross-Origin Resource Sharing (CORS) in Flask apps.


1-![Capture d'écran 2025-03-31 161749](https://github.com/user-attachments/assets/c2fdc3f5-2e10-4684-bc90-451c69911913)
/*signup page you will have to register first before login*/
2-![WhatsApp Image 2025-03-31 at 13 23 32_56b824b6](https://github.com/user-attachments/assets/7de049f2-ae2e-4951-9eed-a9a51a21ac06)
/*you can add event , date , and time , location and modify as you can see but the event name won't be changed because the event name function is not very dynamic so it can only recognize specific name from the code */
3- ![WhatsApp Image 2025-03-31 at 13 28 32_c3fb1e61](https://github.com/user-attachments/assets/2fec6662-f7c3-46c3-b62d-635c9e6b39cf)
/*you can delete event by starting from the database */ 

4- event function name the system recognize : ![WhatsApp Image 2025-03-31 at 13 25 39_f7cd6bd9](https://github.com/user-attachments/assets/e8653961-88b5-46f7-b918-d8ff3b570824)




