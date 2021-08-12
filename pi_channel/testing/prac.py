from test_functions import do_i_change_impact_test, do_i_change_priority_test


class ticket():
    def __init__(self):
        self.id = "id = PI-5344"
        self.old_impact = "None"
        self.new_impact = "Severe 1"
        self.old_priority = "Low"
        self.new_priority = "Medium"
        self.new = False


ticket1 = ticket()


print(do_i_change_priority_test(ticket1))
print(do_i_change_impact_test(ticket1))
