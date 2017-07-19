from rest_framework import viewsets
from django.utils.translation import ugettext_lazy as _

from .models import (Overview, PersonalSocialMedia, PersonalPhone,
                     EducationInfo, JobInfo, Accomplishment, Skillset, Skill,
                     Language, LanguageInfo)
from .serializers import (OverviewSerializer, PersonalSocialMediaSerializer,
                          PersonalPhoneSerializer, EducationInfoSerializer,
                          JobInfoSerializer, AccomplishmentSerializer,
                          SkillsetSerializer, SkillSerializer,
                          LanguageSerializer, LanguageInfoSerializer)


class OverviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Overview.objects.filter().order_by('-created')
    serializer_class = OverviewSerializer


class PersonalSocialMediaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = PersonalSocialMedia.objects.filter().order_by('-created')
    serializer_class = PersonalSocialMediaSerializer


class EducationInfoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = EducationInfo.objects.filter().order_by('-created')
    serializer_class = EducationInfoSerializer


class JobInfoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = JobInfo.objects.filter().order_by('-created')
    serializer_class = JobInfoSerializer


class AccomplishmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Accomplishment.objects.filter().order_by('-created')
    serializer_class = AccomplishmentSerializer


class SkillsetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Skillset.objects.filter().order_by('-created')
    serializer_class = SkillsetSerializer


class SkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Skill.objects.filter().order_by('-created')
    serializer_class = SkillSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Language.objects.filter().order_by('-created')
    serializer_class = LanguageSerializer


class LanguageInfoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = LanguageInfo.objects.filter().order_by('-created')
    serializer_class = LanguageInfoSerializer
