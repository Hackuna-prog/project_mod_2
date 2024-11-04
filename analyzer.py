import os
from queue import Empty, Queue
from threading import Thread
import time
from ipaddress import ip_address
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from random import uniform


FILENAME = "/var/log/httpd/access_log"
MAX_COUNT_ATTACS = 1
TIME_TO_LIVE = 173063420
TIMER = int(time.time())
TIME_LIMIT = 10



main_data_fr = pd.DataFrame([[0, 0, 0]],columns = ["err", "time", "cnt"], index=["127.0.0.0"])
time_time_data_fr = pd.DataFrame([[[1730634200]]],columns = ["time"], index=["127.0.0.0"])

'''
def block_ip(attacker_ip):
    pid = os.fork()
    if pid == 0:
        os.execl("/usr/sbin/iptables", "iptables", "-I", "INPUT", "1", "--src", attacker_ip, "-j", "REJECT")
    else:
        return -1

    os.wait()
'''

def graph_builder():
    global time_time_data_fr
    pid = os.fork()
    if pid == 0:
        for label, content in time_time_data_fr.items(): 
            for i in range(len(content)):
                time_list = content.iloc[i]
                
                # INSTEAD I FIND IP TO BLOCK

                time1 = [time_list[0]]
                cnt1 = [0]                
                for i in range(len(time_list)):
                    if time_list[i] in time1:
                        cnt1[time1.index(time_list[i])] += 1
                    else:
                        time1.append(time_list[i])
                        cnt1.append(1)

                if len(time1) != 1:
                    time_dif = [0]
                    for i in range(1,len(time1)):
                        rand_num = uniform(0.0001,0.0002) 
                        time_dif.append(time1[i]-time1[i-1]+rand_num)

                    print("time1 ", time1)
                    print("cnt1  ", cnt1)
                    time_dif_div = [0]
                    for i in range(1,len(time_dif)):
                        time_dif_div.append((1/time_dif[i]))

                    f1 = [0]
                    for i in range(1,len(time_dif_div)):
                        ff1 = ( (time_dif_div[i])**2 + (cnt1[i])**2  )
                        f1.append(ff1)

                    print("time_dif_div ",time_dif_div)
                    print("f1           ",f1)
                    plt.plot(time_dif_div, f1,'o')
                else:
                    print("CHECK COUNT CNT\n")


                
        plt.show()
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
            global time_time_data_fr
            print('\033[1;92m{}\033[00m'.format('\nnew item:    '),  item)
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
                time_column.get(item_ip) #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
                extrime_time_col = time_time_data_fr["time"] 
                try:             
                    extrime_time_col.get(item_ip)
                    temp_extrim_list = extrime_time_col.get(item_ip)
                    time_graf_list = time_time_data_fr.at[item_ip, "time"]
                    time_graf_list.append(item_time)
                    time_time_data_fr.at[item_ip, "time"] = time_graf_list
                except:
                    temp_extrim_df =  pd.DataFrame([[[item_time]]],columns = ["time"],\
                    index=[item_ip])
                    time_time_data_fr = pd.concat([time_time_data_fr, temp_extrim_df])
                    '''
                    
                    print('\033[1;92m{}\033[00m'.format('ATTACKS!!! block incoming connections by firewall'),  item_ip)
                    block_ip(item_ip) 
            
                        '''
            print('\033[1;36m{}\033[00m'.format('\ntime_time_data_fr\n'), time_time_data_fr)
            print('\033[1;36m{}\033[00m'.format('\nmain_data_fr\n'),  main_data_fr)
            time.sleep(0.5)

            queue.task_done()


def main():
    fd = -1 
    
    while(1):

        global TIMER
        global time_time_data_fr
        if int(time.time()) - TIMER >= TIME_LIMIT:
            TIMER = int(time.time())

            print('\033[1;92m1MIN   1MIN    1MIN SPENT\033[00m')
            graph_builder()
            time_time_data_fr = pd.DataFrame([[[1730634200]]],columns = ["time"], index=["127.0.0.0"])
            #print('\033[1;37m{}\033[00m'.format('\ntime_time_data_fr\n'), time_time_data_fr)

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



'''
GOOD LOGS EXAMPLE

10.193.93.249 403 1730634201
10.193.93.249 403 1730634202
10.193.93.249 403 1730634203
10.193.93.249 403 1730634204
10.193.93.249 403 1730634230
10.193.93.249 403 1730634240
10.193.93.249 403 1730634250
10.193.93.249 403 1730634265
10.193.93.249 403 1730634265
10.193.93.249 403 1730634265
10.193.93.249 403 1730634265
10.193.93.249 403 1730634265
10.193.93.249 403 1730634265
10.193.93.249 403 1730634265

'''

