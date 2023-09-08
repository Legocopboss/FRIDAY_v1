import openai
import json
import os
import ast
from datetime import datetime
from loggingFunctions import *
from spotifyFunctions import *
from notionFunctions import *
from dotenv import load_dotenv

load_dotenv()

query = ""

available_functions = {
    "mark_log": markLog,
    "SpotifyAPIRequest": newMusicQuery,
    "getUnfinishedAssignments": getUnfinishedAssignments,
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
                f"You are a helpful assistant. "
                f"The current log is dated as {date} with the timestamp being {time}. "
                f"Don't make assumptions about what values to plug into functions. "
                f"Ask for clarification if needed. "
                f"If something breaks or a value is not what you expect ask about it, then call the mark log function and mark the log as 'Found Bug'."
            },
        ]

    messages.append({"role": "user", "content": query})

    gpt = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        functions = functions,
        function_call = "auto",
    )

    gpt_response = gpt["choices"][0]["message"]

    if gpt_response.get("function_call"):
        function_name = gpt_response["function_call"]["name"]
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
        messages.append(second_response["choices"][0]["message"])

        if function_name == "mark_log":
            postMarkLogWrite(messages, function_args.get("reason"), time, date)
    else:
        print(gpt_response["content"])
        messages.append(gpt_response)
        #print(messages)

    #logWrite(query, "Query", time, date)
    logWriteNew(messages, time, date)

    #print(messages)

now = datetime.now()
_time = now.strftime("%H-%M-%S")
_date = now.strftime("%m-%d-%Y")
print(_time, _date)

while query != "quit":
    query = input()
    run_gpt(query, _time, _date)
