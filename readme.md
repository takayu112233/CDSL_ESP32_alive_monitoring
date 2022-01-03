# このレポジトリについて
創成課題用プログラム管理用です．

# レポジトリの構成について
* client
ESP32で使用するプログラムです
* server
監視サーバで使用するプログラムです

# 監視に使用するMQTT　トピック名一覧

## subscribeトピック

### c/all/#
全てのIoT機器

### s/all/#
すべてのServer

### c/[グローバルIP]/#
監視サーバ → 指定したセグメントの全てのIoT機器

## 制御用

### s/join
IoT機器 → 監視サーバ   
接続した際に送る   
メッセージ形式 JSON   

### s/disconnect
対応機器 → 監視サーバ   
切断際に送る   
サーバーは対象機器を切断する   
メッセージ形式 JSON   

### c/[グローバルIP]/search_bt
監視サーバ → 指定したセグメントの全てのIoT機器   
Bluetooth電波のスキャンをIoT機器に要求   
メッセージ形式 [求めるbtmacアドレス],[管理用wifimacアドレス]   

### s/return_bt
IoT機器 → 監視サーバ   
スキャン内容をサーバに送信   
メッセージ形式 JSON   

### c/[global_ip]/want_ping
監視サーバ → 特定のIoT機器（1台）   
PING応答の確認をIoT機器に要求   
メッセージ形式 [求めるローカルIPアドレス],[管理用wifimacアドレス]   

### s/return_ping
IoT機器 → 監視サーバ   
PING応答の有無をサーバに送信   
メッセージ形式 JSON   

### s/ping
監視機器 → 監視サーバ   
HeartBeatやKeepAlivePacketの送信   
メッセージ形式 [wifimacアドレス]   

### c/[wifimac]/wont_join
監視サーバ → 特定のIoT機器（1台）   
IoT機器に対してs/joinパケットを要求   
メッセージ なし   
