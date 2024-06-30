from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import InvestmentForm, ContactForm, ContactFormAuthenticated
from .models import UserProfile, InvestmentModel
import logging
from django.views import View
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

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
                    #f"Thank you for subscribing to Fund VIP Services, {subscription.user.first_name}!\n\n"
                    f"Details of your subscription:\n"
                    #f"Name: {subscription.user.first_name} {subscription.user.first_name}\n"
                    f"Name: {subscription.user.last_name} {subscription.user.last_name}\n"
                    f"Email: {subscription.user.email}\n"
                    f"Investment Amount: ${subscription.investment_amount}\n"
                    f"Comments: {subscription.comments}\n"
                    f"Start Date: {subscription.start_date}\n"
                    f"Duration: {subscription.investment_duration}\n\n"
                    f"We appreciate your trust in our services."
                )
                sender_email = settings.DEFAULT_FROM_EMAIL
                recipient_email = subscription.user.email

                admin_subject = "New Subscription"
                admin_message = (
                    #f"There is a new subscriber to our services, {subscription.user.first_name}!\n\n"
                    f"Details of the subscription:\n"
                    #f"Name: {subscription.user.first_name} {subscription.user.first_name}\n"
                    f"Name: {subscription.user.last_name} {subscription.user.last_name}\n"
                    f"Email: {subscription.user.email}\n"
                    f"Investment Amount: ${subscription.investment_amount}\n"
                    f"Comments: {subscription.comments}\n"
                    f"Start Date: {subscription.start_date}\n"
                    f"Duration: {subscription.investment_duration}\n\n"
                )
                admin_email = [admin[1] for admin in settings.ADMINS]

                send_mail(subject, message, sender_email, [recipient_email])
                send_mail(admin_subject, admin_message, sender_email, admin_email)
                
                #messages.success(request, "Subscription successful!")
                return redirect('account_balance')
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                #messages.error(request, "Subscription was successful, but we couldn't send a confirmation email.")
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

def send_contact_email(subject, message, sender_email, admin_emails, user_email=None):
    """
    Send the contact email to the admin and optionally send a confirmation email to the user.
    """
    admin_message = f"Subject: {subject}\n\nMessage:\n{message}\n\nFrom: {sender_email}"
    send_mail(
        subject,
        admin_message,
        sender_email,  # Sender email
        admin_emails,  # Receiver email
        fail_silently=False,
    )

    if user_email:
        confirmation_subject = "Your message has been received"
        confirmation_message = (
            "Thank you for contacting us.\n\n"
            "We have received your message and will get back to you shortly.\n\n"
            "Please find the details of your message below:\n\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{message}"
        )
        send_mail(
            confirmation_subject,
            confirmation_message,
            admin_emails[0],  # Send from admin email
            [user_email],  # Send to user email
            fail_silently=False,
        )

@method_decorator(csrf_protect, name='dispatch')
class ContactView(View):
    def get(self, request):
        """
        Render the contact form.
        If the user is authenticated, use the ContactFormAuthenticated form,
        otherwise use the ContactForm.
        """
        if request.user.is_authenticated:
            form = ContactFormAuthenticated()
        else:
            form = ContactForm()
        return render(request, 'subscription/contact.html', {'form': form})

    def post(self, request):
        """
        Handle the submitted contact form.
        If the form is valid, send an email to the admin and a confirmation email to the user.
        Redirect to the contact page with a success message.
        If the form is invalid, re-render the contact page with the form errors.
        """
        if request.user.is_authenticated:
            form = ContactFormAuthenticated(request.POST)
            email = request.user.email
        else:
            form = ContactForm(request.POST)
            email = request.POST.get('email')

        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            admin_emails = [admin[1] for admin in settings.ADMINS]

            try:
                send_contact_email(subject, message, email, admin_emails, email)
            except Exception as e:
                # Log the error or display an appropriate error message
                print(f"Error sending email: {e}")
                messages.error(request, "An error occurred while sending your message. Please try again later.")
            else:
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('contact')

        return render(request, 'subscription/contact.html', {'form': form})