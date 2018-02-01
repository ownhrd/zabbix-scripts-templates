#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Igor Sidorenko"
__email__ = "neither89@gmail.com"
__status__ = "Testing"

# Work with networkx (1.11) and only Arista device

import napalm
import networkx as nx
import optparse
import sys
import re
from pyzabbix import ZabbixAPI

parser = optparse.OptionParser()
parser.add_option('-u', '--username', help="Zabbix username", default="admin")
parser.add_option('-p', '--password', help="Zabbix password", default="zabbix")
parser.add_option('-s', '--host', help="Host To talk to the web api", default="localhost")
parser.add_option('-d', '--path', help="Path", default="/zabbix/")
parser.add_option('-g', '--groupname', help="Host group in Zabbix")
parser.add_option('-r', '--protocol', help="Zabbix protocol to be used", default="http")
parser.add_option('-c', '--api_username', help="API username", default="zabbix_map_user")
parser.add_option('-k', '--api_password', help="API password", default="zabbix_map_password")
parser.add_option('-f', '--mapfile', help=".dot graphviz file for imput", default="data.dot")
parser.add_option('-m', '--mapname', help="Map name to put into zabbix")
(options,args)=parser.parse_args()

if not options.groupname:
    print "Must have a group name!"
    parser.print_help()
    sys.exit(-1)

if not options.mapname:
    print "Must have a map name!"
    parser.print_help()
    sys.exit(-1)

def main(host):
    driver = napalm.get_network_driver('eos')
    device = driver(hostname=host, username=options.api_username,
                    password=options.api_password)
    try:
        device.open()
        lldpGet(device, host)
    except:
        device.close()

def api_connect():
    zapi = ZabbixAPI(options.protocol + "://" + options.host + options.path)
    zapi.login(options.username, options.password)
    return zapi

def group_id_lookup():
    group_id = zapi.hostgroup.get(filter={"name" : options.groupname})
    if group_id:
        return str(group_id[0]['groupid'])

def host_id_lookup():
    host_id = zapi.host.get(groupids=group_id, output=["hostid", "name", "status"], filter={"status": "0"})
    for host in host_id:
        hostid_list.append(host['hostid'])

def host_ip_lookup():
    host_ip = zapi.hostinterface.get(hostids=hostid_list)
    for host in host_ip:
        hosts.append(host['ip'])

def icons_get():
	icons = {}
	iconsData = zapi.image.get(output=["imageid","name"])
	for icon in iconsData:
		icons[icon["name"]] = icon["imageid"]
	return icons

def host_lookup(hostname):
    hostid = zapi.host.get(filter={"host": hostname})
    if hostid:
        return str(hostid[0]['hostid'])

def map_lookup(mapname):
    mapid = zapi.map.get(filter={"name": mapname})
    if mapid:
        return str(mapid[0]['sysmapid'])

def trigger_id_lookup(host, port, triggerkey):
    triggerids = []
    description = zapi.trigger.get(output=["triggerid", "description"], filter={"host": host})
    for triggerid in description:
        a, b = triggerkey.split(",")
        if re.search(port + r'\b', triggerid['description']) and re.search(a + r'\b',triggerid['description']) and re.search(b + r'\b',triggerid['description']):
            triggerids.append(str(triggerid['triggerid']))
    return triggerids

# Get lldp from device and write to data.dot

