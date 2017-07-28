from django.utils import timezone

from glitter.managers import GlitterManager


class GlitterManagerOverride(GlitterManager):

    def published(self):
        now = timezone.now()
        filter = super().published().filter(publish_at__lte=now)

        return filter
