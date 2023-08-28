import json
import datetime
import pickle


def add_report(nick, operation):
    data = json.load(open("reports.json", encoding='utf-8'))
    print(data)
    if not user_exists(nick):
        data[nick] = {}
        with open("reports.json", "w", encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    data = json.load(open("reports.json", encoding='utf-8'))
    data[nick][str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))] = operation
    with open("reports.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def create_user(nick):
    data = json.load(open("reports.json", encoding='utf-8'))
    data[nick] = {}
    with open("reports.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def user_exists(nick):
    data = json.load(open("reports.json", encoding='utf-8'))
    try:
        data[nick]
        return True
    except:
        return False


def get_tables():
    data = json.load(open("tables.json", encoding='utf-8'))
    return data


def take_table(table_type, table_number, user_id):
    data = json.load(open("tables.json", encoding='utf-8'))
    data[table_type][table_number]['croupier'] = user_id
    with open("tables.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def save_session(crouier_id, session):
    data = json.load(open("logs.json", encoding='utf-8'))
    if str(crouier_id) not in data:
        data[str(crouier_id)] = []
    data[str(crouier_id)].append(session)
    with open("logs.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def vacate_table(table_type, table_number):
    data = json.load(open("tables.json", encoding='utf-8'))
    data[table_type][table_number]['current_players'] = 0
    data[table_type][table_number]['croupier'] = None
    with open("tables.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def update_statement(table_type, table_number, statement_type, statement):
    data = json.load(open("tables.json", encoding='utf-8'))
    data[table_type][table_number][statement_type] = statement
    with open("tables.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def update_table(data):
    with open("reports.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def add_free_croupier(discord_id):
    data = json.load(open("reports.json", encoding='utf-8'))
    data.append(discord_id)
    with open("reports.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_free_croupiers():
    data = json.load(open("reports.json", encoding='utf-8'))
    return data


def remove_free_croupier(discord_id):
    data = json.load(open("reports.json", encoding='utf-8'))
    data.remove(discord_id)
    with open("reports.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


