import json
import requests
from props import props
from make_graph import graphdata


"""
Desc: continuously checks messages from teams channel 
Returns: any new message that it receives
"""


def check_new_messages():
    headers = {"Authorization": props['token']}
    teamschannel = f"{props['base_url']}/teams/{props['teams_id']}/channels/{props['channel_id']}/messages?$top=5"
    r = requests.get(teamschannel, headers=headers)
    data = r.json()
    messages = []
    for i in range(len(data['value'])):
        message_id = data['value'][i]['id']
        if not is_message_processed(message_id):
            new_message = process(data['value'][i])
            messages.append(new_message)
    return messages



"""
Desc: Used to check whether a given message is in the processed dictionary
Params: ID of given message
Returns: Boolean
"""


def is_message_processed(message_id):
    with open(props['processed_filepath']) as d:
        processed_messages = json.load(d)
    if message_id in processed_messages:
        return True
    return False


"""
Desc: If a message is not processed, this function processes it
Params: list of message ID, sender, content
Returns: list of message content, sender
"""


def process(message_info):
    with open(props['processed_filepath']) as d:
        processed_messages = json.load(d)
    message_id = message_info['id']
    message = message_info['body']['content']
    name = message_info['from']['user']['displayName']
    processed_messages[message_id] = [message, name]
    out_file = open(props['processed_filepath'], 'w')
    json.dump(processed_messages, out_file)
    info = [message, name, message_id]
    return info


# checks if there is an error message
def check_data(data_url):
    if graphdata(data_url) == 1:
        return 1
    return 0


# replies to the command with an image
def post_image(channel_url, data_url):
    graph_bytes = graphdata(data_url)
    json_payload = {
        "body": {
            "contentType": "html",
            "content": f"<div><img src=\"../hostedContents/1/$value\" width=\"400px\" height=\"300px\"></div>"
        },
        "hostedContents": [
            {
                '@microsoft.graph.temporaryId': '1',
                "contentBytes": graph_bytes,
                "contentType": "image/jpeg"
            }
        ]
    }
    headers = {
                "Content-type": "application/json",
                "Authorization": props['token']
                }
    return requests.post(channel_url, json=json_payload, headers=headers)


# replies to the command with an error message
def post_message(message, channel_url):
    json_payload = {
        "body": {
            "contentType": "html",
            "content": f"<div>{message}</div>"
        },
    }
    headers = {
                "Content-type": "application/json",
                "Authorization": props['token']
               }
    return requests.post(channel_url, json=json_payload, headers=headers)

