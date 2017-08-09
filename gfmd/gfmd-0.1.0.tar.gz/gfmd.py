import requests
import json


def markdown(text):
    url = 'https://api.github.com/markdown'
    data = {
        "text": text,
        "mode": "markdown"
    }
    url = 'https://api.github.com/markdown'
    r = requests.post(url=url, data=json.dumps(data))
    html = r.content.decode("utf-8")
    css = open('github-markdown.css').read()
    style = '<style>\n%s</style>\n' % css
    return style + '<div class="markdown-body">\n' + html + '\n</body>'


def main():
    readme_md = open('README.md', 'r').read()
    html = markdown(readme_md)
    with open('index.html', 'w') as f:
        f.write(html)


if __name__ == '__main__':
    main()
