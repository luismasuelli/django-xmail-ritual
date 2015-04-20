from django.db import models
from base64 import encodestring, decodestring
from pickle import loads, dumps
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from .settings import XMAIL_CHUNK_SIZE


class AsyncEmailEntryQuerySet(models.QuerySet):
    """
    Queryset capaz de obtener un subconjunto de sus elementos. Se da preferencia a los que hace mucho no son
      intentados y, en caso de empate, a los que hace mucho hayan sido creados.
    """

    def chunk(self, mark=False):
        queryset = self.exclude(state__in=['succeeded', 'busy']).order_by('tried_on', 'created_on')[0:XMAIL_CHUNK_SIZE]
        if mark:
            fetched_ids = list(queryset.values_list('pk', flat=True))
            queryset = self.filter(pk__in=fetched_ids)
            queryset.update(state='busy')
        return queryset


class AsyncEmailEntry(models.Model):
    """
    Guarda una entrada de mail para ser enviada luego. Los mails con fecha mas "vieja" de ultimo intento seran
      los que primero se intenten enviar.

    Este modelo no nos interesa realmente, salvo que queramos depurar a ver que ha pasado con el envio de los
      correos.
    """

    class CantDecode(Exception):
        pass

    CHOICES = (
        ('pending', _(u'Pending')),
        ('busy', _(u'Busy')),
        ('failed', _(u'Failed')),
        ('succeeded', _(u'Succeeded'))
    )

    # Manager personalizado para bancar otro metodo
    objects = AsyncEmailEntryQuerySet.as_manager()

    # Datos reales
    created_on = models.DateTimeField(default=now, null=False, verbose_name=_(u'Created'),
                                      help_text=_(u"Message creation date (i.e. when send_mail was called on it)"))
    tried_on = models.DateTimeField(default=None, null=True, verbose_name=_(u'Tried'),
                                    help_text=_(u'Last try date'))
    content = models.TextField(null=False, verbose_name=_(u'Pickled e-mail'),
                               help_text=_(u"Pickled message being sent (it is a pickled EmailMessage instance "
                                           u'encoded in base 64)'))
    state = models.CharField(max_length=10, null=False, default='pending', choices=CHOICES,
                             help_text=_(u'Current state of the message (pending, busy, already sent, or failed)'),
                             verbose_name=_(u'Message state'))
    last_error = models.TextField(null=True, editable=False, verbose_name=_(u"Last error"),
                                  help_text=_(u"Details for the last error occurred with this message"))

    # Datos indexados
    to = models.TextField(null=False, verbose_name=_(u"To"),
                          help_text=_(u'Prefetched destinations from the "to" field in the original message'))
    cc = models.TextField(null=True, verbose_name=_(u"Cc"),
                          help_text=_(u'Prefetched destinations from the "cc" field in the original message'))
    bcc = models.TextField(null=True, verbose_name=_(u"Bcc"),
                          help_text=_(u'Prefetched destinations from the "bcc" field in the original message'))
    subject = models.TextField(null=True, verbose_name=_(u"Subject"),
                               help_text=_(u'Prefetched subject from the original message'))

    class Meta:
        verbose_name = _(u'Async e-mail entry')
        verbose_name_plural = _(u'Async e-mail entries')

    def log_exception(self, e):
        """
        Guarda los detalles de la excepcion ocurrida.
        :param e:
        :return:
        """
        self.last_error = "%s : %r" % (type(e).__name__, e.args)

    @property
    def source(self):
        """
        Recupera el mensaje original, o None si hubo un error (la excepcion ocurrida es logueada).
        :return:
        """
        try:
            content = self.content.encode('ascii') if isinstance(self.content, type(u'')) else self.content
            content = content or ''
            return loads(decodestring(content))
        except Exception as e:
            self.log_exception(e)

    @source.setter
    def source(self, value):
        """
        Asigna el mensaje original, si no hubo ningun error (si lo hubo, la excepcion ocurrida es logueada).
        :param value:
        :return:
        """
        try:
            self.content = encodestring(dumps(value))
            self.to = self._comma_break(value.to)
            self.cc = self._comma_break(value.cc)
            self.bcc = self._comma_break(value.bcc)
            self.subject = value.subject
        except Exception as e:
            self.log_exception(e)

    @classmethod
    def build(cls, sources):
        """
        Crea muchas instancias con sus mensajes originales y las guarda.
        :param sources: secuencia de objetos EmailMessage
        :return:
        """
        def instantiate(source):
            instance = cls()
            instance.source = source
            return instance
        if not isinstance(sources, (list, tuple, set, frozenset)):
            sources = [sources]
        return cls.objects.bulk_create([instantiate(source) for source in sources])

    def _comma_break(self, value):
        """
        Une mediante comas los elementos de una secuencia, o devuelve como vino el valor si no es una secuencia.
        :param value:
        :return:
        """
        return u", ".join(value) if isinstance(value, (tuple, list, frozenset, set)) else value

    def _tried(self):
        """
        Actualiza fecha del ultimo intento.
        :return:
        """
        self.tried_on = now()

    def succeeded(self):
        """
        Marca al e-mail como enviado exitosamente.
        :return:
        """
        self._tried()
        self.state = 'succeeded'

    def failed(self):
        """
        Marca al e-mail como fallado al enviarse.
        :return:
        """
        self._tried()
        self.state = 'failed'