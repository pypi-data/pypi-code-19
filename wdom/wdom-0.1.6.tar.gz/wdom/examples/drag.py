#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Data binding example
'''

from wdom.themes.default import Div, Span


def dragged(elm):
    print(elm)
    print(elm.target.parentNode._listeners)
    elm.target.parentNode.addEventListener('dragstart', dragged)


class App(Div):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elm1 = Div(parent=self, draggable=True)
        self.elm1.addEventListener('dragstart', dragged)
        self.elm1.setAttribute(
            'style',
            'width: 70px; height: 50px; display: inline-block'
        )
        self.elm2 = self.elm1.cloneNode()
        self.elm3 = self.elm1.cloneNode()
        self.append(self.elm2, self.elm3)
        self.elm1.style['background'] = 'red'
        self.elm1.appendChild(Span('1'))
        self.elm2.style['background'] = 'green'
        self.elm2.appendChild(Span('2'))
        self.elm3.style['background'] = 'blue'
        self.elm3.appendChild(Span('3'))
        self.elm1.firstChild.addEventListener('click', dragged)

    def update(self, event):
        self.text.textContent = self.textbox.getAttribute('value')


def sample_app(**kwargs):
    return App()


if __name__ == '__main__':
    import asyncio
    from wdom.document import get_document
    from wdom import server
    document = get_document()
    document.body.prepend(sample_app())
    server.start_server()
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    server.stop_server()
