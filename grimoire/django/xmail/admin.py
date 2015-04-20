from django.contrib.admin import site, ModelAdmin
from django.utils.translation import ugettext_lazy as _
from .models import AsyncEmailEntry


class AsyncMailAdmin(ModelAdmin):
    """
    No permite editar ni crear pero permite borrar. Muestra un subconjunto de los campos.
    """

    list_display = ['created_on', 'tried_on', 'get_state', 'to', 'cc', 'bcc', 'subject', 'last_error']
    list_display_links = None

    def get_state(self, obj):
        return obj.get_state_display()
    get_state.short_description = _(u'Message state')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # permitimos que, si no tenemos un objeto seleccionado,
        # podamos listarlo
        return obj is None

    def has_delete_permission(self, request, obj=None):
        return True


site.register(AsyncEmailEntry, AsyncMailAdmin)