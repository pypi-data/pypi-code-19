from django.views.generic import View
from django.http import JsonResponse

try:
    from jnius import autoclass, cast
except:
    pass


########################################################################
class open_url(View):
    """"""
    #----------------------------------------------------------------------
    def get(self, request):
        """Constructor"""

        url = request.GET.get('url', '')

        try:
            context = autoclass('org.renpy.android.PythonActivity').mActivity
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setData(Uri.parse(url))
            currentActivity = cast('android.app.Activity', context)
            currentActivity.startActivity(intent)

            return JsonResponse({'success': True,})

        except:

            return JsonResponse({'success': False,})
