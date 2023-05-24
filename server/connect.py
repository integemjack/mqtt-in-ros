from http.server import HTTPServer, BaseHTTPRequestHandler
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


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class Resquest(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "ROS"

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
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
            if pid != 0:
                buf = '{"success": false, "error": "MQTT is connected!"}'
                return self.wfile.write(buf.encode())
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
            if len(params['command']) > 0:
                try:
                    command = params['command'][0]
                    print(command)
                    proc = subprocess.Popen(command, shell=True, executable="/bin/bash",
                                            preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    buf = "{\"suceesss\": true, \"pid\": %d}" % (
                        proc.pid)
                    commands["%d" % proc.pid] = proc
                    thisPid = proc.pid
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

        elif path == '/watch':
            if len(params['pid']) > 0:
                try:
                    commandThis = commands[params['pid'][0]]
                    # Set the timeout for reading subprocess output
                    commandThis.stdout.timeout = 1  # Set timeout to 1 second
                    commandThis.stderr.timeout = 1  # Set timeout to 1 second
                    self.send_header("Content-type", "text/plain")

                    # Get the current stdout flags
                    flags = fcntl.fcntl(commandThis.stdout, fcntl.F_GETFL)
                    # Set the stdout to non-blocking
                    fcntl.fcntl(commandThis.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

                    # Get the current stdout flags
                    flagse = fcntl.fcntl(commandThis.stderr, fcntl.F_GETFL)
                    # Set the stdout to non-blocking
                    fcntl.fcntl(commandThis.stderr, fcntl.F_SETFL, flagse | os.O_NONBLOCK)

                    i = 0
                    # timeout = 3  # 设置超时时间为5秒

                    while True:
                        i += 1
                        print('读取%d次数据...' % i)

                        # 检查子进程的状态
                        returncode = commandThis.poll()
                        if returncode is not None:
                            output_line = commandThis.stdout.read()#.decode('utf-8')
                            if output_line:
                                self.wfile.write(output_line.encode('utf-8'))

                            error_line = commandThis.stderr.read()#.decode('utf-8')
                            if error_line:
                                self.wfile.write(error_line.encode('utf-8'))

                            self.wfile.write(("exit(%d)" % returncode).encode())
                            break

                        # start_time = time.time()
                        
                        # while True:
                        #     print(self.wfile.closed)
                        #     if self.wfile.closed:
                        #         print('网页关闭.')
                        #         # Check if the connection is closed
                        #         break

                            # Read one line from the subprocess output with timeout
                            # ready = select.select([commandThis.stdout, commandThis.stderr], [], [], timeout)
                            # if commandThis.stdout in ready[0]:
                        print('读取%d次数据...stdout.' % i)
                        output_line = commandThis.stdout.read()#.decode('utf-8')
                        if output_line:
                            self.wfile.write(output_line)
                            self.wfile.flush()

                            # if commandThis.stderr in ready[0]:
                        print('读取%d次数据...stderr.' % i)
                        error_line = commandThis.stderr.read()#.decode('utf-8')
                        if error_line:
                            self.wfile.write(error_line)
                            self.wfile.flush()

                            # elapsed_time = time.time() - start_time
                            # if elapsed_time >= timeout:
                            #     print('读取%d次数据...失败.' % i)
                            #     # Timeout occurred, break the inner loop
                            #     break

                        print('读取%d次数据...完成.' % i)

                        print(self.wfile.closed)
                        if self.wfile.closed:
                            print('网页关闭.')
                            # Check if the connection is closed
                            break

                    return

                except Exception as e:
                    buf = "{\"suceesss\": false, \"error\": \"%s\"}" % e
                    self.wfile.write(buf.encode())
            else:
                buf = "{\"suceesss\": false, \"error\": \"No pid\"}"
                self.wfile.write(buf.encode())

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
