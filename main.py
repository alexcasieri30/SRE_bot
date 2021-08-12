from teams_message import check_new_messages, post_message, post_image
from message_parser import parse_message
import time
from props import props


while True:
    new_message = check_new_messages()
    if new_message:
        for i in new_message:
            argument = i[0]
            id = i[2]
            base_channel = f"{props['base_url']}/teams/{props['teams_id']}/channels/{props['channel_id']}/messages"
            teamschannel = base_channel + "/" + str(id) + "/replies"
            # code specifies case type, url is for images, message includes responses
            code, url, message = parse_message(argument)
            if code == 1:
                post_message(message, teamschannel)
                print("Response sent.")
                print("-"*40)
            elif code == 2:
                t2 = time.time()
                print(f"Posting image...")
                post_image(teamschannel, url)
                print(f"Image posted in {time.time()-t2} seconds.")
                print("-"*40)
    time.sleep(int(props['query_time']))

