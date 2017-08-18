from os import listdir
from os.path import isdir, join

from . import sources

DEFAULT_SOURCES = (
    sources.EnvironmentSource(),
    sources.IniFileSource(),
)


class SourceList:
    def __init__(self, search_path, input_sources=None):
        if input_sources is None:
            input_sources = DEFAULT_SOURCES

        # FileSource subclasses are actually meta-sources that can potentially
        # spawn multiple sources (see FileSource's docstring), so we separate
        # out the ambient sources at the start, the file sources in the middle,
        # and the other ambient sources at the end.

        # Having multiple non-contiguous runs of file sources creates
        # ambiguities that are difficult to resolve in an intuitive way.
        # Specifically: we want the file search path to be more significant
        # than the source order so e.g. if the passed-in source list is
        # [FooFileSource(), BarFileSource()] and the search path is
        # ['/eggs', '/spam'], '/eggs/config.bar' takes precedence over
        # '/spam/config.foo'. But what if we have [FooFileSource(),
        # AmbientSource(), BarFileSource()]? We can either resolve this as
        # [FooSource(<'/spam/config.foo'>), AmbientSource(),
        # BarSource(<'/eggs/config.bar'>)], which violates the expectation that
        # '/eggs' be before '/spam', or [BarSource(<'/eggs/config.bar'>),
        # FooSource(<'/spam/config.foo'>), AmbientSource()] which violates the
        # expectation that BarFileSource come after AmbientSource. So, to avoid
        # this, we only allow one contiguous run of file sources; if multiple
        # are supplied a ValueError is raised.

        input_source_iter = iter(input_sources)
        ambient_sources_first = []
        file_sources = []
        ambient_sources_last = []

        for source in input_source_iter:
            if isinstance(source, sources.FileSource):
                file_sources.append(source)
                break
            ambient_sources_first.append(source)

        for source in input_source_iter:
            if not isinstance(source, sources.FileSource):
                ambient_sources_last.append(source)
                break
            file_sources.append(source)

        for source in input_source_iter:
            if isinstance(source, sources.FileSource):
                raise ValueError("Non-contiguous file sources in source list")
            ambient_sources_last.append(source)

        # ...And now we resolve the file sources.
        resolved_file_sources = []
        for path in search_path:
            if not isdir(path):
                continue
            listing = listdir(path)
            for source in file_sources:
                for filename in listing:
                    if source.match_filename(filename):
                        with open(join(path, filename)) as f:
                            resolved_file_sources.append(source.create(f))

        # Step three: combine with a whisk for two minutes or until fluffy.
        self.sources = ambient_sources_first
        self.sources.extend(resolved_file_sources)
        self.sources.extend(ambient_sources_last)

    def __getitem__(self, key):
        for source in self.sources:
            try:
                return source[key]
            except KeyError:
                continue
        raise KeyError(key)
