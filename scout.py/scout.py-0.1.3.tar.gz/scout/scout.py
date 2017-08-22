import os
import platform
import requests


class Scout:

    def __init__(self, app, version, install_id, **kwargs):
        self.app = Scout.__not_blank("app", app)
        self.version = Scout.__not_blank("version", version)
        self.install_id = Scout.__not_blank("install_id", install_id)
        self.metadata = kwargs if kwargs is not None else {}
        self.user_agent = self.create_user_agent()

        # scout options; controlled via env vars
        self.scout_host = os.getenv("SCOUT_HOST", "kubernaut.io")
        self.use_https = os.getenv("SCOUT_HTTPS", "1").lower() in {"1", "true", "yes"}
        self.disabled = Scout.__is_disabled()

    def report(self, **kwargs):
        result = {'latest_version': self.version}

        if self.disabled:
            return result

        merged_metadata = Scout.__merge_dicts(self.metadata, kwargs)

        headers = {
            'User-Agent': self.user_agent
        }

        payload = {
            'application': self.app,
            'version': self.version,
            'install_id': self.install_id,
            'user_agent': self.create_user_agent(),
            'metadata': merged_metadata
        }

        url = ("https://" if self.use_https else "http://") + "{}/scout" .format(self.scout_host).lower()
        try:
            resp = requests.post(url, json=payload, headers=headers)
            if resp.status_code / 100 == 2:
                result = Scout.__merge_dicts(result, resp.json())
        except:
            # If scout is down or we are getting errors just proceed as if nothing happened. It should not impact the
            # user at all.
            pass

        return result

    def create_user_agent(self):
        result = "{0}/{1} ({2}; {3}; python {4})".format(
            self.app,
            self.version,
            platform.system(),
            platform.release(),
            platform.python_version()).lower()

        return result

    @staticmethod
    def __not_blank(name, value):
        if value is None or str(value).strip() == "":
            raise ValueError("Value for '{}' is blank, empty or None".format(name))

        return value

    @staticmethod
    def __merge_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

    @staticmethod
    def __is_disabled():
        if str(os.getenv("TRAVIS_REPO_SLUG")).startswith("datawire/"):
            return True

        return os.getenv("SCOUT_DISABLE", "0").lower() in {"1", "true", "yes"}
