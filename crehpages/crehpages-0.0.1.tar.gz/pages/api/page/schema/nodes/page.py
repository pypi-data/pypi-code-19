# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from pages.models.page import Page
from pages.api.slider.schema.nodes.slider import SliderNode


class PageNode(DjangoObjectType):

    sliders = graphene.List(SliderNode)

    class Meta:
        model = Page

    def resolve_sliders(self, args, request, info):
        return self.slidercontent_set.all()
