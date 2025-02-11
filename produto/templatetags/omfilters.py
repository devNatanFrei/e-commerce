

from django.template import Library

from utils import utils


register = Library()

@register.filter
def formata_preco(value):
    return utils.formata_preco(value)

@register.filter
def cart_total_qtd(value):
    return utils.cart_total_qtd(value)

@register.filter
def cart_totals(value):
    return utils.cart_totals(value)