import time
import random
import requests
import re
import math
import os.path
import argparse
import tld

from requests.exceptions import TooManyRedirects
from include.colored import *
from include.config import VERBOSE, BAD_TYPES
from plugins.wayback import time_machine

from urllib.parse import urlparse

SESSION = requests.Session()
SESSION.max_redirects = 3

def requester(
    url,
    main_url=None,
    delay=0,
    cook=None,
    headers=None,
    timeout=10,
    host=None, 
    proxies=[None],
    user_agents=[None],
    failed=None,
    processed=None
    ):
    """
        Method for handling requests
    """
    cook = cook or set()
    headers = headers or set()
    user_agents = user_agents or ['Bolt']
    failed = failed or set()
    processed = processed or set()
    processed.add(url)
    time.sleep(delay)

    def request(url):
        """ Default Requests """
        refined_headers = headers or {
            'Host': host,
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip',
            'DNT': '1',
            'Connection': 'close',
        }
        try:
            response = SESSION.get(
                url,
                cookies = cook,
                verify = False,
                timeout = timeout,
                stream = True,
                proxies = random.choice(proxies)
            )

        except TooManyRedirects:
            return 'dummy'
        
        if 'text/html' in response.headers['content-type'] or 'text/plain' in response.headers['content-type']:
            if response.status_code != '404' :
                return response.text

            else:
                response.close()
                failed.add(url)
                return 'dummy'
    
    return request(url)

def updater():
    print('%s Checking for updates' % run)
    # Changes must be separated by ;
    changes = '''List_changes'''
    latest_commit = requester('https://raw.githubusercontent.com/viveksorathiya/BOLT/master/include/util.py', host='raw.githubusercontent.com')
    # Just a hack to see if a new version is available
    if changes not in latest_commit:
        changelog = re.search(r"changes = '''(.*?)'''", latest_commit)
        # Splitting the changes to form a list
        changelog = changelog.group(1).split(';')
        print('%s A new version of Bolt is available.' % good)
        print('%s Changes:' % info)
        for change in changelog: # print changes
            print('%s>%s %s' % (green, end, change))

        current_path = os.getcwd().split('/') # if you know it, you know it
        folder = current_path[-1] # current directory name
        path = '/'.join(current_path) # current directory path
        choice = input('%s Would you like to update? [Y/n] ' % que).lower()

        if choice != 'n':
            print('%s Updating Bolt' % run)
            os.system('git clone --quiet https://github.com/viveksorathiya/BOLT %s'
                      % (folder))
            os.system('cp -r %s/%s/* %s && rm -r %s/%s/ 2>/dev/null'
                      % (path, folder, path, path, folder))
            print('%s Update successful!' % good)
    else:
        print('%s Bolt is up to date!' % good)

def extr(pattern, response, suppressed, custom):
    """
        Extract pattern based on regex pattern applied
    """
    try:
        finds = re.findall(r'%s' % pattern, response)
        for find in finds:
            verb('Custom regex', find)
            custom.add(find)


    except:
        suppressed = True

def check_link(url, processed, files):
    """
        check whether should be crawled or not
        do not crawl for file or crawled already
    """
    if url not in processed:
        if url.startswith('#') or url.startswith('javascript:'):
            return False

        if url.endswith(BAD_TYPES):
            files.add(url)
            return False

        return True

    return False

def removex(urls, regex):
    """
        parse a list for non-matches to regex
    """
    if not regex:
        return urls

    if not isinstance(urls, (list, set, tuple)):
        urls = [urls]

    try:
        non_matches = [url for url in urls if not re.search(regex, url)]

    except TypeError:
        return []

    return non_matches

def write(datasets, names, out_dir):
    """
        writes results
    """    
    for dataset, name in zip(datasets, names):
        if dataset:
            filepath = out_dir + '/' + name + '.txt'
            with open(filepath, 'w+') as out_file:
                combined = '\n'.join(dataset)
                out_file.write(str(combined.encode('utf-8').decode('utf-8')))
                out_file.write('\n')


def timer(dif, processed):
    """
        return the time taken
    """
    minutes, seconds = divmod(dif, 60)
    try:
        time_per_request = dif/float(len(processed))


    except:
        time_per_request = 0

    return minutes, seconds, time_per_request


def entropy(string):
    """Calculate the entropy of a string."""
    entropy = 0
    for number in range(256):
        result = float(string.encode('utf-8').count(
            chr(number))) / len(string.encode('utf-8'))
        if result != 0:
            entropy = entropy - result * math.log(result, 2)
    return entropy


