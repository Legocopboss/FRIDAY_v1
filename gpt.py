import threading
import time

import openai
import json
import os
import ast
from datetime import datetime
from loggingFunctions import *
from spotifyFunctions import *
from notionFunctions import *
from dotenv import load_dotenv
from gui_v3 import setAiText, setUserText, startGUIWindow, preLoop
from fileAccessFunctions import file_access
from currentEventFunctions import get_current_event, accuweather_api_request

load_dotenv()


GuiThread = threading.Thread(target=startGUIWindow)
GuiThread.start()

query = ""

available_functions = {
    "mark_log": markLog,
    "SpotifyAPIRequest": newMusicQuery,
    "getUnfinishedAssignments": getUnfinishedAssignments,
    "file_access": file_access,
    "get_current_events": get_current_event,
    "get_weather": accuweather_api_request,
}

functions = [
    {
        "name": "mark_log",
        "description": "Mark and end the current conversation",
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": "The date of the log",
                },
                "date": {
                    "type": "string",
                    "description": "The time of the log",
                },
                "reason": {
                    "type": "string",
                    "description": "The reason for marking the log",
                },
            },
            "required": ["date", "time"],
        },
    },
    {
        "name": "SpotifyAPIRequest",
        "description": "This function allows you to have full control over making requests to the spotify API. Anything relating to music will most likely run through this function. If you have questions or concerns ask, do not make too big of assumptions. Use your knowledge of the spotify API to help you with the inputs of the parameters of this function. When requesting playlists from the API make sure to set a limit of 5 at a time or else you will exceed your max amount of tokens",
        "parameters": {
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "This represents the specific Spotify API endpoint that needs to be hit (e.g., 'me/playlists', 'me/player/play)",
                },
                "method": {
                    "type": "string",
                    "description": "This specifies the HTTP method to use for the request (e.g, 'GET', 'POST', 'PUT', 'DELETE'). Use cases are documented in the Spotify API"
                },
                "queryParams": {
                    "type": "string",
                    "description": "This is an optional parameter that can be used to pass or request any additional query parameters to the API.",
                },
                "body": {
                    "type": "string",
                    "description": "This is an optional parameter that can be used to pass or request any additional body data to the API.",
                },
            },
            "required": ["endpoint", "method"]
        },
    },
    {
        "name": "getUnfinishedAssignments",
        "description": "Returns a list of all unfinished assignments in a json format. You can use this to find assignments which are due using today's date",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The date to search for the unfinished assignments",
                },
            },
            "required": ["date"]
        },
    },
    {
        "name": "file_access",
        "description": "Allows for reading and writing to the file system.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "This is file path to the wanted file. Do not guess about this information if it is unclear of where a file is or where a file should be stored then ask.",
                },
                "mode": {
                    "type": "string",
                    "description": "This is the operation to be done to the file. Your options are reading and writing",
                    "enum": ["read", "write"]
                },
                "data": {
                    "type": "string",
                    "description": "This field is optional as it is only needed for the writing mode. This is the data to be written in the file."
                }
            },
            "required": ["filename", "mode"],
        },
    },
    {
        "name": "get_current_events",
        "description": "Allows for you to gain access to current news events. This runs through the mediastack API so use your knowledge on that to assist you in filling out the fields.",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "This is the keywords field and can be used to search for more specific news events."
                },
                "categories": {
                    "type": "string",
                    "description": "This is a way to specifically include or exclude (exclude by prefixing the category with a '-') categories. Multiple categories can be inputted as long as they are sperated by a comma. The default value for this value is 'general'. The category options are as follows: general, business, entertainment, health, science, sports, technology"
                }
            }
        }
    },
    {
        "name": "get_weather",
        "description": "Allows for you to make requests to the Accuweather weather API. Use your knowledge on this api to help you fill in the needed values",
        "parameters": {
            "type": "object",
            "properties": {
                "config": { #TODO: THIS NEEDS TO BE FIXED. DONT USE AN ARRAY IDIOT USE LIKE ACTUAL PARAMETERS
                    "type": "array",
                    "description": "Pass the necessary configuration parameters (endpoint, method, queryParams, body) as a dictionary in this value. Use your knowledge on the Accuweather API to help you with this. Do not assume any values. If you need clarification ask.",
                    "items": {
                        "type": "string"
                    }
                },
            },
            "required": ["config"]
        }
    }
]
def run_gpt(query, time, date):
    logFile = logRead(time, date)
    messages = []

    if logFile is not None:
        for statement in logFile:
            #if not statement.startswith("Function Call"):
            #    messages.append({"role": "user" if statement.startswith("Query: ") else "assistant", "content": statement.removeprefix("Query: ").removeprefix("Response: ").removesuffix("\n")})
            messages.append(statement)
    else:
        messages = [
            {
                "role": "system", "content":
                f"You are a helpful assistant that has a decent amount of sarcasm. "
                f"The current log is dated as {date} with the timestamp being {time}. "
                f"Ask for clarification if needed. Don't assume values. "
                f"Current Location is Bloomington Indiana. "
                f"Your main directory (The one where your code is stored) is in C:\\Users\\legoc\\PycharmProjects\\FRIDAY. "
                f"The file 'notes.txt' which is in your main directory is for YOUR USAGE. You are to use this file to store notes and any information which you think may be important in the future. Use the file as a form of permanent memory. Modify the file whenever you need. You do not need permission to modify the file. "
                f"Check your notes file often as important information may be contained within it. "
                #f"If there is information or a service that you don't have the needed functions to fulfill, then mark the log as 'New Feature List' and explain what functions you need to fulfil the need. "
                f"If something breaks or a value is not what you expect ask about it, then call the mark log function and mark the log as 'Found Bug'. "
            },
        ]

    messages.append({"role": "user", "content": query})

    setUserText(query)

    gpt = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        functions = functions,
        function_call = "auto",
    )

    gpt_response = gpt["choices"][0]["message"]


    if gpt_response.get("function_call"):
        function_name = gpt_response["function_call"]["name"]
        if function_name in available_functions:
            function_to_call = available_functions[function_name]
            function_args = json.loads(gpt_response["function_call"]["arguments"])
            function_response = function_to_call(**function_args)



            messages.append(gpt_response)
            messages.append(
                {"role": "function", "name": function_name, "content": function_response}
            )

            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )

            print(second_response["choices"][0]["message"]["content"])

            setAiText(second_response["choices"][0]["message"]["content"])

            messages.append(second_response["choices"][0]["message"])

            if function_name == "mark_log":
                postMarkLogWrite(messages, function_args.get("reason"), time, date)

        else:
            messages.append(gpt_response)
            messages.append({'role': 'system', 'content': "Function does not exist."})
    else:
        print(gpt_response["content"])

        setAiText(gpt_response["content"])

        messages.append(gpt_response)


    logWriteNew(messages, time, date)



now = datetime.now()
_time = now.strftime("%H-%M-%S")
_date = now.strftime("%m-%d-%Y")
print(_time, _date)

time.sleep(1)
preLoop()

while query != "quit":
    query = input()
    run_gpt(query, _time, _date)
