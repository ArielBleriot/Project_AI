import sqlite3
from flask import jsonify
import sqlite3
import re
import spacy
import dateparser
import uuid
from datetime import datetime

dtb = r"D:\ENV\Ariels\data\university_assistant.db"


def get_all_users():
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM users")
    for results in result:
        print(results)
    conn.close()
    return result

def get_user(username):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    result = cursor.execute("SELECT username FROM users WHERE username = ?")

def insert_user(data):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    result = cursor.execute("INSERT INTO users (username, password, email, phone_number) VALUES (%s, %s, %s, %s) RETURNING id;", (data['username'], data['password'], data['email'], data['phone_number']))
    print("Successfully inserted")
    conn.commit()
    conn.close()
    return result

def delete(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    
    # Corrected DELETE syntax
    cursor.execute('DELETE FROM users WHERE name = ?', (name,))
    
    conn.commit()
    conn.close()

def check_user(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM users WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        print(result[0])
    conn.commit()
    conn.close()
    return result[0] if result else None

def add_event(user_id, event_name, event_date, event_time, location):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO events (user_id, event_name, event_date, event_time, location) VALUES (?, ?, ?, ?, ?)',
                   (user_id, event_name, event_date, event_time, location))
    conn.commit()
    conn.close()
    return True

def get_allevents(user_id):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM events WHERE user_id = ?', (user_id,))
    for results in result:
        print(results)
    conn.commit()
    conn.close()
    return 

def get_events(user_id):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT id_event, event_name, event_date, event_time, location FROM events WHERE user_id = ?', (user_id,))
    events = cursor.fetchall()
    conn.close()
    
    if not events:
        return "No events found.", []

    event_list = "\n".join([f"{idx+1}. {name} - {date} at {time}, Location: {loc}" for idx, (eid, name, date, time, loc) in enumerate(events)])
    return event_list, events

def get_specific_event(user_id, chosen_index):

    get_event = sorted_events(user_id)
    
    # Retrieve the event from the sorted list
    event = get_event[chosen_index-1]
    
    event_name = event['event_name']
    event_date = event['event_date']
    event_time = event['event_time']
    location = event['location']
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT id_event, event_name, event_date, event_time, location FROM events '
                    + 'WHERE user_id = ? AND event_name = ? AND event_date = ? AND event_time = ? AND location = ?', 
                   (user_id, event_name, event_date, event_time, location))
    index = cursor.fetchall()
    conn.close()
    return index[0][0]

def delete_events(user_id, event_id):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()

    # Delete the event
    cursor.execute(
        '''DELETE FROM events WHERE user_id = ? AND id_event = ?''',
        (user_id, event_id)
    )
    conn.commit()

    # Reorder the id_event column
    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]

    if count > 0:  # Only reset IDs if there are remaining events
        cursor.execute("CREATE TABLE temp_events AS SELECT * FROM events ORDER BY event_date ASC, event_time ASC")
        cursor.execute("DELETE FROM events")
        cursor.execute("""
            INSERT INTO events (id_event, user_id, event_name, event_date, event_time, location)
            SELECT ROW_NUMBER() OVER () AS id_event, user_id, event_name, event_date, event_time, location FROM temp_events
        """)
        cursor.execute("DROP TABLE temp_events")

    conn.commit()
    conn.close()
    
    return True

def create_sorted_view():
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()

    cursor.execute("DROP VIEW IF EXISTS sorted_events")  # Optional: Refresh the view
    cursor.execute("""
        CREATE VIEW sorted_events AS
        SELECT * FROM events
        ORDER BY event_date ASC, event_time ASC
    """)
    
    conn.commit()
    conn.close()

def sorted_events(user_id):
    event_list, events = get_events(user_id)

    if event_list == "No events found.":
        return []  # Return an empty array if no events are found

    # Convert events data into a list of dictionaries for JSON response
    event_dict_list = [
        {
            "event_name": event[1],  # event_name
            "event_date": event[2],  # event_date
            "event_time": event[3],  # event_time
            "location": event[4]    # location
        }
        for event in events
    ]
    event_dict_list.sort(key=lambda e: datetime.strptime(f"{e['event_date']} {e['event_time']}", "%d-%m-%Y %H:%M"))

    return event_dict_list  # Return events as a JSON array

