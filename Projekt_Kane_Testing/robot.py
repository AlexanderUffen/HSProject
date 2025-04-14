from necessary import laden_aus_datei, speichern_in_datei
import sys
import config


class StopExecution(Exception):
    pass

def stop_execution():
    if config.current_mode == 'test':
        print("Testing: stop execution")
    else:
        raise StopExecution

def plan_motion(x):

    if config.current_mode == 'test':
        print("Testing: motion planed")
    else:
        dateiname = 'variablen.json'
        output = "moved to {}"
        output = output.format(x)
        parameter = laden_aus_datei(dateiname)
        parameter['location'] = x
        parameter['last_action'] = output
        speichern_in_datei(parameter, dateiname)
        print("location reached")
        return 1

def resolve_ingredients():
    if config.current_mode == 'test':
        print("Testing: ingredients resolved")
    else:
        print("ingredients resolved")
        return 1

def turn_on_coffee_machine():
    if config.current_mode == 'test':
        print("Testing: Coffemachine ON")
    else:
        print("Coffemachine ON")
        return 1

def  turn_off_coffee_machine():
    if config.current_mode == 'test':
        print("Testing: Coffemachine OFF")
    else:
        print("Coffemachine OFF")
        return 1

def locate_cup():
    if config.current_mode == 'test':
        print("Testing: Cup Located")
    else:
        print("Cup Located")
        return 1

def check_coffee_machine_status():
    if config.current_mode == 'test':
        print("Testing: checked Coffemachine status")
    else:
        print("Status checked")
    return 1

def place(x):
    if config.current_mode == 'test':
        print("Testing: objekt placed")
    else:
        dateiname = 'variablen.json'
        print("Objekt placed")
        output = "Placed {}"
        output = output.format(x)
        parameter = laden_aus_datei(dateiname)
        parameter['content_hand'] = 'none'
        parameter['last_action'] = output
        speichern_in_datei(parameter, dateiname)
        stop_execution()

def grasp(x):
    if config.current_mode == 'test':
        print("Testing: Objekt graped")
    else:
        dateiname = 'variablen.json'
        print("Objekt grapped")
        output = "Grapped {}"
        output = output.format(x)
        parameter = laden_aus_datei(dateiname)
        parameter['content_hand'] = x
        parameter['last_action'] = output
        speichern_in_datei(parameter, dateiname)
        stop_execution()
 
def push(x):
    if config.current_mode == 'test':
        print("Testing: pushed")
    else:
        print("Objekt pushed")
        return 1

def pull(x):
    print("Objekt pulled")
    return 1

def locate(x):
    if config.current_mode == 'test':
        print("Testing: Object located")
    else:
        print("Objekt located")
        return 1

def moveto(x):
    if config.current_mode == 'test':
        print("Testing: moved")
    else:
        dateiname = 'variablen.json'
        output = "moved to {}"
        output = output.format(x)
        parameter = laden_aus_datei(dateiname)
        parameter['location'] = x
        parameter['last_action'] = output
        speichern_in_datei(parameter, dateiname)
        print("moved to %s", x)
        stop_execution()

