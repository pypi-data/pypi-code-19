from django.db.models import Q
from django.template import loader


class FilteredListView:
    """
    Subclass with Djangos' ListView or e.g. django-tables2 SingleTableView and provide at least the allowed_filters tuple

    Attributes::

        allowed_filters: Tuple of allowed query parameters. Only these will be handled for the search
        verbose_names: Tuple of tuples giving a more human readable name for each filter
        lookup_expr: Dict to provide an alternative django lookup expression for a filter. By default
                     <filter_name>__icontains is used, see get_lookup_expr
        search_form_tpl: path to the template for the search
    """
    allowed_filters = None
    verbose_names = None
    search_template = 'django_filteredlist/search_form.html'

    def get_queryset(self):
        queryset = super(FilteredListView, self).get_queryset()
        filters = Q()
        if self.request.GET:
            for field in self.allowed_filters:
                if not self.request.GET.get(field):
                    continue
                filters &= self.get_filter(field)
        return queryset.filter(filters)

    def get_filter(self, field):
        """
        Get the Q Object for a filter name.
        If there are multiple search values for the same filter the lookups are OR'ed
        """
        field_filter = Q()
        field_values = self.request.GET.getlist(field)
        lookup_expr = self.get_lookup_expr(field)
        for val in field_values:
            field_filter |= Q(**{lookup_expr: val})
        return field_filter

    def get_lookup_expr(self, field):
        """
        Returns the django lookup expr for a field
        By default returns: <field>__icontains
        as we want to filter for LIKE
        Can be overridden with self.lookup_expressions['field'] = 'field__somemore__evenmore'
        so e.g. self.lookup_expressions = { 'location': 'location__location__icontains'} <- foreign key here
        """
        if hasattr(self, 'lookup_expressions') and field in self.lookup_expressions:
            return self.lookup_expressions[field]
        else:
            return '{}__icontains'.format(field)

    def get_active_filters(self):
        active_filters = []
        d = dict(self.verbose_names)
        for field in self.allowed_filters:
            if field in self.request.GET:
                for val in self.request.GET.getlist(field):
                    active_filters.append((field, d[field], val))
        return active_filters

    def get_search_context_data(self):
        return {'active_filters': self.get_active_filters(), 'options': self.verbose_names}

    def get_context_data(self):
        context = super(FilteredListView, self).get_context_data()
        context['active_filters'] = self.get_active_filters()
        template = loader.get_template(self.search_template)
        context['search'] = template.render(self.get_search_context_data())
        return context
