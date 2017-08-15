# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2017 Datmellow

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from league import riotDTO
from league.enums import DataDragon


class Champion(riotDTO.RiotDto):
    """
    Representation of a league Champion

    Attributes
    -----------
    ranked_enabled: bool
        Ranked play enabled flag.

    bot_enabled: bool
        Bot enabled flag (for custom games).

    bot_mm_enabled: bool
        Bot Match Made enabled flag (for Co-op vs. AI games).

    active: bool
        Indicates if the champion is active.

    free: bool
        Indicates if the champion is free to play. Free to play champions are rotated periodically.

    cid: long
        Champion ID.

    name: str
        The Champions Name

    title: str
        The Champions Title

    skins : list[dict]
        List of skins the champion has
            dict contains:

                * id : The ID of the skin
                * name : The name of the skin
                * num : The position of the skin in the client

    lore : str
        The Champions Lore, as if they have any :P

    image : :class:`Image`
        Champion image data

    stats : :class:`ChampionStats`
        Champion's Stats

    spells : list[:class:`Spell`]
        List of all the champion's spells.

    passive : dict
        Contains:

            * image : class:`Image`
            * sanitizedDescription : str
            * name : str
            * description : str
    ally_tips : str
        tips for playing with this champion

    enemy_tips : str
        tips for playing against this champion

    partype : str
        resource type

    blurb : str
        The champion's blurb

    info : dict
        Contains:
            * difficulty : int
            * attack : int
            * defense : int
            * magic : int
    recommended : list[:class:`Recommended`]

    """

    def __init__(self, **kwargs):
        super(Champion, self).__init__(**kwargs)
        self.ranked_enabled = kwargs.get('rankedPlayEnabled')
        self.bot_enabled = kwargs.get('botEnabled')
        self.bot_mm_enabled = kwargs.get('botMmEnabled')
        self.active = kwargs.get('active')
        self.free = kwargs.get('freeToPlay')
        self.cid = kwargs.get('id')
        self.name = kwargs.get('name')
        self.title = kwargs.get('title')
        self.skins = kwargs.get('skins')
        self.lore = kwargs.get('lore')
        self.image = Image(image_type=DataDragon.champion_square, **kwargs.get('image', {}))
        self.stats = ChampionStats(**kwargs.get('stats', {}))
        self.spells = [Spell(**data) for data in kwargs.get('spells', {})]
        self.passive = kwargs.get('passive')
        self.ally_tips = kwargs.get('allytips')
        self.enemy_tips = kwargs.get('enemytips')
        self.partype = kwargs.get('partype')
        self.blurb = kwargs.get('blurb')
        self.info = kwargs.get('info')
        self.recommended = [Recommended(**data) for data in kwargs.get('recommended', {})]

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Champion):
            if self.cid == getattr(other, "cid"):
                return True

    def __ne__(self, other):
        return self.__eq__(other)

    def __hash__(self):
        return hash(self.cid)


class ChampionStats:
    """ Represents a Champion's Stats

    Attributes
    ----------
    armor_per_level : float
    hp_per_level : float
    base_attack_damage : float
    mp_per_level : float
    attack_speed_offset : float
    base_armor : float
    base_hp : float
    hp_regen_per_level : float
    spell_block : float
    attack_range : float
    move_speed : float
    attack_damage_per_level : float
    mp_regen_per_level : float
    base_mp : float
    spell_block_per_level : float
    base_crit : float
    base_mp_regen : float
    attack_speed_per_level : float
    base_hp_regen : float
    crit_per_level : float



    """

    def __init__(self, **kwargs):
        self.armor_per_level = kwargs.get('armorperlevel')
        self.hp_per_level = kwargs.get('hpperlevel')
        self.base_attack_damage = kwargs.get('attackdamage')
        self.mp_per_level = kwargs.get('mpperlevel')
        self.attack_speed_offset = kwargs.get('attackspeedoffset')
        self.base_armor = kwargs.get('armor')
        self.base_hp = kwargs.get('hp')
        self.hp_regen_per_level = kwargs.get('hpregenperlevel')
        self.spell_block = kwargs.get('spellblock')
        self.attack_range = kwargs.get('attackrange')
        self.move_speed = kwargs.get('movespeed')
        self.attack_damage_per_level = kwargs.get('attackdamageperlevel')
        self.mp_regen_per_level = kwargs.get('mpregenperlevel')
        self.base_mp = kwargs.get('mp')
        self.spell_block_per_level = kwargs.get('spellblockperlevel')
        self.base_crit = kwargs.get('crit')
        self.base_mp_regen = kwargs.get('mpregen')
        self.attack_speed_per_level = kwargs.get('attackspeedperlevel')
        self.base_hp_regen = kwargs.get('hpregen')
        self.crit_per_level = kwargs.get('critperlevel')


