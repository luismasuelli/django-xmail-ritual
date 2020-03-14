from datetime import datetime
from django.http import HttpResponse
from django.core.mail import send_mail


def sample(request):
    """
    Sample view that sends an e-mail with the current date.
    """

    current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    send_mail("Sample", "Notification sent at time: %s asynchronously" % current,
              "me@example.org", ["somebody@example.org"])

    return HttpResponse("""
    E-mail sent for date: %s
    """ % current)
