#  NAS.py
#  Network automation sys
#
#  Created by yassen on 5/6/20.
#  Copyright © 2021 yassen & nouhaila. All rights reserved.


from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, AuthenticationException
from paramiko.ssh_exception import SSHException
import getpass
from time import time, sleep
from datetime import datetime
import os
from simple_term_menu import TerminalMenu
from colorama import Fore, Back, Style
import csv
from threading import Thread
from tabulate import tabulate





###################################################################################################
                                          #SSH CONNECTION
###################################################################################################

def ssh_connection(device):
        info_device = {
        'device_type':'cisco_ios',
        'ip':device[0],
        'host':device[1],
        'username': 'LANLord',
        'password': 'GumoGumoNo'
        }
        try:
                connection = ConnectHandler(**info_device)
        except (AuthenticationException):
                print('Authentication failure: '+ ip)
        except (NetMikoTimeoutException):
                print('Timeout to device: ' + ip)    
        except (EOFError):
                print('End of file while attempting device: '+ ip)       
        except (SSHException):
                print('Be sure that SSH is enabled in: '+ ip +'?')
        except Exception as unknown_error:
                print ('Some other error: '+unknown_error)
        return connection



####################################################################################################
                                    #CHECK VERSION
####################################################################################################

def check_version(connection):
        list_versions = ['vios_l2-ADVENTERPRISEK9-M', 'VIOS-ADVENTERPRISEK9-M']
        output_version = connection.send_command('show version')
        for software_ver in list_versions:
                int_version = 0 
                int_version = output_version.find(software_ver)
                if int_version > 0:
                        break
                else:
                        pass
        return software_ver



##########################################################################################
                                   #device_input
##########################################################################################
def device_input():
        input_list = []
        devices_list = []       
        while True:
                ip = input(Back.GREEN +'\nEnter the IP address of the device: '+Style.RESET_ALL)
                name = input(Back.GREEN +'Enter the hostname : '+Style.RESET_ALL)
                input_list.append(ip)
                input_list.append(name)
                ask = input("\n Do you want more devices? answer by 'y' or 'n'! : " )
                devices_list.append(input_list)
                input_list = []
                if ask == 'y':
                        continue
                elif ask == 'n':
                        break
                else:
                        input("\n Do you want more devices? answer by 'y' or 'n'! : " )
        return devices_list



####################################################################################################
                                     #CONFIG ALL DEVICES
####################################################################################################
def configuration(device):
        ip = device [0]
        name = device [1]
        connection = ssh_connection(device)
        print (Back.GREEN+'\nconnection to '+ name + ' is up' + Style.RESET_ALL)
        software_ver = check_version(connection)
        if software_ver == 'vios_l2-ADVENTERPRISEK9-M':
                print ('Running Switch config file ...')
                output = connection.send_config_set(switch_config_file)
                print(output)
        elif software_ver == 'VIOS-ADVENTERPRISEK9-M':
                print ('Running Router config_file ...')
                output = connection.send_config_set(router_config_file)
        connection.disconnect()

        return output


#############################################################################################
                                    #VERIFY ALL DEVICES
#############################################################################################
def verification(device):
        ip = device [0]
        name = device [1]
        print(Back.GREEN +'\n'+80*'#'+ Style.RESET_ALL)
        connection = ssh_connection(device)
        print (Back.GREEN+'\nconnection to  %s ' %name + ' is up'+ Style.RESET_ALL)
        software_ver = check_version(connection)
        if software_ver == 'vios_l2-ADVENTERPRISEK9-M':
                running_config = connection.send_command('show running-config')
                length = len(switch_config_file)
                count = 0
                for item in switch_config_file:
                        if item in running_config:
                                count = count + 1
                        else:
                                print(Fore.RED+'{'+ item + '} not found in running-config}'+Style.RESET_ALL)
                        continue
                if count == length:
                        print(Back.GREEN+'\nCONFIGURATION CORRECT'+Style.RESET_ALL)
                else:
                        print(Back.RED+'\nCONFIGURATION NOT CORRECT'+Style.RESET_ALL)
       elif software_ver == 'VIOS-ADVENTERPRISEK9-M':
                running_config = connection.send_command('show running-config')
                length = len(router_config_file)
                count = 0
                for item in router_config_file:
                        if item in running_config:
                                count = count + 1
                        else:
                                print(Fore.RED+'{'+ item + '} not found in running-config}'+Style.RESET_ALL)
                        continue
                if count == length:
                        print(Back.GREEN+'\nCONFIGURATION CORRECT'+Style.RESET_ALL)
                else:
                        print(Back.RED+'\nCONFIGURATION NOT CORRECT'+Style.RESET_ALL)




