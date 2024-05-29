from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import InvestmentForm
from .models import UserProfile, InvestmentModel
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)
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
            
            try:
                # Prepare email content with user details
                subject = 'Subscription Confirmation'
                message = (
                    f"Thank you for subscribing to Fund VIP Services, {subscription.name}!\n\n"
                    f"Details of your subscription:\n"
                    f"Name: {subscription.name} {subscription.last_name}\n"
                    f"Email: {subscription.email}\n"
                    f"Investment Amount: ${subscription.investment_amount}\n"
                    f"Comments: {subscription.comments}\n"
                    f"Start Date: {subscription.start_date}\n"
                    f"Duration: {subscription.investment_duration}\n\n"
                    f"We appreciate your trust in our services."
                )
                sender_email = settings.DEFAULT_FROM_EMAIL
                recipient_email = subscription.email

                admin_subject = "New Subscription"
                admin_message = (
                    f"There is a new subscriber to our services, {subscription.name}!\n\n"
                    f"Details of the subscription:\n"
                    f"Name: {subscription.name} {subscription.last_name}\n"
                    f"Email: {subscription.email}\n"
                    f"Investment Amount: ${subscription.investment_amount}\n"
                    f"Comments: {subscription.comments}\n"
                    f"Start Date: {subscription.start_date}\n"
                    f"Duration: {subscription.investment_duration}\n\n"
                )
                admin_email = [admin[1] for admin in settings.ADMINS]

                send_mail(subject, message, sender_email, [recipient_email])
                send_mail(admin_subject, admin_message, sender_email, admin_email)
                
                messages.success(request, "Subscription successful!")
                return redirect('account_balance')
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                messages.error(request, "Subscription was successful, but we couldn't send a confirmation email.")
        else:
            messages.error(request, "There was an error with your form. Please check the details and try again.")
    else:
        form = InvestmentForm()

    return render(request, 'subscription/subscribe.html', {'form': form, 'user': request.user})

@login_required
def account_balance(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    subscriptions = InvestmentModel.objects.filter(user=request.user)
    total_investments = sum(subscription.investment_amount for subscription in subscriptions)
    user_email = user_profile.user.email
    context = {
        'account_number': user_profile.account_number,
        'subscriptions': subscriptions,
        'total_investments': total_investments,
        'user_email': user_email
    }
    return render(request, 'subscription/account_balance.html', context)

@login_required
def success_page(request):
    return render(request, 'subscription/success.html')

def others(request):
    return render(request, 'subscription/others.html')
