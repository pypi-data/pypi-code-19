from sniper.controllers import Controller

from .template import render


class JinjaMixin:
    template_name = 'index.html'
    base_template_name = 'base'
    template_name_action_map = None

    def get_template_name(self):
        action = self.kwargs.get('action')
        if action:
            if self.template_name_action_map:
                return self.template_name_action_map.get(action)
            elif self.base_template_name:
                return '%s/%s.html' % (
                    self.base_template_name,
                    action
                )

        return self.template_name

    def process_return_data(self, ret):
        ret = super().process_return_data(ret)

        action = self.kwargs.get('action')
        if action:
            ret.setdefault('action', action)

        return ret

    async def create_response(self, context):
        return await self.render(
            self.get_template_name(),
            context
        )

    async def render(self, name, context=None):
        return await render(self.request, name, context)

    def handle(self):
        return {}


class JinjaController(JinjaMixin, Controller):
    pass
