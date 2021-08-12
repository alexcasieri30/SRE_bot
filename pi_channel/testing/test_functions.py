


def do_i_change_priority_test(ticket):
    priority = ticket.new_priority
    severe_state = False
    change = False
    old_priority = ticket.old_priority
    if old_priority in ['Blocker', 'High']:
        severe_state = True
    if not severe_state:
        if priority in ['Blocker', 'High']:
            change = True
    else:
        if priority == "Blocker" and old_priority == "High":
            change = True
    return change


def do_i_change_impact_test(ticket):
    new_impact = ticket.new_impact
    old_impact = ticket.old_impact
    severe_state = False
    change = False
    if old_impact in ['Severe 1', 'Severe 2']:
        severe_state = True
    if severe_state:
        if new_impact == "Severe 1" and old_impact == "Severe 2":
            change = True
    else:
        if new_impact in ['Severe 1', 'Severe 2']:
            change = True
    return change
