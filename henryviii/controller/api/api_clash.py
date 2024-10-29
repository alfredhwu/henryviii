from flask import Blueprint, current_app, jsonify, request

import json, yaml, requests, datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs
from base64 import b64decode

from henryviii.model import (
    off_account_user_category as model_off_account_user_category, 
    off_account as model
)

bp = Blueprint('api_clash', __name__)


def convert_srkt_clash_vmess(srkt_params):
  # print(srkt_params)
  proxy = {
    "name": srkt_params["ps"],
    "type": "vmess",
    "server": srkt_params["add"],
    "port": int(srkt_params["port"]),
    "uuid": srkt_params["id"],
    "cipher": srkt_params["scy"] if "scy" in srkt_params and len(srkt_params["scy"])>0 else "auto",
    "alterId": int(srkt_params["aid"]),
    "udp": True,
  }
  match srkt_params["net"]:
    case "tcp":
      if "type" not in srkt_params or srkt_params["type"] != "http":
        if proxy["server"] == "127.0.0.1":
          return proxy
        print("not normal format, please verify")
        print(srkt_params)
        return None
      # shadowrocket type = http
      proxy["network"] = "http"
      proxy["http-opts"] = {
        # "host": srkt_params["host"],
        "method": "GET",
        "path": srkt_params["path"].split(","),
        # "headers": {
        #   "Host": srkt_params["host"].split(","),
        #   "Connection": ["keep-alive"]
        # }
      }

    case "ws":
      proxy["network"] = "ws"
      proxy["ws-opts"] = {
        # "host": srkt_params["host"],
        "path": srkt_params["path"]
      }
    case _:
      print("not normal format, please verify")
      print(srkt_params)
      return None
  return proxy

def convert_srkt_clash_vless(srkt_params):
  proxy = {
    "name": srkt_params["fragment"],
    "type": "vless",
    "server": srkt_params["address"],
    "port": int(srkt_params["port"]),
    "uuid": srkt_params["user"],
    "tls": True,
    "udp": True,
  }
  match srkt_params["security"]:
    case "reality":
      proxy["network"] = "tcp"
      proxy["flow"] = srkt_params["flow"]
      proxy["servername"] = srkt_params["sni"]
      proxy["reality-opts"] = {
        "public-key": srkt_params["pbk"]
      }
      proxy["client-fingerprint"] = srkt_params["fp"]
    case _:
      print("not normal format, please verify")
      print(srkt_params)
      return None
  return proxy