def lldpGet(device, host):
    get_hostname = device.get_facts()['hostname']
    lldp_neighbors = device.get_lldp_neighbors()

    if get_hostname.startswith('dc1-lab-sw'):
        dot.write('"{0}" [hostname="{0}" zbximage="{2}" label="{1}"]\n'.format(get_hostname,host,sw_icon))
        for key in lldp_neighbors.keys():
            format_key = lldp_neighbors[key]
            if host_lookup(format_key[0]['hostname']):
                for get_id1 in trigger_id_lookup(format_key[0]['hostname'], format_key[0]['port'], triggerkey1):
                    if get_id1:
                        dot.write('"{0}" -- "{1}"  [triggerid1="{3}" label="In: {{{1}:ifInOctets[{2}].last()}}\nOut: {{{1}:ifOutOctets[{2}].last()}}"]\n'.format(get_hostname,format_key[0]['hostname'],format_key[0]['port'],get_id1))

    if get_hostname.startswith('dc1-lab-csw'):
        dot.write('"{0}" [hostname="{0}" zbximage="{2}" label="{1}"]\n'.format(get_hostname,host,csw_icon))
        for key in lldp_neighbors.keys():
            format_key = lldp_neighbors[key]
            if host_lookup(format_key[0]['hostname']):
                for get_id1 in trigger_id_lookup(format_key[0]['hostname'], format_key[0]['port'], triggerkey1):
                    if get_id1:
                        dot.write('"{0}" -- "{1}"  [triggerid1="{3}" label="In: {{{1}:ifInOctets[{2}].last()}}\nOut: {{{1}:ifOutOctets[{2}].last()}}"]\n'.format(get_hostname,format_key[0]['hostname'],format_key[0]['port'],get_id1))

    device.close()

if __name__ == '__main__':

    # Image name in Zabbix
    sw_icon = "Router_symbol_(96)"
    csw_icon = "Switch_(96)"
    
    # Two key world in Zabbix trigger name separated by commas
    triggerkey1 = "Operational, status"
    triggerkey2 = ""

    hostid_list = []
    hosts = []

    zapi = api_connect()
    group_id = group_id_lookup()
    host_id = host_id_lookup()
    host_ip = host_ip_lookup()
    dot = open(options.mapfile, "w")
    dot.write("graph lldp2dot2zabbix {\n")
    dot.write("graph [layout=dot overlap=false sep=\"+6\" splines=true]\n")
    dot.write("node [shape=box fixedsize=true width=1 height=1]\n")

    for host in hosts:
        main(host)

    dot.write("}")
    dot.close()

# Part of the code is taken from https://github.com/jasonmcintosh/zabbix-map-creation

"""
Creates a Zabbix map from a Dot file
zbximage and hostname are custom attributes that can be attached to nodes.
Nodes with a hostname attribute are considered Zabbix hosts and looked up
for. Other nodes are treated as images. zbximage and label can be used there.
Edges have their color and label attributes considered.
This script is meant as an example only!
"""

width = 1920
height = 1280

ELEMENT_TYPE_HOST = 0
ELEMENT_TYPE_MAP = 1
ELEMENT_TYPE_TRIGGER = 2
ELEMENT_TYPE_HOSTGROUP = 3
ELEMENT_TYPE_IMAGE = 4

ADVANCED_LABELS = 1
LABEL_TYPE_LABEL = 0

#TODO: Available images should be read via the API instead

icons = {
    "router": 130,
    "cloud": 26,
    "desktop": 27,
    "laptop": 28,
    "server": 106,
    "database": 20,
    "sat": 30,
    "tux": 31,
    "default": 40,
    "house":34
}

colors = {
    "purple": "FF00FF",
    "green": "00FF00",
    "default": "00FF00",
}

# Use bold line in links
drawtype = 2

# Convert your dot file to a graph
G = nx.drawing.nx_agraph.read_dot(options.mapfile)

# Use an algorithm of your choice to layout the nodes in x and y
pos = nx.drawing.nx_agraph.graphviz_layout(G)

# Find maximum coordinate values of the layout to scale it better to the desired output size
#TODO: The scaling could probably be solved within Graphviz
# The origin is different between Zabbix (top left) and Graphviz (bottom left)
# Join the temporary selementid necessary for links and the coordinates to the node data
poslist = list(pos.values())
maxpos = map(max, zip(*poslist))
    
