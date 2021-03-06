#!/usr/bin/env python

import argparse
import dateutil.parser
import json
import requests
import threading
import time
import websocket
import db

global_things = {
    'API_URL'   : None,
    'WS_URL'    : None,
    'TEAMNAME'  : None,
    'TEAMAUTH'  : None,
    'LASTTIME'  : None,
}

def activate_shield(turn_shield_on):
    url  = "{base}/shield/{toggle}".format(base=global_things['API_URL'], toggle='enable' if turn_shield_on else 'disable')
    auth = {'X-Auth-Token': global_things['TEAMAUTH']}
    response = requests.post(url, headers=auth)

    if response.status_code == 200:
        if turn_shield_on:
            log("Enabled shield")
            print("Enabled shield!")
        else:
            log("Disabled shield")
            print("Disabled shield.")
    elif response.status_code == 400:
        if turn_shield_on:
            log("Could not enable shield.")
            raise RuntimeError("Could not enable shield.")
        else:
            log("Could not disable shield.")
            raise RuntimeError("Could not disable shield.")
    else:
        log("Error during shield toggling")
        raise RuntimeError("Error during shield toggling.")

def register_team():
    log("TEAMNAME: {}".format(global_things['TEAMNAME']))
    print("TEAMNAME: {}".format(global_things['TEAMNAME']))
    response = requests.post(global_things['API_URL'] + '/join/' + global_things['TEAMNAME'], data='')
    global_things['TEAMAUTH'] = response.text

    if response.status_code == 200:
        log("Joined the game. Auth code: {}".format(global_things['TEAMAUTH']))
        print("Joined the game. Auth code: {}".format(global_things['TEAMAUTH']))
    elif response.status_code == 400:
        log({"Team already exists"})
        raise RuntimeError("Team already exists.")
    else:
        log("Error during team registration")
        raise RuntimeError("Error during team registration.")

def get_team_info(info):
    for team in info['teams']:
        if team['name'] == global_things['TEAMNAME']:
            return team
    return None

def display_info(info):
    team_info = get_team_info(info)
    if team_info is None:
        return
    msg = "{}  Life: {:<3}%  Energy: {:<3}%  Shield: {}".format(
        info['timestamp'],
        team_info['life'],
        team_info['energy'],
        'on' if team_info['shield'] else 'off')

    log(msg)
    print(msg)

def log(data):
    db.log_insert({"time": time.time(), "message": data})

def write_data_to_log(data):
    # Log to system
    db.game_insert(data)

def build_log_data(info):
    result = {}
    result['timestamp']     = info['timestamp']
    result['solarFlare']    = info['readings']['solarFlare']
    result['temperature']   = info['readings']['temperature']
    result['radiation']     = info['readings']['radiation']
    return result

def strategize(shields_on, timestamp):
    log("Shields are currently: {}".format('on' if shields_on else 'off'))
    print("Shields are currently: {}".format('on' if shields_on else 'off'))
    lasttime = global_things['LASTTIME']
    if lasttime is None:
        global_things['LASTTIME'] = timestamp
    else:
        if (timestamp - lasttime).total_seconds() > 10:
            activate_shield(not shields_on)
            global_things['LASTTIME'] = timestamp

def receive_message(ws, message):
    data      = json.loads(message)
    log_data  = build_log_data(data)
    write_data_to_log(log_data)
    display_info(data)
    ts = threading.Thread(target=strategize, args=[get_team_info(data)['shield'], dateutil.parser.parse(data['timestamp'])])
    ts.start()

def receive_error(ws, error):
    log("Error: {}".format(error))
    print("Error: {}".format(error))

def connection_closed(ws):
    log("Connection closed.")
    print("Connection closed.")

def open_connection(ws):
    def run():
        ws.close()
    threading.Thread(target=run)

def main(api_url, ws_url, teamname):
    global_things['API_URL']  = api_url
    global_things['WS_URL']   = ws_url
    global_things['TEAMNAME'] = teamname

    log("API Url:  {}".format(global_things['API_URL']))
    log("WS Url:   {}".format(global_things['WS_URL']))
    log("Teamname: {}".format(global_things['TEAMNAME']))
    print("API Url:  {}".format(global_things['API_URL']))
    print("WS Url:   {}".format(global_things['WS_URL']))
    print("Teamname: {}".format(global_things['TEAMNAME']))

    register_team()

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        global_things['WS_URL'],
        on_message = receive_message,
        on_error   = receive_error,
        on_close   = connection_closed
    )
    ws.on_open = open_connection
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        log("Terminating")
        print("Terminating")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('api_url', help="URL to the game controller API")
    parser.add_argument('ws_url', help="URL to the game controller websocket")
    parser.add_argument('teamname', help="The name of your team")
    args = parser.parse_args()

    main(args.api_url, args.ws_url, args.teamname)
