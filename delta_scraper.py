from datetime import date
import smtplib
import time
import sys
import getopt

from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver import ActionChains


base_url = 'https://delta.greatjob.net'

headers = {'User-Agent':
           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36'}


def parse_args(argv):
    sender = password = receiver = None
    opts, args = getopt.getopt(
        argv, "s:p:r:", ["sender=", "receiver=", "password="])
    for opt, arg in opts:
        if opt in ("-s", "--sender"):
            sender = opt
        if opt in ("-p", "--password"):
            password = opt
        if opt in ('-r', "--receiver"):
            receiver = opt
    if sender is not None and password is not None and receiver is not None:
        kwargs = {'sender': sender,
                  'password': password,
                  'recipient': receiver,
                  }
        return kwargs
    print "Valid arguements are: -s <sender> -p <password> -r <recipient>"
    return None


def scrape_delta_jobs(args):
    """ scrape delta jobs in the Atlanta area and email the results """
    today = date.today()
    today = today.strftime("%m/%d/%Y")
    print args
    kwargs = parse_args(args)

    if kwargs is None:
        return

    browser = webdriver.Firefox()
    browser.get(base_url)
    actionChains = ActionChains(browser)
    try:
        link = browser.find_element_by_link_text("Search All Jobs")
        actionChains.move_to_element(link).click(link).perform()
        print "getting page..."
        time.sleep(3)

        html = browser.page_source
        soup = BeautifulSoup(html)
        table = soup.find('table')
        jobs_link = table.findAll('a')[-1]['href']
        browser.execute_script(jobs_link)
        print "getting page..."
        time.sleep(3)
        html = browser.page_source
        soup = BeautifulSoup(html)
        table = soup.find('table')
        rows = table.findAll('tr')

        jobs = {}
        titles = []
        for row in rows:
            try:
                location = row.find('td', {'class': 'column-3'}).text
                if 'GA-Atlanta-ATG' in location:
                    date_posted = row.find('td', {'class': 'column-5'}).text
                    department = row.find('td', {'class': 'column-4'}).text
                    title = row.find('td', {'class': 'column-1'})
                    link = title.find('a')['href']
                    if today in date_posted:
                        jobs[title.text] = {
                            'date_posted': date_posted,
                            'department': department,
                        }
                        titles.append(title.text)
            except:
                pass

        formatted_titles = []
        for title in titles:
            formatted_titles.append(title.rstrip().encode('utf-8'))

        sentence = ""
        for title in formatted_titles:
            sentence = sentence + \
                " New Job Posting for Postion: {}".format(title) + " \n"
        # receivers = ['ngmejias@gmail.com']
        sender = kwargs['sender']
        receivers = kwargs['recipient']

        message = """From: {}
        To: {}
        Subject: New Delta Jobs for {}

        {}

        {}
        """.format(semder, receivers, today, base_url, sentence)
        if len(sentence) > 0:
            print sender
            print kwargs['password']
            print receivers
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(sender, kwargs['password'])
            server.sendmail(sender, receivers, message)
            browser.close()
    except:
        browser.close()

if __name__ == '__main__':
    scrape_delta_jobs(sys.argv[1:])
