from nocaptcha_recaptcha.fields import NoReCaptchaField
from django.contrib.auth.forms import AuthenticationForm
from nocaptcha_recaptcha.widgets import InvisibleReCaptchaWidget

class MyAdminLoginForm(AuthenticationForm):
    captcha = NoReCaptchaField(  
                gtag_attrs={ 
                    'callback': 'onSubmit',  # name of JavaScript callback function
                    'bind': 'submit-button'  # submit button's ID in the form template
                },
                widget=InvisibleReCaptchaWidget)
