########################
# You'll need to fill in these fields for this script to work

SLACK_TOKEN = "" # use your own one from https://api.slack.com/web#authentication
SLACK_CHANNEL = "" # the bot will post in this channel e.g. "#android"
SLACK_BOT_NAME = "Release Reporter" # This is the name the bot will post under

JIRA_SEARCH_FILTER_ID = "" # When you save a search query in Jira, you'll find its filter id in the url. e.g. for the saved search "https://feedback.kobobooks.com/issues/?filter=17553", the filter id is 17553
JIRA_USERNAME = "" # The JIRA username for the user that has the above filter
JIRA_PASSWORD = "" # The JIRA password for the above user
JIRA_FIELDS = "all" # should be either "all" or "current" based on whether you want to download all fields, or just the currently selected ones as displayed for the JIRA user at https://feedback.kobobooks.com/issues/

WORKING_DIR = r"" # The location where this script will download temporary files. Any files in this directory with the names below will get overridden. e.g. /Users/mali/
TEMP_DOWNLOADED_FILE = "temp"
STATS_FILE_BUGS = "bug_stats.txt"
STATS_FILE_STORIES = "story_stats.txt"

########################