####################################################################################################
                                    #TESTING CONNECTION
####################################################################################################
def test_connection(source, destination, connection):
    ip_source = source [0]
    name_source = source [1]
    ip_destination = destination[0]
    name_destination = destination[1]
    command = 'ping '+ ip_destination
    output_ping = connection.send_command(command) #delay_factor = 1)
    check_list = ['Success rate is 80 percent (4/5)','Success rate is 100 percent (5/5)']
    if any (item in output_ping for item in check_list):
        print (Back.GREEN+'Connection from '+name_source+' to '+name_destination+' is reachable==> Success rate'+Style.RESET_ALL)
    else:
        print (Back.RED+'Connection from '+name_source+' to '+name_destination
                +' is unreachable ==> Check Interfaces and protocols !'+Style.RESET_ALL)





#############################################################################################
                                     #CONFIRMATION
#############################################################################################
def confirmation(device):
        ip = device [0]
        name = device [1]
        connection = ssh_connection(device)
        print (Back.GREEN+'\nconnection to  %s ' %name +' is up'+ Style.RESET_ALL)
        saving = connection.save_config()
        print(saving +'\n--------------------- Succesful-- Saving-------------------------')
        connection.disconnect()
#############################################################################################
                                      #BUCKUPS
#############################################################################################
def backups(device):
        ip = device [0]
        name = device [1]
        connection = ssh_connection(device)
        Backup = connection.send_command("show running-config")
        file = open("%s_backup.txt" %name ,"w")
        file.write(Backup)
        file.close()
        print(Back.GREEN+"\nBackup for %s is done" %name + Style.RESET_ALL)
        connection.disconnect()



#############################################################################################
                                    #CHECK INTERFACE
#############################################################################################
def check_interfaces(device):
    ip = device[0]
    name = device[1]
    connection=ssh_connection(device)
    print (Back.GREEN+'\nconnection to  %s ' %name +' is up' +Style.RESET_ALL)
    output_one = connection.send_command('show int', use_textfsm=True)
    output_two = connection.send_command('show ip int br', use_textfsm=True)
    output_three = connection.send_command('show version', use_textfsm=True)
    i = 0
    table_data = [[device[1]+'=>'+output_three[0]['version'], 'Interface', 'IP-Address', 'Protocol', 'Status', 'Uptime',
    'In Error', 'In Pckts', 'Out Error', 'Out Pckts']]
    while i < len(output_one):
        int_info = [device[1], output_two[i]['intf'], output_two[i]['ipaddr'], 
        output_two[i]['proto'], output_two[i]['status'], output_three[0]['uptime'],
        output_one[i]['input_errors'], output_one[i]['input_packets'], 
        output_one[i]['output_errors'], output_one[i]['output_packets']]
        int_info[1] = int_info[1].replace('GigabitEthernet', 'Gi')
        if int_info[4] == 'administratively down':
            int_info[4] = int_info[4].replace('administratively down', 'ad-down')
        table_data.append(int_info)
        i = i + 1
    print(tabulate(table_data, headers="firstrow", tablefmt="fancy_grid", stralign="center", numalign="center"))
    return table_data



#############################################################################################
                                    #CHECK ROUTING
#############################################################################################
def check_routing(device):
        ip = device[0]
        name = device[1]
        connection=ssh_connection(device)
        software_ver = check_version(connection)
        print (Back.GREEN+'\nconnection to  %s ' %name +' is up'+ Style.RESET_ALL)
        output_one =connection.send_command('show ip route', use_textfsm=True)
        output_two =connection.send_command('sh ip ospf database', use_textfsm=True)
        output_three =connection.send_command('sh ip ospf neighbor', use_textfsm=True)
        if len(output_three) < 1:
                output_three = [{'address':'No neighbor'}]
        i = 0
        table_one = [['Ospf\nR-table=>'+device[1], 'Network', 'Mask', 'Next-Hop', 'Protocol', 'Neighbor']]
        while i < len(output_one):
                tt = ['', output_one[i]['network'], output_one[i]['mask'], output_one[i]['nexthop_if'],
                output_one[i]['protocol'], output_three[0]['address']]
                table_one.append(tt)
                i = i + 1
        print(tabulate(table_one, headers="firstrow", stralign="center", numalign="center", tablefmt="fancy_grid"))
        table_two = [['Ospf\nData-base=>'+device[1], 'adv_router', 'age', 'area', 'link_count', 'link_id', 'process_id', 'router_id']]
        if len(output_two) > 0:
                j = 0 
                while j < len(output_two):
                        tt = ['', output_two[j]['adv_router'], output_two[j]['age'], output_two[j]['area'],
                        output_two[j]['link_count'], output_two[j]['link_id'], output_two[j]['process_id'], output_two[j]['router_id']]
                        table_two.append(tt)
                        j = j + 1
        print(tabulate(table_two, headers="firstrow", stralign="center", numalign="center", tablefmt="fancy_grid"))
        return table_one, table_two
