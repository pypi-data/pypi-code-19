from django.contrib import admin
from .models import (Overview, PersonalSocialMedia, PersonalPhone,
                     EducationInfo, JobInfo, Accomplishment, Skillset, Skill,
                     Language, LanguageInfo)


class OverViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'created', 'modified']
    list_filter = ['created', 'modified']


class PersonalSocialMediaAdmin(admin.ModelAdmin):
    list_display = ['user', 'linkedin', 'twitter', 'github', 'bitbucket',
                    'gitlab', 'gplus', 'instagram', 'snapchat', 'skype',
                    'wordpress', 'youtube']
    list_filter = ['created', 'modified']


class PersonalPhone(admin.ModelAdmin):
    list_display = ['user', 'name', 'phone']
    list_filter = ['created', 'modified']


class EducationInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'location', 'school_url', 'summary',
                    'is_current']
    list_filter = ['created', 'modified']


class JobInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'location', 'title', 'company_url',
                    'description', 'is_current', 'is_public']
    list_filter = ['created', 'modified']


class AccomplishmentAdmin(admin.ModelAdmin):
    list_display = ['job', 'description', 'order']
    list_filter = ['created', 'modified']


class AccomplishmentAdmin(admin.ModelAdmin):
    list_display = ['job', 'description', 'order']
    list_filter = ['created', 'modified']


class SkillsetAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['created', 'modified']


class SkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'skill_url', 'skillset']
    list_filter = ['created', 'modified']


class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['created', 'modified']


class LanguageInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'level']
    list_filter = ['created', 'modified']


admin.site.register(Overview, OverViewAdmin)
admin.site.register(PersonalSocialMedia, PersonalSocialMediaAdmin)
admin.site.register(PersonalPhone, PersonalPhoneAdmin)
admin.site.register(EducationInfo, EducationInfoAdmin)
admin.site.register(JobInfo, JobInfoAdmin)
admin.site.register(Accomplishment, AccomplishmentAdmin)
admin.site.register(Skillset, SkillsetAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(LanguageInfo, LanguageInfoAdmin)
