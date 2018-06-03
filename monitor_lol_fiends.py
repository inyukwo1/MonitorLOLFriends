import requests
import json
import datetime
import time
import smtplib
import argparse
from email.mime.text import MIMEText

PIVOT_TIME = datetime.datetime(2018, 6, 3, hour=18, minute=0, second=0)
API_KEY="RGAPI-e5d89e0f-a145-41a8-9acf-3a4bb6e9cdf3"
FRIENDS=["매일 슬퍼요", "분명히아침이었어", "요퍼슬 일매", "이거만 끝내고"]
GMAIL_ID=""
GMAIL_PASSWORD=""
TARGET_EMAIL=""


def send_api_with_key(api):
    return requests.get(api, params={'api_key': API_KEY})


def parse_http_res(res):
    string_res_content = res.content.decode('utf-8')
    json_res_content = json.loads(string_res_content)
    return json_res_content


def get_summoners_by_name(name):
    api_url = "https://kr.api.riotgames.com/lol/summoner/v3/summoners/by-name/"
    return send_api_with_key(api_url + name)


def get_accountid_by_name(name):
    res = get_summoners_by_name(name)
    parsed_res = parse_http_res(res)
    return parsed_res['accountId']


def get_match_by_accountid(accountid):
    api_url = "https://kr.api.riotgames.com/lol/match/v3/matchlists/by-account/"
    return send_api_with_key(api_url + str(accountid))


def get_latest_matchtime_by_accoundid(accoundid):
    res = parse_http_res(get_match_by_accountid(accoundid))
    latest_match = res['matches'][0]
    latest_timestamp = latest_match['timestamp']
    return datetime.datetime.fromtimestamp(latest_timestamp / 1000.0)


def get_latest_matchtime_by_name(name):
    accountid = get_accountid_by_name(name)
    return get_latest_matchtime_by_accoundid(accountid)


def send_message(subject, content):
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp.login(GMAIL_ID, GMAIL_PASSWORD)

    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['To'] = TARGET_EMAIL
    smtp.sendmail(GMAIL_ID, TARGET_EMAIL, msg.as_string())

    smtp.quit()


def main():
    while(True):
        for name in FRIENDS:
            latest_matchtime = get_latest_matchtime_by_name(name)
            if latest_matchtime > PIVOT_TIME:
                message= "name: " + name + " played game at " + str(latest_matchtime)
                send_message("임현호 게임함", message)
                print(message)
        print("current time: " + str(datetime.datetime.now()) + ", check succeed!")
        time.sleep(60 * 60) # 1 hour


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gmail_id", help="gmail id for log in")
    parser.add_argument("--gmail_password", help="gmail password for log in")
    parser.add_argument("--target_email", help="email id for send mail")
    args = parser.parse_args()
    GMAIL_ID = args.gmail_id
    GMAIL_PASSWORD = args.gmail_password
    TARGET_EMAIL = args.target_email
    main()