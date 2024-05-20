from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import InvestmentForm
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.

def home_view(request):
    return render(request, 'subscription/home.html')
@login_required
def subscribe(request):
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            # Send confirmation email
            subject = 'Subscription Confirmation'
            message = 'Thank you for subscribing to Fund VIP Services!'
            sender_email = 'rbnndng@gmail.com'  # Replace with your sender email
            recipient_email = subscription.email
            send_mail(subject, message, sender_email, [recipient_email])
            # Redirect to a success page or display a confirmation message
            return redirect('success')  # Replace with your actual URL
    else:
        form =InvestmentForm()

    return render(request, 'subscription/subscribe.html', {'form': form})
@login_required
def success_page(request):
    return render(request, 'subscription/success.html')

@user_passes_test(lambda u: u.is_superuser)
def subscribed_users(request):
    # Retrieve all subscribed users (you can customize this query)
    subscribed_users = User.objects.filter(subscription__is_subscribed=True)
    return render(request, 'subscription/subscribed_users.html', {'subscribed_users': subscribed_users})

def others(request):
    return render(request, 'subscription/others.html')

def error_404(request, exception):
    print(hh)
    return render(request, 'templates/505_404.html', status=404)
 
def error_500(request):
    return render(request, 'templates/505_404.html', status=500)

