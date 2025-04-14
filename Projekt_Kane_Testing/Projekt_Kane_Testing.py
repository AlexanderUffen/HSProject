from openai import OpenAI

client = OpenAI(api_key="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")
import textwrap
import config
import task_identify
import threading
import time
import logging
import base64
from necessary import laden_aus_datei, speichern_in_datei, encode_image
from robot import StopExecution, stop_execution, moveto, grasp, place
import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import os
import sys
import io
import re

parameter = {
    'location': 'Bedroom',
    'content_hand': 'none',
    'last_action': 'none'
}

available_functions = {
    "moveto": moveto,
    "grasp": grasp,
    "place": place,
    # You can add more functions here
}

# based on example from link: https://falcond.ai/blog/llm-robot-interaction/

DATA_FILE = 'session_data.json'
FUNCTIONS_FILE = 'functions.json'

dateiname = 'variablen.json'
speichern_in_datei(parameter, dateiname)
image_path = './assets/picture_without_coke.jpg'
response = "some random text '''some other text''' extracted"
Question = "Bring me a Coke"
response_picture = "some generated list"
config.current_mode = 'test'

abort_process = False

def process_input():
    global Question
    global response_picture
    global response
    global abort_process
    abort_process = False  # Reset the abort flag at the beginning of each process

    while True:
        if abort_process:
            break

        print("Python code being generated")
        parameter = laden_aus_datei(dateiname)

        outer_input_task = (
            "Starting with the following incomplete python snippet(zero shot!): from robot import moveto, grasp, place  "
            "# The functions take the following inputs: moveto = string(the sting contains a place or name of a room where to move), "
            "grasp = string(takes a name of an objekt which the robot is supposed to grab) , place = string(the string contains the location "
            "where to place the current gripper content)  How do I program my robot to {} given the following starting parametes: "
            "list of objekts you can see in this room: {} , current location of robot:{} , content in gripper of robot:{} "
        )
        outer_input_question = "You've been asked: {}. Tell me in one word, is this a task or a question?"
        Question = entry.get()

        log_list.insert(tk.END, Question + "\n\n", 'right')

        Question_pre = outer_input_question.format(Question)
        print(Question_pre)

        # Check if Task or Question
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": Question_pre}
            ]
        )

        response_content = response.choices[0].message.content.strip()
        response_content_clean = response_content.rstrip(".").lower()
        print(response_content_clean)

        if abort_process:
            break

        # Formation Question depending on Type
        if response_content_clean == "task":
            input_text = outer_input_task.format(Question, response_picture, parameter['location'], parameter['content_hand'])
            task = 1
        elif response_content_clean == "question":
            input_text = Question
            task = 2
        else:
            input_text = Question
            task = 2

        print(input_text)

        if abort_process:
            break

        # Appropriate Answer to Question or Task
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.2,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": "You are a robot household assistant."},
                {"role": "user", "content": input_text}
            ]
        )

        logging.basicConfig(
            filename='gpt.log',
            format='----------------------------\n%(asctime)s GPT-4 %(levelname)s: %(message)s\n\n',
            encoding='utf-8',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logger = logging.getLogger(__name__)

        if task == 1:
            # Format for execution
            # Separate Python Code
            x = response.choices[0].message.content.split("```")
            y = x[1]
            text = textwrap.dedent(y[6:])
            undefined_functions = validate_code(text, available_functions)
            while undefined_functions:
                if abort_process:
                    break
                for func in undefined_functions:
                    if abort_process:
                        break
                    user_choice = ask_user_for_function_creation(func)
                    if user_choice == "Manuell":
                        create_manual_function_placeholder(func)
                    elif user_choice == "Automatisch":
                        new_function_code = generate_function_definition(func)
                        while not display_and_confirm_function(new_function_code):
                            new_function_code = generate_function_definition(func)
                        save_function_to_file(new_function_code)
                        exec(new_function_code, globals())
                        # Extract function name and add it to available_functions via globals()
                        function_name = re.search(r'def (\w+)\(', new_function_code).group(1)
                        available_functions[function_name] = globals()[function_name]
                # Nach dem Durchlauf werden undefinierte Funktionen erneut validiert;
                # bereits erstellte Funktionen tauchen so nicht mehr auf.
                undefined_functions = validate_code(text, available_functions)
            if abort_process:
                break
            exec(text)

        elif task == 2:
            text = response.choices[0].message.content

        if abort_process:
            break

        log_list.insert(tk.END, text + "\n", 'left')
        log_list.insert(tk.END, "-------------------------------------------------------------------------------------------------\n")
        session_data.append({"input": Question, "output": text})
        entry.delete(0, tk.END)
        save_data()
        break

def ask_user_for_function_creation(function_name):
    user_choice = tk.StringVar()
    global abort_process

    def set_choice(choice):
        user_choice.set(choice)
        popup.destroy()

    def abort():
        global abort_process
        abort_process = True
        user_choice.set(None)
        popup.destroy()

    popup = tk.Toplevel(root)
    popup.title("Neue Funktion erkannt")
    tk.Label(popup, text=f"Die Funktion '{function_name}' wurde erkannt. Möchten Sie sie manuell oder automatisch erstellen?").pack(padx=20, pady=20)
    tk.Button(popup, text="Manuell", command=lambda: set_choice("Manuell")).pack(side=tk.LEFT, padx=20, pady=20)
    tk.Button(popup, text="Automatisch", command=lambda: set_choice("Automatisch")).pack(side=tk.LEFT, padx=20, pady=20)
    tk.Button(popup, text="Abbrechen", command=abort).pack(side=tk.RIGHT, padx=20, pady=20)

    popup.wait_window(popup)
    return user_choice.get()

def create_manual_function_placeholder(function_name):
    placeholder_code = f"def {function_name}(*args, **kwargs):\n    pass\n"
    exec(placeholder_code,globals())
    available_functions[function_name] = globals()[function_name]

def generate_function_definition(function_name):
    prompt = f"Please write a Python function definition for a function named '{function_name}'. It's meant to be for a robotic arm that is used inside the household. You can use the functions moveto(x), grasp(x), and place(x) within your definition."
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    x = response.choices[0].message.content.split("```")
    y = x[1]
    text = textwrap.dedent(y[6:])
    print(text)
    return text

def display_and_confirm_function(function_code):
    confirmed = tk.BooleanVar()
    global abort_process

    def confirm_choice(choice):
        confirmed.set(choice)
        popup.destroy()

    def abort():
        global abort_process
        abort_process = True
        confirmed.set(False)
        popup.destroy()

    popup = tk.Toplevel(root)
    popup.title("Neue Funktion")
    tk.Label(popup, text="Hier ist die generierte Funktion:").pack(padx=20, pady=10)

    text_widget = tk.Text(popup, wrap=tk.WORD, height=10, width=50)
    text_widget.pack(padx=20, pady=10)
    text_widget.insert(tk.END, function_code)

    tk.Button(popup, text="Akzeptieren", command=lambda: confirm_choice(True)).pack(side=tk.LEFT, padx=20, pady=20)
    tk.Button(popup, text="Ablehnen", command=lambda: confirm_choice(False)).pack(side=tk.LEFT, padx=20, pady=20)
    tk.Button(popup, text="Abbrechen", command=abort).pack(side=tk.RIGHT, padx=20, pady=20)

    popup.wait_window(popup)
    return confirmed.get()

def save_function_to_file(function_code):
    with open(FUNCTIONS_FILE, 'a') as file:
        file.write(f"\n{function_code}")

def load_functions_from_file():
    if os.path.exists(FUNCTIONS_FILE):
        with open(FUNCTIONS_FILE, 'r') as file:
            code = file.read()
            exec(code, globals(), available_functions)

def task_picture():
    global response_picture
    print("Analysing image input")
    base64_image = encode_image(image_path)
    while True:
        if abort_process:
            break
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': 'Provide me with a list of Keyword of what you can see in this Image, Only one Word per Objekt and without any numbers or "-" in front just the word'},
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{base64_image}'
                            },
                        },
                    ],
                }
            ],
            max_completion_tokens=300
        )
        response_picture = response.choices[0].message.content
        updated_text.set(response_picture)
        event.set()
        time.sleep(1000)

