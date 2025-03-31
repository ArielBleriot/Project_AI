import sqlite3
import re
import spacy
from datetime import datetime

from back_end.database import dtb

nlp = spacy.load("en_core_web_sm")

def add_event(user_id, message):
    event_id, event_name, event_date, event_time, location = extract_details(user_id, message)
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO events (user_id, event_name, event_date, event_time, location) VALUES (?, ?, ?, ?, ?)',
                   (user_id, event_name, event_date, event_time, location))
    conn.commit()
    conn.close()
    return True

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

def modify_event(user_id, message):
    event_list, events = get_events(user_id)
    old_event = sorted_events(user_id)
    event_id, new_event_name, new_event_date, new_event_time, new_location = extract_details(user_id, message)
    print(events)
    print(event_id)
    old_event_id, old_event_name, old_event_date, old_event_time, old_location = events[event_id]

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

def delete_event(user_id, message):
    event_id, event_name, event_date, event_time, location = extract_details(user_id, message)
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
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

# def extract_event_details(user_id, message):
#     """
#     Extracts event details (event_id, name, date, time, location) from natural language input and generates a unique event ID.
#     """
#     message = message.lower()

#     # Initialize variables
#     event_id, event_name, event_date, event_time, location = None, "Unnamed Event", None, "00:00", "Unknown"
    
#     # Extract event ID
#     index_match = re.search(r'(the\s)?(\d+)(st|nd|rd|th)?\s*(one|event|item)?\s*(at\snumber\s?\d+)?', message)
#     if index_match:
#         event_id = index_match.group(2)
#         if event_id:
#             event_id = int(event_id)
#             event_id = get_specific_event(user_id, event_id)
#         else: event_id = None

#     # Extract event date using dateparser
#     event_date = dateparser.parse(message, settings={'PREFER_DATES_FROM': 'future'})
#     if event_date:
#         event_date = event_date.strftime('%d-%m-%Y')  # Format date as d-m-Y
#     else:
#         event_date = None

#     # Extract time (e.g., "6pm", "14:30", "at 7:45 AM")
#     time_match = re.search(r'(\d{1,2}(:\d{2})?\s?(am|pm)?)', message)
#     if time_match:
#         extracted_time = time_match.group(1)
#         parsed_time = dateparser.parse(extracted_time)
#         if parsed_time:
#             event_time = parsed_time.strftime('%H:%M')  # 24-hour time format
#         else:
#             event_time = "00:00"
    
#     # Extract location (assume "at [location]" or "in [location]")
#     location_match = re.search(r'(at|in)\s([a-zA-Z0-9\s\'-]+)', message)
#     if location_match:
#         location = location_match.group(2).strip()

#     # Extract event name
#     clean_message = re.sub(r'(on\s.|at\s.|add it.|schedule.|change.|delete.)', '', message).strip()
#     event_name = clean_message.capitalize() if clean_message else "Unnamed Event"

#     return event_id, event_name, event_date, event_time, location

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

def get_specific_event(user_id, chosen_index):

    get_event = sorted_events(user_id)
    
    # Retrieve the event from the sorted list
    event = get_event[chosen_index-1]
    print(event)
    
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

ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10
}

def extract_event_index(msg):
    event_indices = None
    match = re.search(r'\b(?:number|#)?\s*(\d+)(?:\s*(?:th|st|nd|rd)?\s*event)?\b', msg, re.IGNORECASE)
    word_match = re.search(r'\b(' + '|'.join(ORDINALS.keys()) + r')\b', msg, re.IGNORECASE)

    if word_match:
        event_indices = ORDINALS[word_match.group(1).lower()]
    elif match:
        num = int(match.group(1))
        if not re.search(rf'\b{num}:\d{{2}}\b', msg):  
            event_indices = num
    return int(event_indices) if event_indices else None

def extract_event_names(message):
    event_name = None
    keywords = ["birthday", "meeting", "party", "house"]
    
    if any(keyword in message.lower() for keyword in keywords):
        if "brother's birthday" in message.lower():
            event_name = "brother's birthday"
        elif "company meeting" in message.lower():
            event_name = "company meeting"
        elif "lucy's party" in message.lower():
            event_name = "lucy's party"
        elif "grandma's house" in message.lower():
            event_name = "grandma's house"
        elif "mom's house" in message.lower():
            event_name = "mom's house"
    
    return event_name if event_name else None

def extract_dates(message):
    match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?', message, re.IGNORECASE)
    date = None
    if match:
        month_str, day_str = match.groups()
        try:
            date_obj = datetime.strptime(f"{day_str} {month_str} {datetime.now().year}", "%d %B %Y")
            date = date_obj.strftime("%d-%m-%Y")
        except ValueError:
            date = None
    else:
        match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)', message, re.IGNORECASE)
        if match:
            day_str, month_str = match.groups()
            try:
                date_obj = datetime.strptime(f"{day_str} {month_str} {datetime.now().year}", "%d %B %Y")
                date = date_obj.strftime("%d-%m-%Y")
            except ValueError:
                date = None
    return str(date) if date else None

def extract_time(text):
    patterns = [
        r'(\d{1,2}):(\d{2})',  # HH:MM
        r'(\d{1,2})\s*(am|pm)',   # HH am/pm
        r'\b(\d{1,2})\b'          # HH (assumed to be a full hour)
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2 and ":" in match.group(0):  # HH:MM format
                hour = int(match.group(1))
                minute = int(match.group(2))
                return str(f"{hour:02d}:{minute:02d}")
            elif len(match.groups()) == 2:  # HH am/pm format
                hour = int(match.group(1))
                am_pm = match.group(2).lower()
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                return str(f"{hour:02d}:00")
            elif len(match.groups()) == 1:  # Just an hour
                hour = int(match.group(1))
                return str(f"{hour:02d}:00")
    return None

def extract_locations(message):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(message)
    found_location = None

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC", "FAC"]:
            found_location = ent.text
            break

    if not found_location:
        for token in doc:
            if token.dep_ == "poss" and token.head.text.lower() in ["house", "office", "party"]:
                found_location = f"{token.text} {token.head.text}"
                break

    location = found_location if found_location else None
    return str(location)

def extract_details(user_id, message):
    extracted_id = extract_event_index(message)
    if extracted_id:
        id = get_specific_event(user_id, int(extracted_id))
    else:
        id = extracted_id
    name = extract_event_names(message)
    date = extract_dates(message)
    time = extract_time(message)
    location = extract_locations(message)
    return id, name, date, time, location
