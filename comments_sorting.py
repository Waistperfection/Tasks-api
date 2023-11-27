from pprint import pprint


COMMENTS = [
    {"id": 7, "body": "efsa", "task": 3, "answer_to": None},
    {"id": 10, "body": "первый", "task": 3, "answer_to": 7},
    {"id": 11, "body": "первый-глубже", "task": 3, "answer_to": 10},
    {"id": 12, "body": "первый-глубже2", "task": 3, "answer_to": 10},
    {"id": 13, "body": "первый-глубже-2глубже", "task": 3, "answer_to": 12},
    {"id": 14, "body": "первый-глубже2-глубже2", "task": 3, "answer_to": 12},
    {"id": 15, "body": "первый-глубже-глубже", "task": 3, "answer_to": 11},
    {"id": 16, "body": "первый-глубже-глубже2", "task": 3, "answer_to": 11},
    {"id": 17, "body": "aboba", "task": 3, "answer_to": None},
    {"id": 18, "body": "kiloma", "task": 3, "answer_to": None},
    {"id": 19, "body": "am'eba", "task": 3, "answer_to": None},
]

comments = {i["id"]: i for i in COMMENTS}

for comment in COMMENTS:
    if comment["answer_to"] is None:
        continue
    comments[comment["answer_to"]].setdefault("subcomments", []).append(comment)

pprint([comment for comment in comments.values() if comment["answer_to"] is None])
