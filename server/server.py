'''
====================================
IMPORTS
====================================
'''
from flask import Flask,request
from settings import *
import re
import json
import traceback

'''
====================================
CONSTANTS
====================================
'''
TRIGGER_WORD   = "GymBot:"
JSON_EXERCISES = "../json/exercises.json"

app = Flask(__name__)

'''
====================================
FUNCTIONS
====================================
'''

@app.route("/slack_gymbot",methods=['POST'])
def new_exercise():
    try:
        if request.method == 'POST':
            # Get relevant POST params
            outgoing_token = request.form['token']
            channel_id = request.form['channel_id']
            text = request.form['text']
            parameters = parse_text(text)
            execute_command(parameters)
            return 'Added new Exercise!'
        else:
            return 'Nothing to do here -_-'
    except Exception as e:
        traceback.print_exc()
        return e.message


'''
Parse out the incoming message and break it into variable pieces.
Incoming message should be formatted as follows:
    GymBot: ACTION NAME | var1 | var2 | var3 ...
    Ex:
        GymBot: Add New Exercise | JUMPING_JACKS | 5 | 5 | reps

ReturnObject:
    {   'name':'COMMAND', 
        'item_1':SOME_VALUE,
        'item_2':SOME_VALUE,
        ...
    }
'''
def parse_text(text):
    return_object = {}
    pattern = '(([_a-zA-Z0-9\s]*)\|{1})'
    pattern_trigger_word = '(%s)' % (TRIGGER_WORD)
    # 1. Parse out all Spaces
    text = re.sub("\s",'',text)
    # 2. Parse out the Trigger Word
    text = re.sub(pattern_trigger_word,'',text)
    # 3 . Iterate through rest of text and get all values
    index = 1
    while re.match(pattern,text):
        key = "item_"+ str(index)
        match = re.search(pattern,text)
        value = match.group(2)
        return_object[key] = value
        index+=1
        text = re.sub(pattern,'',text,1)
    return return_object

def execute_command(parameters):
    print parameters
    if parameters['item_1'].lower() == 'AddNewExercise'.lower():
        exercise = parameters['item_2']
        exercise = exercise.replace("_"," ")
        min_reps = parameters['item_3']
        max_reps = parameters['item_4']
        rep_type = parameters['item_5']
        add_exercise_to_file(exercise,max_reps,min_reps,rep_type)


'''
Adds the new exercise to the existing list of exercises
'''
def add_exercise_to_file(exercise,max_reps,min_reps,rep_type):
    tmp = {}
    # Need to do 2 separate opens since after reading the file the first time, the cursor is pointing to the end of file
    # By opening the file again, we can set the cursor to the top of the file thus overwriting everything instead of appending
    with open(JSON_EXERCISES,"r+") as file:
        data = json.load(file)
        tmp = data

    with open(JSON_EXERCISES,"w+") as file:
        exercises = tmp['exercises']
        new_exercise = {
            "name": exercise,
            "max": max_reps,
            "min":min_reps,
            "rep":"reps"
        }

        # TODO: Check for duplicates by name
        exercises.append(new_exercise)
        data['exercises'] = exercises
        json.dump(tmp,file)

'''
====================================
MAIN
====================================
'''
if __name__ == '__main__':
    app.debug = DEBUG
    app.run(host='0.0.0.0')

