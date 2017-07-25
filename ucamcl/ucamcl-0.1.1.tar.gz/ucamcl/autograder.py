import json, webbrowser, urllib, collections, requests, urllib, base64, tempfile, time, secrets, sys
use_ipython = False
try:
    from IPython.core.display import display, HTML
    from IPython import get_ipython
    use_ipython = True
except:
    pass
from cryptography.hazmat.primitives import serialization, hashes, asymmetric
from cryptography.hazmat.backends import default_backend


def connect_autograder(url, section=''):
    if url[-1] != '/':
        url = url + '/'
    if section and section[-1] != '/':
        section = section + '/'
    key = asymmetric.rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())
    grader = Autograder(url=url, prefix=section, key=key)

    login_parameters = {'url': url + 'login/raven/',
                        'id1': secrets.token_urlsafe(10),
                        'signing_key': urllib.parse.quote(grader.signing_key_pem)}
    if not (use_ipython and get_ipython()):
        webbrowser.open('{url}?signing_key={signing_key}'.format(**login_parameters))
    else:
        html = '''
        <style type="text/css">
        #{id1} a {{
          font-size: 130%;
          display: inline-block;
          padding: 0.15em 0.4em; margin-bottom: 0;
          border-radius: 0.3em;
          color: white;
          background-color: #337ab7;
          border: 1px solid transparent;
          border-color: #2e6da4;
          font-weight: normal; text-align: center; vertical-align: middle;
          cursor: pointer;
          white-space: nowrap;
          text-decoration: none;
          }}
        #{id1} a:hover {{
          background-color: #286090;
          border-color: #204d74;
          }}
        </style>
        <div>
        <span id='{id1}'>
        <a href="{url}?signing_key={signing_key}" target='_blank'>log in</a>
        </span>
        </div>
        <script type='text/javascript'>
        window.setTimeout(function() {{
            var n = document.getElementById('{id1}');
            n.parentNode.removeChild(n);
            console.log('Sign-in link expired');
        }}, 1000*30);
        </script>
        '''.format(**login_parameters)
        display(HTML(html))
    
    sys.stdout.flush()
    t0 = time.time()
    last_dot = t0 + 15
    shown_start = False
    authenticated = False
    while time.time() < t0 + 15:
        if not shown_start and time.time() > t0 + 2:
            print("Waiting for you to log in ..", end='')
            shown_start = True
            last_dot = t0 + 1
        if time.time() > last_dot + 2:
            print(".", end='')
            sys.stdout.flush()
            last_dot = time.time()
        if grader.ready(verbose=False):
            authenticated = True
            break
        time.sleep(0.5)
    if authenticated:
        print(" done")
        if use_ipython and get_ipython():
            html = '''
            <script type="text/javascript">
            var n = document.getElementById('{id1}');
            n.parentNode.removeChild(n);
            console.log('Sign-in link used');
            </script>
            '''.format(**login_parameters)
            display(HTML(html))
    else:
        print(" not yet done\nWhen you have finished logging in, the autograder will be ready")
    
    return grader


class Autograder(object):
    def __init__(self, url, prefix, key):
        self.url = url
        self.prefix = prefix
        self.key = key

    @property
    def signing_key_pem(self):
        return self.key.public_key().public_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo)
    @property
    def cookies(self):
        return {'signing_key': urllib.parse.quote(self.signing_key_pem)}

    def ready(self, verbose=True):
        status = requests.get(self.url + 'ping/', cookies=self.cookies).status_code
        if verbose and status == 401:
            print("Not logged in")
        return status == 200
    
    def fetch_question(self, label):
        r = requests.get(self.url + 'fetch_question/' + self.prefix + label, cookies=self.cookies)
        if r.status_code == 404:
            raise KeyError(self.prefix + label)
        elif r.status_code == 403:
            raise ConnectionRefusedError(r.reason)
        elif r.status_code != 200:
            raise Exception("Unable to fetch question ({}): {}".format(r.status_code, r.reason))
        q = Question(r.json())
        print(q)
        return q

    def submit_answer(self, q, ans):
        ans_bytes = json.dumps(ans).encode('utf8')
        signature = self.key.sign(
            data = ans_bytes,
            padding = asymmetric.padding.PSS(
                mgf = asymmetric.padding.MGF1(hashes.SHA256()),
                salt_length = asymmetric.padding.PSS.MAX_LENGTH),
            algorithm = hashes.SHA256())
        r = requests.post(self.url + 'submit_answer/',
                          cookies = self.cookies,
                          data = {'answer': base64.b64encode(ans_bytes),
                                  'question_id': q.id,
                                  'signature': base64.b64encode(signature)
                                  })
        if r.status_code == 400:
            raise Exception("Internal error in ucamcl package: {}".format(r.reason))
        elif r.status_code == 401:
            raise ConnectionRefusedError("Error: {}\nPlease re-authenticate and try again".format(r.reason))
        elif r.status_code == 403:
            raise KeyError("Error: {}\nPlease re-fetch the question and try again".format(r.reason))
        elif r.status_code >= 500 and r.status_code < 600:
            raise Exception("Server error: {}\nPlease try again later.".format(r.text[:1000]))
        elif r.status_code != 200:
            raise Exception("Unexpected error: {}".format(r.text[:1000]))
        res = r.json()
        if res['correct']:
            print("Correct!")
        else:
            print("Incorrect")
        return res['correct'], res['answer']

    
class Question(collections.abc.Mapping):
    def __init__(self, qspec):
        self.label = qspec['label']
        self.description = qspec['description']
        self.id = qspec['id']
        self._parameters = json.loads(qspec['parameters'])
    def __getitem__(self, key):
        return self._parameters[key]
    def __iter__(self):
        return iter(self._parameters)
    def __len__(self):
        return len(self._parameters)
    def __str__(self):
        return self.description + '\n' + str(self._parameters)
