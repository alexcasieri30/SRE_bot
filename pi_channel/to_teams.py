import requests
from authentication import token
from processing import get_id


# post function for messages
def post_message(message, channel_url):
    json_payload = {
        "body": {
            "contentType": "html",
            "content": f"<div>{message}</div>"
        },
    }
    headers = {
                "Content-type": "application/json",
                "Authorization": token
               }
    return requests.post(channel_url, json=json_payload, headers=headers)


# posts the info to the teams channel
def post_info(info):
    teams_id = "ea7db30e-e76a-4c9b-b95a-6ccc8911f83a"
    channel_id = "19%3a7207ce83252247d79174f1ab53f64fb0%40thread.tacv2"
    base = "https://graph.microsoft.com/v1.0/"
    url = f"{base}teams/{teams_id}/channels/{channel_id}/messages"
    return post_message(info, url)


# formats messages to send to Teams channel
def create_priority_message(ticket):
    id = get_id(str(ticket))
    pri = ticket.get_priority().get_name()
    return f"Ticket \"{id}\" priority changed to {pri}"


def create_impact_message(ticket):
    id = get_id(str(ticket))
    impact = ticket.get_value(['fields', 'customfield_12195'])
    return f"Ticket \"{id}\" impact changed to {impact}"


