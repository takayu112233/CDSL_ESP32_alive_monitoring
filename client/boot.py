import config

def do_connect(wifi_config):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)

        scandata = sta_if.scan() 

        for scan in scandata:
            for config in wifi_config:
                if(scan[0].decode() == config[0]):
                    sta_if.connect(config[0], config[1])

        while not sta_if.isconnected():
            pass
    print('connected: ' , sta_if.config('essid'))
    print('network config:' , sta_if.ifconfig())
    return sta_if

if __name__ == "__main__":
    print("power on:" + config.NAME)
    wifi = do_connect(config.WIFI_CONFIG)
    execfile("do.py")
    

