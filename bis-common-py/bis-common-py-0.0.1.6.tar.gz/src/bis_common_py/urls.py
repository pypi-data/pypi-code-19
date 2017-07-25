# coding: utf-8
from django.urls import RegexURLPattern


def add_prefix_to_urls(prefix, urlpatterns):
    prefixed_urlpatterns = []
    for old_pattern in urlpatterns:
        if not old_pattern.regex.pattern[1:].startswith(r"%s" % prefix):
            new_regexp = r"^%s/%s" % (prefix, old_pattern.regex.pattern[1:])
            callback = old_pattern._callback or old_pattern._callback_str
            patched_pattern = RegexURLPattern(
                new_regexp, callback, old_pattern.default_args,
                old_pattern.name)
        else:
            # Паттерн уже с префиксом
            patched_pattern = old_pattern
        prefixed_urlpatterns.append(patched_pattern)

    return prefixed_urlpatterns
