import schedule
import sqlite3
import requests
import datetime
import time
import tweepy
import os
import json


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
    try:
        check_status = requests.get(url)
    except Exception as e:
        print(e)
        return 1
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
        return [0, 0, 0]
    elif current_status == 1:
        outage_start = datetime.datetime.now()
        outage_end = ""
        print("{0} -- Possible outage detected.  Entering grace period".format(datetime.datetime.now()))
        time.sleep(10)
        current_status = check_internal_up(url)
        if current_status == 0:
            print("{0} -- Recovered in grace period".format(datetime.datetime.now()))
            return [0, 0, 0]
        elif current_status == 1:
            print("{0} -- Outage confirmed.  Beginning timer".format(datetime.datetime.now()))
            while current_status != 0:
                outage_end = datetime.datetime.now()
                current_status = check_internal_up(url)
                time.sleep(2)
            print("{0} -- Outage over".format(datetime.datetime.now()))
            # At this point an outage event has ended and we have start and end time
            return [1, outage_start, outage_end]


def time_delta(time_start, time_end):
    time_delta_hours = 0
    time_delta_minutes = 0
    time_delta_seconds = 0
    time_delta_record = time_end - time_start
    while time_delta_record.total_seconds() >= 3600:
        time_delta_hours += 1
        time_delta_record = time_delta_record - datetime.timedelta(hours=1)
    while time_delta_record.total_seconds() >= 60:
        time_delta_minutes += 1
        time_delta_record = time_delta_record - datetime.timedelta(minutes=1)
    while time_delta_record.total_seconds() > 0:
        time_delta_seconds += 1
        time_delta_record = time_delta_record - datetime.timedelta(seconds=10)
    return_string = ""
    if time_delta_hours >= 1:
        return_string = return_string + "{0} Hours ".format(time_delta_hours)
    if time_delta_minutes >= 1:
        return_string = return_string + "{0} Minutes ".format(time_delta_minutes)
    if time_delta_seconds >= 1:
        return_string = return_string + "{0} Seconds".format(time_delta_seconds)
    return return_string


def twitter_post(tweet_string):
    twitter_auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
    twitter_auth.set_access_token(twitter_access_token, twitter_access_secret)
    twitter_api = tweepy.API(twitter_auth)
    twitter_api.update_status(status=tweet_string)


def twitter_post_outage(outage_start, outage_end, time_delta_string):
    tweet_string = "Internet service was down for {0} between {1} and {2}. {3} {4} ".format(time_delta_string,
                                                                                            outage_start, outage_end,
                                                                                            twitter_target_accounts,
                                                                                            twitter_target_hashtags)
    print("Sending out the following tweet:")
    print(tweet_string)
    twitter_post(tweet_string)


def get_outage_24h():
    connection = get_db_connection(db_file)
    cursor = connection.cursor()
    yesterday = (datetime.datetime.now()) - (datetime.timedelta(days=1))
    sql_query = "SELECT outage_start FROM outagehistory WHERE outage_start > ?", (yesterday,)
    cursor.execute(sql_query)
    outage_count = len(cursor.fetchall())
    connection.close()
    return outage_count


def get_speed_24h():
    speedtest_json = json.loads(requests.get(monitor_url_speedtest).text)
    download = speedtest_json["24_hour_average"][0]["download"]
    upload = speedtest_json["24_hour_average"][0]["upload"]
    latency = speedtest_json["24_hour_average"][0]["latency"]
    return [download, upload, latency]


def create_daily_outage_tweet(outage_count):
    yesterday_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%B %d, %Y")
    tweet_string = "There have been {0} recorded outages since {1}. {2} {3}".format(outage_count, yesterday_date,
                                                                                    twitter_target_accounts,
                                                                                    twitter_target_hashtags)
    print("Sending out the following tweet:")
    print(tweet_string)
    twitter_post(tweet_string)


def create_daily_speedtest_tweet():
    speedtest_values = get_speed_24h()
    tweet_string = """Speedtest average over last 24H:
    DL - {0}
    UL - {1}
    Lat - {2}""".format(speedtest_values[0], speedtest_values[1], speedtest_values[2])
    print("Sending out the following tweet:")
    print(tweet_string)
    twitter_post(tweet_string)


def twitter_post_daily():
    outage_count = get_outage_24h()
    if outage_count >= 1:
        create_daily_outage_tweet(outage_count)
    create_daily_speedtest_tweet()


def monitor():
    current_status = check_internal_control(monitor_url)
    if current_status[0] == 1:
        outage_start = current_status[1]
        outage_end = current_status[2]

        outage_start_string = outage_start.strftime("%H:%M:%S")
        outage_end_string = outage_end.strftime("%H:%M:%S")

        outage_to_db(outage_start, outage_end)
        time_delta_string = time_delta(outage_start, outage_end)

        twitter_post_outage(outage_start_string, outage_end_string, time_delta_string)


monitor_url = os.environ.get('MONITOR_URL')
monitor_url_speedtest = monitor_url + "/speedtest.json"
twitter_api_key = os.environ.get('TWITTER_API_KEY')
twitter_api_secret = os.environ.get('TWITTER_API_SECRET')
twitter_access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
twitter_access_secret = os.environ.get('TWITTER_ACCESS_SECRET')
twitter_target_accounts = os.environ.get('TWITTER_TARGET_ACCOUNTS')
twitter_target_hashtags = os.environ.get('TWITTER_TARGET_HASHTAGS')
db_file = "/db/outagerecords.db"
web_dir = "/usr/share/nginx/html/"

db_connection = get_db_connection(db_file)
create_db_table(db_connection)
db_connection.close()

schedule.every().day.at("12:00").do(twitter_post_daily)
while True:
    monitor()
    schedule.run_pending()
    time.sleep(10)