def xml_parser(response):
    """Extract links from .xml files."""
    # Regex for extracting URLs
    return re.findall(r'<loc>(.*?)</loc>', response)


def verb(kind, string):
    """Enable verbose output."""
    if VERBOSE:
        print('%s %s: %s' % (info, kind, string))


def extract_headers(headers):
    """This function extracts valid headers from interactive input."""
    sorted_headers = {}
    matches = re.findall(r'(.*):\s(.*)', headers)
    for match in matches:
        header = match[0]
        value = match[1]
        try:
            if value[-1] == ',':
                value = value[:-1]
            sorted_headers[header] = value
        except IndexError:
            pass
    return sorted_headers


def top_level(url, fix_protocol=True):
    """Extract the top level domain from an URL."""
    ext = tld.get_tld(url, fix_protocol=fix_protocol)
    toplevel = '.'.join(urlparse(url).netloc.split('.')[-2:]).split(
        ext)[0] + ext
    return toplevel


def is_proxy_list(v, proxies):
    if os.path.isfile(v):
        with open(v, 'r') as _file:
            for line in _file:
                line = line.strip()
                if re.match(r"((http|socks5):\/\/.)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})", line) or \
                   re.match(r"((http|socks5):\/\/.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}:(\d{1,5})", line):
                    proxies.append({"http": line,
                                    "https": line})
                else:
                    print("%s ignored" % line)
        if proxies:
            return True
    return False


def proxy_type(v):
    """ Match IP:PORT or DOMAIN:PORT in a losse manner """
    proxies = []
    if re.match(r"((http|socks5):\/\/.)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})", v):
        proxies.append({"http": v,
                        "https": v})
        return proxies
    elif re.match(r"((http|socks5):\/\/.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}:(\d{1,5})", v):
        proxies.append({"http": v,
                        "https": v})
        return proxies
    elif is_proxy_list(v, proxies):
        return proxies
    else:
        raise argparse.ArgumentTypeError(
            "Proxy should follow IP:PORT or DOMAIN:PORT format")


def luhn(purported):

    # sum_of_digits (index * 2)
    LUHN_ODD_LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)

    if not isinstance(purported, str):
        purported = str(purported)
    try:
        evens = sum(int(p) for p in purported[-1::-2])
        odds = sum(LUHN_ODD_LOOKUP[int(p)] for p in purported[-2::-2])
        return (evens + odds) % 10 == 0
    except ValueError:  # Raised if an int conversion fails
        return False


def is_good_proxy(pip):
    try:
        requests.get('http://example.com', proxies=pip, timeout=3)
    except requests.exceptions.ConnectTimeout as e:
        return False
    except Exception as detail:
        return False

    return True

def zap(input_url, archive, domain, host, internal, robots, proxies):
    """Extract links from robots.txt and sitemap.xml."""
    if archive:
        print('%s Fetching URLs from archive.org' % run)
        if False:
            archived_urls = time_machine(domain, 'domain')
        else:
            archived_urls = time_machine(host, 'host')
        print('%s Retrieved %i URLs from archive.org' % (
            good, len(archived_urls) - 1))
        for url in archived_urls:
            verb('Internal page', url)
            internal.add(url)
    # Makes request to robots.txt
    response = requests.get(input_url + '/robots.txt',
                            proxies=random.choice(proxies)).text
    # Making sure robots.txt isn't some fancy 404 page
    if '<body' not in response:
        # If you know it, you know it
        matches = re.findall(r'Allow: (.*)|Disallow: (.*)', response)
        if matches:
            # Iterating over the matches, match is a tuple here
            for match in matches:
                # One item in match will always be empty so will combine both
                # items
                match = ''.join(match)
                # If the URL doesn't use a wildcard
                if '*' not in match:
                    url = input_url + match
                    # Add the URL to internal list for crawling
                    internal.add(url)
                    # Add the URL to robots list
                    robots.add(url)
            print('%s URLs retrieved from robots.txt: %s' % (good, len(robots)))
    # Makes request to sitemap.xml
    response = requests.get(input_url + '/sitemap.xml',
                            proxies=random.choice(proxies)).text
    # Making sure robots.txt isn't some fancy 404 page
    if '<body' not in response:
        matches = xml_parser(response)
        if matches: # if there are any matches
            print('%s URLs retrieved from sitemap.xml: %s' % (
                good, len(matches)))
            for match in matches:
                verb('Internal page', match)
                # Cleaning up the URL and adding it to the internal list for
                # crawling
                internal.add(match)