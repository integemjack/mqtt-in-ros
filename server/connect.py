from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import subprocess
import os
import urllib
import uuid
import signal
import select

host = ('', 80)
pid = 0
ip = '*'
port = 0
command = ""
commands = {}


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class Resquest(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "ROS"

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        paths = self.path.split('?', 1)
        print(paths)
        path = paths[0]
        if len(paths) == 1:
            return self.wfile.write('No this function!'.encode())
        self.queryString = urllib.parse.unquote(paths[1])
        params = urllib.parse.parse_qs(self.queryString)
        print(params)

        topic = params['machineid'][0]
        global pid, ip, port, command, commands

        buf = 'no function'
        print('machineId: "', machineId(), '"  topic: ', topic)
        if machineId() != topic:
            return self.wfile.write('No this device!'.encode())

        if path == '/connect':
            if len(params['mqtt_ip']) > 0:
                ips = params['mqtt_ip'][0].split(':', 1)
                ip = ips[0]
                port = ips[1] * 1
            cmd = "sed -i \"s/host: localhost/host: {}/g\" /home/nvidia/mqtt_ws/src/mqtt/config/demo_params.yaml && sed -i \"s/port: 1883/port: {}/g\" /home/nvidia/mqtt_ws/src/mqtt/config/demo_params.yaml && chmod +x -R /home/nvidia/mqtt_ws && cd /home/nvidia/mqtt_ws/devel && source setup.bash && roslaunch mqtt_bridge demo.launch".format(
                ip, port)
            print("Command: ", cmd)
            self.proc = subprocess.Popen(
                cmd, shell=True, executable="/bin/bash", preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            buf = "{\"suceesss\": true, \"pid\": %d}" % self.proc.pid
            pid = self.proc.pid
            commands["%d" % self.proc.pid] = self.proc

        elif path == '/stop':
            try:
                # print("id:", self.proc)
                # self.proc.terminate()
                # self.proc.wait()
                if len(params['pid']) > 0:
                    print("pid", params['pid'])
                    os.killpg(params['pid'], signal.SIGTERM)
                    print("stoped!")
                    buf = 'ok'
                elif pid != 0:
                    print("pid", pid)
                    os.killpg(pid, signal.SIGTERM)
                    print("stoped!")
                    buf = 'ok'
                    pid = 0
                else:
                    print("no stop!")
                    buf = 'no stop!'
            except:
                print("no ros to stop...")
                buf = 'no ros to stop...'

        elif path == '/status':
            mqtt_connect = "false"
            if pid != 0:
                mqtt_connect = "true"
            buf = "{" + "\"success\": {}, \"mqtt_ip\": \"{}:{}\", \"device\": \"nano\"".format(
                mqtt_connect, ip, port) + "}"

        elif path == '/command':
            if len(params['command']) > 0:
                try:
                    command = params['command'][0]
                    print(command)
                    proc = subprocess.Popen(command, shell=True, executable="/bin/bash",
                                            preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    buf = "{\"suceesss\": true, \"pid\": %d}" % (
                        proc.pid)
                    commands["%d" % proc.pid] = proc

                except Exception as e:
                    buf = "{\"suceesss\": false, \"error\": %s}" % e
            else:
                buf = "{\"suceesss\": false, \"error\": \"No command param\"}"

        elif path == '/watch':
            if len(params['pid']) > 0:
                try:
                    print(commands)
                    commandThis = commands[params['pid'][0]]
                    print(commandThis)
                    # Set the timeout for reading subprocess output
                    commandThis.stderr.settimeout(1)  # 设置超时时间为1秒
                    # Set the timeout for reading subprocess output
                    commandThis.stdout.settimeout(1)  # 设置超时时间为1秒

                    while True:


                        # Read one line from the subprocess output with timeout
                        ready = select.select([commandThis.stderr], [], [], 1)
                        if ready[0]:
                            output_line = commandThis.stdout.readline()
                        else:
                            output_line = b''  # 超时时返回空字符串

                        # Write the output line as the response
                        self.wfile.write(output_line)

                        # Read one line from the subprocess output with timeout
                        ready = select.select([commandThis.stdout], [], [], 1)
                        if ready[0]:
                            output_line = commandThis.stdout.readline()
                        else:
                            output_line = b''  # 超时时返回空字符串

                        # Write the output line as the response
                        self.wfile.write(output_line)

                except Exception as e:
                    buf = "{\"suceesss\": false, \"error\": %s}" % e
            else:
                buf = "{\"suceesss\": false, \"error\": \"No pid\"}"

        self.wfile.write(buf.encode())

    def do_POST(self):
        # datas = self.rfile.read(int(self.headers['content-length']))
        # datas = urllib.unquote(datas).decode("utf-8", 'ignore')

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = '''No Data!!!'''
        self.wfile.write(html.encode())


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
