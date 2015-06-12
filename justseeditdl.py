#!/usr/bin/python3.4
import pprint, os, re, logging, sys, requests, math
import urllib.request
import urllib.parse
from xml.dom.minidom import parseString

KEY = "xxxxxxxxxxxxxxxxxxxxxxxxx"
PATH = "/storage/jsdownloads/"
LOG_FILENAME = "/var/log/jslog.log"

mlogger = logging.getLogger('jsdownall')
mlogger.setLevel(logging.INFO)

handler = logging.FileHandler(LOG_FILENAME)
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

mlogger.addHandler(handler)

def api_call(instruc, params):

    if params != "":
      url = 'https://api.justseed.it' + instruc + "api_key=" + KEY + "&" + params
    else:
      url = 'https://api.justseed.it' + instruc + "api_key=" + KEY

    mlogger.info("Retrieving URL [" + url + "]")

    with urllib.request.urlopen(url) as response:
      xml = response.read()

    return xml


def convertSize(size):
    size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size,1024)))
    p = math.pow(1024,i)
    s = round(size/p,2)
    if (s > 0):
       return '%s %s' % (s,size_name[i])
    else:
       return '0B'


def download_file(url):
    local_filename = url.split('/')[-1]
    file_path = PATH + local_filename
    r = requests.get(url, stream=True)

    with open(file_path, 'wb') as f:
        file_size = 0
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: 
                file_size = file_size + 1024
                f.write(chunk)
                f.flush()
    return file_size


def get_files(fulldom):
  dom = parseString(fulldom)

  urllist = dom.getElementsByTagName('url')

  i = 0 
  for a in urllist:
    u = a.firstChild.data
    url = urllib.parse.unquote(u)
    m = re.search("(ample.*)", url)
    if m:
      mlogger.info("url [" + url + "] matches \"ample\" skipping")
    else:
      mlogger.info("Writing [" + url + "]")
      size_downloaded = download_file(url)
      mlogger.info("Wrote [" + convertSize(size_downloaded) + "]")
      
  return True

def parse_list(fulldom):
  dom = parseString(fulldom)

  namelist = dom.getElementsByTagName('name')
  info_hashlist = dom.getElementsByTagName('info_hash')
  statuslist = dom.getElementsByTagName('status')
  percent = dom.getElementsByTagName('percentage_as_decimal')

  tors = {}

  i = 0
  for a in namelist:
    tors.update({i : { 'name' : a.firstChild.data}})
    i = i + 1

  i = 0
  for a in info_hashlist:
    tors.update({i : { 'hash' : a.firstChild.data, 'name' : tors[i]['name']}})
    i = i + 1

  i = 0
  for a in percent:
    tors.update({i : { 'percent' : a.firstChild.data, 'name' : tors[i]['name'], 'hash' : tors[i]['hash'] }})
    i = i + 1

  i = 0
  for a in statuslist:
    if a.firstChild.data == "SUCCESS":
      next
    else:
      mlogger.info("Adding [" + tors[i]['name'] + "] with hash [" + tors[i]['hash'] + "] and status [" + a.firstChild.data + "] percent [" + tors[i]['percent'] + "]")  
      tors.update({i : { 'status' : a.firstChild.data, 'name' : tors[i]['name'], 'hash' : tors[i]['hash'], 'percent' : tors[i]['percent']}})
      i = i + 1

  return tors


if __name__ == '__main__':
  mlogger.info("Starting download")

  r = api_call("/torrents/list.csp?", "" )
  torrents = parse_list(r)

  for x in torrents:
    if torrents[x]['status'] == "stopped":
      if torrents[x]['percent'] == "0.0":
        mlogger.info(torrents[x]['name'] + " has percentage of [" + torrents[x]['percent'] + "] deleting torrent")
        params = "info_hash=" + torrents[x]['hash']
        r = api_call("/torrent/delete.csp?", params)
        continue
        
      if torrents[x]['percent'] != "100.0":
        mlogger.info(torrents[x]['name'] + " has percentage of [" + torrents[x]['percent'] + "] skipping")
        continue
      
      if torrents[x]['percent'] == "100.0": 
        params = "info_hash=" + torrents[x]['hash']
        r = api_call("/torrent/files.csp?", params)
        get_files(r)
        mlogger.info(torrents[x]['name'] + " download complete, deleting torrent")
        params = "info_hash=" + torrents[x]['hash']
        r = api_call("/torrent/delete.csp?", params)

  mlogger.info("Exiting gracefully")
  
