# coding: utf-8
from django.urls import RegexURLPattern, RegexURLResolver


def add_prefix_to_urls(prefix, urlpatterns):
    prefixed_urlpatterns = []
    for old_pattern in urlpatterns:
        if not old_pattern.regex.pattern[1:].startswith(r"%s" % prefix):
            new_regexp = r"^%s/%s" % (prefix, old_pattern.regex.pattern[1:])
            if isinstance(old_pattern, RegexURLResolver):
                patched_pattern = RegexURLResolver(
                    new_regexp, old_pattern.urlconf_module,
                    old_pattern.default_kwargs,
                    app_name=old_pattern.app_name,
                    namespace=old_pattern.namespace)
            else:
                patched_pattern = RegexURLPattern(
                    new_regexp, old_pattern.callback, old_pattern.default_args,
                    old_pattern.name)
        else:
            # Паттерн уже с префиксом
            patched_pattern = old_pattern
        prefixed_urlpatterns.append(patched_pattern)

    return prefixed_urlpatterns
