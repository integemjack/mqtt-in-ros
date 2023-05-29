import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import socket
from socketserver import ThreadingMixIn
import subprocess
import os
import urllib
import uuid
import signal
import time
import select
import fcntl

host = ('', 80)
pid = 0
ip = '*'
port = 0
command = ""
commands = {}
logs = {}


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def exec_command(command):
    global commands, logs
    print(command)
    thisPid = -1
    if command:
        try:
            proc = subprocess.Popen(command, shell=True, executable="/bin/bash",
                                    preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            buf = "{\"suceesss\": true, \"pid\": %d}" % (
                proc.pid)
            commands["%d" % proc.pid] = proc
            thisPid = proc.pid
            logs["%d" % thisPid] = b''
            time.sleep(1)

            commandThis = commands["%d" % thisPid]
            # Set the timeout for reading subprocess output
            commandThis.stdout.timeout = 1  # Set timeout to 1 second
            commandThis.stderr.timeout = 1  # Set timeout to 1 second
            returncode = commandThis.poll()
            if returncode is not None:
                output_line = commandThis.stdout.read().decode('utf-8')
                error_line = commandThis.stderr.read().decode('utf-8')
                success = "true"
                if error_line != "":
                    success = "false"
                buf = "{\"suceesss\": %s, \"pid\": %d, \"stdout\": \"%s\", \"error\": \"%s\"}" % (success, thisPid, output_line, error_line)

        except Exception as e:
            buf = "{\"suceesss\": false, \"error\": \"%s\"}" % e
    else:
        buf = "{\"suceesss\": false, \"error\": \"No command param\"}"

    return buf, thisPid

def watch(self, pid, once=False, output=True):
    if pid:
        try:
            print(logs[pid])
            if logs[pid] and output:
                self.wfile.write(logs[pid])
            else:
                logs[pid] = b''

            commandThis = commands[pid]
            # Set the timeout for reading subprocess output
            commandThis.stdout.timeout = 1  # Set timeout to 1 second
            commandThis.stderr.timeout = 1  # Set timeout to 1 second
            # self.send_header("Content-type", "text/plain")

            # Get the current stdout flags
            flags = fcntl.fcntl(commandThis.stdout, fcntl.F_GETFL)
            # Set the stdout to non-blocking
            fcntl.fcntl(commandThis.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            # Get the current stdout flags
            flagse = fcntl.fcntl(commandThis.stderr, fcntl.F_GETFL)
            # Set the stdout to non-blocking
            fcntl.fcntl(commandThis.stderr, fcntl.F_SETFL, flagse | os.O_NONBLOCK)

            # i = 0

            while True:
                # i += 1
                # print('读取%d次数据...' % i)

                # 检查子进程的状态
                returncode = commandThis.poll()
                if returncode is not None:
                    logs[pid] = b''
                    output_line = commandThis.stdout.read()#.decode('utf-8')
                    if output_line and output:
                        self.wfile.write(output_line) #.encode('utf-8')

                    error_line = commandThis.stderr.read()#.decode('utf-8')
                    if error_line and output:
                        self.wfile.write(error_line) #.encode('utf-8')

                    self.wfile.write(("exit(%d)" % returncode).encode())
                    break

                # print('读取%d次数据...stdout.' % i)
                output_line = commandThis.stdout.read()#.decode('utf-8')
                if output_line:
                    logs[pid] += output_line
                    if output:
                        self.wfile.write(output_line)
                        self.wfile.flush()

                # print('读取%d次数据...stderr.' % i)
                error_line = commandThis.stderr.read()#.decode('utf-8')
                if error_line:
                    logs[pid] += error_line
                    if output:
                        self.wfile.write(error_line)
                        self.wfile.flush()

                # print('读取%d次数据...完成.' % i)

                # print(self.wfile.closed)
                if self.wfile.closed:
                    print('网页关闭.')
                    # Check if the connection is closed
                    break
                
                if once and logs[pid] != b'':
                    break
                # time.sleep(1)

            return

        except Exception as e:
            print('结束循环.')
            print(e)
            buf = "{\"suceesss\": false, \"error\": \"%s\"}" % e
    else:
        buf = "{\"suceesss\": false, \"error\": \"No pid\"}"

    return buf

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass
class Resquest(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "ROS"

    def do_GET(self):
        paths = self.path.split('?', 1)
        print(paths)
        path = paths[0]
        if len(paths) == 1:
            return self.wfile.write('No this function!'.encode())
        self.queryString = urllib.parse.unquote(paths[1])
        params = urllib.parse.parse_qs(self.queryString)
        print(params)

        topic = params['machineid'][0]
        global pid, ip, port, command, commands, logs, exec_command

        buf = 'no function'
        print('machineId: "', machineId(), '"  topic: ', topic)
        if machineId() != topic:
            return self.wfile.write('No this device!'.encode())

        if path == '/connect':
            if pid != 0:
                buf = '{"success": false, "error": "MQTT is connected!"}'
                return self.wfile.write(buf.encode())
            if len(params['mqtt_ip']) > 0:
                ips = params['mqtt_ip'][0].split(':', 1)
                ip = ips[0]
                port = ips[1] * 1
            cmd = "cd /home/nvidia/mqtt_ws/src/mqtt && git checkout -- /home/nvidia/mqtt_ws/src/mqtt/config/demo_params.yaml && sed -i \"s/host: localhost/host: {}/g\" /home/nvidia/mqtt_ws/src/mqtt/config/demo_params.yaml && sed -i \"s/port: 1883/port: {}/g\" /home/nvidia/mqtt_ws/src/mqtt/config/demo_params.yaml && chmod +x -R /home/nvidia/mqtt_ws && cd /home/nvidia/mqtt_ws/devel && source setup.bash && roslaunch mqtt_bridge demo.launch".format(
                ip, port)
            print("Command: ", cmd)
            self.proc = subprocess.Popen(
                cmd, shell=True, executable="/bin/bash", preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            buf = "{\"suceesss\": true, \"pid\": %d}" % self.proc.pid
            pid = self.proc.pid
            commands["%d" % self.proc.pid] = self.proc
            logs["%d" % self.proc.pid] = b''
            time.sleep(1)

            commandThis = commands["%d" % pid]
            # Set the timeout for reading subprocess output
            commandThis.stdout.timeout = 1  # Set timeout to 1 second
            commandThis.stderr.timeout = 1  # Set timeout to 1 second
            returncode = commandThis.poll()
            if returncode is not None:
                output_line = commandThis.stdout.read().decode('utf-8')
                error_line = commandThis.stderr.read().decode('utf-8')
                success = "true"
                if error_line != "":
                    success = "false"
                buf = "{\"suceesss\": %s, \"pid\": %d, \"stdout\": \"%s\", \"error\": \"%s\"}" % (success, pid, output_line, error_line)
                pid = 0

        elif path == '/stop':
            try:
                # print("id:", self.proc)
                # self.proc.terminate()
                # self.proc.wait()
                print(params['pid'])
                if len(params['pid']) > 0:
                    print("pid", params['pid'])
                    os.killpg(int(params['pid'][0]), signal.SIGTERM)
                    print("stoped!")
                    buf = '{"suceess": true, "pid": %s}' % params['pid'][0]
                elif pid != 0:
                    print("pid", pid)
                    os.killpg(pid, signal.SIGTERM)
                    print("stoped!")
                    buf = '{"suceess": true, "pid": %d}' % pid
                    pid = 0
                else:
                    print("no stop!")
                    buf = '{"suceess": false, "error": "No stop"}'
            except Exception as e:
                print("no ros to stop...")
                buf = '{"suceess": false, "error": "%s"}' % e

        elif path == '/status':
            mqtt_connect = "false"
            returncode = commands["%d" % pid].poll()
            if returncode is None:
                mqtt_connect = "true"
            buf = "{" + "\"success\": {}, \"mqtt_ip\": \"{}:{}\", \"device\": \"nano\"".format(
                mqtt_connect, ip, port) + "}"

        elif path == '/command':
            buf, thisPid = exec_command(params['command'][0])

        elif path == '/watch':
            buf = watch(self, params['pid'][0])

        elif path == '/jupyter':
            buf, thisPid = exec_command("cd / && source /home/nvidia/myenv/bin/activate && source /opt/ros/melodic/setup.bash && source /home/nvidia/mqtt_ws/devel/setup.bash && jupyter lab --allow-root")
            time.sleep(3)
            try:
                log = ""
                token = ""
                port = ""
                while re.search(r'http://0.0.0.0:(\d+)/', log) is None:
                    watch(self, "%d" % thisPid, once=True, output=False)
                    log = logs["%d" % thisPid].decode('utf-8')
                    print("log=", end="")
                    print(log)

                    match = re.search(r'http://0.0.0.0:(\d+)/', log)
                    if match:
                        port = match.group(1)
                        print(port)  # 输出: 8909

                    match = re.search(r'token=([a-zA-Z0-9]+)', log)
                    if match:
                        token = match.group(1)
                        print(token)  # 输出: 87a841ac9af475641528eb1610494ed256b1e966673f076d


                url = "http://{}:{}/?token={}".format(get_lan_ip(), port, token)

                print("url=", end="")
                print(url)
                self.send_response(301)
                self.send_header('Location', url)
                self.end_headers()

            except Exception as e:
                buf = "{\"suceesss\": false, \"error\": \"%s\"}" % e

        
        if path == '/jupyter':
            pass
        elif path == "/watch":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(buf.encode())
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            self.wfile.write(buf.encode())

    def do_POST(self):
        global pid, ip, port, command, commands, logs

        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        print(ctype)
        if ctype == 'multipart/form-data':
            # Ensure that boundary is bytes, not str
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.get('Content-Length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        elif ctype == 'text/plain':
            content_length = int(self.headers.get('Content-Length'))
            post_data = self.rfile.read(content_length)
            postvars = json.loads(post_data)
        else:
            postvars = {}
        # now you can use postvars

        postvars_utf8 = {}

        for key, value in postvars.items():
            if isinstance(value, str):
                value = value
            elif isinstance(value, bytes):
                value = value.decode("utf-8")
            elif isinstance(value, list):
                value = [(item.encode("utf-8") if isinstance(item, str) else item.decode("utf-8")) for item in value][0]
            elif isinstance(value, dict):
                value = {(k if isinstance(k, str) else k.decode("utf-8")): (v.encode("utf-8") if isinstance(v, str) else v.decode("utf-8")) for k, v in value.items()}
            if isinstance(key, str):
                postvars_utf8[key] = value
            else:
                postvars_utf8[key.decode("utf-8")] = value

        self.send_response(200)
        self.send_header("Content-type", "text/json")


        print(postvars_utf8)
        topic = postvars_utf8['machineid']

        buf = 'no function'
        print('machineId: "', machineId(), '"  topic: ', topic)
        if machineId() != topic:
            return self.wfile.write('No this device!'.encode())

        # print(postvars)
        paths = self.path.split('?', 1)
        print(paths)
        path = paths[0]

        if path == '/command':
            buf, thisPid = exec_command(postvars_utf8['command'])
        
        self.end_headers()
        self.wfile.write(buf.encode())


def readFile(file):
    file_object = open(file)
    try:
        all_the_text = file_object.read()
    finally:
        file_object.close()
    return all_the_text


def writeFile(file, all_the_text):
    file_object = open(file, 'w')
    file_object.write(all_the_text)
    file_object.close()


def machineId():
    try:
        mid = readFile('/machineId')
    except:
        mid = uuid.uuid4()
        writeFile('/machineId', str(mid) + '')

    if (mid == ''):
        mid = uuid.uuid4()
        writeFile('/machineId', str(mid) + '')
    return mid.strip()


if __name__ == '__main__':
    server = ThreadedHTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
