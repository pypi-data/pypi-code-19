import packaging.version


def get_version(version=None, base=False) -> str:

    from configfactory import VERSION

    if version is None:
        version = VERSION

    version_obj = packaging.version.Version(version)

    if not base:
        base = version_obj.public == version_obj.base_version

    if base:
        return str(version_obj.public)

    return str(packaging.version.Version(version))
