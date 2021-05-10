import requests
from bs4 import BeautifulSoup
import json
import sys, re, os
import ssl, OpenSSL
import socket
import traceback
from requests.exceptions import Timeout
import time
# External
from config import PLUS, WARNING, INFO, LESS, LINE, FORBI, BACK

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class before_start:
    

    def get_header(self, url, directory):
        """Get header of website (cookie, link, etc...)"""
        r = requests.get(url, allow_redirects=False, verify=False, headers={"User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"})
        print(INFO + "HEADER")
        print(LINE)
        print("  {} \n".format(r.headers).replace(',','\n'))
        print(LINE)
        with open(directory + '/header.csv', 'w+') as file:
            file.write(str(r.headers).replace(',','\n'))


    def gitpast(self, url):
        """
        Github: check github informations
        Pastebin: check pastebin information #TODO
        """
        print("{}Check in Github".format(INFO))
        print(LINE)
        url = url.split(".")[1] if "www" in url else url.split("/")[2]
        url = "{}".format(url)
        print("search: {}\n".format(url))
        types = ["Commits", "Issues", "Code", "Repositories", "Marketplace", "Topics", "Wikis", "Users"]
        try:
            for t in types:
                github = "https://github.com/search?q={}&type={}".format(url, t)
                req = requests.get(github, verify=False)
                soup = BeautifulSoup(req.text, "html.parser")
                search = soup.find('a', {"class":"menu-item selected"})
                if search:
                    for s in search.find("span"):
                        print("  {}{}: {}".format(INFO, t, s))
                else:
                    print("  {}{}: not found".format(INFO, t))
        except:
            print("{}You need connection to check the github".format(WARNING))
        print("\n" + LINE)


    def get_dns(self, url, directory):
        """Get DNS informations"""
        port = 0
        print(INFO + "DNS information")
        print(LINE)
        try:
            if "https" in url:
                url = url.replace('https://','').replace('/','')
                port = 443
            else:
                url = url.replace('http://','').replace('/','')
                port = 80
            context = ssl.create_default_context()
            conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=url)
            conn.connect((url, port))
            cert = conn.getpeercert()
            print(" Organization: {}".format(cert['subject']))
            print(" DNS: {}".format(cert['subjectAltName']))
            print(" SerialNumber: {}".format(cert['serialNumber']))
            conn.close()
            with open(directory + '/dns_info.csv', 'w+') as file:
                file.write(str(cert).replace(',','\n').replace('((','').replace('))',''))
        except:
            erreur = sys.exc_info()
            typerr = u"%s" % (erreur[0])
            typerr = typerr[typerr.find("'")+1:typerr.rfind("'")]
            print(typerr)
            msgerr = u"%s" % (erreur[1])
            print(msgerr + "\n")
        print(LINE)


    def firebaseio(self, url):
        """
        Firebaseio: To check db firebaseio
        ex: --firebase facebook
        """
        get_domain = url.split("/")[2]
        parse_domain = get_domain.split(".")
        if not "www" in get_domain:
            dire = "{}-{}".format(parse_domain[0], parse_domain[1]) if len(parse_domain) > 2 else "{}".format(parse_domain[0])
        else:
            dire = "{}".format(parse_domain[1])
        print("{}Firebaseio Check".format(INFO))
        print(LINE)
        url = 'https://{}.firebaseio.com/.json'.format(dire.split(".")[0])
        print("Target: {}\n".format(url))
        try:
            r = requests.get(url, verify=False).json()
            if 'error' in r.keys():
                if r['error'] == 'Permission denied':
                    print(" {}{} seems to be protected".format(FORBI, url)) #successfully protected
                elif r['error'] == '404 Not Found':
                    print(" {}{} not found".format(LESS, url)) #doesn't exist
                elif "Firebase error." in r['error']:
                    print(" {}{} Firebase error. Please ensure that you spelled the name of your Firebase correctly ".format(WARNING, url))
            else:
                print(" {}{} seems to be vulnerable !".format(PLUS, url)) #vulnerable
        except AttributeError:
            '''
            Some DBs may just return null
            '''
            print("{} null return".format(INFO))
        except:
            print("Error with the requests, please do a manual check")
            pass
        print(LINE)
        

    def wayback_check(self, url, directory):
        """
        Wayback_check:
        Check in a wayback machine to found old file on the website or other things...
        Use "waybacktool"
        """
        print("{}Wayback Check".format(INFO))
        print(LINE)
        print(url + "\n")
        try:
            os.system('python3 tools/waybacktool/waybacktool.py pull --host {} | python3 tools/waybacktool/waybacktool.py check > {}/wayback.txt'.format(url, directory))
        except Exception:
            traceback.print_exc()
        try:
            statinfo = os.path.getsize(directory + "/wayback.txt")
        except:
            print(" {} Nothing wayback found ".format(LESS))
        if statinfo < 1 :
            print(" {} Nothing wayback found".format(LESS))
        else:
            with open(directory + "/wayback.txt", "r+") as wayback:
                wb_read = wayback.read().splitlines()
                for wb in wb_read:
                    wb_res = list(wb.split(","))
                    try:
                        if wb_res[1] == " 200":
                            print("{}{}{}".format(PLUS, wb_res[0], wb_res[1]))
                        elif wb_res[1] == " 301" or wb_res[1] == " 302":
                            print("{}{}{}".format(LESS, wb_res[0], wb_res[1]))
                        elif wb_res[1] == " 404" or wb_res[1] == " 403":
                            pass
                        else:
                            print("{}{}{}".format(INFO, wb_res[0], wb_res[1]))
                    except:
                        pass
        print(LINE)


    def check_localhost(self, url):
        #TODO
        """
        CHeck_localhost: Function which try automatically if it's possible scanning with "localhost" host for discovery other files/directories
        """
        list_test = ["127.0.0.1", "localhost"]
        localhost = False
        print("{}Try localhost host".format(INFO))
        print(LINE)
        for lt in list_test:
            header = {"Host": lt}
            try:
                req = requests.get(url, headers=header, verify=False, timeout=10)
                if req.status_code == 200:
                    print(" {} You can potentialy try bf directories with this option '-H \"Host:{}\"' ".format(PLUS, lt))
                    localhost = True
                else:
                    pass
            except:
                pass
        if not localhost:
            print(" {} Not seem possible to scan with localhost host".format(LESS))
        print(LINE)


    def check_vhost(self, domain, url):
        """
        check_ip:
        Check the host ip if this webpage is different or not
        """
        print("{}Check Vhosts misconfiguration".format(INFO))
        print(LINE)
        try:
            req_index = requests.get(url, verify=False, headers={"User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"})
            len_index = len(req_index.content)
            retrieve_ip = False
            dom = socket.gethostbyname(domain)
            ips = ["https://{}/".format(dom), "http://{}/".format(dom), "http://www2.{}/".format(domain), "http://www3.{}/".format(domain)]
            for ip in ips:
                try:
                    req_ip = requests.get(ip, verify=False, timeout=6)
                    if req_ip.status_code not in [404, 403, 425, 503, 500, 400] and len(req_ip.content) != len_index:
                        retrieve_ip = True
                        print(" {} The host IP seem to be different, check it: {} ".format(PLUS, ip))
                except:
                    pass
            if not retrieve_ip:
                print(" {} This IP Not seem different host".format(LESS))
            print(LINE)
        except:
            pass


    def check_backup_domain(self, domain, url):
        print("{}Check domain backup".format(INFO))
        print(LINE)
        backup_dn_ext = ["zip", "rar", "iso", "tar", "gz", "tgz", "tar.gz", "7z", "jar"]
        req_index = requests.get(url, verify=False, timeout=6, headers={"User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"})
        len_index = len(req_index.content)
        domain = domain.split('.')[1] if len(domain.split('.')) > 2 else domain.split('.')[0]
        print("{}List of backup extension for domain {}: {}\nExemple: {}{}.zip\n".format(INFO, domain, backup_dn_ext, url, domain.split('.')[0]))
        found_bdn = False
        for bdn in backup_dn_ext:
            url_dn_ext = "{}{}.{}".format(url, domain.split('.')[0], bdn)
            try:
                req_dn_ext = requests.get(url_dn_ext, verify=False, timeout=6)
                if req_dn_ext.status_code not in [404, 403, 401, 500, 400, 425] and len(req_dn_ext.content) != len_index:
                    print(" {} {} found ({}b)".format(PLUS, url_dn_ext, len(req_dn_ext.text)))
                    found_bdn = True
            except:
                pass
        if not found_bdn:
            print(" {} Nothing backup domain name found".format(LESS))
        print(LINE)



    def test_timeout(self, url):
        """
        Test_timeout: just a little function for test if the connection is good or not
        """
        try:
            req_timeout = requests.get(url, timeout=30, verify=False, headers={"User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"})
        except Timeout:
            print("{}Service potentialy Unavailable, The site web seem unavailable please wait...\n".format(WARNING))
            time.sleep(180)
        except requests.exceptions.ConnectionError:
            pass