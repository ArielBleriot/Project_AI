import re
from datetime import datetime
import spacy

ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10
}

def extract_event_index(msg):
    event_indices = []
    match = re.search(r'\b(?:number|#)?\s*(\d+)(?:\s*(?:th|st|nd|rd)?\s*event)?\b', msg, re.IGNORECASE)
    word_match = re.search(r'\b(' + '|'.join(ORDINALS.keys()) + r')\b', msg, re.IGNORECASE)

    if word_match:
        event_indices.append(ORDINALS[word_match.group(1).lower()])
    elif match:
        num = int(match.group(1))
        if not re.search(rf'\b{num}:\d{{2}}\b', msg):  
            event_indices.append(num)
    return str(event_indices) if event_indices else None

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
    
    return event_name if event_name else [None]

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
    id = extracted_id
    name = extract_event_names(message)
    date = extract_dates(message)
    time = extract_time(message)
    location = extract_locations(message)
    return id, name, date, time, location

message = "change the event at number 4 to 6pm at grandma's house"
id, name, date, time, location = extract_details(1, message)

print(id, name, date, time, location)
