import json

from slackbot import settings
from slackbot.bot import listen_to, respond_to
from jira import JIRA, JIRAError
import re

client = JIRA(settings.ATLASSIAN_JIRA_SERVER, basic_auth=(settings.ATLASSIAN_JIRA_USER, settings.ATLASSIAN_JIRA_PASSWORD))
issue_pattern = r'(?:^|\s|[\W]+)(?<!CLEAN\s)((?:{})-[\d]+)(?:$|\s|[\W]+)'.format('|'.join(settings.ATLASSIAN_JIRA_PROJECTS))
issue_patten_compiled = re.compile(issue_pattern, re.IGNORECASE)

try:
    SHOW_DESCRIPTION = settings.ATLASSIAN_JIRA_SHOW_DESCRIPTION
except AttributeError:
    SHOW_DESCRIPTION = False

try:
    USER_MAPPING = settings.ATLASSIAN_USER_MAPPINGS
except AttributeError:
    USER_MAPPING = {}

def field(title, value, short=True):
    return {
        "title": title,
        "value": value,
        "short": short
    }


def link_user(client, user, format_str=None):
    user_id = client.find_user_by_name(user)
    linked_user = "<@{}>".format(user_id)
    if format_str:
        return format_str.format(linked_user)
    else:
        return linked_user

def build_issue_attachment(key, slack_client):
    try:
        issue = client.issue(key)
        summary = issue.fields.summary
        reporter = issue.fields.reporter
        assignee = issue.fields.assignee
        reporter_slack = link_user(slack_client, USER_MAPPING[reporter.name], " ({})") if reporter and reporter.name in USER_MAPPING else ""
        assignee_slack = link_user(slack_client, USER_MAPPING[assignee.name], " ({})") if assignee and assignee.name in USER_MAPPING else ""
        fields = [
            field("Reporter", issue.fields.reporter.displayName + reporter_slack if issue.fields.reporter else "Anonymous"),
            field("Assignee", issue.fields.assignee.displayName + assignee_slack if issue.fields.assignee else "Unassigned"),
            field("Status", str(issue.fields.status))
        ]
        if SHOW_DESCRIPTION:
            fields.append(field("Description", issue.fields.description, False))
        return {
            'fallback': '{key} - {summary}\n{url}'.format(
                key=issue.key,
                summary=summary,
                url=issue.permalink()
            ),
            'title': issue.key,
            'title_link': issue.permalink(),
            'text': summary,
            'color': '#59afe1',
            'fields': fields
        }
    except JIRAError as e:
        return build_issuenotfound_attachment(key)


def build_issuenotfound_attachment(key):
    return {
        'fallback': 'Issue {key} not found'.format(key=key),
        'title': key,
        'text': ':exclamation: Issue not found',
        'color': 'warning'
    }


@listen_to(issue_pattern, re.IGNORECASE)
@respond_to(issue_pattern, re.IGNORECASE)
def show_issues(message, _):
    slack_client = message._client
    issues = issue_patten_compiled.findall(message.body['text'])
    attachments = [build_issue_attachment(issue, slack_client) for issue in issues]
    if attachments:
        message.send_webapi('', json.dumps(attachments))

@respond_to(r'(?:jira|atlassian)\s+user\s+(\w+?)\s+is\s+@?(\w+?)\s+on\s+slack', re.IGNORECASE)
def connect_user(message, atlassian_user, slack_user):
    USER_MAPPING[atlassian_user] = slack_user
    user_id = message._client.find_user_by_name(slack_user)
    message.reply("Got it! <@{}> is {} on Jira".format(user_id, atlassian_user))