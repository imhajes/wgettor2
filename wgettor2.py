from threading import Thread, Lock
from argparse import ArgumentParser
from os import popen
from subprocess import call, Popen, PIPE
from random import randint
from sys import exit

 
 
class WgetTor:
    def __init__(self, target_address, number):
        self.target_address = target_address
        self.number_requests = int(number)
        self.reload = 'service tor reload'
        self.wget = "torsocks wget -q --spider --user-agent='%s' %s"
        self.lock = Lock()
        self.user_agents = self.set_user_agents()
 
    # replace or add additional user agents here
    @staticmethod
    def set_user_agents():
        return [
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "SAMSUNG-SGH-E250/1.0 Profile/MIDP-2.0 Configuration/CLDC-1.1 UP.Browser/6.2.3.3.c.1.101 (GUI) MMP/2.0 (compatible; Googlebot-Mobile/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Googlebot/2.1 (+http://www.google.com/bot.html) Mozilla/5.0 (compatible); Googlebot/2.1; (+http://www.google.com/bot.html) Googlebot-Image/1.0",
            "Googlebot-Video/1.0",
            "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "facebot",
            "facebookexternalhit/1.0 (+http://www.facebook.com/externalhit_uatext.php)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "admantx-sap/2.4 (+http://www.admantx.com/service-fetcher.html)",
            "Twitterbot",
            "facebookexternalhit/1.1;line-poker/1.0",
            "Twitterbot/1.0",
            "Mozilla/5.0 (compatible; Twitterbot/1.0)",
            "Twitterbot/1.0 Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.12.3 Chrome/69.0.3497.128 Safari/537.36",
            "TelegramBot+(like+TwitterBot)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.11.1 Facebot Twitterbot/1.0",
            "NetResearchServer/2.5(loopimprovements.com/robot.html)",
            "facebookexternalhit"
        ]
 
    @staticmethod
    def whoami():
        who = ['whoami']
        return 'root' in Popen(who, stdout=PIPE).communicate()[0].decode()
 
    @staticmethod
    def check_listening():
        for line in popen('netstat -na --tcp'):
            if '127.0.0.1:9050' in line:
                return True
        return False
 
    def reload_tor(self):
        with self.lock:
            try:
                call(self.reload, shell=True)
            except Exception:
                pass
 
    def service_status(self):
        for line in popen('service --status-all'):
            yield line.split()
 
    def check_services(self):
        for i in self.service_status():
            if '+' in i and 'tor' in i:
                return True
        return False
 
    def check_config(self):
        if not self.whoami():
            error = "Please run wgettor.py with root privileges"
            print(error)
            exit(1)
        if not self.check_listening() or not self.check_services():
            error = 'Please ensure the Tor service is started '
            error += 'and listening on socket 127.0.0.1:9050'
            print(error)
            exit(1)
 
    def get_agent(self):
        return self.user_agents[randint(0, len(self.user_agents) - 1)]
 
    def request(self):
        cmd = self.wget % (self.get_agent(), self.target_address)
        try:
            print(cmd)
            Popen(cmd, stdout=PIPE, shell=True)
        except Exception:
            pass
        finally:
            self.reload_tor()
 
    def run(self):
        for get in range(self.number_requests):
            t = Thread(target=self.request)
            t.start()
 
 
if __name__ == '__main__':
    description = 'Usage: python wgettor.py -t <target URL or IP> '
    description += '-n <number of requests to make on target>'
    parser = ArgumentParser(description=description)
    h = ('target URL or IP', 'number of requests')
    parser.add_argument('-t', '--target', required=True, help=h[0])
    parser.add_argument('-n', '--number', required=True, help=h[1])
    args_in = parser.parse_args()
    wgettor = WgetTor(args_in.target, args_in.number)
    print('executing ->')
    wgettor.check_config()
    wgettor.run()