def get_clash_config_content(proxy_list):
  proxy_name_list = []
  proxy_name_list_hk = []
  proxy_name_list_sg = []
  proxy_name_list_etc = []
  for proxy in proxy_list:
    proxy_name_list.append(proxy["name"])
    if "香港" in proxy["name"]:
      proxy_name_list_hk.append(proxy["name"])
    elif "新加坡" in proxy["name"]:
      proxy_name_list_sg.append(proxy["name"])
    else:
      proxy_name_list_etc.append(proxy["name"])

  updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  proxy_string = yaml.dump({
      "proxies": proxy_list,
      "proxy-groups": [
        {
          "name": "PROXY",
          "type": "select",
          "proxies": [f"♻️ 自动选择@{updated_at}", 'auto-hk', 'auto-sg', 'sel-other', 'DIRECT']
        },
        {
          "name": f"♻️ 自动选择@{updated_at}",
          "type": 'url-test',
          "url": 'http://www.gstatic.com/generate_204',
          "interval": 300,
          "tolerance": 50,
          "proxies": proxy_name_list
        },
        {
          "name": "auto-hk",
          "type": 'url-test',
          "url": 'http://www.gstatic.com/generate_204',
          "interval": 300,
          "tolerance": 50,
          "proxies": proxy_name_list_hk
        },
        {
          "name": "auto-sg",
          "type": 'url-test',
          "url": 'http://www.gstatic.com/generate_204',
          "interval": 300,
          "tolerance": 50,
          "proxies": proxy_name_list_sg
        },
        {
          "name": "sel-other",
          "type": 'select',
          "proxies": proxy_name_list_etc
        }
      ]
    }, allow_unicode=True, sort_keys=False)

  return f'''
# Port of HTTP(S) proxy server on the local end
# port: 7890

# Port of SOCKS5 proxy server on the local end
# socks-port: 7891

# Transparent proxy server port for Linux and macOS (Redirect TCP and TProxy UDP)
# redir-port: 7892

# Transparent proxy server port for Linux (TProxy TCP and TProxy UDP)
# tproxy-port: 7893

# HTTP(S) and SOCKS4(A)/SOCKS5 server on the same port
mixed-port: 7890

# authentication of local SOCKS5/HTTP(S) server
# authentication:
#  - "user1:pass1"
#  - "user2:pass2"

# Set to true to allow connections to the local-end server from
# other LAN IP addresses
# allow-lan: false

# This is only applicable when `allow-lan` is `true`
# '*': bind all IP addresses
# 192.168.122.11: bind a single IPv4 address
# "[aaaa::a8aa:ff:fe09:57d8]": bind a single IPv6 address
# bind-address: '*'

# Clash router working mode
# rule: rule-based packet routing
# global: all packets will be forwarded to a single endpoint
# direct: directly forward the packets to the Internet
mode: rule

# Clash by default prints logs to STDOUT
# info / warning / error / debug / silent
# log-level: info
log-level: warning

# When set to false, resolver won't translate hostnames to IPv6 addresses
# ipv6: false

# RESTful web API listening address
external-controller: 127.0.0.1:9090

# A relative path to the configuration directory or an absolute path to a
# directory in which you put some static web resource. Clash core will then
# serve it at `http://{{external-controller}}/ui`.
# external-ui: folder

# Secret for the RESTful API (optional)
# Authenticate by spedifying HTTP header `Authorization: Bearer ${{secret}}
# ALWAYS set a secret if RESTful API is listening on 0.0.0.0
# secret: ""

# Outbound interface name
# interface-name: en0

# fwmark on Linux only
# routing-mark: 6666

# Static hosts for DNS server and connection establishment (like /etc/hosts)
#
# Wildcard hostnames are supported (e.g. *.clash.dev, *.foo.*.example.com)
# Non-wildcard domain names have a higher priority than wildcard domain names
# e.g. foo.example.com > *.example.com > .example.com
# P.S. +.foo.com equals to .foo.com and foo.com
# hosts:
#   'cittadella.xyy': 127.0.0.1

# profile:
  # Store the `select` results in $HOME/.config/clash/.cache
  # set false If you don't want this behavior
  # when two different configurations have groups with the same name, the selected values are shared
  # store-selected: true

  # persistence fakeip
  # store-fake-ip: false

# DNS server settings
# This section is optional. When not present, the DNS server will be disabled.
dns:
  enable: true
  listen: 0.0.0.0:53
  # ipv6: false # when the false, response to AAAA questions will be empty

  # These nameservers are used to resolve the DNS nameserver hostnames below.
  # Specify IP addresses only
  default-nameserver:
    - 114.114.114.114
    - 8.8.8.8
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16 # Fake IP addresses pool CIDR
  use-hosts: true # lookup hosts and return IP record

  # search-domains: [local] # search domains for A/AAAA record

  # Hostnames in this list will not be resolved with fake IPs
  # i.e. questions to these domain names will always be answered with their
  # real IP addresses
  # fake-ip-filter:
  #   - '*.lan'
  #   - localhost.ptlogin2.qq.com

  # Supports UDP, TCP, DoT, DoH. You can specify the port to connect to.
  # All DNS questions are sent directly to the nameserver, without proxies
  # involved. Clash answers the DNS question with the first result gathered.
  nameserver:
    # - 114.114.114.114 # default value
    # - 8.8.8.8 # default value
    - 119.29.29.29
    - 223.5.5.5
    - tls://dns.rubyfish.cn:853 # DNS over TLS
    - https://1.1.1.1/dns-query # DNS over HTTPS
    - dhcp://en0 # dns from dhcp
    # - '8.8.8.8#en0'

  # When `fallback` is present, the DNS server will send concurrent requests
  # to the servers in this section along with servers in `nameservers`.
  # The answers from fallback servers are used when the GEOIP country
  # is not `CN`.
  # fallback:
  #   - tcp://1.1.1.1
  #   - 'tcp://1.1.1.1#en0'

  # If IP addresses resolved with servers in `nameservers` are in the specified
  # subnets below, they are considered invalid and results from `fallback`
  # servers are used instead.
  #
  # IP address resolved with servers in `nameserver` is used when
  # `fallback-filter.geoip` is true and when GEOIP of the IP address is `CN`.
  #
  # If `fallback-filter.geoip` is false, results from `nameserver` nameservers
  # are always used if not match `fallback-filter.ipcidr`.
  #
  # This is a countermeasure against DNS pollution attacks.
  # fallback-filter:
  #   geoip: true
  #   geoip-code: CN
  #   ipcidr:
  #     - 240.0.0.0/4
  #   domain:
  #     - '+.google.com'
  #     - '+.facebook.com'
  #     - '+.youtube.com'

  # Lookup domains via specific nameservers
  # nameserver-policy:
  #   'www.baidu.com': '114.114.114.114'
  #   '+.internal.crop.com': '10.0.0.1'

{ proxy_string }

rule-providers:
  # ads url list
  reject:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt"
    path: ./ruleset/reject.yaml
    interval: 86400

  # icloud services
  icloud:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt"
    path: ./ruleset/icloud.yaml
    interval: 86400

  # available apple services in mainland china
  apple:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt"
    path: ./ruleset/apple.yaml
    interval: 86400

  # available google services in mainland china
  google:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/google.txt"
    path: ./ruleset/google.yaml
    interval: 86400

  # proxy url list
  proxy:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt"
    path: ./ruleset/proxy.yaml
    interval: 86400

  # direct url list
  direct:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt"
    path: ./ruleset/direct.yaml
    interval: 86400

  # private url list
  private:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt"
    path: ./ruleset/private.yaml
    interval: 86400

  # gfw list
  gfw:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt"
    path: ./ruleset/gfw.yaml
    interval: 86400

  # top level domain names outside china
  tld-not-cn:
    type: http
    behavior: domain
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt"
    path: ./ruleset/tld-not-cn.yaml
    interval: 86400

  # telegram
  telegramcidr:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt"
    path: ./ruleset/telegramcidr.yaml
    interval: 86400

  # IP addr in China
  cncidr:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt"
    path: ./ruleset/cncidr.yaml
    interval: 86400

  # IP addr in LAN
  lancidr:
    type: http
    behavior: ipcidr
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt"
    path: ./ruleset/lancidr.yaml
    interval: 86400

  # apps that usually using direct link
  applications:
    type: http
    behavior: classical
    url: "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt"
    path: ./ruleset/applications.yaml
    interval: 86400

## rules using black-list mechanism
rules:
  # # by def using direct
  # - RULE-SET,direct,DIRECT
  # - RULE-SET,private,DIRECT
  # - RULE-SET,lancidr,DIRECT
  # - RULE-SET,cncidr,DIRECT
  # # applications set to direct
  # - RULE-SET,applications,DIRECT
  # - RULE-SET,apple,DIRECT
  # - RULE-SET,icloud,DIRECT
  # filter out ads
  - RULE-SET,reject,REJECT
  # proxy for selected urls
  - RULE-SET,tld-not-cn,PROXY
  - RULE-SET,gfw,PROXY
  - RULE-SET,telegramcidr,PROXY
  - MATCH,DIRECT

'''