def data_dragon_builder(picture_type: DataDragon, data: list) -> str:
    current_version = DataDragon.__data_version__
    base_url = DataDragon.__base_url__
    endpoint = picture_type.value
    return "{0}{1}".format(base_url, endpoint.format(current_version, *data))


class Image(riotDTO.RiotDto):
    """Represents an Image

    Attributes
    ----------
    full : str
        The filename of the full width image.
    group : str
        The group this image belongs to.
    sprite : str
        The filename of the sprite image.
    h : int
        Height of the image.
    w : int
        Width of the image.
    y : int
        The y spec of the image.
    x : int
        The x spec of the image.
    """

    def __init__(self, **kwargs):
        super(Image, self).__init__(**kwargs)
        self.full = kwargs.get('full')
        self.full_url = data_dragon_builder(kwargs.get('image_type', DataDragon.profile_icons), [self.full])
        self.group = kwargs.get('group')
        self.sprite = kwargs.get('sprite')
        self.sprite_url = data_dragon_builder(kwargs.get('image_type', DataDragon.profile_icons),
                                              [self.sprite])
        self.h = kwargs.get('h')
        self.w = kwargs.get('w')
        self.y = kwargs.get('y')
        self.x = kwargs.get('x')


class Recommended:
    """

    Attributes
    ----------
    map : str
    blocks : list[dict]
    champion : str
    title : str
    priority : bool
    mode : str
    type : str
    """

    def __init__(self, **kwargs):
        self.map = kwargs.get('map')
        self.blocks = kwargs.get('blocks')
        self.champion = kwargs.get('champion')
        self.title = kwargs.get('title')
        self.priority = kwargs.get('priority')
        self.mode = kwargs.get('mode')
        self.type = kwargs.get('type')


class Spell:
    """Represents a League spell

    Attributes
    ----------
    cooldown_burn : list
    resource : str
    level_tip : dict
    vars : list[:class:`Spell`]
    cost_type : str
    image : :class:`Image`
    clean_description : str
    clean_tooltip : str
    effect : list[object]
    tooltip : str
    max_rank : int
    cost_burn : str
    range_burn : str
    range : object
    cool_down : list[double]
    cost : list[int]
    description : str
    effect_burn : list[str]
    alt_images : list[:class:`Image`]
    name : str

    """

    def __init__(self, **kwargs):
        self.cooldown_burn = kwargs.get('cooldownBurn').split("/")
        self.resource = kwargs.get('resource')
        self.level_tip = kwargs.get('leveltip')
        self.vars = kwargs.get('vars')
        self.cost_type = kwargs.get('costType')
        self.image = Image(image_type=DataDragon.champion_spell, **kwargs.get('image'))
        self.clean_description = kwargs.get('sanitizedDescription')
        self.clean_tooltip = kwargs.get('sanitizedTooltip')
        self.effect = kwargs.get('effect')
        self.tooltip = kwargs.get('tooltip')
        self.max_rank = kwargs.get('maxrank')
        self.cost_burn = kwargs.get('costBurn')
        self.range_burn = kwargs.get('rangeBurn')
        self.range = kwargs.get('range')
        self.cool_down = kwargs.get('cooldown')
        self.cost = kwargs.get('cost')
        self.key = kwargs.get('key')
        self.description = kwargs.get('description')
        self.effect_burn = kwargs.get('effectBurn')
        self.alt_images = [Image(**data) for data in kwargs.get('altimages', {})]
        self.name = kwargs.get('name')


