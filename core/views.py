
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.conf import settings

from projects.models import Project
from contact.models import ContactMessage


def home(request):
    form_data = {}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        form_data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }

        errors = []

        # Validate name
        if not name or len(name) > 100:
            errors.append("Enter a name within 100 characters.")

        # Validate email
        if not email or len(email) > 254:
            errors.append("Enter a valid email address.")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Enter a valid email address.")

        # Validate subject
        if not subject or len(subject) > 150:
            errors.append("Enter a subject within 150 characters.")

        # Validate message
        if not message:
            errors.append("Please enter your message.")

        if errors:
            for error in errors:
                messages.error(request, error)

        else:
            try:
                # Save message in MySQL database
                ContactMessage.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message,
                )

            except Exception as e:
                print("DATABASE ERROR:", str(e))

                messages.error(
                    request,
                    "Unable to save your message. Please try again."
                )

            else:
                # Send email notification to your Gmail
                try:
                    email_message = EmailMessage(
                        subject=f"Portfolio Contact: {subject}",
                        body=(
                            f"New Portfolio Contact Message\n\n"
                            f"Name: {name}\n"
                            f"Email: {email}\n"
                            f"Subject: {subject}\n\n"
                            f"Message:\n{message}"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=["gopikam0405@gmail.com"],
                        reply_to=[email],
                    )

                    email_message.send(fail_silently=False)

                    messages.success(
                        request,
                        "Thank you! Your message was sent successfully."
                    )

                except Exception as e:
                    print("EMAIL ERROR:", str(e))

                    messages.warning(
                        request,
                        "Your message was saved, but email notification failed."
                    )

                return redirect("/#contact")

    project_list = Project.objects.all()

    return render(
        request,
        "core/home.html",
        {
            "projects": project_list,
            "form_data": form_data,
        },
    )