for host, coordinates in pos.iteritems():
   pos[host] = [int(coordinates[0]*width/maxpos[0]*0.75-coordinates[0]*0.1), int((height-coordinates[1]*height/maxpos[1])*0.65+coordinates[1]*0.1)]
nx.set_node_attributes(G,'coordinates',pos)

selementids = dict(enumerate(G.nodes_iter(), start=1))
selementids = dict((v,k) for k,v in selementids.iteritems())
nx.set_node_attributes(G,'selementid',selementids)

# Prepare map information
map_params = {
    "name": options.mapname,
    "label_format": ADVANCED_LABELS,
    "label_type_image": LABEL_TYPE_LABEL,
    "width": width,
    "height": height
}

element_params = []
link_params = []

icons = icons_get()

# Prepare node information
for node, data in G.nodes_iter(data=True):
    # Generic part
    map_element = {}
    map_element.update({
            "selementid": data['selementid'],
            "x": data['coordinates'][0],
            "y": data['coordinates'][1],
            "use_iconmap": 0,
            })

    if "hostname" in data:
        map_element.update({
                "elementtype": ELEMENT_TYPE_HOST,
                "elementid": host_lookup(data['hostname'].strip('"')),
                "iconid_off": icons['Router_symbol_(128)'],
                })
    elif "map" in data:
        map_element.update({
		"elementtype": ELEMENT_TYPE_MAP,
		"elementid": map_lookup(data['map'].strip('"')),
                "iconid_off": icons['Cloud_(96)'],
                })
		
    else:
        map_element.update({
            "elementtype": ELEMENT_TYPE_IMAGE,
            "elementid": 0,
        })
    # Labels are only set for images
    # elementid is necessary, due to ZBX-6844
    # If no image is set, a default image is used
    if "label" in data:
        map_element.update({
            "label": data['label'].strip('"')
        })
    if "zbximage" in data:
        map_element.update({
            "iconid_off": icons[data['zbximage'].strip('"')],
        })
    elif "hostname" not in data and "zbximage" not in data:
        map_element.update({
            "iconid_off": icons['Cloud_(96)'],
        })

    element_params.append(map_element)

# Prepare edge information -- Iterate through edges to create the Zabbix links,
# based on selementids
nodenum = nx.get_node_attributes(G,'selementid')
for nodea, nodeb, data in G.edges_iter(data=True):
    link = {}
    link.update({
        "selementid1": nodenum[nodea],
        "selementid2": nodenum[nodeb],
        })

    if "color" in data:
        color =  colors[data['color'].strip('"')]
        link.update({
            "color": color
        })
    else:
        link.update({
            "color": colors['default']
        })

    if "label" in data:
        label =  data['label'].strip('"')
        link.update({
            "label": label,
            "drawtype": drawtype,
        })

    if "triggerid1" in data:
        triggerid1 = data['triggerid1'].strip('"')
        link.update({
            "linktriggers": [
            {"triggerid": triggerid1,
             "color": "FFA500",
             "drawtype": drawtype}
            ],
        })

    if "triggerid2" in data:
        triggerid2 = data['triggerid2'].strip('"')
        link.update({
            "linktriggers": [
            {"triggerid": triggerid2,
             "color": "FF0000",
             "drawtype": drawtype}
            ],
        })

    link_params.append(link)

# Join the prepared information
map_params["selements"] = element_params
map_params["links"] = link_params
    
# Get rid of an existing map of that name and create a new one
del_mapid = zapi.map.get(filter={"name": options.mapname})
if del_mapid:
	zapi.map.update({"sysmapid":del_mapid[0]['sysmapid'], "links":[], "selements":[], "urls":[] })
	map_params["sysmapid"] = del_mapid[0]['sysmapid']
	#del map_params["name"]
	#del map_params["label_format"]
	#del map_params["label_type_image"]
	#del map_params["width"]
	#del map_params["height"]
	map = zapi.map.update(map_params)
else:
	map = zapi.map.create(map_params)