@bp.route('/clash', methods=['GET'])
def subscribe_clash():
    # token = "9915d241a8ad054a2da67c8303a08ce2"
    token = request.args.get("token")
    current_app.logger.info("clash token is: " + token)
    url = f"https://cccc.v2ray.ws/api/subscribe?token={token}&flag=shadowrocket"
    server_list_base64 = requests.get(url).content
    proxy_list_with_vless = []
    proxy_status = ''
    for line in b64decode(server_list_base64).decode("utf-8").strip().split("\n"):
        # if "STATUS=" in line:
        #   proxy_status = line
        #   continue
        params = line.split("://")
        if len(params) == 0:
            continue
        match params[0]:
            case "vmess":
                server_param = json.loads(b64decode(params[1]).decode("utf-8"))
                proxy = convert_srkt_clash_vmess(server_param)
            case "vless":
                parsed_params = urlparse(params[1])
                server_param = {}
                server_param["fragment"] = parsed_params.fragment
                parsed_params_path = parsed_params.path.split("@")
                server_param["user"] = parsed_params_path[0]
                server_param["address"] = parsed_params_path[1].split(":")[0]
                server_param["port"] = parsed_params_path[1].split(":")[1]
                parsed_params_query = parse_qs(parsed_params.query)
                for key in parsed_params_query:
                    server_param[key] = parsed_params_query[key][0]
                # print(server_param)
                # break
                proxy = convert_srkt_clash_vless(server_param)
            case _:
                continue
        if proxy:
            proxy_list_with_vless.append(proxy)
    # return jsonify(proxy_list_with_vless)
    proxy_list = []
    for proxy in proxy_list_with_vless:
        if proxy["type"] == "vless":
            continue
        proxy_list.append(proxy)
    return get_clash_config_content(proxy_list)