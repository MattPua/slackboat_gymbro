#!/usr/bin/python
'''
====================================
IMPORTS
====================================
'''
import json
import requests
import random
import csv
import traceback
from datetime import datetime

from settings import *
'''
====================================
CONSTANTS
====================================
'''
BASE_URL             = 'https://slack.com/api/'
BASE_PARAMS          = {
"token": TOKEN,
}


CMD_NEW_MESSAGE      = 'chat.postMessage'
CMD_GET_CHANNEL_INFO = 'channels.info'


JSON_EXERCISES       = "exercises.json"
JSON_INSPIRATION     = "inspiration.json"
CSV_RESULTS          = "results.csv"


'''
====================================
FUNCTIONS
====================================
'''


""" 
Returns a list of users for a specific channelId
"""
def get_channel_users(channelId):

    get_channel_params = {
    "channel": channelId,
    }

    get_channel_params = dict(get_channel_params.items() + BASE_PARAMS.items())

    response           = requests.post(BASE_URL+CMD_GET_CHANNEL_INFO,params=get_channel_params)
    data               = response.json()
    members            = data['channel']['members']
    return members

"""
Returns a random member from the set
"""
def get_random_member(members):
    total_members = len(members)
    random_member = random.randint(0,len(members)-1)
    return members[random_member]

"""
Returns a random Exercise from a JSON file along with maximum and minimum rep count
"""
def get_random_exercise():
    with open(JSON_EXERCISES) as file:
        data = json.load(file)
        exercises = data['exercises']
        random_exercise = random.randint(0,len(exercises)-1)
        return exercises[random_exercise]

"""
Creates the message that you want to post on Slack for the exercise announcement
"""
def create_exercise_message(member,exercise):
    exercise_name = exercise['name']
    min_reps      = int(exercise['min'])
    max_reps      = int(exercise['max'])
    unit          = exercise['unit']

    reps_to_do = random.randint(min_reps,max_reps)
    inspiration = get_random_inspiration()

    message = "<@%s> %s *_%s_ for %s %s*! " % (member,inspiration,exercise_name,reps_to_do,unit)

    log_exercise(member,exercise,reps_to_do)

    return message

"""
Gets a random message to attach to the announcement from a JSON file
"""
def get_random_inspiration():
    with open(JSON_INSPIRATION) as file:
        data = json.load(file)
        inspiration = data['message']
        random_inspiration = random.randint(0,len(inspiration)-1)
        return inspiration[random_inspiration]['text']

"""
Sends the new message to Slack
"""
def new_message(member,exercise):

    message = create_exercise_message(member,exercise)

    new_message_params = {
        "channel":CHANNEL_GYMLIFE,
        "username":"GymBot#gains",
        "link_names":"1",
        "text":message
    }
    new_message_params = dict(new_message_params.items() + BASE_PARAMS.items())

    response = requests.post(BASE_URL+CMD_NEW_MESSAGE,params=new_message_params)

    print 'SlackBot_GymBro has posted a new challenge!'


"""
Adds the entry into a csv file. Contains the user_id, exercise name, # reps, and date
"""
def log_exercise(random_member,exercise,reps_to_do):
    with open(CSV_RESULTS,"a") as file:
        writer = csv.writer(file)
        writer.writerow([random_member,exercise['name'],reps_to_do,datetime.now()])

'''
====================================
MAIN
====================================
'''
def main():
    try:
        exercise      = get_random_exercise()
        members       = get_channel_users(CHANNEL_GYMLIFE)
        random_member = get_random_member(members)

        new_message(random_member,exercise)

    except Exception as e:
        traceback.print_exc()
        print "ERROR: " 
        print e


main()



