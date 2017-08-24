from django.contrib import admin
from mmogo.company.models import Company

class CompanyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Company, CompanyAdmin)