import json
import csv

JSON_FILE_PATH = "users.json"
CSV_FILE_PATH = "books.csv"
RESULT_FILE_PATH = "result.json"

with open(JSON_FILE_PATH, "r") as f:
    users_list = json.load(f)

for user in users_list:
    user["books"] = []

with open(CSV_FILE_PATH, "r") as f:
    books_reader = csv.DictReader(f)
    books_list = list(books_reader)

user_count = len(users_list)

i = 0
for book in books_list:
    users_list[i]["books"].append(book)
    i = (i + 1) % user_count

result = []
for user in users_list:
    filtered_user = {
        "name": user["name"],
        "gender": user["gender"],
        "address": user["address"],
        "age": user["age"],
        "books": []
    }

for book in user["books"]:
    filtered_book = {
        "title": book["Title"],
        "author": book["Author"],
        "pages": int(book["Pages"]),  # Если pages — число, приведём к int
        "genre": book["Genre"]
    }
    filtered_user["books"].append(filtered_book)

result.append(filtered_user)

with open(RESULT_FILE_PATH, "w") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

print(f"Ready {RESULT_FILE_PATH}")