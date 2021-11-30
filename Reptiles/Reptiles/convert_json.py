import json

docs = []

with open("./ACM.json", 'rb') as load_f:
    for line in load_f:
        docs.append(json.loads(line))
for dic in docs:
    del dic['_id']


with open("./test_out.json", "w") as dump_f:
    for dic in docs:
        json.dump(dic, dump_f)
        if dic != docs[-1]:
            dump_f.write('\n')
