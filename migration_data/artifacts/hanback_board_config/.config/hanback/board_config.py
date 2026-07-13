import http.server
from urllib.parse import urlparse
import subprocess as sp
import base64 as cryptogram
import time, json

passwd="soda"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        data=urlparse(self.path)

        if data.path == "/" or data.path == "/wifi_config.html" or data.path == "/board_config.html" or data.path == "/lang_config.html" or "/images/" in data.path:
            super().do_GET()
        elif data.path == "/set":
            param = data.query

            if "&" in param:
                param = param.split("&")
            else:
                param = [param]

            #*** select board type ***
            #1: PyC Basic
            #2: AIoT Home
            #3: IoT Smart Server Plus
            #4: Auto CAR
            #5: SerBot
            #6: ES-101

            model = int(param[0])

            msg=sp.check_output(["echo "+passwd+" | sudo -S bash board_config.sh "+str(model)], shell=True, universal_newlines=True)
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(msg.encode("UTF-8"))
        elif data.path == "/reboot":
            param = data.query

            if "&" in param:
                param = param.split("&")
            else:
                param = [param]

            code=cryptogram.b64decode(param[0])

            if code != b'' and time.time() - float(code) <= 5. :
                msg="Reboot now."
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(msg.encode("UTF-8"))

                sp.check_output(["echo "+passwd+" | sudo -S reboot"], shell=True)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write("Doesn't supported request.".encode("UTF-8"))
        elif data.path == "/apmode":
            try:
                param = data.query

                if "&" in param:
                    param = param.split("&")
                else:
                    param = [param]

                param={p.split("=")[0]:(p+"=").split("=")[1] for p in param}

                if 'ssid' in param and 'pw' in param:
                    if len(param['pw'])>=8:
                        result=sp.check_output(["echo "+passwd+" | sudo -S nmcli dev wifi hotspot ifname wlan0 ssid "+param['ssid']+" password \""+param['pw']+"\""], shell=True, universal_newlines=True)
                        
                        if "Error" in str(result):
                            self.send_response(500)
                            self.end_headers()
                            self.wfile.write(str(result).encode("UTF-8"))
                        else:
                            ip=sp.check_output("ifconfig wlan0 | grep 'inet' | cut -d: -f2 | awk '{print $2}'", shell=True, universal_newlines=True).replace("\n","")
                            msg="Activated AP mode to "+ip+"."

                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(msg.encode("UTF-8"))
                    else:
                        msg="Password is less than 8 characters."
                        
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(msg.encode("UTF-8"))
                else:
                    msg="Doesn't found parameters."
                        
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(msg.encode("UTF-8"))
            except:
                msg="An error occured."
                        
                self.send_response(500)
                self.end_headers()
                self.wfile.write(msg.encode("UTF-8"))
        elif data.path == "/wifimode":
            try:
                param = data.query

                if "&" in param:
                    param = param.split("&")
                else:
                    param = [param]

                param={p.split("=")[0]:(p+"=").split("=")[1] for p in param}
                
                try:
                    sp.check_output(["echo "+passwd+" | sudo -S nmcli dev disconnect wlan0"], shell=True, universal_newlines=True).encode("UTF-8")
                except:
                    pass
                time.sleep(0.5)

                if 'ssid' in param and 'pw' in param:
                    if len(param['pw'])>=8:
                        result=sp.check_output(["echo "+passwd+" | sudo -S nmcli dev wifi connect "+param['ssid']+" password \""+param['pw']+"\""], shell=True, universal_newlines=True)
                        
                        if "Error" in str(result):
                            if "(7)" in str(result):
                                self.send_response(500)
                                self.end_headers()
                                self.wfile.write("The passphrase is incorrect.".encode("UTF-8"))
                            else:
                                self.send_response(500)
                                self.end_headers()
                                self.wfile.write(str(result).encode("UTF-8"))
                        else:
                            ip=sp.check_output("ifconfig wlan0 | grep 'inet' | cut -d: -f2 | awk '{print $2}'", shell=True, universal_newlines=True).replace("\n","")
                            msg="Connected to "+ip+"."

                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(msg.encode("UTF-8"))
                    elif len(param['pw'])==0:
                        result=sp.check_output(["echo "+passwd+" | sudo -S nmcli dev wifi connect "+param['ssid']], shell=True, universal_newlines=True)

                        if "Error" in str(result):
                            if "(7)" in str(result):
                                self.send_response(500)
                                self.end_headers()
                                self.wfile.write("The passphrase is incorrect.".encode("UTF-8"))
                            else:
                                self.send_response(500)
                                self.end_headers()
                                self.wfile.write(str(result).encode("UTF-8"))
                        else:
                            ip=sp.check_output("ifconfig wlan0 | grep 'inet' | cut -d: -f2 | awk '{print $2}'", shell=True, universal_newlines=True).replace("\n","")
                            msg="Connected to "+ip+"."

                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(msg.encode("UTF-8"))
                    else:
                        msg="Password is less than 8 characters."
                        
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(msg.encode("UTF-8"))
                else:
                    msg="Doesn't found parameters."
                        
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(msg.encode("UTF-8"))
            except:
                msg="An error occured."
                        
                self.send_response(500)
                self.end_headers()
                self.wfile.write(msg.encode("UTF-8"))

        elif data.path == "/wifi_status":
            try:
                table=sp.check_output(["sudo nmcli dev wifi rescan & nmcli dev wifi list"], shell=True, universal_newlines=True).split("\n")[1:-3]

                for i in range(len(table)):
                    if table[i][0]!="*":table[i]="-"+table[i][1:]
                    else:
                        table.insert(0,table.pop(i))
                        i=0
                        
                    tmp=[]
                    cnt=0
                    tmpstr=""
                    for j in range(len(table[i])):
                        if table[i][j]==" ": 
                            cnt+=1
                            if cnt>=2 and tmpstr!="":
                                tmp.append(tmpstr[:-1])
                                tmpstr=""
                            elif cnt<2:
                                tmpstr+=table[i][j]
                        elif cnt>=2:
                            cnt=0
                            tmpstr=""+table[i][j]
                        elif cnt<2:
                            cnt=0
                            tmpstr+=table[i][j]
                            
                    if tmpstr!="":
                        tmp.append(tmpstr[:-1])
                        tmpstr=""
                        
                    table[i]=[tmp[0],tmp[1],tmp[-3],tmp[-1]]
                            

                msg=json.dumps(table)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(msg.encode("UTF-8"))
            except:
                msg="An error occured."
                        
                self.send_response(500)
                self.end_headers()
                self.wfile.write(msg.encode("UTF-8"))
        elif data.path == "/set_lang":
            param = data.query

            if "&" in param:
                param = param.split("&")
            else:
                param = [param]

            if param[0]=="0": #Korean
                sp.check_output(["echo "+passwd+" | sudo -S sed -i \"2s/.*/LANG=ko_KR.UTF-8/g\" /etc/default/locale "], shell=True, universal_newlines=True).encode("UTF-8")
            elif param[0]=="1": #English
                sp.check_output(["echo "+passwd+" | sudo -S sed -i \"2s/.*/LANG=en_US.UTF-8/g\" /etc/default/locale "], shell=True, universal_newlines=True).encode("UTF-8")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Doesn't supported request.".encode("UTF-8"))
        

server = http.server.HTTPServer(('0.0.0.0',7000),Handler)
print("Server Start.")
server.serve_forever()
