# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models.role import Role
from models.team import Team
from models.user import User
from models.userrole import UserRole
from models.userteam import UserTeam
from django.contrib import admin

# Register your models here.

admin.site.register(Role)
admin.site.register(Team)
admin.site.register(User)
admin.site.register(UserRole)
admin.site.register(UserTeam)
