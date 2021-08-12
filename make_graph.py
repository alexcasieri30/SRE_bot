import requests
from grapher import Graph


def graphdata(url):
    r = requests.get(url)
    data = r.json()
    if len(data) == 0:
        return 1
    li = []
    la = []
    for n, d in enumerate(data):
        li += [d['dps']]
        la += [print_dict_info(data[n]['tags'])]
        title = data[n]['metric'] + " over Time"
        ylabel = data[n]['metric']
    g1 = Graph(data=li, labels=la, title=title, xlabel="Time", ylabel=ylabel)
    return g1.get_base64()


def print_dict_info(dict1):
    keys = list(dict1.keys())
    values = list(dict1.values())
    string = "{"
    for i in range(len(keys)):
        key = keys[i]
        value = values[i]
        str = key + "=" + value
        if i < len(keys)-1:
            str += ", "
        string += str
    return string + "}"

