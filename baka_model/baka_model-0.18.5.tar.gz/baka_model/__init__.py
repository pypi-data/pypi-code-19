"""
 # Copyright (c) 2017 Boolein Integer Indonesia, PT.
 # suryakencana 2/17/17 @author nanang.suryadi@boolein.id
 #
 # You are hereby granted a non-exclusive, worldwide, royalty-free license to
 # use, copy, modify, and distribute this software in source code or binary
 # form for use in connection with the web services and APIs provided by
 # Boolein.
 #
 # As with any software that integrates with the Boolein platform, your use
 # of this software is subject to the Boolein Developer Principles and
 # Policies [http://developers.Boolein.com/policy/]. This copyright notice
 # shall be included in all copies or substantial portions of the software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 # THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 # DEALINGS IN THE SOFTWARE
 # 
 # __init__.py
"""
from baka_model.model.meta.base import get_engine, get_session_factory, get_tm_session, bind_engine
from pyramid.settings import asbool

__all__ = ('__version__',)
__version__ = '0.18.5'


def tm_activate_hook(request):
    if request.path.startswith(("/_debug_toolbar/", "/static/")):
        return False
    return True


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('baka_model')``.

    """
    settings = config.get_settings()
    should_create = asbool(settings.get('baka_model.should_create_all', False))
    should_drop = asbool(settings.get('baka_model.should_drop_all', False))

    # Configure the transaction manager to support retrying retryable
    # exceptions. We also register the session factory with the thread-local
    # transaction manager, so that all sessions it creates are registered.
    #    "tm.attempts": 3,
    config.add_settings({
        "retry.attempts": 3,
        "tm.activate_hook": tm_activate_hook,
        "tm.annotate_user": False,
    })

    # use pyramid_retry couse pyramid_tm disabled it
    config.include('pyramid_retry')
    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)

    config.registry['db_session_factory'] = session_factory

    # make request.db available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'db',
        reify=True
    )

    # service model factory
    config.include('.service')

    # Register a deferred action to bind the engine when the configuration is
    # committed. Deferring the action means that this module can be included
    # before model modules without ill effect.
    config.action(None, bind_engine, (engine,), {
        'should_create': should_create,
        'should_drop': should_drop
    }, order=10)

