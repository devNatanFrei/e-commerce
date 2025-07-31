# produto/models.py (Versão final e robusta)

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
        print("--- DEBUG: INICIANDO O MÉTODO SAVE ---")
        
        if not self.slug:
            self.slug = slugify(self.nome)
            print(f"--- DEBUG: Slug gerado: {self.slug} ---")

 
        if not settings.DEBUG and self.imagem and hasattr(self.imagem.file, 'read'):
            print("--- DEBUG: Ambiente de produção detectado, processando imagem. ---")
            try:
                # Lógica de redimensionamento
                img = Image.open(self.imagem.file)
                new_width = 800
                if img.width > new_width:
                    print(f"--- DEBUG: Redimensionando imagem de {img.width}px para {new_width}px ---")
                    new_height = int(new_width * img.height / img.width)
                    new_img = img.resize((new_width, new_height), Image.LANCZOS)
                    
                    buffer = BytesIO()
                    new_img.save(buffer, format='JPEG', quality=60, optimize=True)
                    
                    file_name = os.path.basename(self.imagem.name)
                    self.imagem.file = ContentFile(buffer.getvalue())
                    self.imagem.name = file_name
                    print(f"--- DEBUG: Imagem redimensionada e pronta para upload: {file_name} ---")
                else:
                    print("--- DEBUG: Imagem já tem o tamanho correto, não precisa redimensionar. ---")
            except Exception as e:
                print(f"--- ERRO FATAL: Falha ao redimensionar a imagem: {e} ---")
        
        try:
            print("--- DEBUG: Chamando super().save() para salvar no banco/storage... ---")
            # Salva o modelo e faz o upload da imagem
            super().save(*args, **kwargs)
            print("--- DEBUG: super().save() concluído com SUCESSO. ---")
        except Exception as e:
            print(f"--- ERRO FATAL: Falha durante o super().save(): {e} ---")
            # Re-lança a exceção para que o Django mostre a página de erro
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