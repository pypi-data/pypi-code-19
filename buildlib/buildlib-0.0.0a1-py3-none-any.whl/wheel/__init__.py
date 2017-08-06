def extract_version_from_wheel_name(name: str) -> str:
    """Get the version part out of the wheel file name."""
    parted: list = name.split('-')
    return '' if len(parted) < 2 else parted[1]
