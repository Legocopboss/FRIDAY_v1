import os
import sys
from datetime import datetime
import requests
import json

notion_key = os.getenv("NOTION_KEY")
notion_page_id = os.getenv("NOTION_PAGE_ID")
database_id = "9c2aeca0dc944621957a295602fead29"
page_id = ""

headers = {
            'Authorization': 'Bearer ' + notion_key,
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

def getUnfinishedAssignments(date):
    get_assignments = requests.post(
        url=f"https://api.notion.com/v1/databases/{database_id}/query",
        headers=headers,
        json={
            'filter': {
                "and": [
                    {
                        "property": "Finished?",
                        'checkbox': {
                            'equals': bool(0)
                        }
                    },
                    {
                        "property": "Due",
                        "date": {
                            'equals': str(datetime.strptime(date, "%m-%d-%Y").strftime("%Y-%m-%d"))
                        }
                    }
                ]
            }
        }
    )

    formatJson = []
    for x in get_assignments.json()["results"]:
        formatJson.append({
            'title': x["properties"]["Name"]["title"][0]["plain_text"],
            'class': x["properties"]["Course"]["select"]["name"],
        })
    #return formatJson
    #return json.dumps(get_assignments.json(), indent=2)
    raw_assignments = get_assignments.json()["results"]

    return json.dumps([x['properties'] for x in raw_assignments])

#print(getUnfinishedAssignments("08-30-2023"))

