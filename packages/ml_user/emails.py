from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class EmailFromTemplate(object):
    def __init__(self, subject, to_email, template_name, context):
        self.subject = subject
        self.to_email = to_email
        self.template_name = template_name
        self.context = context

    def send_mail(self):
        html_content = render_to_string('email/{}'.format(self.template_name), context=self.context)
        email = EmailMessage(
            subject=self.subject,
            body=html_content,
            to=[self.to_email],
        )
        email.content_subtype = "html"
        email.send()

