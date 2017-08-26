from django import forms
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from thorson_wiki.models import *

class ArticleUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(ArticleUpdateForm, self).__init__(*args, **kwargs)

        users = User.objects.all()
        groups = Group.objects.all()

        user_choices = [(user.username, user) for user in users]
        group_choices = [(group.name, group) for group in groups]

        choices = [
            (_("Groups"), group_choices),
            (_("Users"), user_choices),
        ]

        current_read_permissions = []
        current_edit_permissions = []
        if self.instance.pk:
            read_permission = Permission.objects.get(
                    codename='read-article:%s:%s' % (self.instance.namespace,
                        self.instance.slug)
            )

            for user in User.objects.all():
                if read_permission in user.user_permissions.all():
                    current_read_permissions.append(user)
            for group in Group.objects.all():
                if read_permission in group.permissions.all():
                    current_read_permissions.append(group)

            edit_permission = Permission.objects.get(
                    codename='edit-article:%s:%s' % (self.instance.namespace,
                        self.instance.slug)
            )

            for user in User.objects.all():
                if edit_permission in user.user_permissions.all():
                    current_edit_permissions.append(user)
            for group in Group.objects.all():
                if edit_permission in group.permissions.all():
                    current_read_permissions.append(group)

        self.fields['read_permissions'] = forms.MultipleChoiceField(
            label=_("Read permissions"),
            choices=choices,
            required=False,
            initial=current_read_permissions,
            help_text=_("Select users and groups to grant permission" \
                    " to read this article.")
        )

        self.fields['edit_permissions'] = forms.MultipleChoiceField(
            label=_("Edit permissions"),
            choices=choices,
            required=False,
            initial=current_edit_permissions,
            help_text=_("Select users and groups to grant permission" \
                    " to edit this article.")
        )

    def save(self, commit=True):
        """
        If commit is set to False, then permissions cannot be updated. Be sure
        to call :func:`save_permissions` at some point if commit is set to
        False.
        """

        article = super(ArticleUpdateForm, self).save(commit=False)

        if commit:
            article.save()
            self.save_permissions(article)

        return article

    def save_permissions(self, article):
        """
        Saves an article's permissions.
        """


        users = User.objects.all()
        groups = Group.objects.all()

        user_choices = dict([(user.username, user) for user in users])
        group_choices = dict([(group.name, group) for group in groups])

        user_choices.update(group_choices)

        all_choices = user_choices

        read_permissions = self.cleaned_data['read_permissions']
        read_permission = Permission.objects.get(
                codename='read-article:%s:%s' % (article.namespace,
                    article.slug)
        )

        for user in User.objects.all():
            user.user_permissions.remove(read_permission)
        for group in Group.objects.all():
            group.permissions.remove(read_permission)

        for item in read_permissions:
            if isinstance(all_choices[item], User):
                all_choices[item].user_permissions.add(read_permission)
            elif isinstance(all_choices[item], Group):
                all_choices[item].permissions.add(read_permission)

        edit_permissions = self.cleaned_data['edit_permissions']
        edit_permission = Permission.objects.get(
            codename='edit-article:%s:%s' % (article.namespace, article.slug)
        )

        for user in User.objects.all():
            user.user_permissions.remove(edit_permission)
        for group in Group.objects.all():
            group.permissions.remove(edit_permission)

        for item in read_permissions:
            if isinstance(all_choices[item], User):
                all_choices[item].user_permissions.add(edit_permission)
            elif isinstance(all_choices[item], Group):
                all_choices[item].permissions.add(edit_permission)

    def clean_title(self):

        title = self.cleaned_data.get('title')

        if self.instance:
            namespace = self.cleaned_data.get('namespace',
                    self.instance.namespace)
            query = ~models.Q(pk=self.instance.pk) & \
                    models.Q(namespace=namespace)
            queryset = Article.objects.filter(query)
        else:
            queryset = Article.objects.filter(
                    namespace=self.cleaned_data['namespace']
            )

        if queryset.filter(slug=slugify(title)).exists():
            raise ValidationError(
                    _("An article with that name already" \
                            " exists."),
                    code='already_exists'
            )

        return title

    class Meta:

        model = Article
        fields = ['title', 'namespace', 'content', 'public',
                'redirect']

class UserCreateForm(forms.ModelForm):

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    password1 = forms.CharField(label=_("Password"),
            widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
            widget=forms.PasswordInput,
            help_text=_("Enter your password again."))

    def clean_password2(self):

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 == password1:
            pass
        else:
            raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
            )

        password_validation.validate_password(
                self.cleaned_data.get('password2')
        )

        return password2

    def save(self, commit=True):

        user = super(UserCreateForm, self).save(commit=commit)
        user.username = self.cleaned_data.get('username')
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']

class UserUpdateForm(forms.ModelForm):

    class Meta:

        model = User
        fields = ['username', 'email']
