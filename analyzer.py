import os
from queue import Empty, Queue
from threading import Thread
import time
from ipaddress import ip_address
import pandas as pd


FILENAME = "/var/log/httpd/access_log"
MAX_COUNT_ATTACS = 3
TIME_TO_LIVE = 5888888888 
NUM_ITEMS = 4

temp_list = [0, 0, 0]
main_data_fr = pd.DataFrame([temp_list],columns = ["err", "time", "cnt"], index=["127.0.0.0"])

def block_ip(attacker_ip):
    pid = os.fork()
    if pid == 0:
        os.execl("/usr/sbin/iptables", "iptables", "-I", "INPUT", "1", "--src", attacker_ip, "-j", "REJECT")
    else:
        return -1

    os.wait()


def add_strings(queue,line):
    for one_data in line:
        if one_data != '':  
            queue.put(one_data)

def consume_strings(queue):
    while True:
        try:
            item = queue.get()
        except Empty:
            continue
        else:
            global main_data_fr
            #print(f'new item:    {item}')
            

            temp_list = list(item.split())
            curr_time = int(time.time())
            
            #print('temp_list ',temp_list)

            try:
                item_err = int(temp_list[1])
                #print('item_err ', item_err)
                if item_err < 400 or item_err > 600:
                    continue
            except:
                continue

            try:
                if temp_list[0] != '127.0.0.1':
                    item_ip = str(ip_address(temp_list[0]))
                    #print('item_ip ', item_ip)
            except:
                continue
            
            try:
                item_time = int(temp_list[2])
                #print('item_time ', item_time)
                if item_time < 0 or item_time > curr_time:
                    continue
            except:
                continue

            work_list = [item_err, item_time,1] 
            #print('work_list', work_list)
            time_column = main_data_fr["time"]
            cnt_column = main_data_fr["cnt"]
            #print('columns:\n',time_column,'\n',cnt_column,'\n')
            
            try:
                time_column.get(item_ip)
                #print('ININININI')
                last_attack_time = time_column.get(item_ip)
                if (curr_time - last_attack_time) <= TIME_TO_LIVE:
                    main_data_fr.at[item_ip, "cnt"] += 1
                else:
                    main_data_fr.at[item_ip, "cnt"] = 1
            except:
                
                #print('OUTOUTOUT')
                temp_df =  pd.DataFrame([work_list],columns = ["err", "time", "cnt"],\
                index=[item_ip])
                #print('temp_df:\n',temp_df, '\n')
                main_data_fr = pd.concat([main_data_fr, temp_df])
                #print('mmain_df:\n', main_data_fr, '\n')

            
            curr_count = main_data_fr.at[item_ip, "cnt"]
            if curr_count >= MAX_COUNT_ATTACS:
                print('\033[91m{}\033[00m'.format('ATTACKS!!! block incoming connections by firewall'),  item_ip)
                block_ip(item_ip) 
            
            
            #print(main_data_fr, '\n\n')
            time.sleep(0.5)

            queue.task_done()


def main():
    fd = -1 
    
    while(1):

        if (fd < 0): 
            while(fd < 0):
                access_log = open(FILENAME, mode='r', encoding= 'utf8', errors='ignore')
                fd = access_log.fileno()
                inode = os.stat(fd).st_ino

        line = access_log.read().split('\n')      
        
        if line == ['']:
            new_fd = access_log.fileno()
            if os.stat(new_fd).st_ino != inode:
                access_log.close()
                os.close(fd)
        else:
            
            queue = Queue() 
            
            add_strings_thread = Thread(
                target=add_strings,
                args=(queue,line)
            )
            add_strings_thread.start()

            consume_strings_thread = Thread(
                target=consume_strings,
                args=(queue,),
                daemon=True
            )
            consume_strings_thread.start()          
                

        
        
        
          
        





if __name__ == '__main__':
    main()

