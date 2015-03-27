from django.conf import settings


# How many e-mails can be sent at a given time
XMAIL_CHUNK_SIZE = getattr(settings, 'XMAIL_CHUNK_SIZE', 20)

# The actual e-mail backend which will send the e-mails
XMAIL_BRIDGED_BACKEND = getattr(settings, 'XMAIL_BRIDGED_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')