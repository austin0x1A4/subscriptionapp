from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .forms import RegistrationForm

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.http import HttpResponse

from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.shortcuts import render, redirect
from .forms import RegistrationForm  # Assuming you have a RegistrationForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Set user to inactive initially
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            
            # Redirect to a page indicating the activation email has been sent
            return render(request, 'registration/activation_sent.html')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


# views.py
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode

from .tokens import account_activation_token

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        
        return redirect('login')
    else:
        return render(request, 'registration/activation_invalid.html')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
@login_required
def account_settings(request):

    context = {}
    return render(request, "registration/account_settings.html", context)

@login_required
def change_info(request):

    if request.method == "POST":
        currentUser = request.user
        currentUser.username = request.POST.get("username")
        currentUser.first_name = request.POST.get('first_name')
        currentUser.last_name = request.POST.get("last_name")
        currentUser.email = request.POST.get("email")
        currentUser.save()
        return redirect("/accounts/account_settings/")
    else:
        return HttpResponse("BAD!")
    
