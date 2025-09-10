from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Contact
from .forms import ContactForm
from jobs.forms import JobSearchForm


class ContactView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contact/contact.html'
    success_url = reverse_lazy('contact:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm()
        return context

    def form_valid(self, form):
        contact = form.save()
        
        # Send email notification to admin
        try:
            subject = f'New Contact Form Submission: {contact.subject}'
            context = {
                'contact': contact,
            }
            html_message = render_to_string('contact/email/contact_notification.html', context)
            plain_message = render_to_string('contact/email/contact_notification.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [settings.EMAIL_HOST_USER],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the form submission
            print(f"Failed to send email notification: {e}")
        
        messages.success(self.request, 'Thank you for your message! We will get back to you soon.')
        return super().form_valid(form)
