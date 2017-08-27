
from django.core.paginator import Paginator

class SlicePaginatorMixin(object):
	
	def __init__(self, *args, **kwargs):
		super(SlicePaginatorMixin, self).__init__(*args, **kwargs)
		if not hasattr(self, 'slice_count'):
			self.slice_count = 10
	
	def get_context_data(self, **kwargs):
		context = super(SlicePaginatorMixin, self).get_context_data(**kwargs)

		class SlicePaginator(Paginator): page_range = None

		page_obj = context.get('page_obj')

		if page_obj:
			current_page_num = page_obj.number
			page_range = page_obj.paginator.page_range
			start_page_num = current_page_num // self.slice_count if current_page_num % self.slice_count else current_page_num // self.slice_count - 1
			start_page_num *=self.slice_count
			end_page_num = start_page_num + self.slice_count
			new_paginator = SlicePaginator(object_list=self.get_queryset(), per_page=self.paginate_by, orphans=self.get_paginate_orphans(), allow_empty_first_page=self.get_allow_empty())
			new_paginator.page_range = page_range[start_page_num: end_page_num]
			page_obj.paginator = new_paginator
			context['page_obj'] = page_obj
			
		return context