def save_data():
    all_sessions = load_all_sessions()
    session_name = session_var.get()
    all_sessions[session_name] = session_data
    with open(DATA_FILE, 'w') as file:
        json.dump(all_sessions, file)

def load_all_sessions():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def delete_session():
    all_sessions = load_all_sessions()
    session_name = session_var.get()
    if session_name in all_sessions:
        del all_sessions[session_name]
        with open(DATA_FILE, 'w') as file:
            json.dump(all_sessions, file)
        session_var.set('')
        update_session_menu()

def load_session(session_name):
    global session_data
    all_sessions = load_all_sessions()
    session_data = all_sessions.get(session_name, [])
    log_list.delete(1.0, tk.END)
    for item in session_data:
        log_list.insert(tk.END, item["input"] + "\n", 'right')
        log_list.insert(tk.END, item["output"] + "\n", 'left')
        log_list.insert(tk.END, "-------------------------------------------------------------------------------------------------\n")

def change_session(*args):
    session_name = session_var.get()
    if session_name:
        load_session(session_name)

def create_new_session():
    session_name = new_session_entry.get()
    if session_name:
        session_var.set(session_name)
        log_list.delete(1.0, tk.END)
        session_data.clear()
        save_data()
        update_session_menu()
    new_session_entry.delete(0, tk.END)

