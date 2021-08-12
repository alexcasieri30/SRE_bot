import datetime


# reformats help message
def help_msg(parser, flag):
    args = parser.format_help().split("\n")
    h_m = ""
    for i in args:
        if i[:6]=="usage:":
            i = i.replace("main.py", "--PI")
        h_m += i
        h_m += "<br>"
    if flag == 0:
        h_m += "For information on how to use PI mode, type '--PI' before help command.<br>"
    h_m += "<br>For a more detailed description on how to use the Bot, please visit the wiki page: https://wiki.cnvrmedia.net/display/EN/SRE+Teams+Bot "
    return h_m


# re-formats the name into query readable format
def correct_name(name):
    if "," in name:
        names = name.split(",")
        newname = names[0] + ", " + names[1]
        return newname
    return name


# gets rid of blank spaces in list
def clean_list(list):
    cleanlist = []
    for i in range(len(list)):
        if list[i] != "":
            cleanlist += [list[i]]
    return cleanlist


# converts previous time format to more readable format
def convert_time(timestring):
    timestring = timestring[:-5]
    d = datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S.%f')
    return d.strftime('%b %d, %Y -- %I:%M:%S %p')



def get_assign_index(command):
    for num, i in enumerate(command):
        if i in ['--assign', '-a']:
            return num
    return False


# gets the index of --name command, returns False otherwise
def get_name_index(command):
    for num, i in enumerate(command):
        if i in ['--name', '-name']:
            return num
    return False

