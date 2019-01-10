#!/usr/bin/python

ABOUT = "\n"\
                " -------------------------------------------------\n" \
                " | [-f] set source file default is tcp_ip        |\n" \
                " |      eg: python tcp-client.py -f file-name    |\n" \
                " | [-i] set connect interval in second           |\n" \
                " |      eg: python tcp-client.py -i 0.5          |\n" \
                " | [-o] set log file default is time-tcp.log     |\n" \
                " |      eg: python tcp-client.py -o log-name     |\n"\
                " | [-p] set server port default is 55555         |\n" \
                " |      eg: python tcp-client.py -p 55555        |\n"\
                " | [p]  pause                                    |\n" \
                " | [r]  continue                                 |\n" \
                " | [e]  exit or ctrl+c                           |\n" \
                " -------------------------------------------------\n"

import socket
import sys
import os
import time
import threading

# in second
INTERVAL = 0.2
TIME_OUT = 0.1
RUN_FLAG = True
PAUSE = False
WORK_MODE = "TCP"

#-------------some constant--------------

GOOD_FORMAT = " {s}---good---{e}\n"
BAD_FORMAT =  " {s}---bad----{e}\n"
SERVER_PORT = 55555
SUCESS = True
FAILED = False
DOWN_TIME_OUT = 1
LOG_DICT = {}

#----------------------------------------

class Common(object):
    def __init__(self):
        self.count = 0
        self.good_seg = [0, 0]
        self.bad_seg = [0, 0]
        self.good = 0
        self.bad = 0
        self.log = []
        self.above_down_time = False

    def getime(self):
        ct = time.time()
        local_time = time.localtime(ct)
        # "%Y-%m-%d "
        data_head = time.strftime("%H:%M:%S", local_time)
        data_secs = (ct - long(ct)) * 1000
        time_stamp = "%s:%03d" % (data_head, data_secs)
        return time_stamp

    def record(self, status, time=''):
        self.count += 1
        if status:
            if self.bad_seg[0]:
                self.log.append(self.get_str(FAILED))
            if self.good_seg[0]:
                self.good_seg[1] = time
            else:
                self.good_seg[0] = time
            self.good += 1
        else:
            if self.good_seg[0]:
                self.log.append(self.get_str(SUCESS))
            if self.bad_seg[0]:
                self.bad_seg[1] = time
            else:
                self.bad_seg[0] = time
            self.bad += 1
        self.last_try = status

    def get_str(self, flag):
        res_str = ''
        if flag == True:
            if self.good_seg[1]:
                res_str = GOOD_FORMAT.format(s=self.good_seg[0],
                                             e=self.good_seg[1])
            elif self.good_seg[0]:
                res_str = GOOD_FORMAT.format(s=self.good_seg[0], e="ONE")
            self.good_seg = [0, 0]
        else:
            if self.bad_seg[1]:
                res_str = BAD_FORMAT.format(s=self.bad_seg[0],
                                            e=self.bad_seg[1])
            elif self.bad_seg[0]:
                res_str = BAD_FORMAT.format(s=self.bad_seg[0], e="ONE")
            self.above_time_limit_check()  # before update check bad time field
            self.bad_seg = [0, 0]
        return res_str

    def above_time_limit_check(self):
        if not self.above_down_time:
            if self.bad_seg[1]:
                a = self.bad_seg[0]
                b = self.bad_seg[1]
                a_l = [int(elm) for elm in a.split(":")[:-1]]
                b_l = [int(elm) for elm in b.split(":")[:-1]]
                if b_l[0] < a_l[0]:
                    b_l[0] += 24
                end = b_l[0] * 3600 + b_l[1] * 60 + b_l[2]
                start = a_l[0] * 3600 + a_l[1] * 60 + a_l[2]
                if (end - start) >= DOWN_TIME_OUT:
                    self.above_down_time = True

    def final_process(self):
        final_str = self.get_str(self.last_try)
        self.log.append(final_str)


class Client(threading.Thread, Common):
    def __init__(self, server, lock):
        super(Client,self).__init__(name=server[0])
        Common.__init__(self)
        self.server = server
        self.lock = lock

    def get_socket(self):
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cs.settimeout(TIME_OUT)
        return cs

    def run(self):
        while RUN_FLAG:
            if PAUSE:
                continue
            try:
                s = self.get_socket()
                s.connect(self.server)
                self.record(SUCESS, self.getime())
                s.shutdown(2)
                s.close()
            except socket.error :
                try:
                    s.shutdown(2)
                except socket.error:
                    pass
                s.close()
                self.record(FAILED, self.getime())
            time.sleep(INTERVAL)
        self.final_process()
        self.lock.acquire()
        LOG_DICT[self.name] = self
        self.lock.release()

