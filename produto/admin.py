from django.contrib import admin
from .models import Produto, Variacao

class VaracaoInline(admin.TabularInline):
    model = Variacao
    extra = 1

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao_curta', 'get_preco_formatado', 'get_preco_promocional_formatado']
    inlines = [
        VaracaoInline
    ]

# Register your models here.
admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Variacao)