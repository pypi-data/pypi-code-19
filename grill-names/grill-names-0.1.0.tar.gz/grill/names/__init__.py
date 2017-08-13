from naming import Name, File, Pipe, PipeFile  # bring standard names to this module level


class Project(PipeFile):
    """Inherited by: :class:`grill.names.Environment`

    Project Name objects.

    ==========  ==========
    **Config:**
    ----------------------
    *project*   Any amount of characters in the class [a-zA-Z0-9]
    *workarea*  Any amount of word characters
    ==========  ==========

    =========== ==
    **Drops:**
    --------------
    *base*
    ==============

    Basic use::

        >>> from grill.names import Project
        >>> p = Project()
        >>> p.get_name()
        '[project]_[workarea].[pipe].[extension]'
        >>> f.get_name(extension='png')
        '[project]_[workarea].[pipe].png'
        >>> p.set_name('test_concept_art.1.psd')
        >>> p.values
        {'project': 'test', 'workarea': 'concept_art', 'version': '1', 'extension': 'psd'}
        >>> p.workarea
        'concept_art'
        >>> p.workarea = 'rigging'
        >>> p.name
        'test_rigging.1.psd'
        >>> p.path
        WindowsPath('test/rigging/test_rigging.1.psd')
    """
    config = dict(project='[a-zA-Z0-9]+', workarea='\w+')
    drops = 'base',

    def get_path_pattern_list(self):
        return ['project', 'workarea']


class Environment(Project):
    """Inherited by: :class:`grill.names.Primitive`

    Environment splits the project field to know more about where it belongs.

    ============= ==========
    **Config:**
    ------------------------
    *environment* Composed of 3 lowercase letters
    *code*        Any amount of characters in the class [a-zA-Z0-9]
    ============= ==========

    ========= ====
    **Compounds:**
    --------------
    *project* environment, code
    ========= ====

    Basic use::

        >>> from grill.names import Environment
        >>> e = Environment('flmtest_concept_art.1.psd')
        >>> e.values
        {'project': 'flmtest',
        'environment': 'flm',
        'code': 'test',
        'workarea': 'concept_art',
        'version': '1',
        'extension': 'psd'}
        >>> e.get_name(code='melon', output='blueprints')
        'flmmelon_concept_art.blueprints.1.psd'
        >>> e.path
        WindowsPath('test/flm/concept_art/flmtest_concept_art.1.psd')
    """
    config = dict(environment='[a-z]{3}', code='[a-z0-9]+')
    compounds = dict(project=('environment', 'code'))

    def get_path_pattern_list(self):
        return ['code', 'environment', 'workarea']


class Primitive(Environment):
    """Inherited by: :class:`grill.names.Asset`

    For primitive names with multiple stages of development.

    ======= ================
    **Config:**
    ------------------------
    *prim*  Any amount of characters in the class [a-zA-Z0-9]
    *stage* Any amount of characters in the class [a-zA-Z0-9]
    ======= ================

    Basic use::

        >>> from grill.names import Primitive
        >>> a = Primitive('prmtest_concept_art_hero_color.1.psd')
        >>> a.values
        {'project': 'prmtest',
        'environment': 'prm',
        'code': 'test',
        'workarea': 'concept_art',
        'prim': 'hero',
        'stage': 'color',
        'version': '1',
        'extension': 'psd'}
        >>> a.prim = 'dragon'
        >>> e.path
        WindowsPath('test/prm/concept_art/prmtest_concept_art_dragon_color.1.psd')
    """
    config = dict(prim='[a-zA-Z0-9]+', stage='[a-z0-9]+')


class Asset(Primitive):
    """
    Elemental resources that, when composed, generate the entities that bring an idea to a tangible product
    through their life cycles (e.g. a character, a film, a videogame).

    =========== ============
    **Config:**
    ------------------------
    *kind*      Any lowercase letter
    *group*     Accepts 3 characters in the class [a-z0-9]
    *area*      Any amount of characters in the class [a-zA-Z0-9]
    *variant*   Any amount of word characters
    *partition* Any amount of characters in the class [a-zA-Z0-9]
    *layer*     Any amount of characters in the class [a-zA-Z0-9]
    =========== ============

    Basic use::

        >>> from grill.names import Asset
        >>> a = Asset()
        >>> a.get_name()
        '[project]_[workarea]_[prim]_[stage]_[variant]_[partition]_[layer].[pipe].[extension]'
        >>> a = Asset.get_default()
        >>> a.name
        'envcode_kgrparea_prim_stage_original_master_default.0.ext'
    """
    config = dict(kind='[a-z]',
                  group='[a-z0-9]{3}',
                  area='[a-z0-9]+',
                  variant='\w+',
                  partition='[a-zA-Z0-9]+',
                  layer='[a-zA-Z0-9]+')
    compounds = dict(workarea=('kind', 'group', 'area'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._branch = 'pro'

    def get_path_pattern_list(self):
        pattern = super().get_path_pattern_list()
        wa_i = pattern.index('workarea')
        new_p = pattern[:wa_i]
        new_p.extend(['branch', 'kind', 'group', 'prim', 'area', 'stage'])
        new_p.extend(pattern[wa_i + 1:])
        new_p.extend(['variant', 'partition', 'layer', 'version'])
        return new_p

    @property
    def branch(self) -> str:
        """
        The branch in the production of the project (pro, dev, test, etc)
        """
        return self._branch

    @branch.setter
    def branch(self, value):
        self._branch = value

    @classmethod
    def get_default(cls) -> 'Asset':
        """Get a new instance with the defaults of this Name values."""
        defaults = dict(project='envcode', workarea='kgrparea', prim='prim', stage='stage', variant='original',
                        partition='master', layer='default', version=0, extension='ext')
        name = cls()
        name.set_name(name.get_name(**defaults))
        return name