class Process(object):

    IP_COUNT = 0
    IP_FAILED = 0

    def __init__(self):
        self.form = '- '*10+ "[ ip:{ip:<15}  all:{all:<4}  fail:{fail:<4} ]"+'- '*10 + "\n\n" + "{detail}"+"\n"
        self.fail_form = '* ' * 10 + "[ all_ip:{ip:<11}  fail:{fail:<4} ]" + '* ' * 10 + "\n\n" + "{detail}" + "\n\n"
        self.result = ''
        self.failed_ip = ''
        self.log_file = Common().getime() + "-tcp.log"
        self.ip_file = 'ip'

    def process(self):
        for key in LOG_DICT:
            res = LOG_DICT[key]
            if not res:
                continue
            else:
                self.failed_ip += (' ' + key + ' ') if res.above_down_time else ''
                self.result += self.form.format(ip=res.name,
                                            all=res.count,
                                            fail=res.bad,
                                            detail=''.join(res.log))
        Process.IP_FAILED = len(self.failed_ip.split())
        self.failed_str = self.fail_form.format(ip=self.__class__.IP_COUNT,
                                                fail=Process.IP_FAILED,
                                                detail=self.failed_ip)
        return self.failed_str + self.result

    def write_result(self):
        result = self.process()
        with open(self.log_file, 'w') as f:
            f.write(result)
            f.close()

class ConnectTest(Process):

    def process_argv(self, argv):
        global INTERVAL, SERVER_PORT
        if "-i" in argv:
            interval = argv[argv.index("-i") + 1]
            try:
                INTERVAL = float(interval)
            except Exception as e:
                print ">> [error]: connect interval is not valid use default 1s\n"
        if "-f" in argv:
            self.ip_file = argv[argv.index("-f") + 1]
            if not os.path.exists(self.ip_file):
                print ">> [error]: source ip file is not exist \n"
                sys.exit(0)
        if "-f" not in argv:
            if not os.path.exists("tcp_ip"):
                print ">> [error]: source ip file doest not specify and default tcp_ip file not exist! "
                sys.exit(0)
        if "-p" in argv:
            port_str = argv[argv.index("-p") + 1]
            try:
                if int(port_str) < 5000 or int(port_str) > 65535:
                    raise Exception("port error")
                SERVER_PORT = int(port_str)
            except Exception:
                print ">> [error]: port not in range [50000, 65535) \n"
                sys.exit(0)
        if "-o" in argv:
            self.log_file = argv[argv.index("-o") + 1]

    def wait_input(self):

        global PAUSE, RUN_FLAG

        while True:
            try:
                cmd = raw_input(">> ")
                cmd = cmd.strip()
                if cmd.lower() == 'p':
                    PAUSE = True
                elif cmd.lower() == 'r':
                    PAUSE = False
                elif cmd.lower() == 'e':
                    RUN_FLAG = False
                    break
            except KeyboardInterrupt:
                RUN_FLAG = False
                break

    def main(self, argv):

        self.process_argv(argv)
        with open(self.ip_file, 'r') as f:
            ip_list = f.read().split()
            self.__class__.IP_COUNT = len(ip_list)
            f.close()

        thread_list = []
        lock = threading.Lock()
        for ip in ip_list:
            thread_list.append(Client((ip,SERVER_PORT), lock))
        for thr in thread_list:
            thr.start()

        self.wait_input()

        for thr in thread_list:
            thr.join()
        self.write_result()
        print ">> Test finish ,result: " + self.log_file
        print ">> Tcp test port: {p}, interval: {i}s, timeout: {t}s ".format(i=INTERVAL,
                                                                             t=TIME_OUT,
                                                                             p=SERVER_PORT)
        print ">> Fail {num} ip below (down > {d}s)".format(num=self.IP_FAILED,
                                                            d=DOWN_TIME_OUT)
        print self.failed_ip

if __name__ == '__main__':
    print ABOUT
    ConnectTest().main(sys.argv)















