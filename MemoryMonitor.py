'''
Created on 2020-10-19
@author: dandan.yao
'''
import os,sys,json
import time, base64,requests
import configparser
import psutil
import queue
import _thread,threading
import datetime
import multiprocessing

global path

def Memory_Record(process,pid):

    #print(meminfo)
    localtime=time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    filename = process.name() + "-" + str(pid) + "-" + localtime + ".txt"
    f = open(path+os.sep+filename, 'a+')
    f.write("Data                        CPU(%)  Mem(%)  Mem_Size(KB)  VM_Size(KB)\n")
    f.close()
    while 1:
        meminfo = process.memory_full_info()
        #print(meminfo)
        #print(process.memory_info())
        memlist = str(meminfo).split(',')
        vms = memlist[1]
        wset = memlist[4]
        vmsize = int(vms[5:])/1024
        memsize =int(wset[6:])/1024
        f = open(path + os.sep + filename, 'a+')
        #f = open(process.name() + "-" + str(pid) + "-" + localtime + ".txt", 'a+')
        f.write(time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time())) + "      " + str(round(process.cpu_percent(), 2))+"      "+str(round(process.memory_percent(), 2))+"        "+str(memsize)+"     "+str(vmsize)+'\n')
        f.close()
        time.sleep(Interval)
def System_Record():
    localtime = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    filename = "System-" + localtime + ".txt"
    f = open(path+os.sep+filename, 'a+')
    #f = open("System-" + localtime + ".txt", 'a+')
    f.write("Data                        CPU(%)  Mem(%)  Disk(%)   IO_Read(Count)    IO_Write(Count)\n")
    f.close()
    while 1:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        io = psutil.disk_io_counters()
        #print(disk)
        #print(io)

        memlist = str(mem).split(',')
        mem_percent = memlist[2]
        disklist = str(disk).split(',')
        disk_percent = disklist[3]
        iolist = str(io).split(',')
        io_read = iolist[0]
        io_write = iolist[1]
        f = open(path + os.sep + filename, 'a+')
        #f = open("System-" + localtime + ".txt", 'a+')
        f.write(time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time())) + "      " + str(cpu) + "      " + str(mem_percent[9:]) + "     "+str(disk_percent[9:13]) + "         "+str(io_read[19:])+"         "+str(io_write[13:]) + '\n')
        f.close()
        time.sleep(Interval)


if __name__ == '__main__':

    multiprocessing.freeze_support()
    starttime = datetime.datetime.now()
    # get config
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    elif __file__:
        path = os.path.dirname(os.path.abspath(__file__))
    #configPath = os.path.join(path, "BVT.ini")


    #path = os.getcwd()
    configPath = os.path.join(path, "MemoryMonitor.ini")
    config = configparser.ConfigParser()
    config.read_file(open(configPath))
    Interval = config.getint("Time", "Interval")
    Duration= config.getint("Time", "Duration")
    ProcessList=config.get("Process", "process")

    pidlist=psutil.pids()
    threads=[]
    if "system" in ProcessList:
        #print("监控系统资源：system")
        threads.append(threading.Thread(target=System_Record, args=()))
    if "System" in ProcessList:
        #print("监控系统资源：System")
        threads.append(threading.Thread(target=System_Record, args=()))
    for i in pidlist:
        p = psutil.Process(i)
        processname =p.name()
        if processname in ProcessList:
            if processname !="System":
                #print("监控应用程序：", processname)
                threads.append(threading.Thread(target=Memory_Record, args=(p,i,)))
            else:
                continue

    for t in threads:
        t.setDaemon(True)
        t.start()
    #t.join()
    while 1:
        endtime = datetime.datetime.now()
        if (endtime-starttime).total_seconds() > Duration*60*60:
            exit()
        time.sleep(Interval)