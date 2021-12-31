# pip3 install paho-mqtt
from threading import local
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

topics = ("s/ping","s/join","s/disconnect","s/return_bt","s/return_ping")

broker = '192.168.0.250'
port = 1883

ping = {}
disconnect_time = {}

version = "1.2.0"

class Client:
    def __init__(self,global_ip,local_ip,name,bt_mac,wifi_mac,heart_beat_time,keep_alive_time,version) :
        self.global_ip = global_ip
        self.local_ip = local_ip
        self.name = name
        self.bt_mac = bt_mac
        self.wifi_mac = wifi_mac
        self.heart_beat_time = heart_beat_time
        self.keep_alive_time = keep_alive_time
        self.version = version

        global_ip_cnt_add(global_ip)

        self.status = 0
        self.lasttime = time.time()

        self.ping_result = {}
        self.bt_result = {}
        self.ping_result["ok"] = 0
        self.ping_result["ng"] = 0
        self.bt_result["ok"] = 0
        self.bt_result["ng"] = 0

        print_log("[join] <wifi_mac> " + self.wifi_mac + " <name> " + self.name)

    def receive_ping(self):
        """
        Pingを受け取った際に時間を最新にする関数
        """
        if(not self.status == 0):
            global_ip_cnt_add(self.global_ip)
        self.lasttime = time.time()
        self.status = 0
        #print_log("[ping] <wifi_mac> " + self.wifi_mac + " <name> " + self.name)

def global_ip_cnt_add(global_ip):
    """
    グローバルIP毎の接続数に追加する
    """
    if(global_ip_cnt.get(global_ip) == None):
        global_ip_cnt[global_ip] = 1
    else:
        global_ip_cnt[global_ip] += 1 

def global_ip_cnt_remove(global_ip):
    """
    グローバルIP毎の接続数から削除する
    """
    global_ip_cnt[global_ip] -= 1
    if(global_ip_cnt[global_ip] <= 0):
        del global_ip_cnt[global_ip]

def connect_mqtt():
    """
    MQTTブローカサーバに接続
    """
    client = mqtt_client.Client("server1")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.connect(broker, port)
    return client

def on_connect(client, userdata, flags, rc):
    """
    MQTTブローカーサーバにした場合の処理
    """
    global connect
    if rc == 0:
        print_log("[system] MQTT_SERVER_Connected")
        connect = True
    else:
        print_log("[system] MQTT_SERVER_ERR %d\n", rc)
        connect = False

def on_disconnect(client, userdata, rc):
    """
    MQTTブローカーサーバから切断された場合の処理
    """
    global connect
    print_log("[system] MQTT_SERVER_DisConnected")
    connect = False

def on_publish(client, userdata, msg):
    """
    MQTTブローカーサーバにメッセージを送信した時の処理
    """
    print_log("[system] MQTT_PUBLISH")

def subscribe(client):
    """
    MQTTサブスクライブトピックの設定
    """
    for topic in topics:
        print_log("[system] subtopic: " + topic)
        client.subscribe(topic)
    client.on_message = on_message

def publish(topic,msg):
    """
    MQTTメッセージの送信処理
    """
    print_log("[system] publish: <topic>" + topic + " <msg>" + msg)
    client.publish(topic,msg)
    

def on_message(client, userdata, msg):
    """
    MQTTメッセージの受信した際の処理
    """
    topic_data = msg.topic.split("/")
    if(topic_data[1] == "join"):
        client_data_list = json.loads(msg.payload.decode())

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

        if(client_data.get(client_data_list["wifi_mac"]) == None):
            print_log("[system] 接続処理未実行 wifimac: " + client_data_list["wifi_mac"])
            topic = "c/" + client_data_list["wifi_mac"] + "/want_join"
            msg = client_data_list["wifi_mac"]
            publish(topic , msg)
        else:
            client_data[client_data_list["wifi_mac"]].receive_ping()

    if(topic_data[1] == "return_bt"):
        return_bt_data_list = json.loads(msg.payload.decode())
        wifi_mac = return_bt_data_list["wifi_mac"]
        if return_bt_data_list["result"] == "ok":
            client_data[return_bt_data_list["wifi_mac"]].bt_result["ok"] += 1
        if return_bt_data_list["result"] == "ng":
            client_data[wifi_mac].bt_result["ng"] += 1
        print_log("[system] return_bt" + wifi_mac + " <ng>" + str(client_data[wifi_mac].bt_result["ng"]) + " <ok>" + str(client_data[wifi_mac].bt_result["ok"]))

    if(topic_data[1] == "return_ping"):
        return_ping_data_list = json.loads(msg.payload.decode())
        wifi_mac = return_ping_data_list["wifi_mac"]
        if return_ping_data_list["result"] == "ok":
            client_data[wifi_mac].ping_result["ok"] += 1
        if return_ping_data_list["result"] == "ng":
            client_data[wifi_mac].ping_result["ng"] += 1
        print_log("[system] return_ping" + wifi_mac + " <ng>" + str(client_data[wifi_mac].ping_result["ng"]) + " <ok>" + str(client_data[wifi_mac].ping_result["ok"]))



