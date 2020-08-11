import schedule
import datetime
import time
import sqlite3
import speedtest
import json


def create_db_table(connection):
    cursor = connection.cursor()
    sql_query = 'CREATE TABLE IF NOT EXISTS speedhistory (record integer PRIMARY KEY AUTOINCREMENT,' \
                ' record_time TIMESTAMP, download INTEGER, upload INTEGER, latency INTEGER)'
    cursor.execute(sql_query)


def get_db_connection(dbfile):
    connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
    return connection


def speedtest_get():
    test_result = speedtest.Speedtest()
    test_result.get_servers()
    test_result.get_best_server()
    test_result.download()
    test_result.upload()
    return test_result.results


def speedtest_to_db(st_results, connection):
    timestamp = datetime.datetime.now()
    st_download = int(st_results.download)
    st_upload = int(st_results.upload)
    st_ping = int(st_results.ping)
    cursor = connection.cursor()
    sql_query = "INSERT INTO speedhistory VALUES (NULL, ?, ?, ?, ?)"
    sql_params = timestamp, st_download, st_upload, st_ping
    cursor.execute(sql_query, sql_params)
    connection.commit()


def speedtest_hourly(connection):
    speedtest_results = speedtest_get()
    speedtest_to_db(speedtest_results, connection)

    time_delta = (datetime.datetime.now()) - (datetime.timedelta(days=1))
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM speedhistory WHERE record_time > ?", (time_delta,))
    results = cursor.fetchall()

    def get_average(position):
        number_list = []
        for row in results:
            number_list.append(row[position])
        average = sum(number_list) / len(number_list)
        return average

    def bits_to_megabits(value):
        return value / 1048576

    download_average = round(bits_to_megabits(get_average(2)), 2)
    upload_average = round(bits_to_megabits(get_average(3)), 2)
    latency_average = round(get_average(4), 2)

    speedtest_json = {'24_hour_average': []}
    speedtest_json['24_hour_average'].append(
        {'download': download_average,
         'upload': upload_average,
         'latency': latency_average
         }
    )
    json_file = open(speedtest_output, 'w+')
    json.dump(speedtest_json, json_file)
    json_file.close()


db_file = "/db/speedtest.db"
web_dir = "/usr/share/nginx/html/"
speedtest_output = web_dir + "speedtest.json"

db_connection = get_db_connection(db_file)
create_db_table(db_connection)
db_connection.close()


def speedtest_hourly_control():
    connection = get_db_connection(db_file)
    speedtest_hourly(connection)
    connection.close()


schedule.every().hour.do(speedtest_hourly_control())
while True:
    schedule.run_pending()
    time.sleep(1)
