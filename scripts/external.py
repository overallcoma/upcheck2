import schedule
import sqlite3
import requests
import datetime
import time


def get_db_connection(dbfile):
    connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
    return connection


def create_db_table(connection):
    cursor = connection.cursor()
    sql_query = 'CREATE TABLE IF NOT EXISTS outagehistory (record integer PRIMARY KEY AUTOINCREMENT,' \
                ' outage_start TIMESTAMP, outage_end TIMESTAMP)'
    cursor.execute(sql_query)


def outage_to_db(outage_start, outage_end):
    connection = get_db_connection(db_file)
    cursor = connection.cursor()
    sql_query = "INSERT INTO outagehistory VALUES (NULL, ?, ?)"
    sql_params = outage_start, outage_end
    cursor.execute(sql_query, sql_params)
    connection.commit()
    connection.close()


def check_internal_up(url):
    check_status = requests.get(url)
    try:
        if check_status.status_code == 200:
            return 0
        else:
            return 1
    except Exception as e:
        print(e)
        return 2


def check_internal_control(url):
    current_status = check_internal_up(url)
    if current_status == 0:
        return 0
    elif current_status == 1:
        outage_start = datetime.datetime.now()
        outage_end = ""
        print("{0} -- Possible outage detected.  Entering grace period".format(datetime.datetime.now()))
        time.sleep(10)
        current_status = check_internal_up(url)
        if current_status == 0:
            print("{0} -- Recovered in grace period")
            return 0
        elif current_status == 1:
            print("{0} -- Outage confirmed.  Beginning timer")
            while current_status != 0:
                outage_end = datetime.datetime.now()
                current_status = check_internal_up(url)
            print("{0} -- Outage over".format(datetime.datetime.now()))

            # At this point an outage event has ended and we have start and end time

            time_delta_string = time_delta(outage_start, outage_end)
            outage_to_db(outage_start, outage_end)

            



def time_delta(time_start, time_end):
    time_delta_hours = 0
    time_delta_minutes = 0
    time_delta_seconds = 0
    time_delta_record = time_end - time_start
    while time_delta_record.total_seconds() >= 3600:
        time_delta_hours += 1
        time_delta_record = time_delta_record - 3600
    while time_delta_record.total_seconds() >= 60:
        time_delta_minutes += 1
        time_delta_record = time_delta_record - 60
    while time_delta_record.total_seconds() > 0:
        time_delta_seconds += 1
        time_delta_record = time_delta_record - 1
    return_string = ""
    if time_delta_hours >= 1:
        return_string = return_string + "{0} Hours ".format(time_delta_hours)
    if time_delta_minutes >= 1:
        return_string = return_string + "{0} Minutes ".format(time_delta_minutes)
    if time_delta_seconds >= 1:
        return_string = return_string + "{0} Seconds".format(time_delta_seconds)
    return return_string


def get_outage_24h():
    print("blah")


def get_speed_24h():
    print("blah")


def twitter_post_outage():
    print("blah")


def twitter_post_daily():
    print("blah")


def twitter_compose_message():
    print("blah")


db_file = "/db/outagerecords.db"
web_dir = "/usr/share/nginx/html/"
