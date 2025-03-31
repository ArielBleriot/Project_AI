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
