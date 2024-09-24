#!/usr/bin/python
'''
entrydns-updater.py ~ ajclarkson.co.uk

Updater for Dynamic DNS on EntryDNS Domains
Performs an update for each given domain access token in
the hosts.json file.
'''
import json
from urllib.request import urlopen
import requests
import os
from time import strftime
import sys

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__)) +"/"

def get_cached_ip():
	'''
	Retrieve Cached IP From File, cuts down on API requests to EasyDNS if
	IP Address hasn't changed.

	Returns: 
		cached_ip: Cached IP or 0 to force refresh of public IP
	'''
	try:
		cached_file = open(SCRIPT_PATH + '.entrydns-cachedip', 'r')
		cached_ip = cached_file.read()
		cached_file.close()
		return cached_ip
	except IOError:
		return "0"

def set_cached_ip(ip):
	'''
	Stores IP Address in the Cached

	Args:
		ip: Address to be Cached
	'''
	try:
		cached_file = open(SCRIPT_PATH + '.entrydns-cachedip', 'w')
		cached_file.write(ip)
		cached_file.close()
	except IOError as e:
		print(e)

def get_ip():
	'''
	Retrieves public IP (from httpbin) with cached IP and returns import

	Returns:
		Public IP as a string
	'''
	response = requests.get('https://api.ipify.org?format=json')
	ip_address = response.json()['ip']
	return ip_address

def load_hosts():
	'''
	Loads the hosts.json file containing access tokens for EasyDNS

	Returns: 
		A dictionary of hosts and access tokens, e.g 

		{'example-host':'678dxjvid928skf',
		 'example-host2':'8299fd0as88fd8d'}
	'''
	try:
		hosts_file = open(SCRIPT_PATH + 'hosts.json', 'r')
		hosts_data = json.load(hosts_file)
		return hosts_data
	except IOError as e:
		print(e)

def update_host(token):
	'''
	Formulate and Execute an Update request on EntryDNS API for a given access token / IP

	Args:
		token: (string) Access Token for an EntryDNS Domain
		current_ip: (string) IP to point EasyDNS Domain to

	Returns: 
		Status (Either OK, or Error + Code)
	'''
	url = 'https://entrydns.net/records/modify/%s' % token
	response = requests.post(url)
	if response.status_code == requests.codes.ok:
		return "OK"
	else:
		return "ERROR: Code %s" % response.status_code
	
def print_help():
	print(f"USAGE:\n\t{sys.argv[0]} [FLAGS]")
	print("FLAGS:")
	print("\t-h, --help\tDisplays this help message")
	print("\t-f, --force\tForces script to update EntryDNS entries (ignores cache)")

def parse_args():
	# check if any arguments were passed
	for arg in sys.argv[1:]:
		match arg:
			case "-h" | "--help":
				print_help()
				# terminate script if --help was passed
				sys.exit()
			case "-f" | "--force":
				global force_update # modify global var instead of creating a local one
				force_update = True
			case _:
				print(f"Error: unrecognized command-line option \'{arg}\'")
				print_help()
				# terminate script, if unrecognized arg was passed
				sys.exit()

# set defaults for variables
force_update = False

# main program execution
parse_args()
current_ip = get_ip()
cached_ip = get_cached_ip()
if cached_ip != current_ip or force_update:
	if force_update == True:
		print("forcing update")
	set_cached_ip(current_ip)
	hosts = load_hosts()
	for host in hosts:
		result = update_host(hosts[host])
		print("%s -- Updating %s: %s" % (strftime("%Y-%m-%d %H:%M:%S"),host, result))
else:
	print("%s -- Public IP Matches Cache (%s), Nothing to Do..." % (strftime("%Y-%m-%d %H:%M:%S"), current_ip))
