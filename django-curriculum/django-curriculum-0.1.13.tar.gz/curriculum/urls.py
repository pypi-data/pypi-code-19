# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.views.generic import TemplateView
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'overview', views.OverviewViewSet)
router.register(r'socialmedia', views.PersonalSocialMediaViewSet)
router.register(r'education', views.EducationInfoViewSet)
router.register(r'job', views.JobInfoViewSet)
router.register(r'acomplishment', views.AccomplishmentViewSet)
router.register(r'skillet', views.SkillsetViewSet)
router.register(r'skill', views.SkillViewSet)
router.register(r'language', views.LanguageViewSet)
router.register(r'languageinfo', views.LanguageInfoViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
