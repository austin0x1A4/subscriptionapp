from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import InvestmentForm
import logging

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

            return redirect('success')
    else:
        form = InvestmentForm()

    return render(request, 'subscription/subscribe.html', {'form': form})

@login_required
def success_page(request):
    return render(request, 'subscription/success.html')

def others(request):
    return render(request, 'subscription/others.html')
