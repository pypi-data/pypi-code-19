#! /usr/bin/python3

import argparse
import datetime

from githubapi import GitHubApi
from githubapi import add_issue_to_project_column
from winaproachapi import WinAproachApi


def sync():
    parser = argparse.ArgumentParser()
    parser.add_argument('keywords', metavar='searchKeyWords', nargs='+',
                        help='keyword(s) for IR search')
    parser.add_argument('ghOrg', help="GitHub organization")
    parser.add_argument('ghRepo', help="GitHub repository")
    parser.add_argument('ghProjectBoard', help="GitHub project")
    parser.add_argument('ghProjectBoardColumn', help="GitHub project column")
    parser.add_argument("--days", help="number of past days for the IR lookup",
                        type=int, default=1)
    parser.add_argument('--env', help="WinAproach environment", choices=['PRD', 'PPT'], default='PPT')
    parser.add_argument('--ghIrLabel', help="GitHub Label to tag IR", default='IR')
    parser.add_argument('--winlink', help="Winaproach browser link",
                        default='http://aproach.muc.amadeus.net/NotesLink/nl?RNID=')
    parser.add_argument('--windesc', help="Winaproach auto comment description",
                        default='Incident internally tracked and investigated by project team in')

    args = parser.parse_args()

    endDateIso = datetime.date.today()
    startDateIso = endDateIso - datetime.timedelta(days=args.days)
    startDate = str(startDateIso).replace('-', '/')
    endDate = str(endDateIso).replace('-', '/')

    win_api = WinAproachApi(args.env)
    recordType = 'IR'
    recordIds = []
    for keyword in args.keywords:
        recordIds = recordIds + win_api.search(recordType, keyword, startDate, endDate)

    recordIds = set(recordIds)

    github_api = GitHubApi(args.ghOrg, args.ghRepo)
    projectColumnId = github_api.get_project_column_id(args.ghProjectBoard, args.ghProjectBoardColumn)
    issueDescriptions = github_api.list_github_issues(args.ghIrLabel, startDateIso)

    for rid in recordIds:
        # only sync if IR number can't be found in existing issue with IR label
        if not any(rid in desc for desc in issueDescriptions):
            record = win_api.retrieve(rid)
            title = record.getTitle()
            severity = record.getSeverity()
            urgency = record.getUrgencyCode()
            labels = [args.ghIrLabel, 'SEV%s' % severity]
            if urgency == 'Y':
                labels.append('URGENT')

            description = 'UTC Time|%s %s \n ---|--- \n External tracking| %s%s ' % (
                record.getDetectionDate(), record.getDetectionTime(), args.winlink, rid)
            ghIssue = github_api.create_github_issue(title, description, None, None, labels)
            ghIssueId = ghIssue['id']
            ghUrl = ghIssue['html_url']
            add_issue_to_project_column(ghIssueId, projectColumnId)

            # from GH to WinAproach
            updatedDesc = '%s %s' % (args.windesc, ghUrl)
            win_api.update_ir_description(rid, updatedDesc)
