from from_jira import get_info, get_new_pi_tickets, do_i_post_impact, do_i_post_priority
from to_teams import post_info, create_priority_message, create_impact_message
from processing import process_ticket, is_ticket_processed, check_priority, change_priority, check_impact, change_impact


# adds all the functions together into one
def driver():
    all_info = []
    # iterates through all tickets
    for i in get_new_pi_tickets():

        if not is_ticket_processed(i):
            all_info += [get_info(i)]
            process_ticket(i)

        if not check_priority(i):
            print("priority changed")
            if do_i_post_priority(i):
                post_info(create_priority_message(i))
            change_priority(i)

        if not check_impact(i):
            print('impact changed')
            print(do_i_post_impact(i))
            if do_i_post_impact(i):
                print("criteria met")
                post_info(create_impact_message(i))
            change_impact(i)

    # if anything in the list
    if len(all_info) > 0:
        # post list of all previously unprocessed tickets
        post_info(all_info)
    return


while True:
    driver()
    # time.sleep(5)

