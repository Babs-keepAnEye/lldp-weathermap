#!/usr/bin/python
#This program will produce a .conf file that holds the necessary headings/nodes/links
#The node positions are currently decided by their name any changes to or new node names will result in the nodes being missed
#The link thickness (representing the connection speed) only represents 40GB or 1Gb

# To use this take the ConfigFile that produces and overwrite the existing configfile in /opt/observium/html/weathermap/configs

#Uses information retrieved by lldp protocol stored in a database on observium.gridpp.rl.ac.uk

#If any naming conventions are changed or new nodes want to be displayed there are 3 things that need updating
#1) SQL search on line 122 modify the where statements (currently anything with swt or rtr-x in its name is included but anything with note[swt and then 7 then t is excluded].
#2) from line 148 will decide where the node is placed on the bottom row. 3) SQL search on line 258 modify the where statements (currently links a combination of with swt or rtr in the name is selected)


import MySQLdb as mdb
import fnmatch
import math

def main(config):
    placer_list = []
    name = []
    if_gone = []
    if_gone_reverse = []
    check = 0
    primary_key = 0

    no7 = 0
    no6 = 0
    no5 = 0
    no4 = 0
    no3 = 0
    no2 = 0
    no1 = 0

    # Connects to the observium database

    con = mdb.connect(
        config.get('database', 'hostname'),
        config.get('database', 'username'),
        config.get('database', 'password'),
        config.get('database', 'schema'),
    )


    file0 = open(config.get('weathermap', 'filename'), 'w')

    header = open('header.txt').read()

    #Writesthe header of the config file
    file0.write(header)





    with con:

        cur = con.cursor()

        cur.execute( " select hostname, ifSpeed from devices join ports on devices.device_id = ports.device_id where (hostname like ('swt%') and hostname not like ('swt%7%t%') ) or (hostname like ('%rtr-x%')) group by hostname"   )

        rows = cur.fetchall()

        for row in rows:
            row = str(row)

            compos = row.find(",")
            dotpos   = row.find(".")


            #removes the .pcs... at the end of name if present
            if dotpos > 1:
                hostname = (row[2:dotpos])

            else:
                hostname = (row[2:compos-1])

            speed = row[compos+2:len(row)-2]

    #Finds an identifiable part of any switch the is worth watching
    #To make spacing even between nodes they are assigned row so the number in each can be counted

    #The placer_list holds a value which coresponds to which row the node should be placed
    #No_ is used to count the ammount of nodes in a row

            if "swt-z9000" in hostname:
                name.append(hostname)
                placer_list.append(1)
                no1 = no1 +1

            #This is for the current switches with a 40Gb link

            elif "swt-s4810" in hostname and speed == "10000000000":
                name.append(hostname)
                placer_list.append(2)
                no2 = no2+1

            elif "swt-s4810" in hostname:
                name.append(hostname)
                placer_list.append(3)
                no3 = no3+1

            elif "s60" in hostname:
                name.append(hostname)
                placer_list.append(5)
                no5 = no5+1

            elif "swt-5" in hostname:
                name.append(hostname)
                placer_list.append(6)
                no6 = no6+1

            elif "rtr" in hostname:
                name.append(hostname)
                placer_list.append(7)
                no7 = no7 +1

            else :
                name.append(hostname)
                placer_list.append(4)
                no4 = no4+1


    #Works out how many pixels to put between each node on a row
    #Iteration could have been used but this was just easier than thinking of how to set it up
    S1 = 1800/no1
    S2 = 1800/no2
    S3 = 1800/no3
    S4 = 1800/no4
    S5 = 1800/no5
    S6 = 1800/no6
    S7 = 1800/no7

    #0.5 will produce an equal between the end and start

    no7 = float(0.5)
    no5 = float(0.5)
    no6 = float(0.5)
    no4 = float(0.5)
    no3 = float(0.5)
    no2 = float(0.5)
    no1 = float(0.5)


    #This writes all the infomation for NODES to the confing file
    #The str(int( is used as decimals in the config file will stop the nodes being placed

    for current in range(0,len(name)):


        file0.write("NODE " + str(name[current]) + "\n")
        file0.write("    LABEL " + str(name[current]) +"\n")

        if placer_list[current] == 1:
            file0.write("    ICON images/network-switch-qsfp-128.png\n")
            file0.write("    POSITION " + str(int(S1 * no1)) + " 300\n")
            no1 = no1 + 1

        elif placer_list[current] == 2:
            file0.write("    ICON images/network-switch-sfp-96.png \n")
            file0.write("    POSITION " + str(int(S2 * no2)) + "  500\n")
            no2 = no2 + 1

        elif placer_list[current] == 3:
            file0.write("    ICON images/network-switch-sfp-96.png \n")
            file0.write("    POSITION " + str(int(S3 * no3)) + " 600\n")
            no3 = no3 + 1

        elif placer_list[current] == 4:
            file0.write("    ICON images/network-hub-generic.png\n")
            file0.write("    POSITION " + str(int(S4 * no4)) + " 800\n")
            no4 = no4+ 1

        elif placer_list[current] == 5:
            file0.write("    ICON images/network-hub-generic.png\n")
            file0.write("    POSITION " + str(int(S5 * no5)) + " 700\n")
            no5 = no5+ 1

        elif placer_list[current] == 6:
            file0.write("    ICON images/network-hub-generic.png\n")
            file0.write("    POSITION " + str(int(S6 * no6)) + " 750\n")
            no6 = no6+ 1

        elif placer_list[current] == 7:
            file0.write("    ICON images/network-router-blue.png\n")
            file0.write("    POSITION " + str(int(S7 * no7)) + " 100\n")
            no7 = no7+ 1

        file0.write("\n")



    #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #This part deals with the links

    with con:

        cur = con.cursor()

        f=cur.execute( "select links.remote_hostname, devices.hostname, links.local_port_id, ifSpeed, ifIndex, devices.device_id,port_id from links join ports on ports.port_id=links.local_port_id join devices on devices.device_id=ports.device_id where (remote_hostname like ('%swt%') and hostname like ('%swt%')) or (hostname like ('%rtr%') and (remote_hostname like ('%swt%') or remote_hostname like ('%rtr%')))")
        rows = cur.fetchall()

        for row in rows:

            row = str(row)

            # remove the .pscs... / splits the many components up

            compos = row.find(",")

            First = row[2:compos-1]

            if "pscs" in First:
                First = First[0:(len(First))-14]

            row = row[compos+3:len(row)]
            compos = row.find(",")

            Second = row[0:compos-1]
            SecondRaw = Second
            if "pscs" in Second:
                Second = Second[0:(len(Second))-14]

            row = row[compos+2:len(row)]
            compos = row.find(",")

            graphNo = row[0:compos-1]

            row = row[compos+2:len(row)]
            compos = row.find(",")

            speed = row[0:compos-1]

            row = row[compos+2:len(row)]
            compos = row.find(",")

            ifIndex = row[0:compos-1]

            row = row[compos+2:len(row)]
            compos = row.find(",")

            deviceId = row[0:len(row)-2]

            row = row[compos+2:len(row)]
            compos = row.find(",")

            port_id = row[0:len(row)-1]



            #writes all the lines to file

            Names = First + Second

            #'used to check if the link has already happend in reverse (from the other nodes perspective )

            NamesRev = Second + First

            if Names in if_gone_reverse:
                check = check +1 # seeing what is rejected (no effect on anything)
           #/opt/observium/rrd/swt-s4810p-0b/port-7173101.rrd

            else :
                file0.write("LINK " + First + "-" + Second + "-" + str(primary_key) +  "\n")
                if "40000000000" in speed:
                    file0.write("    WIDTH 4\n")
                file0.write("    OVERLIBGRAPH /graph.php?height=100&width=512&id=" + graphNo + "&type=port_bits&legend=no \n")
                file0.write("    INFOURL /device/device=" + deviceId + "/tab=port/port=" + graphNo + "/\n")
                file0.write("    TARGET /opt/observium/rrd/" + SecondRaw + "/port-" + ifIndex + ".rrd:INOCTETS:OUTOCTETS\n")
                if Names in if_gone:
                    file0.write("    NODES " + Second + ":10:10 " + First + ":10:10\n")
                else:
                    file0.write("    NODES " + Second + ":-10:-10 " + First + ":-10:-10\n")
                if "40000000000" in speed:
                    file0.write("    BANDWIDTH 40G\n\n")
                else :
                    file0.write("\n")

                #The primary key is used in the LINK line to stop links from being deleted as they had the same name
                #As some nodes will have 2 links connecting them

                primary_key = primary_key +1
                if_gone.append(Names)
                if_gone_reverse.append(NamesRev)

    file0.close()

if __name__ == "__main__":
    from ConfigParser import SafeConfigParser
    config = SafeConfigParser()
    config.readfp(open('makeweathermap.defaults'))
    config.read(['makeweathermap.cfg'])
    main(config)
