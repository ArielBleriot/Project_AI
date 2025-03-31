import spacy

def extract_locations(messages):
    # Load the spaCy English model
    nlp = spacy.load("en_core_web_sm")

    locations = []
    for message in messages:
        doc = nlp(message)
        found_location = None

        # Check for named entities labeled as GPE/LOC/FAC
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC", "FAC"]:
                found_location = ent.text
                break

        # If no entity found, look for possessive phrases dynamically
        if not found_location:
            for token in doc:
                # Check for possessive structure (e.g., "John's house")
                if token.dep_ == "poss" and token.head.text.lower() in ["house", "office", "party"]:
                    found_location = f"{token.text} {token.head.text}"
                    break
        
        locations.append(found_location if found_location else None)

    return locations

# Example messages
messages = [
    "add an event on April 4th that I have to be at John's house at 7pm",
    "can you help me create an event on April 4th at 2pm for my brother's birthday",
    "please add into the calendar that I have a company meeting at 16:00 on April 20th",
    "change the event at number 4 to 6pm at grandma's house"
]

# Extracting locations
locations = extract_locations(messages)
print(locations)
