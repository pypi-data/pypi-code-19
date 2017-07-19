from rest_framework import serializers
from .models import (Overview, PersonalSocialMedia, PersonalPhone,
                     EducationInfo, JobInfo, Accomplishment, Skillset,
                     Skill, Language, LanguageInfo)


class OverviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Overview
        fields = '__all__'


class PersonalSocialMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalSocialMedia
        fields = '__all__'


class PersonalPhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalPhone
        fields = '__all__'


class EducationInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = EducationInfo
        fields = '__all__'


class JobInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobInfo
        fields = '__all__'


class AccomplishmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Accomplishment
        fields = '__all__'


class SkillsetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skillset
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = '__all__'


class LanguageInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = LanguageInfo
        fields = '__all__'
