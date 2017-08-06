from buildlib import semver
import prmt


def prompt_semver_num_manually() -> str:
    """
    Ask user to enter a new version num. If input invalid recurse.
    """
    version: str = prmt.string('Please enter new semver num.')

    if not semver.validate(version):
        print('Provided version num is not semver conform.')
        version: str = prompt_semver_num_manually()

    return version


def _generate_update_semver_options(
    cur_version: str,
    is_pre: bool
    ) -> list:
    """
    Generate the options that are shown to the user when she has to pick a version num.
    """
    options: list = []
    options.insert(0, 'Enter a new version number manually.')
    options.insert(1, semver.increase(cur_version, 'major') + '\t(Major)')
    options.insert(2, semver.increase(cur_version, 'minor') + '\t(Minor)')
    options.insert(3, semver.increase(cur_version, 'patch') + '\t(Patch)')

    if is_pre:
        options.insert(4, semver.increase(cur_version, 'pre') + '\t(Pre)')

    return options


def prompt_semver_num_by_choice(cur_version: str) -> str:
    """
    Ask user to select a pre-defined version num or enter a new one manually.
    @return: A new semver number as str.
    """
    if cur_version and not semver.validate(cur_version):
        raise Exception('Current version is not "semver" conform.')

    is_pre_release: bool = len(cur_version.split('.')) > 3

    question: str = 'Please select a version number or insert a new one: ' \
                    '(Current version: ' + cur_version + ')'
    options: list = _generate_update_semver_options(cur_version, is_pre_release)
    default: str = '4' if is_pre_release else '3'
    answer: int = prmt.select(question, options, default=default, return_value=False, sort=False)

    if answer == 0:
        return prompt_semver_num_manually()
    else:
        return options[answer].split('\t')[0]
