import os
from io import BytesIO
from PIL import Image

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify
from utils import utils


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(
        upload_to='produto_imagens/%Y/%m/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField(verbose_name='Preço')
    preco_marketing_promocional = models.FloatField(
        default=0, verbose_name='Preço Promo.')
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variável'),
            ('S', 'Simples'),
        )
    )

    def get_preco_formatado(self):
        return utils.formata_preco(self.preco_marketing)
    get_preco_formatado.short_description = 'Preço'

    def get_preco_promocional_formatado(self):
        return utils.formata_preco(self.preco_marketing_promocional)
    get_preco_promocional_formatado.short_description = 'Preço Promo.'

    def save(self, *args, **kwargs):

        if not self.slug:
            slug = f'{slugify(self.nome)}'
            self.slug = slug

        super().save(*args, **kwargs)

 
        if self.imagem:
           
            img = Image.open(self.imagem)
            original_width, original_height = img.size
            new_width = 800


            if original_width > new_width:
 
                new_height = round((new_width * original_height) / original_width)
                
           
                new_img = img.resize((new_width, new_height), Image.LANCZOS)
                
      
                buffer = BytesIO()
                new_img.save(buffer, format='JPEG', quality=60, optimize=True)
                
    
                file_name = os.path.basename(self.imagem.name)
                
           
                self.imagem.save(file_name, ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return self.nome


class Variacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, blank=True, null=True)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nome or self.produto.nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'