def want_ping_and_bt(global_ip,bt_mac,wifi_mac,local_ip):
    topic = "c/" + global_ip + "/want_ping"
    msg = local_ip + "," + wifi_mac
    publish(topic , msg)

    topic = "c/" + global_ip + "/search_bt"
    msg = bt_mac + "," + wifi_mac
    publish(topic , msg)

def check_time(client_data):
    now_time = time.time()
    for i in client_data:
        if client_data[i].heart_beat_time * 1.5 - (now_time - client_data[i].lasttime) <= 0 and client_data[i].status == 0:
            client_data[i].status = -1 #warning
            global_ip_cnt_remove(client_data[i].global_ip)
            client_data[i].ping_result = {}
            client_data[i].bt_result = {}
            client_data[i].ping_result["ok"] = 0
            client_data[i].ping_result["ng"] = 0
            client_data[i].bt_result["ok"] = 0
            client_data[i].bt_result["ng"] = 0
            print_log("[warning] <wifi_mac> " + client_data[i].wifi_mac + "  <msg> HeartBeat timeout")
            want_ping_and_bt(client_data[i].global_ip, client_data[i].bt_mac, client_data[i].wifi_mac, client_data[i].local_ip)        
    
    del_client = []
    for i in client_data:
        if client_data[i].keep_alive_time * 1.5 - (now_time - client_data[i].lasttime) <= 0 and not client_data[i].status != -1:
            print_log("[disconnect] <wifi_mac> " + client_data[i].wifi_mac + "  <msg> KeepAliveTime timeout")
            del_client.append(i)

    for key in del_client:
        del client_data[key]
    
def check_connection(client_data,global_ip_cnt):
    """
    ここで切断可能IoT端末を切断する
    """
    del_client = []

    for wifi_mac in client_data:
        if(client_data[wifi_mac].status == -1):
            if(not client_data[wifi_mac].ping_result["ok"] == 0):
                print_log("[system] " +  client_data[wifi_mac].name + "のPINGを他の機器が受信,ソフトウェアに異常発生の可能性")
                client_data[wifi_mac].status = -2
                break

            if(not client_data[wifi_mac].bt_result["ok"] == 0):
                print_log("[system] " +  client_data[wifi_mac].name + "のBT電波を他の機器が受信,ネットワークに異常発生の可能性")
                client_data[wifi_mac].status = -2
                break

            global_ip_data = client_data[wifi_mac].global_ip
            if not global_ip_cnt.get(global_ip_data) == None:
                global_ip_cnt_data = global_ip_cnt[global_ip_data]
                if(client_data[wifi_mac].bt_result["ng"] >= global_ip_cnt_data and client_data[wifi_mac].ping_result["ng"] >= global_ip_cnt_data):
                    print_log("[system] " +  client_data[wifi_mac].name + "同一セグメント上のIoT機器がBTとPINGを受信できません，電源遮断の可能性 切断処理を行います．")
                    client_data[wifi_mac].status = -2
                    del_client.append(wifi_mac)
                    break
            else:
                print_log("[system] " +  client_data[wifi_mac].name + "と通信が可能な機器がありません ネットワークに異常がある可能性があります，タイムアウトまで待機")
                client_data[wifi_mac].status = -2

    
    for key in del_client:
        print_log("[disconnect] <wifi_mac> " + client_data[key].wifi_mac + "  <msg> --")
        del client_data[key]
                


def print_log(data):
    dt_now = datetime.datetime.now()
    print("[" + dt_now.strftime('%Y-%m-%d %H:%M:%S') + "] " + str(data))


if __name__ == "__main__":
    print("[version] " + version)

    client_data = {} # IoT機器のデータを入れるDictionary
    global_ip_cnt = {} # グローバルIP毎の接続台数を入れるDictionary(warningは入れず)

    client = connect_mqtt()
    subscribe(client)

    cnt = 0
    connect = False
    client.loop_start()

    while True:
        if(connect):
            time.sleep(1)
            check_time(client_data)
            check_connection(client_data,global_ip_cnt)
            #print(global_ip_cnt)
        else:
            pass
    
    