def update_session_menu():
    session_menu['menu'].delete(0, 'end')
    all_sessions = load_all_sessions()
    for session in all_sessions.keys():
        session_menu['menu'].add_command(label=session, command=tk._setit(session_var, session))

def validate_code(code, available_functions):
    pattern = re.compile(r'\b\w+\s*(?=\()')
    # Extrahiere eindeutige Funktionsaufrufe (als Set)
    function_calls = {func.strip() for func in pattern.findall(code)}
    # Berücksichtige eine Funktion als definiert, wenn sie in available_functions oder in globals() vorhanden ist
    undefined_functions = [func for func in function_calls if func not in available_functions and func not in globals()]
    return list(undefined_functions)

root = tk.Tk()
root.title("Textverarbeitung")

entry = tk.Entry(root, width=80)
entry.grid(row=0, column=0, padx=10, pady=10)

process_button = tk.Button(root, text="Verarbeiten", command=process_input)
process_button.grid(row=0, column=1, padx=5)

mode_var = tk.IntVar()
mode_switch = tk.Checkbutton(root, text="Mode: Testing", variable=mode_var, onvalue=1, offvalue=0,
                             command=lambda: mode_switch.config(text="Mode: Running" if mode_var.get() else "Mode: Testing"))
mode_switch.grid(row=0, column=2, padx=5)

log_list = scrolledtext.ScrolledText(root, width=100, height=40, wrap=tk.WORD)
log_list.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

log_list.tag_configure('left', justify='left')
log_list.tag_configure('right', justify='right')

session_var = tk.StringVar(value='Select a session')
session_var.trace('w', change_session)
session_menu = tk.OptionMenu(root, session_var, 1, *list(load_all_sessions().keys()))
session_menu.grid(row=2, column=0, pady=10)

new_session_entry = tk.Entry(root, width=20)
new_session_entry.grid(row=2, column=1, padx=5)

new_session_button = tk.Button(root, text="Neue Sitzung", command=create_new_session)
new_session_button.grid(row=2, column=2, padx=5)

delete_session_button = tk.Button(root, text="Session löschen", command=delete_session)
delete_session_button.grid(row=3, column=0, columnspan=3, pady=5)

objects_label = tk.Label(root, text="Objects in Sight:", font=('Helvetica', 16))
objects_label.grid(row=4, column=0, columnspan=3, pady=5)

updated_text = tk.StringVar()
updated_text.set("")
updated_label = tk.Label(root, textvariable=updated_text, font=('Helvetica', 16))
updated_label.grid(row=5, column=0, columnspan=3, pady=5)

event = threading.Event()

thread_picture = threading.Thread(target=task_picture)
thread_picture.start()

session_data = []
if load_all_sessions():
    session_var.set(next(iter(load_all_sessions().keys())))
else:
    session_var.set('New Session')

# Load functions from file at startup
load_functions_from_file()

root.mainloop()
