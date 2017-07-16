# coding: utf-8

from candv import Values, VerboseValueConstant, with_constant_class

from .utils import translations


_ = translations.ugettext_lazy


class TargetType(VerboseValueConstant):
    pass


class TargetTypes(with_constant_class(TargetType), Values):
    destroy = TargetType(0, _("destroy"))
    destroy_area = TargetType(1, _("destroy area"))
    destroy_bridge = TargetType(2, _("destroy bridge"))
    recon = TargetType(3, _("recon"))
    escort = TargetType(4, _("escort"))
    cover = TargetType(5, _("cover"))
    cover_area = TargetType(6, _("cover area"))
    cover_bridge = TargetType(7, _("cover bridge"))


class TargetPriority(VerboseValueConstant):
    pass


class TargetPriorities(with_constant_class(TargetPriority), Values):
    primary = TargetPriority(0, _("primary"))
    secondary = TargetPriority(1, _("secondary"))
    hidden = TargetPriority(2, _("hidden"))
