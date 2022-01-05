from umqtt.simple import MQTTClient
import time
import machine
import gc
import ubluetooth
import ubinascii
import ujson
import urequests
import uping
import ubluetooth
import config
import machine
import os

<<<<<<< HEAD
VERSION = "1.3.1_e2"
=======
VERSION = "1.5.1_e"
>>>>>>> experiment_information

HEART_BEAT_TIME = 5 #[s]
KEEP_ALIVE_TIME = 60 #[s]

BROKER_SERVER = "192.168.0.250"

DISCONNECT_TIME_LIMIT = 121 #[s] -1で試験用プログラムを実施しない

NAME = config.NAME

if not 'broker_server' in locals():
    broker_server = BROKER_SERVER

def get_wifi_mac(wifi):
    """
    Wi-FiのMacアドレスを取得する関数
    """
    wifi_mac = ubinascii.hexlify(wifi.config('mac'),':').decode()
    print("[wifi_mac] : " + wifi_mac)
    return wifi_mac

def get_bt_mac(ble):
    """
    Wi-FiのMacアドレスを取得する関数
    """
    ble.active(True)
    bt_mac = ubinascii.hexlify((ble.config("mac")[1]),':').decode()
    print("[bt_mac] : " + bt_mac)
    return bt_mac

def get_global_ip():
    """
    Wi-FiのグローバルIPを返却する関数
    ESP32自身で取得できない為，Webサーバを使用
    """
    url = "https://cdsl.nosuke.net/return_global_ip/"
    res = urequests.get(url)
    global_ip = res.text
    print("[global_ip]: " + global_ip)
    return global_ip

def get_local_ip(wifi):
    """
    ローカルIPを返却するIP
    """
    local_ip = wifi.ifconfig()[0]
    print("[local_ip] : " + local_ip)
    return local_ip
    
def garbage_collection():
    """
    ガベージコレクションを実行
    """
    gc.collect()

def sub_cb(topic, msg):
    """
    メッセージを受信した時に呼ぶ用の関数
    """
    global icmp_check
    global mqtt_client
    global global_ip
    global search_list
    global wifi

    topic = str(topic, 'UTF-8')
    msg = str(msg, 'UTF-8')
    print("[sub] topic: " + topic + "  msg: " + msg)

    topic = topic.split("/")

    if(len(topic) == 3):
        if(topic[2] == "want_join"):
            send_join_packet(NAME,VERSION,wifi_mac,bt_mac,global_ip,local_ip,mqtt_client,KEEP_ALIVE_TIME,HEART_BEAT_TIME)

        if(topic[2] == "want_prog_suicide"):
            bt_send_start(ble)
            tim.deinit() 
            data = 1/0

        if(topic[2] == "want_net_suicide"):
            bt_send_start(ble)
            wifi.disconnect()

        elif(topic[2] == "want_ping"):
            data = msg.split(",")
            result = icmp_check(data[0])
            dic = {"global_ip":global_ip,"want_ip":data[0],"wifi_mac":data[1],"result":result}
            pub("s/return_ping" , ujson.dumps(dic) , mqtt_client)

        elif(topic[2] == "search_bt"):
            global search_list
            data = msg.split(",")
            search_list[data[0]] = data[1]
            bt_scan_start()

def pub(topic , msg , mqtt_client):
    """
    メッセージをPublishする関数
    """
    mqtt_client.publish(topic, msg)
    print("[pub] topic: " + topic + "  msg: " + msg)

def server_disconnect(wifi_mac,mqtt_client):
    """
    切断し，プログラムを終了する関数
    """
    dic = {"wifi_mac":wifi_mac}
    ujson.dumps(dic)
    pub("s/disconnect", ujson.dumps(dic) ,mqtt_client)
    mqtt_client.disconnect() 

def send_die_time(wifi_mac,elapsed_time,mqtt_client):
    dic = {"wifi_mac":wifi_mac, "elapsed_time":elapsed_time}
    pub("s/die", ujson.dumps(dic), mqtt_client)

def send_join_packet(name,version,wifi_mac,bt_mac,global_ip,local_ip,mqtt_client,keep_alive_time,heart_beat_time):
    """
    サーバに接続を通知する関数
    """
    dic = {"name":name, "version":version, "wifi_mac":wifi_mac, "bt_mac":bt_mac, "local_ip":local_ip ,"global_ip":global_ip ,"keep_alive_time":keep_alive_time ,"heart_beat_time":heart_beat_time}
    pub("s/join", ujson.dumps(dic), mqtt_client)

def mqtt_connect(server,sub_topics,name):
    """
    MQTTブローカーサーバに接続する関数
    """
    c = MQTTClient(name, server) 
    c.connect()
    c.set_callback(sub_cb)
    for topic in sub_topics:
        print("[subscribe topic] : " + topic)
        c.subscribe(b'{}'.format(topic))
    return c

def ping_timer_start(ms=5000):
    """
    ハートビート用タイマーの開始
    """
    tim = machine.Timer(3)
    tim.init(period=(ms*1000),mode=tim.PERIODIC,callback=lambda t:timer_do())
    return tim