############################################################################################
                                    #CHECK VLAN
############################################################################################
def check_vlan(device):
    ip = device[0]
    name = device[1]
    connection=ssh_connection(device)
    software_ver = check_version(connection)
    if software_ver == 'vios_l2-ADVENTERPRISEK9-M':
        print (Back.GREEN+'\nconnection to  %s ' %name +' is up'+ Style.RESET_ALL)
        output_one =connection.send_command('show vlan', use_textfsm=True)
        output_two =connection.send_command('show vtp status', use_textfsm=True)
        i = 0
        vlan_data = [[device[1], 'Interfaces', 'Name', 'Status', 'Vlan id', 'VTP-Mode']]
        while i < len(output_one):
                int_info = ['', output_one[i]['interfaces'], output_one[i]['name'],
                output_one[i]['status'], output_one[i]['vlan_id'], output_two[0]['mode']]
                int_info[1] = ','.join(int_info[1])
                vlan_data.append(int_info)
                i = i + 1
        print(tabulate(vlan_data, headers="firstrow", stralign="center", numalign="center", tablefmt="fancy_grid"))
    else:
        vlan_data = [['this option can not'], ['be reported']]
    return vlan_data 
#############################################################################################
                                    #CSV REPORTING
#############################################################################################
def reporting():
        with open('Global_report.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['CHECKING NETWORK IN: ',str(datetime.now())])
                writer.writerow([''])
                print('\nGenerating a global report of the network ...')
                for device in devices_list:
                        name = device[1]
                        print (Back.GREEN+'\nconnection to  %s for reporting' %name + Style.RESET_ALL)
                        writer.writerow([''])
                        writer.writerow(['THIS IS A SPREADSHEET', 'TO GET INTERFACES INFOS FROM %s' %name])
                        writer.writerow([''])
                        writer.writerows(check_interfaces(device))
                        rout_info= check_routing(device)
                        writer.writerow([''])
                        writer.writerow(['THIS IS A SPREADSHEET', 'TO GET ROUTING INFOS FROM %s' %name])
                        writer.writerow([''])
                        writer.writerows(rout_info[0])
                        writer.writerow([''])
                        writer.writerows(rout_info[1])
                        writer.writerow([''])
                        writer.writerow(['THIS IS A SPREADSHEET', 'TO GET VLAN INFOS FROM %s' %name])
                        writer.writerow([''])
                        writer.writerows(check_vlan(device))
                        writer.writerow([''])
        print('Reporting Done')


#############################################################################################
                                     #UI MENU
#############################################################################################           

def main():
    main_menu_title = 12 *'*'+Back.CYAN+" 'WELCOME TO THE NETWORK MANAGEMENT PLATFORM MAIN MENU' "+Style.RESET_ALL+ 12 *'*' +"\n"
    main_menu_items = ["NETWORK CONFIGURATION", "NETWORK VERIFICATION","NETWORK CONFIRMATION", "CHECKING NETWORK", "QUIT"]
    main_menu_exit = False
    main_menu = TerminalMenu(menu_entries=main_menu_items, title=main_menu_title)

    conf_menu_title = 24*'*'+Back.CYAN+"'NETWORK CONFIGURATION SECTION'"+Style.RESET_ALL+24*'*'+"\n"
    conf_menu_items = ["CONFIG ALL DEVICES", "CONFIG SPECIFIC DEVICES", "BACK TO MAIN MENU"]
    conf_menu_back = False
    conf_menu = TerminalMenu(conf_menu_items, title=conf_menu_title)

    ver_menu_title = 24*'*'+Back.CYAN+"'NETWORK VERIFICATION SECTION'"+Style.RESET_ALL+24*'*'+"\n"
    ver_menu_items = ["VERIFY All DEVICES","VERIFY SPECIFIC DEVICES", "TEST CONNECTION", "BACK TO MAIN MENU"]
    ver_menu_back = False
    ver_menu = TerminalMenu(ver_menu_items, title=ver_menu_title)

    com_menu_title = 24*'*'+Back.CYAN+"'NETWORK CONFIRMATION SECTION'"+Style.RESET_ALL+24*'*'+"\n"
    com_menu_items = ["CONFIRMATION", "BUCKUPS", "BACK TO MAIN MENU"]
    com_menu_back = False
    com_menu = TerminalMenu(com_menu_items, title=com_menu_title)

    ch_menu_title = 24*'*'+Back.CYAN+"'CHECK NETWORK SECTION'"+Style.RESET_ALL+24*'*'+"\n"
    ch_menu_items = ["CHECK INTERFACES", "CHECK ROUTING", "CHECK VLAN", "CSV REPORTING","BACK TO MAIN MENU"]
    ch_menu_back = False
    ch_menu = TerminalMenu(ch_menu_items, title=ch_menu_title)


    while not main_menu_exit:
        os.system('clear')
        main_sel = main_menu.show()
        if main_sel == 0:
            while not conf_menu_back:
                os.system('clear')
                conf_sel = conf_menu.show()
                if conf_sel == 0:
                    print("\nConfig All Devices Has Been Selected")
                    ''' Multithreading Integration'''
                    startTime = time()
                    threads=[]
                    for device in devices_list:
                       t = Thread(target=configuration, args= (device,))
                       t.start()
                       threads.append(t)
                    for t in threads:
                       t.join()
                    print("\ntime in second is = ", time() - startTime)
                    for device in devices_list:
                        configuration(device=device)
                    print("time in second is = ", time() - startTime)
                    sleep(60)
                elif conf_sel == 1:
                    print("\nConfig Specific Devices Has Been Selected")
                    devices = device_input()
                    for device in devices:
                        configuration(device)
                elif conf_sel == 2:
                    conf_menu_back = True
                    print("\nBack Selected")
            conf_menu_back = False
        elif main_sel == 1:
            while not ver_menu_back:
                os.system('clear')
                ver_sel = ver_menu.show()
                if ver_sel == 0:
                    print("\nVerify All Devices Has Been Selected")
                    for device in devices_list:
                        verification(device)
                    sleep(60)
                elif ver_sel == 1:
                    print("\nVerify Specific Devices Has Been Selected")
                    devices = device_input()
                    for device in devices:
                        verification(device)
                    sleep(50)
                elif ver_sel == 2:
                    print("\nTest Connection Has Been Selected")
                    print(Back.CYAN + "\nGet source ip =>:" +Style.RESET_ALL)
                    source_ip = device_input()
                    print(Back.CYAN + "\nGet destination ip =>:" +Style.RESET_ALL)
                    destination_ip = device_input()
                    for source in source_ip :
                        print(Back.YELLOW + '\nConnection to %s' %source[1] +'\n'+Style.RESET_ALL)
                        connection = ssh_connection(source)
                        for destination in destination_ip:
                            test_connection(source, destination, connection)
                        sleep(60)
                elif ver_sel == 3:
                    ver_menu_back = True
                    print("\nBack Selected")
            ver_menu_back = False
        elif main_sel == 2:
            while not com_menu_back:
                os.system('clear')
                com_sel = com_menu.show()
                if com_sel == 0:
                    print("\nConfirm All Devices Has Been Selected")
                    for device in devices_list:
                        confirmation(device)
                    sleep(20)
                elif com_sel == 1:
                    print("\nBackups Has Been Selected")
                    for device in devices_list:
                        backups(device)
                    sleep(20)
                elif com_sel == 2:
                    com_menu_back = True
                    print("\nBack Selected")
            com_menu_back = False
        elif main_sel == 3:
            while not ch_menu_back:
                os.system('clear')
                ch_sel = ch_menu.show()
                if ch_sel == 0:
                    print("\nCheck interfaces Has Been Selected")
                    for device in devices_list:
                        check_interfaces(device)
                    sleep(20)
                elif ch_sel == 1:
                    print("\nCheck Routing Has Been Selected")
                    for device in devices_list:
                        check_routing(device)
                    sleep(20)
                elif ch_sel == 2:
                    print("\nCheck Vlan Has Been Selected")
                    for device in devices_list:
                        check_vlan(device)
                    sleep(20)
                elif ch_sel == 3:
                    print("\nCSV Reporting Has Been Selected")
                    reporting()
                elif ch_sel == 4:
                    ch_menu_back = True
                    print("\nBack Selected")
            ch_menu_back = False
        elif main_sel == 4:
            main_menu_exit = True
            print("\nQuit System Has Been Selected")


###################################################################################################
                                        #MAIN PROGRAMME
###################################################################################################

if __name__ == "__main__":
        startTime = time()
        with open('switch_config_file') as f:
                switch_config_file = f.read().splitlines()
        with open('router_config_file') as f:
                router_config_file = f.read().splitlines()
        with open('devices_file', 'r') as f:
                reader = csv.reader(f)
                devices_list = [d for d in reader]

        while True:
                username = getpass.getpass(prompt='Username: ')
                password = getpass.getpass(prompt='Password: ')
                if username.lower() == 'Akatsuki'and password =='Rasengan':
                        break
                else: 
                        print('The answer entered by you is incorrect..!!!') 
        main()

