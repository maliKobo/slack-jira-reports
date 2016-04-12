# to install BeautifulSoup library for python: pip install beautifulsoup4
# to install SlackClient library for python: pip install slackclient
# to install matplotlib: pip install matplotlib
# you can set up a cronjob to run this script regularly. The script, when run, will download the file, parse it, and print one message in the slack channel mentioned below before quitting

########################
# You'll need to fill in these fields for this script to work

from pybot_config import *

# The format of the message outputted can be modified at the bottom of this file by updating the slackMsg variable
########################

import urllib2
from bs4 import BeautifulSoup
from slackclient import SlackClient
import time
import os

os.chdir(WORKING_DIR)

DELIM = "\t"

url = "https://feedback.kobobooks.com/sr/jira.issueviews:searchrequest-excel-"+JIRA_FIELDS+"-fields/"+JIRA_SEARCH_FILTER_ID+"/SearchRequest-"+JIRA_SEARCH_FILTER_ID+".xls?tempMax=1000&os_username="+JIRA_USERNAME+"&os_password=" + JIRA_PASSWORD

f = open(TEMP_DOWNLOADED_FILE, "wb")
f.write(urllib2.urlopen(url).read())
f.close()

f = open(TEMP_DOWNLOADED_FILE, "r")
soup = BeautifulSoup(f, "html.parser")
rows = soup.find_all("tr", class_="issuerow")

# the 3 values in the following lists are: [num total, num blocked, change since last time]
numStories = [0, 0, 0]
numBugs = [0, 0, 0]

bugs_new = [0, 0, 0]
bugs_progress = [0, 0, 0]
bugs_resolved = [0, 0, 0]
bugs_reopened = [0, 0, 0]
bugs_closed = [0, 0, 0]
bugs_left = [0, 0, 0]

stories_new = [0, 0, 0]
stories_progress = [0, 0, 0]
stories_resolved = [0, 0, 0]
stories_reopened = [0, 0, 0]
stories_closed = [0, 0, 0]
stories_left = [0, 0, 0]

def add(item, blocked):
  item[0] += 1
  item[1] += 1 if blocked else 0

for row in rows:
  
  issuetype = row.find(class_="issuetype").text.strip()
  status = row.find(class_="status").text.strip()
  blocked = row.find(class_="customfield_10230").text.strip() == "Impediment"
  
  if issuetype == "Bug":
    add(numBugs, blocked)
    if status == "New":
      add(bugs_new, blocked)
    elif status == "In Progress":
      add(bugs_progress, blocked)
    elif status == "Resolved":
      add(bugs_resolved, blocked)
    elif status == "Reopened" or status == "Open":
      add(bugs_reopened, blocked)
    elif status == "Closed":
      add(bugs_closed, blocked)
  else:
    add(numStories, blocked)
    if status == "New":
      add(stories_new, blocked)
    elif status == "In Progress":
      add(stories_progress, blocked)
    elif status == "Resolved":
      add(stories_resolved, blocked)
    elif status == "Reopened" or status == "Open":
      add(stories_reopened, blocked)
    elif status == "Closed":
      add(stories_closed, blocked)

bugs_left[0] = numBugs[0] - bugs_closed[0]
bugs_left[1] = numBugs[1] - bugs_closed[1]
stories_left[0] = numStories[0] - stories_closed[0]
stories_left[1] = numStories[1] - stories_closed[1]

def format(item):
  format = str(item[0]) + ((" ("+str(item[1])+")") if item[1] > 0 else "")
  
  DELTA_PADDING = 4
  if item[2] > 0:
    format += pad("+%i" % item[2], DELTA_PADDING)
  elif item[2] < 0:
    format += pad("-%i" % item[2], DELTA_PADDING)
  else:
    format += pad("", DELTA_PADDING)
  
  return format

def pad(text, padding=15):
  left = max(padding - len(text), 0)
  text = " " * left + text
  return text

def read_stats(filename):
  f = open(filename, "r")
  stats = []
  for line in f:
    cells = line.split(DELIM)
    stats.append(cells)
  f.close()
  return stats

now = time.time()
OUTPUT_FORMAT = "%f%s%i%s%i%s%i%s%i%s%i\n"
b = open(STATS_FILE_BUGS, "a")
b.write(OUTPUT_FORMAT % (now, DELIM, \
						bugs_new[0], DELIM, \
						bugs_progress[0], DELIM, \
						bugs_resolved[0], DELIM, \
						bugs_reopened[0], DELIM, \
						bugs_closed[0]))
b.close()

s = open(STATS_FILE_STORIES, "a")
s.write(OUTPUT_FORMAT % (now, DELIM, \
						stories_new[0], DELIM, \
						stories_progress[0], DELIM, \
						stories_resolved[0], DELIM, \
						stories_reopened[0], DELIM, \
						stories_closed[0]))
s.close()

bug_stats = read_stats(STATS_FILE_BUGS)
if len(bug_stats) > 1:
  bugs_new[2]      = bug_stats[-1][1] - bug_stats[-2][1]
  bugs_progress[2] = bug_stats[-1][2] - bug_stats[-2][2]
  bugs_resolved[2] = bug_stats[-1][3] - bug_stats[-2][3]
  bugs_reopened[2] = bug_stats[-1][4] - bug_stats[-2][4]
  bugs_closed[2]   = bug_stats[-1][5] - bug_stats[-2][5]

story_stats = read_stats(STATS_FILE_STORIES)
if len(story_stats) > 1:
  stories_new[2]      = bug_stats[-1][1] - bug_stats[-2][1]
  stories_progress[2] = bug_stats[-1][2] - bug_stats[-2][2]
  stories_resolved[2] = bug_stats[-1][3] - bug_stats[-2][3]
  stories_reopened[2] = bug_stats[-1][4] - bug_stats[-2][4]
  stories_closed[2]   = bug_stats[-1][5] - bug_stats[-2][5]


slackMsg = "*Issues Status for v7.0*\n"
slackMsg += "```\n"
slackMsg += "            |    Stories     |       Bugs \n"
slackMsg += "Not Started |" + pad(format(stories_new))      + " |" + pad(format(bugs_new))      + "\n"
slackMsg += "In Progress |" + pad(format(stories_progress)) + " |" + pad(format(bugs_progress)) + "\n"
slackMsg += "Resolved    |" + pad(format(stories_resolved)) + " |" + pad(format(bugs_resolved)) + "\n"
slackMsg += "Reopened    |" + pad(format(stories_reopened)) + " |" + pad(format(bugs_reopened)) + "\n"
slackMsg += "Closed      |" + pad(format(stories_closed))   + " |" + pad(format(bugs_closed))   + "\n"
slackMsg += "Total       |" + pad(format(numStories))       + " |" + pad(format(numBugs))       + "\n"
slackMsg += "Left        |" + pad(format(stories_left))     + " |" + pad(format(bugs_left))     + "\n"
slackMsg += "```"
#print slackMsg
f.close()

sc = SlackClient(SLACK_TOKEN)
sc.api_call("chat.postMessage", channel=SLACK_CHANNEL, text=slackMsg, username=SLACK_BOT_NAME, icon_emoji=':bug:')
