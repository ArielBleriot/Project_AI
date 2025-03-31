from flask import request, jsonify, Blueprint, session 
from pydantic import BaseModel
import json
import openai
import time

from back_end import assistant_funct

assistant = Blueprint('assistant', __name__)

with open("settings/tools.json", "r") as file:
        tools = json.load(file)

with open("settings/config.json", "r") as file:
    config = json.load(file)

openai.api_key = config['api_key']

# Model for a single message
class Message(BaseModel):
    role: str
    message: str

# Receive a dummy message and return a test response from the virtual assistant
@assistant.post("/usermessage/")
async def process_message_and_respond():
    static_thread_id = config['thread_id']
    message = request.args.get('message')
    if "user_id" not in session:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    user_id = session["user_id"]  # Retrieve user_id from session

    # if thread doesnt exist in config, it will be created, if not it will be overwritten in config
    if static_thread_id == "firstrun":
        thread = openai.beta.threads.create()
        print(f"Thread created with ID: {thread.id}")

        static_thread_id = thread.id
        config["thread_id"] = static_thread_id

        with open("settings/config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)

    else:
        thread = openai.beta.threads.retrieve(thread_id=static_thread_id)
        
    assistant = openai.beta.assistants.create(
        name="Custom Tool Assistant",
        instructions="You are an assistant with access to university_assistant.db and help you user manage, create, modify and delete their events with various tools",
        model="gpt-4o-mini",
        tools=tools
    )
            
    message_to_respond = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )
    
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    attempt = 1
    while run.status != "completed":
        print(f"Run status: {run.status}, attempt: {attempt}")
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action":
            break

        if run.status == "failed":

            if hasattr(run, 'last_error') and run.last_error is not None:
                error_message = run.last_error.message
            else:
                error_message = "No error message found..."

            print(f"Run {run.id} failed! Status: {run.status}\n  thread_id: {run.thread.id}\n  assistant_id: {run.assistant_id}\n  error_message: {error_message}")
            print(str(run))

        attempt += 1
        time.sleep(5)
        
    if run.status == "requires_action":
        print("Run requires action, assistant wants to use a tool")
        tool_outputs = []

        print("User message: ", str(message))
        message_lower = message.lower()
        if run.required_action:
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if any(word in message_lower for word in ["schedule", "add", "create", "set up"]):
                    print("add_event called")
                    output =  assistant_funct.add_event(user_id, message)
                
                elif any(word in message_lower for word in ["modify", "change", "edit", "update"]):
                    print("modify_event called")
                    output = assistant_funct.modify_event(user_id, message)

                elif any(word in message_lower for word in ["remove", "delete", "cancel"]):
                    print("delete_event called")
                    output = assistant_funct.delete_event(user_id, message)

                else:
                    print("I'm not sure what you're trying to do. Do you want to add, get, or delete an event?")
                    output = "I'm not sure what you're trying to do. Do you want to add, get, modify, or delete an event?"
            
                print(f"  Generated output: {output}")


                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": str(output)
                })

            openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs 
            )

    if run.status == "requires_action":

        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        attempt = 1
        while run.status not in ["completed", "failed"]:
            print(f"Run status: {run.status}, attempt: {attempt}")
            time.sleep(2)
            run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            attempt += 1

    if run.status == "completed":

        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        final_answer = messages.data[0].content[0].text.value
    elif run.status == "failed":

        if hasattr(run, 'last_error') and run.last_error is not None:
            error_message = run.last_error.message
        else:
            error_message = "No error message found..."

        print(f"Run {run.id} failed! Status: {run.status}\n  thread_id: {run.thread.id}\n  assistant_id: {run.assistant_id}\n  error_message: {error_message}")
        print(str(run))
    else:
        print(f"Unexpected run status: {run.status}")
        
    messages = openai.beta.threads.messages.list(thread_id=thread.id)

    for msg in messages.data:
        openai.beta.threads.messages.create(
            thread_id=static_thread_id,
            role=msg.role,
            content=str(msg.content)
        )
    
    get_events_route()
    
    return {
        "response": final_answer,
        "message_received": message
    }

def get_openai_conversation(thread_id):
    try:
        # Fetch messages from OpenAI's Assistants API
        response = openai.beta.threads.messages.list(thread_id=thread_id)

        # Ensure that response.data exists
        if not response.data:
            return []

        conversation_history = []
        for msg in response.data:
            if not msg.content:
                continue  # Skip empty messages

            # Extracting text from TextContentBlock
            extracted_text = []
            for block in msg.content:
                if block.type == "text":  
                    extracted_text.append(block.text.value)

            # Join multiple text blocks if any exist
            message_text = " ".join(extracted_text) if extracted_text else "No readable content"

            conversation_history.append({
                "sender": msg.role,  # 'user' or 'assistant'
                "content": message_text
            })

        return conversation_history[::-1]  # Reverse to maintain correct order

    except openai.error.OpenAIError as e:
        return {"error": f"OpenAI API error: {str(e)}"}


@assistant.get("/historymessage/")
def conversation_history():
    static_thread_id = config['thread_id']
    if static_thread_id == "firstrun":
        return jsonify({
            "thread_id": static_thread_id,
            "message": "This thread is new. There is no conversation history."
        })

    try:
        conversation_history = get_openai_conversation(static_thread_id)

        if not conversation_history:
            return jsonify({
                "thread_id": static_thread_id,
                "message": "No messages found in this thread."
            })

        return jsonify({
            "thread_id": static_thread_id,
            "conversation_history": conversation_history
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    
@assistant.route('/getevents', methods=['GET'])
def get_events_route():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    user_id = session["user_id"]  # Retrieve user_id from session

    if user_id:
        event_dict_list = assistant_funct.sorted_events(user_id)
        return jsonify(event_dict_list)  # Return events as a JSON array
    
    else:
        # Return a 400 Bad Request if no user_id is provided
        return jsonify({"message": "user_id is required"}), 400
