

# gets only the id from the name
def get_id(name):
    id = name[5:12]
    return id


# checks to see if ticket is processed
def is_ticket_processed(ticket):
    ticket_id = get_id(str(ticket))
    with open("processed_tickets.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            info = line.split(",")
            if ticket_id == info[0]:
                return True
    return False


# adds ticket to the txt file
def process_ticket(i):
    id = get_id(str(i))
    priority = i.get_priority().get_name()
    impact = i.get_value(['fields', 'customfield_12195'])
    impact = impact['value'] if impact is not None else "None"
    with open("processed_tickets.txt", "a") as f:
        f.write(f"{id},{priority},{impact}\n")
    f.close()


# changes only the priority of a specified ticket in the processed_tickets.txt file
def change_priority(ticket):
    new_priority = ticket.get_priority().get_name()
    ticket_id = get_id(str(ticket))
    with open("processed_tickets.txt", "r") as f:
        lines = f.readlines()
        store_data = []
        for i in lines:
            info = i.split(",")
            if info[0] == ticket_id:
                store_data += [[info[0], new_priority, info[2]]]
            else:
                store_data += [[info[0], info[1], info[2]]]
        f.close()
    print(store_data)
    with open("processed_tickets.txt", "w") as f:
        for i in store_data:
            f.write(f"{i[0]},{i[1]},{i[2]}\n")
        f.close()


# detects changes in a ticket's priority
# False means that there is a change
def check_priority(ticket):
    new_priority = ticket.get_priority().get_name()
    id = get_id(str(ticket))
    with open("processed_tickets.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            info = line.split(",")
            if id == info[0]:
                old_priority = info[1]
                if new_priority != old_priority:
                    return False
    return True


# detects changes in a ticket's impact field
# False means that there is a change
def check_impact(ticket):
    new_impact = ticket.get_value(['fields', 'customfield_12195'])
    new_impact = new_impact['value'] if new_impact is not None else "None"
    ticket_id = get_id(str(ticket))
    with open("processed_tickets.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            info = line.split(",")
            if ticket_id == info[0]:
                old_impact = info[2]
                if new_impact + "\n" != old_impact:
                    return False
    return True


# changes the impact field of a given ticket in the processed_tickets.txt file
def change_impact(ticket):
    new_impact = ticket.get_value(['fields', 'customfield_12195'])
    new_impact = new_impact['value'] if new_impact is not None else "None"
    ticket_id = get_id(str(ticket))
    with open("processed_tickets.txt", "r") as f:
        lines = f.readlines()
        store_data = []
        for i in lines:
            info = i.split(",")
            if info[0] == ticket_id:
                store_data += [[info[0], info[1], new_impact + "\n"]]
            else:
                store_data += [[info[0], info[1], info[2]]]
        f.close()
    with open("processed_tickets.txt", "w") as f:
        for i in store_data:
            f.write(f"{i[0]},{i[1]},{i[2]}")
        f.close()

