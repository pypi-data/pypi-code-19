"""
Info commands.
"""

import re
import sys
import six

from collections import defaultdict

from ditz.config import config as userconfig
from ditz import display


class CmdInfo(object):
    def do_todo(self, arg):
        "todo [-a,all] [release] -- Generate todo list"
        show_todo(self, arg)

    def do_show(self, arg):
        "show <issue> -- Describe a single issue"

        issue, _ = self.getissue(arg, 1)
        text = display.show_issue(self.db, issue)
        self.write(text)

    def do_log(self, arg):
        """log [count] -- Show recent activity

        If no count is given, the value is taken from the 'log_lines'
        configuration value (default: 5).  If a count is given, it becomes
        the new default.  A count of zero means show all log entries."""

        if not hasattr(self, "last_log"):
            self.config.add('lines', 5)
            self.last_log = self.config.getint('lines')

        count = self.getint(arg, 1)
        if count is None:
            count = self.last_log
        else:
            self.last_log = count

        text = display.log_events(self.db, count=count, verbose=True)
        self.write(text)

    def do_shortlog(self, arg):
        """shortlog [count] -- Show recent activity (short form)

        If no count is given, the value is taken from the 'shortlog_lines'
        configuration value (default: 20).  If a count is given, it becomes
        the new default.  A count of zero means show all log entries."""

        if not hasattr(self, "last_shortlog"):
            self.config.add('lines', 20)
            self.last_shortlog = self.config.getint('lines')

        count = self.getint(arg, 1)
        if count is None:
            count = self.last_shortlog
        else:
            self.last_shortlog = count

        text = display.log_events(self.db, count=count)
        self.write(text)

    def do_changelog(self, arg):
        "changelog <release> -- Generate a changelog for a release"

        name = self.getrelease(arg, 1)
        text = display.show_changelog(self.db, name)
        self.write(text)

    def do_list(self, arg):
        "list [<regexp>] -- List all issues, optionally matching a regexp"

        try:
            regexp = re.compile(arg or ".*")
        except re.error as msg:
            self.error("invalid regexp: %s" % six.text_type(msg))

        text = display.show_issues(self.db, regexp=regexp, release=True)
        self.write(text or "No matching issues")

    def do_mine(self, arg):
        "mine [-a,all] -- Show all issues claimed by you"
        show_todo(self, arg, claimed=True)

    def do_claimed(self, arg):
        "claimed [-a,all] -- Show claimed issues by claimer"

        allflag = get_allflag(self, arg)

        claimed = defaultdict(list)
        for issue in self.db.issues:
            if issue.claimer and (allflag or not issue.closed):
                claimed[issue.claimer].append(issue)

        if claimed:
            for claimer, issues in sorted(claimed.items()):
                text = display.show_issues(self.db, issues=issues,
                                           release=True)
                self.write(claimer + ":")
                self.write(text)
        else:
            self.write("No issues")

    def do_unclaimed(self, arg):
        "unclaimed [-a,all] -- Show unclaimed issues"

        allflag = get_allflag(self, arg)

        issues = self.db.issues
        issues = filter(lambda issue: not issue.claimer, issues)

        if not allflag:
            issues = filter(lambda issue: not issue.closed, issues)

        text = display.show_issues(self.db, issues=issues, release=True)
        self.write(text or "No issues")

    def do_status(self, arg):
        "status [release] -- Show project status"

        release = self.getrelease(arg, 1, optional=True)
        text = display.show_status(self.db, release)
        self.write(text)

    def do_releases(self, arg):
        "releases -- Show releases"

        text = display.show_releases(self.db)
        self.write(text or "No releases")

    def do_config(self, arg):
        "config [<section>] -- show configuration settings"

        section = self.getarg(arg, 1)

        if not section:
            userconfig.write(sys.stdout)
        elif userconfig.has_section(section):
            for name in sorted(userconfig.options(section)):
                self.write(name, '=', userconfig.get(section, name))
        else:
            self.error("no config section called '%s'" % section)

    def do_info(self, arg):
        "info -- print information about the issue database"

        items = (('project', self.db.project.name),
                 ('path', self.db.path),
                 ('issuedir', self.db.config.issue_dir),
                 ('issues', len(self.db.issues)),
                 ('components', len(self.db.project.components)),
                 ('releases', len(self.db.project.releases)))

        for item in items:
            self.write("%11s: %s" % item)


def show_todo(cmd, arg, claimed=False):
    allflag = get_allflag(cmd, arg)
    idx = 2 if allflag else 1

    release = cmd.getrelease(arg, idx, optional=True)
    text = display.show_todo(cmd.db, relname=release, closed=allflag,
                             claimed=claimed)

    cmd.write(text)


def get_allflag(cmd, arg):
    return cmd.getarg(arg, 1) in ("-a", "all")
