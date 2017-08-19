from jinja2 import Environment, FileSystemLoader, select_autoescape
from sniper.responses import Response


def get_env(app):
    if not hasattr(app, 'jinja_env'):
        path = app.config.get(
            'jinja_template_path',
            'templates'
        )
        app.jinja_env = Environment(
            loader=FileSystemLoader(path),
            autoescape=select_autoescape(['xml', 'html']),
            enable_async=True,
        )

    return app.jinja_env


async def render(request, name, context=None):
    app = request.app
    env = get_env(app)

    tmpl = env.get_template(name)
    context = context or {}
    context['request'] = request

    return Response(
        await tmpl.render_async(**context),
        content_type='text/html'
    )
