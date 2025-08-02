import os
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from utils import utils
from utils.image_handler import process_product_image

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(
        upload_to='produto_imagens/%Y/%m/', blank=True, null=True)
    imagem_url = models.URLField(blank=True, null=True)  
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

    @property
    def imagem_display_url(self):
   
        if self.imagem_url:
            return self.imagem_url
        elif self.imagem:
            return self.imagem.url
        return None
   
    def save(self, *args, **kwargs):
        print("--- DEBUG: INICIANDO O MÉTODO SAVE ---")
        

        if not self.slug:
            self.slug = slugify(self.nome)
            print(f"--- DEBUG: Slug gerado: {self.slug} ---")

     
        if self.imagem and hasattr(self.imagem, 'file'):
            try:
                image_url = process_product_image(self.imagem)
                if image_url:
                    self.imagem_url = image_url  
                    print(f"--- DEBUG: Imagem processada e URL salva: {image_url} ---")
               
                    self.imagem = None
                else:
                    print("--- DEBUG: Imagem não foi processada ---")
            except Exception as e:
                print(f"--- ERRO: Falha ao processar imagem: {e} ---")
        
        try:
            print("--- DEBUG: Chamando super().save() para salvar no banco... ---")
            super().save(*args, **kwargs)
            print("--- DEBUG: super().save() concluído com SUCESSO. ---")
        except Exception as e:
            print(f"--- ERRO FATAL: Falha durante o super().save(): {e} ---")
            raise

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