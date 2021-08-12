from authentication import token

props = {"token": token}

with open("teamsbot.properties") as d:
    lines = d.readlines()
    for i in range(len(lines)):
        line = lines[i]
        if line != "\n" and line[0] != "#":
            items = line.split("=")
            value = items[1][:-1]
            props[items[0]] = value


# for i in props.items():
#     print(i[0] + "---" + i[1])