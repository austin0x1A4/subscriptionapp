from django.shortcuts import render, redirect
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

logger = logging.getLogger(__name__)

@login_required
def subscribe(request):
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            user_profile = UserProfile.objects.get(user=request.user)
            investment_amount = subscription.investment_amount
            
            if user_profile.account_balance >= subscription.investment_amount:
                user_profile.account_balance -= subscription.investment_amount
                user_profile.save()
                subscription.save()

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
                    f"Details of your subscription:\n"
                    f"Name: {subscription.name} {subscription.last_name}\n"
                    f"Email: {subscription.email}\n"
                    f"Investment Amount: ${subscription.investment_amount}\n"
                    f"Comments: {subscription.comments}\n"
                    f"Start Date: {subscription.start_date}\n"
                    f"Duration: {subscription.investment_duration}\n\n"
                )
                admin_email = settings.ADMINS
                try:
                    send_mail(subject, message, sender_email, [recipient_email])
                    send_mail(admin_subject, admin_message, sender_email, admin_email)
                except Exception as e:
                    logger.error(f"Error sending email to {admin_email}: {e}")

                messages.success(request, "Subscription successful!")
                return redirect('account_balance')
            else:
                messages.error(request, "Insufficient account balance. Please top up your account.")
                return render(request, 'subscription/subscribe.html', {'form': form})
    else:
        form = InvestmentForm()

    return render(request, 'subscription/subscribe.html', {'form': form})

@login_required
def account_balance(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    subscriptions = InvestmentModel.objects.filter(user=request.user)
    total_investments = sum(subscription.investment_amount for subscription in subscriptions)
    user_email = user_profile.user.email
    context = {
        'account_number': user_profile.account_number,
        'account_balance': user_profile.account_balance,
        'subscriptions': subscriptions,
        'total_investments': total_investments,
        'email': user_email,
        
    }
    return render(request, 'subscription/account_balance.html', context)

@login_required
def success_page(request):
    return render(request, 'subscription/success.html')

def others(request):
    return render(request, 'subscription/others.html')
