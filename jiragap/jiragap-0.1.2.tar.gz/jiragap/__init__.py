_issue_key_pattern = None
def issue_iden_get_type (issue_iden):
    import re
    global _issue_key_pattern
    if _issue_key_pattern is None:
        _issue_key_pattern = re.compile(r"\A[A-Z]+\-\d+\Z")
    if isinstance(issue_iden, int):
        if issue_iden <= 0:
            error = ValueError("id: must be positive")
            error.actual_value = issue_iden
            raise error
        return "id"
    if isinstance(issue_iden, str):
        if not _issue_key_pattern.search(issue_iden):
            error = ValueError("key: must match regex " + _issue_key_pattern.pattern)
            error.actual_value = issue_iden
            raise error
        return "key"
    error = TypeError("issue_iden: must be int or str")
    error.actual_type_name = "{__module__}.{__name__}".format(**vars(type(issue_iden)))
    raise error

class JiraGap:
    def create_issue (self, project_key, issuetype_name, summary, fields=None):
        pass
    def get_issue (self, iden, expand=[]):
        pass
    def edit_issue (self, iden, fields):
        pass
    def delete_issue (self, iden, fields):
        pass

    def issue_transition (self, iden, transition_id, fields=None):
        pass
    def issue_comment (self, issue_iden, comment):
        pass
    def issue_attach (self, issue_iden, filename, content_type, content):
        pass
    def issues_link (self, inward_issue_iden, outward_issue_iden, type_name):
        pass

    def search_issues (self, jql, start_at=0, max_results=50, expand=[]):
        pass

    def get_user (self, username, expand=[]):
        pass
    def search_users (self, username_fragment, expand=[]):
        pass

    def search_groups (self, query):
        pass