def extract_event_details(user_id, message):
    """
    Extracts event details (event_id, name, date, time, location) from natural language input and generates a unique event ID.
    """
    message = message.lower()

    # Initialize variables
    event_id, event_name, event_date, event_time, location = None, "Unnamed Event", None, "00:00", "Unknown"
    
    # Extract event ID
    index_match = re.search(r'(the\s)?(\d+)(st|nd|rd|th)?\s*(one|event|item)?\s*(at\snumber\s?\d+)?', message)
    if index_match:
        event_id = index_match.group(2)
        # print(event_id)
        if event_id:
            event_id = int(event_id)
            # event_id = get_specific_event(user_id, event_id)
        else: event_id = None

    # Extract event date using dateparser
    event_date = dateparser.parse(message, settings={'PREFER_DATES_FROM': 'future'})
    if event_date:
        event_date = event_date.strftime('%d-%m-%Y')  # Format date as d-m-Y
    else:
        event_date = None

    # Extract time (e.g., "6pm", "14:30", "at 7:45 AM")
    time_match = re.search(r'(\d{1,2}(:\d{2})?\s?(am|pm)?)', message)
    if time_match:
        extracted_time = time_match.group(1)
        parsed_time = dateparser.parse(extracted_time)
        if parsed_time:
            event_time = parsed_time.strftime('%H:%M')  # 24-hour time format
        else:
            event_time = "00:00"
    
    # Extract location (assume "at [location]" or "in [location]")
    location_match = re.search(r'(at|in)\s([a-zA-Z0-9\s\'-]+)', message)
    if location_match:
        location = location_match.group(2).strip()

    # Extract event name
    clean_message = re.sub(r'(on\s.*|at\s.*|add it.*|schedule.*|change.*|delete.*)', '', message).strip()
    event_name = clean_message.capitalize() if clean_message else "Unnamed Event"

    return event_id, event_name, event_date, event_time, location

def modify_event(user_id, message):
    event_list, events = get_events(user_id)
    for event in events:
        print(event)
    event_id, new_event_name, new_event_date, new_event_time, new_location = extract_event_details(user_id, message)
    
    old_event_id, old_event_name, old_event_date, old_event_time, old_location = events[event_id][1:]

    updated_event_name = new_event_name if new_event_name else old_event_name
    updated_event_date = new_event_date if new_event_date else old_event_date
    updated_event_time = new_event_time if new_event_time else old_event_time
    updated_location = new_location if new_location else old_location

    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE events 
           SET event_name = ?, event_date = ?, event_time = ?, location = ?
           WHERE id_event = ? AND user_id = ?''',
        (updated_event_name, updated_event_date, updated_event_time, updated_location, event_id, user_id)
    )
    conn.commit()
    conn.close()

    return f"Event updated: '{updated_event_name}' on {updated_event_date} at {updated_event_time} in {updated_location}."

# Call this function once to create the view

# add_event(1, "test1", "09-04-2025", "12:00", "test1")
# add_event(1, "test2", "09-04-2025", "11:00", "test1")
# add_event(1, "test3", "09-04-2025", "10:00", "test1")
# add_event(1, "test4", "09-04-2025", "5:00", "test1")
# add_event(1, "test5", "09-04-2025", "3:00", "test1")
# add_event(1, "test6", "09-04-2025", "18:00", "test1")

# print("\nBefore\n")
# sorted = sorted_events(1)
# for sort in sorted:
#     print(sort)

# get_allevents(1)
# print("\nAfter\n")
# message = "i want to update event at index 4 with the name to be test666, change also for the time to be at 7pm"
# message = "change the 4th event to be at 5pm in joe's house"
# message = "can you change the event number 4 to 10:00 at grandma's garden"
message1 = "can you help me create an event on april 4th at 2pm that i have my brother's birthday"
message2 = "please add into the calendar that i have a company meeting at 16:00 on april 20th"
message3 = "change the event at number 4 to 6pm at grandma's house"
message4 = "can you change the 2nd event name to lucy's party and set it to 7pm"
message5 = "can you delete the first event"
message6 = "please delete number 5 event"
message7 = "add an event on april 4th that i have to be at my mom's house at 7pm"
event_id, event_name, event_date, event_time, location = extract_event_details(1, message1)
print("id: ", event_id, " name ", event_name, " date ", event_date, " time ", event_time, " location ", location)
event_id, event_name, event_date, event_time, location = extract_event_details(1, message2)
print("id: ", event_id, " name ", event_name, " date ", event_date, " time ", event_time, " location ", location)
event_id, event_name, event_date, event_time, location = extract_event_details(1, message3)
print("id: ", event_id, " name ", event_name, " date ", event_date, " time ", event_time, " location ", location)
event_id, event_name, event_date, event_time, location = extract_event_details(1, message4)
print("id: ", event_id, " name ", event_name, " date ", event_date, " time ", event_time, " location ", location)
event_id, event_name, event_date, event_time, location = extract_event_details(1, message5)
print("id: ", event_id, " name ", event_name, " date ", event_date, " time ", event_time, " location ", location)
event_id, event_name, event_date, event_time, location = extract_event_details(1, message6)
print("id: ", event_id, " name ", event_name, " date ", event_date, " time ", event_time, " location ", location)
event_id, event_name, event_date, event_time, location = extract_event_details(1, message7)
print("id: ", event_id, " name ", event_name, " date ", event_date, " time ", event_time, " location ", location)
# print("event_id: ", event_id)
# print("event name: ", event_name)
# print("event date: ", event_date)
# print("event time: ", event_time)
# print("event location: ", location)
# modify_event(1, message)


# delete_events(1, event_id)
# sorted = sorted_events(1)
# for sort in sorted:
#     print(sort)

# get_allevents(1)
# delete_events(1, 1)
# delete_events(1, 2)
# delete_events(1, 3)
# delete_events(1, 4)
# delete_events(1, 5)
# delete_events(1, 6)
# get_allevents(1)
# delete_events(1, 1)
# delete("test")
# check_user('test')