def timer_do():
    """
    接続後1秒毎に呼ばれる関数
    """
    global ble
    bt_send_start(ble)
    send_ping()

def send_ping():
    """
    ハートビートとKeepAlivePacketの送信
    """
    global wifi_mac
    global mqtt_client
    dic = {"wifi_mac":wifi_mac}
    ujson.dumps(dic)
    pub("s/ping", ujson.dumps(dic) ,mqtt_client)
    # pingを送信する関数

def icmp_check(address):
    """
    指定されたアドレスのPINGが通るか確認する関数
    """
    ping_result = uping.ping(address, count=2, timeout=500)
    if(0 != ping_result[1]):
        print("[icmp ping] global_ip: " + address + " result: OK")
        return "ok"
    else:
        print("[icmp ping] global_ip: " + address + " result: NG")
        return "ng"

def bt_cb(event, data):
    """
    Bluetooth処理に関する呼び出し
    Bluetoothのスキャン結果の処理に使用
    """
    global scan_dict
    global search_list
    global mqtt_client
    global ble
    global bt_scan

    if event == 5:
        addr_type, addr, connectable, rssi, adv_data = data
        addr_hex = ubinascii.hexlify(addr)
        addr_list = list(str(addr_hex).replace("b'","").replace("'",""))
        
        for i in range(10,1,-2):
            addr_list.insert(i,":")
        addr_str = "".join(addr_list)
        scan_dict[addr_str] = '{}'.format(rssi)
        
    if event == 6:
        print("[ble_scan] : " + "end")
        bt_send_start(ble)
        sorted(scan_dict.items())
        for k, v in scan_dict.items():
            print(k, v)

        for search in search_list:
            if(search in scan_dict):
                dic = {"bt_mac":search,"result":"ok","wifi_mac":search_list[search]}
                pub("s/return_bt" , ujson.dumps(dic) , mqtt_client)
                print("[ble_scan] bt_mac: " + search + " result: OK")
            else:
                dic = {"bt_mac":search,"result":"ng","wifi_mac":search_list[search]}
                pub("s/return_bt" , ujson.dumps(dic) , mqtt_client)
                print("[ble_scan] bt_mac: " + search + " result: NG")
        
        search_list = {}
        bt_scan = False

search_list = {}
bt_scan = False

def bt_scan_start():
    """
    指定したBluetooth電波を検出できるかスキャン
    """
    global scan_dict
    global ble
    global bt_scan

    if(not bt_scan):
        print("[ble_scan] : " + "start")
        bt_scan = True
        scan_dict = {}
        ble.irq(bt_cb)
        ble.gap_scan(2000, 1, 1)

def bt_send_start(ble):
    """
    Bluetooth電波を発出開始する関数
    """
    ble.gap_advertise(100,b'0')
    print("[ble_send] : " + "start")

def bt_send_end(ble):
    """
    Bluetooth電波を発出停止する関数
    """
    ble.gap_advertise(None,b'0')
    print("[ble_send] : " + "stop")
    ble.active(False)

if __name__ == "__main__":
    if(not DISCONNECT_TIME_LIMIT == -1):
        if("time.txt" in os.listdir()):
            f = open('time.txt', 'r')
            disconnect_time = int(f.read())  
            f.close()

            if(disconnect_time > DISCONNECT_TIME_LIMIT):
                disconnect_time = 0

            f = open('time.txt', 'w')
            f.write(str(disconnect_time + 1))
            f.close()
        else:   
            disconnect_time = 0 
            f = open('time.txt', 'w')
            f.write(str(disconnect_time + 1))
            f.close()

        print("[system] start disconnect_time:" + str(disconnect_time)) 
    else:
        disconnect_time = -1

    garbage_collection()
    wifi_mac = get_wifi_mac(wifi)
    global_ip = get_global_ip()
    local_ip = get_local_ip(wifi)
    garbage_collection()

    ble = ubluetooth.BLE()
    ble.active(True)
    bt_send_start(ble)

    bt_mac = get_bt_mac(ble)

    sub_topics = ("c/all/#" , "c/" + global_ip + "/#" , "c/" + wifi_mac + "/#")

    print("[system] broker_server: " + broker_server)
    mqtt_client = mqtt_connect(broker_server,sub_topics,NAME)

    send_join_packet(NAME,VERSION,wifi_mac,bt_mac,global_ip,local_ip,mqtt_client,KEEP_ALIVE_TIME,HEART_BEAT_TIME)
    tim = ping_timer_start(HEART_BEAT_TIME)

    time_count = 0
    if(disconnect_time != -1):   
        while True:
            if(time_count >= disconnect_time * 10):
                tim.deinit() 
                #server_disconnect(wifi_mac,mqtt_client)
                #bt_send_end(ble)
                send_die_time(wifi_mac,disconnect_time,mqtt_client)
                sec = 15
                print("[system] " + str(sec) + "s sleep")
                machine.deepsleep(1000 * sec)
                break
            mqtt_client.check_msg()
            time.sleep(0.1)
            time_count += 1
    else:
        while True:
            mqtt_client.check_msg()
            time.sleep(0.1)
            

    
