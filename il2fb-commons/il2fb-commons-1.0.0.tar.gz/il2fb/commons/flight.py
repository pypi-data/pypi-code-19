# coding: utf-8

from candv import Values, VerboseValueConstant, with_constant_class

from .utils import translations


_ = translations.ugettext_lazy


class Formation(VerboseValueConstant):
    pass


class Formations(with_constant_class(Formation), Values):
    echelon_right = Formation('F2', _("echelon right"))
    echelon_left = Formation('F3', _("echelon left"))
    line_abreast = Formation('F4', _("line abreast"))
    line_asteam = Formation('F5', _("line asteam"))
    vic = Formation('F6', _("vic"))
    finger_four = Formation('F7', _("finger four"))
    diamond = Formation('F8', _("diamond"))


class RoutePointType(VerboseValueConstant):
    pass


class RoutePointTypes(with_constant_class(RoutePointType), Values):
    # Take-off ----------------------------------------------------------------
    takeoff_normal = RoutePointType(
        'TAKEOFF',
        _("takeoff (normal)"))
    takeoff_pair = RoutePointType(
        'TAKEOFF_002',
        _("takeoff (pair)"))
    takeoff_in_line = RoutePointType(
        'TAKEOFF_003',
        _("takeoff (in line)"))
    takeoff_taxiing = RoutePointType(
        'TAKEOFF_004',
        _("takeoff (taxiing)"))
    takeoff_taxiing_from_static = RoutePointType(
        'TAKEOFF_005',
        _("takeoff (taxiing from static)"))

    # Normal flight -----------------------------------------------------------
    normal = RoutePointType(
        'NORMFLY',
        _("normal"))

    # Attack ------------------------------------------------------------------
    #: .. warning::
    #:   air attack is not present in game. It is calculated as ``NORMFLY``
    #:   with a target
    air_attack = RoutePointType(
        'X_AIR_ATTACK',
        _("air attack"))
    ground_attack = RoutePointType(
        'GATTACK',
        _("ground attack"))

    # Patrol ------------------------------------------------------------------
    patrol_triangle = RoutePointType(
        'NORMFLY_401',
        _("patrol (triangle)"))
    patrol_square = RoutePointType(
        'NORMFLY_402',
        _("patrol (square)"))
    patrol_pentagon = RoutePointType(
        'NORMFLY_403',
        _("patrol (pentagon)"))
    patrol_hexagon = RoutePointType(
        'NORMFLY_404',
        _("patrol (hexagon)"))
    patrol_random = RoutePointType(
        'NORMFLY_405',
        _("patrol (random)"))

    # Artillery spotter -------------------------------------------------------
    artillery_spotter = RoutePointType(
        'NORMFLY_407',
        _("artillery spotter"))

    # Langing -----------------------------------------------------------------
    landing_on_left = RoutePointType(
        'LANDING',
        _("landing (on left)"))
    landing_on_right = RoutePointType(
        'LANDING_101',
        _("landing (on right)"))
    landing_short_on_left = RoutePointType(
        'LANDING_102',
        _("landing (short on left)"))
    landing_short_on_right = RoutePointType(
        'LANDING_103',
        _("landing (short on right)"))
    landing_straight = RoutePointType(
        'LANDING_104',
        _("landing (straight)"))
