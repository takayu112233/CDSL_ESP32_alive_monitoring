# pip3 install paho-mqtt
from paho.mqtt import client as mqtt_client
import time
import datetime
import os
import json
import time

dt_now = datetime.datetime.now()
dir = "./data"
if not os.path.exists(dir):
    os.makedirs(dir)
out_file_path = dir + "/" + dt_now.strftime('%Y%m%d_%H%M%S') + ".csv"
with open(out_file_path, mode='w') as f:
    f.write("time,key,keepalivetime,killtime,disconnecttime,disconnect_system,delay\n")

topics = ("s/ping","s/join","s/disconnect")

broker = '192.168.0.250'
port = 1883

ping = {}
disconnect_time = {}

def connect_mqtt():
    """
    MQTTブローカサーバに接続
    """
    client = mqtt_client.Client("server1")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)
    return client

def on_connect(client, userdata, flags, rc):
    """
    MQTTブローカーサーバにした場合の処理
    """
    global connect
    if rc == 0:
        print_log("MQTT_SERVER_Connected")
        connect = True
    else:
        print_log("MQTT_SERVER_ERR %d\n", rc)
        connect = False

def on_disconnect(client, userdata, rc):
    """
    MQTTブローカーサーバから切断された場合の処理
    """
    global connect
    print_log("MQTT_SERVER_DisConnected")
    connect = False

def subscribe(client):
    """
    MQTTサブスクライブトピックの設定
    """
    for topic in topics:
        print_log("subtopic: " + topic)
        client.subscribe(topic)
    client.on_message = on_message

def on_message(client, userdata, msg):
    """
    MQTTメッセージの受信した際の処理
    """
    #print_log(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    topic_data = msg.topic.split("/")
    if(topic_data[1] == "join"):
        client_data_list = json.loads(msg.payload.decode())
        #print_log(client_data_list)

        global_ip = client_data_list["global_ip"]
        local_ip = client_data_list["local_ip"]
        name = client_data_list["name"]
        bt_mac = client_data_list["bt_mac"]
        wifi_mac = client_data_list["wifi_mac"]
        heart_beat_time = int(client_data_list["heart_beat_time"])
        keep_alive_time = int(client_data_list["keep_alive_time"])
        version = client_data_list["version"]

        client_data[client_data_list["wifi_mac"]] = Client(global_ip,local_ip,name,bt_mac,wifi_mac,heart_beat_time,keep_alive_time,version)
    
    if(topic_data[1] == "ping"):
        client_data_list = json.loads(msg.payload.decode())
        client_data[client_data_list["wifi_mac"]].receive_ping()


class Client:
    count = 0

    @classmethod
    def get_count(cls):
        return cls.count
    
    def __init__(self,global_ip,local_ip,name,bt_mac,wifi_mac,heart_beat_time,keep_alive_time,version) :
        self.global_ip = global_ip
        self.local_ip = local_ip
        self.name = name
        self.bt_mac = bt_mac
        self.wifi_mac = wifi_mac
        self.heart_beat_time = heart_beat_time
        self.keep_alive_time = keep_alive_time
        self.version = version

        self.status = 0
        self.lasttime = time.time()

        print_log("[join] <wifi_mac> " + self.wifi_mac + " <name> " + self.name)

    def receive_ping(self):
        self.lasttime = time.time()
        self.status = 0
        print_log("[ping] <wifi_mac> " + self.wifi_mac + " <name> " + self.name)

def check_time(client_data):
    now_time = time.time()
    for i in client_data:
        if client_data[i].heart_beat_time * 1.5 - (now_time - client_data[i].lasttime) <= 0 and client_data[i].status == 0:
            client_data[i].status = -1
            print_log("[warning] <wifi_mac> " + client_data[i].wifi_mac + "  <msg> HeartBeat timeout")
    
    del_client = []
    for i in client_data:
        if client_data[i].keep_alive_time * 1.5 - (now_time - client_data[i].lasttime) <= 0 and client_data[i].status == -1:
            print_log("[disconnect] <wifi_mac> " + client_data[i].wifi_mac + "  <msg> KeepAliveTime timeout")
            del_client.append(i)

    for key in del_client:
        del client_data[key]
    
    print_log("[system] connect_count: " + str(len(client_data)))

def print_log(data):
    dt_now = datetime.datetime.now()
    print("[" + dt_now.strftime('%Y-%m-%d %H:%M:%S') + "] " + str(data))


if __name__ == "__main__":

    client_data = {}

    client = connect_mqtt()
    subscribe(client)

    cnt = 0
    connect = False
    client.loop_start()

    while True:
        if(connect):
            time.sleep(1)
            check_time(client_data)
    else:
        pass
    
    