class Item(riotDTO.RiotDto):
    """Represents a league item.

    Attributes
    ----------
    name : str
        The name of the item.
    description : str
        The item's description
    id : int
        The item's ID.
    tags : list[str]
        all the item's tags.
    sprite_image : str
        the filename of the sprite image
    full_image : str
        the filename of the full size image.
    prices : dict

        * sell : int
            how much it sells for
        * total : int
            Total price of the item including all of its components
        * base : int
            How much the item itself costs
        * purchasable : bool
            Is it currently purchasable
    maps : dict{map_id : bool}
        The maps where you can purchase the item
    stats :  dict
        Contains all the stats of the item
    recipe : list[:class:`Item`]
        The items that this builds from
    into : list[:class:`Item`]
        The items that this builds into




    """

    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)

        self.name = kwargs.get('name')
        self.description = kwargs.get('sanitizedDescription')
        self.id = kwargs.get('id')
        self.tags = kwargs.get('tags')
        self.image = Image(image_type=DataDragon.item, **kwargs.get('image', {}))
        self.prices = kwargs.get('gold')
        self.maps = kwargs.get('maps')
        self.stats = kwargs.get('stats')
        self.recipe = kwargs.get('from')
        self.into = kwargs.get('into')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Rune(riotDTO.RiotDto):
    """Represents a league rune.

    Attributes
    ----------
    name : str
        The name of the rune
    description : str
        Rune description, usually what it gives.
    id : int
        The id of the rune.
    tier : str
        the tier of the rune
    type : str
        the type of rune it is

        * red : marks
        * blue : glyphs
        * yellow : seals
        * black : quintessences

    is_rune : bool
        Is it actually a rune.

    """

    def __init__(self, **kwargs):
        super(Rune, self).__init__(**kwargs)
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.id = kwargs.get('id')
        self.tier = kwargs.get('rune', {}).get("tier")
        self.type = kwargs.get('rune', {}).get("type")
        self.is_rune = kwargs.get('rune', {}).get("isRune")
        self.image = Image(image_type=DataDragon.rune, **kwargs.get('image', {}))

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class RunePage(riotDTO.RiotDto):
    """Represents a Summoner's Rune page.


    Attributes
    ----------
    name : str
        The name of the rune page.
    id : int
        The ID of the rune page.
    seals : list[:class:`Rune`]
        all the seals of the rune page
    marks : list[:class:`Rune`]
        all the marks of the rune page
    glyphs : list[:class:`Rune`]
        all the glyphs of the rune page
    quintessences : list[:class:`Rune`]
        all the quintessences of the rune page.


    """

    def __init__(self, **kwargs):
        super(RunePage, self).__init__(**kwargs)
        self.name = kwargs.get('name', "")
        self.id = kwargs.get('id')
        self.seals = kwargs.get('seals')
        self.marks = kwargs.get('marks')
        self.glyphs = kwargs.get('glyphs')
        self.quintessences = kwargs.get('quintessences')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class SummonerMastery(riotDTO.RiotDto):
    """Represents a summoner Mastery talent

    Attributes
    ----------
    name : str
        The name of the mastery
    id : int
        The ID of the mastery.
    description: str
        description of the mastery
    sprite_image : str
        filename of the sprite image for the mastery
    full_image : str
        filename of the full-size image for the mastery
    prereq : int
        the ID of the mastery that is a prerequisite.
    ranks : int
        Amount of ranks for this mastery

    """

    def __init__(self, **kwargs):
        super(SummonerMastery, self).__init__(**kwargs)
        self.name = kwargs.get('name')
        self.id = int(kwargs.get('id'))
        self.description = kwargs.get('sanitizedDescription')
        self.image = Image(image_type=DataDragon.summoner_mastery, **kwargs.get('image', {}))
        self.mastery_tree = kwargs.get('masteryTree')
        self.prereq = kwargs.get('prereq')
        self.ranks = kwargs.get('ranks')


class Map(riotDTO.RiotDto):
    """Represents a league Map

    Attributes
    ----------
    name : str
        The name of the map

    image : :class:`Image`
        The image data

    id : int
        The ID of the map


    """

    def __init__(self, **kwargs):
        super(Map, self).__init__(**kwargs)
        self.name = kwargs.get('mapName')
        self.image = Image(**kwargs.get('image', {}))
        self.id = kwargs.get('mapId')


class MasteryPage(riotDTO.RiotDto):
    def __init__(self, **kwargs):
        super(MasteryPage, self).__init__(**kwargs)
        self.current = kwargs.get('current')
        self.name = kwargs.get('name', "")
        self.id = kwargs.get('id')
        if kwargs.get('masteries'):
            self.masteries = [(self.get_from_cache('masteries', mastery['id']), mastery['rank']) for mastery in
                              kwargs.get('masteries')]

    def __repr__(self):
        return self.name
