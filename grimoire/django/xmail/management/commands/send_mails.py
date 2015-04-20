from ...backends import AsyncEmailBackend
from ...settings import XMAIL_CHUNK_SIZE, XMAIL_BRIDGED_BACKEND
from django.core.management.base import BaseCommand, CommandError
import traceback
from optparse import make_option
from threading import Thread
from time import sleep


class Command(BaseCommand):
    args = 'This command does not expect arguments'
    help = """
    Sends a chunk of e-mails with size as specified in XMAIL_CHUNK_SIZE (defaults to 20) and using the e-mail backend
    specified in XMAIL_BRIDGED_BACKEND (defaults to regular SMTP service).

    You can also pass the --xmail-job-count and --xmail-job-interval if your cron-job tool is not so fine-graned.

    Such options are known to be 1 and 0 by default, which means just one (1) mail-sending loop execution, with zero
    (0) seconds between each execution. As an example, if you want a per-minute execution and your cronjob tool supports
    just a granularity of ten (10) minutes, you should set such options as (10, 60), meaning "10 executions, with a
    distance of 60 seconds between each execution".
    """
    option_list = BaseCommand.option_list + (
        make_option('-c', '--xmail-job-count', action='store', dest='job_count', default=1,
                    type='int', help='number of jobs to run in the same command. By default, 1. Must be >= 1.'),
        make_option('-i', '--xmail-job-interval', action='store', dest='job_interval', default=0,
                    type='int', help='delay (in seconds) between jobs. Must be >= 10 if number of jobs is > 0. '
                                     'Defaults to 0. This value is ignored if the number of jobs is set to 1.')
    )

    def handle(self, *args, **options):
        job_count = options.get('job_count', 1)
        job_interval = options.get('job_interval', 0)

        if job_count <= 0:
            raise CommandError("Bad configuration for -c/--xmail-job-count option. A strictly-positive integer "
                               "is expected.")

        if (job_interval < 10) and (job_count > 1):
            raise CommandError("Bad configuration for -i/--xmail-job-interval option. It must be at least of 10 "
                               "seconds if the number if intervals is > 1.")

        def execute():
            try:
                self.stdout.write('Sending a chunk of %d e-mails using backend `%s` ...' % (
                    XMAIL_CHUNK_SIZE, XMAIL_BRIDGED_BACKEND
                ))
                count, total = AsyncEmailBackend.chunk_send()
            except Exception as e:
                raise CommandError('An internal error has occurred when sending the e-mails chunk. See details:\n%s',
                                   traceback.format_exc())
            else:
                self.stdout.write('In-chunk e-mails have been sent: %d out of %d (Check your administration '
                                  'for details)' % (
                    count, total
                ))

        if job_count == 1:
            execute()
        else:
            for _ in xrange(job_count):
                Thread(target=execute).run()
                sleep(job_interval)