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

JSON_CONFIG          = "config.json"
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
Returns an array of a random number of users chosen for the exercise
The number of users chosen is randomized between 1 and MIN(total members in channel, max_users_to_choose set in the config file)
"""
def get_random_members(members):
    total_members              = len(members)
    random_num_users_to_choose = 1
    total_members_chosen       = 0
    list_of_members            = []
    # Selects the total number of users to choose at a time based randomized between 1 and the MIN value of (total users, total users to choose from in the config)
    with open(JSON_CONFIG) as file:
        data                       = json.load(file)
        max_users_to_choose        = data["max_users_to_choose"]
        max_users_to_choose        = min(total_members,max_users_to_choose)
        random_num_users_to_choose = random.randint(1,max_users_to_choose)

    # keep adding random users to the total list
    # if we've selected a repeat user, continue searching
    while total_members_chosen < random_num_users_to_choose:
        random_member = random.randint(0,len(members)-1)
        if list_of_members.count(members[random_member]):
            continue

        list_of_members.append(members[random_member])
        total_members_chosen+=1

    return list_of_members

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
def create_exercise_message(list_of_members,exercise):
    exercise_name = exercise['name']
    min_reps      = int(exercise['min'])
    max_reps      = int(exercise['max'])
    unit          = exercise['unit']

    reps_to_do  = random.randint(min_reps,max_reps)
    inspiration = get_random_inspiration()

    message     = ""

    for member in list_of_members:
        message+="<@%s> " % (member)

    message+="%s *_%s_ for %s %s*! " % (inspiration,exercise_name,reps_to_do,unit)

    log_exercise(list_of_members,exercise,reps_to_do)

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
def new_message(list_of_members,exercise):

    message = create_exercise_message(list_of_members,exercise)

    new_message_params = {
        "channel":CHANNEL_GYMLIFE,
        "username":"GymBot#gains",
        "link_names":"1",
        "text":message,
        "icon_emoji": ":muscle:",
        "as_user":"false"
    }
    new_message_params = dict(new_message_params.items() + BASE_PARAMS.items())

    response = requests.post(BASE_URL+CMD_NEW_MESSAGE,params=new_message_params)

    print 'SlackBot_GymBro has posted a new challenge to %s users!' % (len(list_of_members))


"""
Adds the entry into a csv file. Contains the user_id, exercise name, # reps, and date
"""
def log_exercise(list_of_members,exercise,reps_to_do):
    with open(CSV_RESULTS,"a") as file:
        writer = csv.writer(file)
        for member in list_of_members:
            writer.writerow([member,exercise['name'],reps_to_do,datetime.now()])

'''
====================================
MAIN
====================================
'''
def main():
    try:
        exercise               = get_random_exercise()
        members                = get_channel_users(CHANNEL_GYMLIFE)
        list_of_random_members = get_random_members(members)

        new_message(list_of_random_members,exercise)
    except Exception as e:
        traceback.print_exc()
        print "ERROR: " 
        print e


main()



