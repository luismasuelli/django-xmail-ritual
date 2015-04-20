from django.core.exceptions import ImproperlyConfigured
from django.db.transaction import atomic
from django.utils.module_loading import import_string
from .settings import XMAIL_BRIDGED_BACKEND
from .models import AsyncEmailEntry


class AsyncEmailBackend(object):
    """
    Este backend no envia los mails sino que, en realidad, los guarda en una base de datos.

    Para utilizar este backend, deberiamos usar, en nuestros settings, algo como:

    EMAIL_BACKEND = 'xmail.backends.AsyncEmailBackend'
    XMAIL_BRIDGED_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    XMAIL_CHUNK_SIZE = 20

    En el caso de XMAIL_BRIDGED_BACKEND, el valor predeterminado es django.core.mail.backends.smtp.EmailBackend,
      por lo que es opcional asignar esa configuracion si es la que se va a utilizar.

    En el caso de XMAIL_CHUNK_SIZE, el valor predeterminado es 20, por lo que es opcional asignarle valor si nos
      sentimos comodos con esa cantidad. Este valor indica la cantidad de mails que se van a procesar por iteracion.

    En algun momento, vamos a tener que enviar los correos guardados en la base de datos, y para esto
      se utiliza una utilidad en este mismo backend (pero sin instanciarlo). Dicha utilidad va a hacer
      uso de un backend regular de mails (uno sincrono), pero esto ocurre en el contexto de una operacion
      externa (es decir: dicha utilidad sera invocada desde un comando de manage.py).

    En cuanto a las configuraciones relativas a cada backend, hay que especificarlas normalmente. Esta configuracion
      es la que se va a utilizar para realizar el envio del mail dentro de la utilidad, de la misma forma en como
      ocurriria normalmente, pero refiriendose a XMAIL_BRIDGED_BACKEND en lugar de a EMAIL_BACKEND.

    Cabe aclarar que NO tendremos control sobre la conexion utilizada cuando los correos sean finalmente enviado, como
      SI lo tenemos cuando enviamos el mail en una invocacion a send_mail (mas que nada por el hecho de que, para esto,
      cada mail deberia tener una conexion diferente segun se le especifique).
    """

    def __init__(self, **kwargs):
        """
        En realidad no deberiamos hacer nada con estas opciones. No parece que las vayamos a usar.
        :param kwargs:
        :return:
        """
        self.options = kwargs

    def open(self):
        """
        No hace nada ya que no se conecta a ningun lado.
        :return:
        """
        pass

    def close(self):
        """
        No hace nada ya que no se conecta a ningun lado.
        :return:
        """
        pass

    def send_messages(self, email_messages):
        """
        Construye y guarda los e-mails. No los envia en este momento.
        :param email_messages:
        :return:
        """
        return len(AsyncEmailEntry.build(email_messages))

    @classmethod
    def chunk_send(cls):
        """
        Realiza el envio real de los mails. Este debe, en realidad, invocarse desde un comando de manage.py.

        El envio de e-mail se hace mediante la instanciacion de algun otro back-end que DEBEMOS
        :return:
        """

        # Debemos tener XMAIL_BRIDGED_BACKEND en el server. Este debe apuntar a un path correcto que seria un
        # backend de e-mail que usariamos regularmente si no hicieramos envios asincronos.
        #
        # Por esto de que el backend debe ser uno sincrono (regular), no se le puede especificar a esta propiedad
        # un backend asincrono que dependa de XMAIL_BRIDGED_BACKEND ya que causaria una recursividad infinita.
        try:
            klass = import_string(XMAIL_BRIDGED_BACKEND)
        except:
            raise ImproperlyConfigured("For this backend to work, XMAIL_BRIDGED_BACKEND must be set to a valid "
                                       "python path for a normal, synchronous, e-mail backend (by default, it is the "
                                       "SMTP backend provided by Django)")

        if issubclass(klass, cls):
            raise ImproperlyConfigured("XMAIL_BRIDGED_BACKEND cannot be an asynchronous mail backend "
                                       "(you used `%s`. Perhaps you wanted to set that value to "
                                       "EMAIL_BACKEND?)" % XMAIL_BRIDGED_BACKEND)

        # Creamos un backend, y mandamos un lote de correos (preferentemente nuevos). Este lote de correos se puede
        # configurar tranquilamente con un setting. De manera predeterminada, en cada vuelta se intentan enviar 20
        # correos.
        backend = klass(fail_silently=False)
        chunk = AsyncEmailEntry.objects.chunk(mark=True)

        try:
            count = 0
            backend.open()
            total = len(chunk)
            for entry in chunk:
                with atomic():
                    # Que esto se nos ejecute dentro de una transaccion es buena idea ya que
                    # independientemente de las otras cosas que ocurran, este mail ya se habra
                    # enviado al destinatario.
                    #
                    # Si el mensaje no se puede despicklear, entonces se guarda un error asociado
                    # a esa operacion. En caso contrario, se intenta enviar el mail.
                    source = entry.source
                    if source:
                        try:
                            if backend.send_messages([source]):
                                entry.succeeded()
                                count += 1
                            else:
                                entry.last_error = "send_messages() could not send it"
                                entry.failed()
                        except Exception as e:
                            entry.log_exception(e)
                            entry.failed()
                    else:
                        entry.failed()
                    entry.save()
            backend.close()
            return count, total
        except:
            raise