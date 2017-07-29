# coding: utf-8

import six
from django.contrib import messages
from django.db.models import Q
from django.db.models.aggregates import Count
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls.base import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from rest_framework import viewsets

from djotali.contacts.forms import ContactForm, ContactsGroupForm
from djotali.contacts.models import Contact, ContactsGroup, ContactsGroupSerializer, ContactSerializer
from djotali.core.views import paginate_in_context


class IndexView(ListView):
    model = Contact
    template_name = 'contacts/index.html'
    context_object_name = 'contacts'
    paginate_by = 15
    paginate_orphans = 5
    ordering = ['last_name', 'first_name']

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context

    def get_queryset(self):
        queryset = super(IndexView, self).get_queryset()
        return IndexView.build_queryset(self.request, queryset)

    @classmethod
    def build_queryset(cls, request, base_queryset=Contact._default_manager.all()):
        querystring = request.GET.get('filter')

        if querystring:
            base_queryset = base_queryset.filter(
                Q(first_name__icontains=querystring) |
                Q(last_name__icontains=querystring) |
                Q(phone_number__icontains=querystring.replace(' ', ''))
            )
        ordering = IndexView.ordering
        if isinstance(ordering, six.string_types):
            ordering = (ordering,)
        base_queryset = base_queryset.order_by(*ordering)

        return base_queryset


class ContactsGroupsIndexView(ListView):
    model = ContactsGroup
    template_name = 'contacts/groups_index.html'
    context_object_name = 'contacts_groups'
    paginate_by = 15
    ordering = ['-modified', 'name', 'contacts_count']
    queryset = ContactsGroup.user_contacts_groups

    def get_queryset(self):
        return ContactsGroupsIndexView.build_queryset(super(ContactsGroupsIndexView, self).get_queryset())

    @classmethod
    def build_queryset(cls, base_queryset=ContactsGroup.user_contacts_groups):
        ordering = ContactsGroupsIndexView.ordering
        if isinstance(ordering, six.string_types):
            ordering = (ordering,)
        base_queryset = base_queryset.order_by(*ordering).annotate(
            contacts_count=Count('contacts')
        )
        return base_queryset


class DeleteContactsGroupView(DeleteView):
    model = ContactsGroup
    success_url = reverse_lazy('contacts:lists_index')
    template_name = 'contacts/groups_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        _object = self.get_object()

        self.object = _object
        context = self.get_context_data(object=_object, contacts_groups=ContactsGroupsIndexView.build_queryset())
        return self.render_to_response(context)

    def delete(self, request, *args, **kwargs):
        success_view = super(DeleteContactsGroupView, self).delete(request, args, kwargs)
        messages.add_message(self.request, messages.SUCCESS, "Contacts' group successfully deleted")
        return success_view

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_all_contacts():
            return HttpResponseBadRequest("Le groupe 'Tous les contacts' ne peut être supprimé")
        return super(DeleteContactsGroupView, self).dispatch(request, *args, **kwargs)


class EditContactsGroupView(UpdateView):
    model = ContactsGroup
    form_class = ContactsGroupForm
    success_url = reverse_lazy('contacts-lists:index')
    template_name = 'contacts/groups_edit.html'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_all_contacts():
            return HttpResponseBadRequest("Le groupe 'Tous les contacts' n'est pas modifiable")
        return super(EditContactsGroupView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        valid = super(EditContactsGroupView, self).form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, "Contacts' group successfully edited")
        return valid


class EditContactView(UpdateView):
    model = Contact
    form_class = ContactForm
    success_url = reverse_lazy('contacts:index')
    template_name = 'contacts/edit.html'

    def form_valid(self, form):
        valid = super(EditContactView, self).form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, "Contact successfully edited")
        return valid

    def get_success_url(self):
        default_success_url = super(EditContactView, self).get_success_url()
        success_url = self.request.GET.get('success_url')
        return success_url if success_url else default_success_url


class CreateContactView(CreateView):
    model = Contact
    form_class = ContactForm
    success_url = reverse_lazy('contacts:index')
    template_name = 'contacts/new.html'

    def form_valid(self, form):
        valid = super(CreateContactView, self).form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, "Contact successfully created")
        return valid


class DeleteContactView(DeleteView):
    model = Contact
    success_url = reverse_lazy('contacts:index')
    template_name = 'contacts/confirm_delete.html'

    def get(self, request, *args, **kwargs):
        _object = self.get_object()

        self.object = _object
        context = self.get_context_data(object=_object, contacts=IndexView.build_queryset(self.request))
        return self.render_to_response(context)

    def delete(self, request, *args, **kwargs):
        success_view = super(DeleteContactView, self).delete(request, args, kwargs)
        messages.add_message(self.request, messages.SUCCESS, "Contact successfully deleted")
        return success_view

    def get_success_url(self):
        default_success_url = super(DeleteContactView, self).get_success_url()
        success_url = self.request.GET.get('success_url')
        return success_url if success_url else default_success_url


class ShowContactsGroupView(DetailView):
    template_name = "contacts/groups_show.html"
    model = ContactsGroup
    context_object_name = 'contacts_group'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Related contacts
        paginate_in_context(self.request, self.object.contacts, context, "contacts", 5)

        context["avoid_deleting_contact"] = True

        return context


class CreateContactsGroupsView(CreateView):
    model = ContactsGroup
    template_name = "contacts/groups_new.html"
    form_class = ContactsGroupForm


class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_queryset(self):
        return IndexView.build_queryset(self.request)


class ContactsGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = ContactsGroup.objects.all()
    serializer_class = ContactsGroupSerializer


class ContactsGroupContactsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    pagination_class = None

    # TODO un petit decorator pour aider à récupérer les arguments dans l'url plus simplement
    def get_queryset(self):
        contacts_group_id = self.request.parser_context['kwargs']['group_id']
        return get_object_or_404(ContactsGroup, pk=contacts_group_id).contacts.all()
