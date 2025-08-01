"""
Módulo para processamento de imagens para o e-commerce.
Centraliza a lógica de redimensionamento e preparação de imagens.
O upload é feito pelo módulo supabase_uploader.
"""

import os
from io import BytesIO
from PIL import Image
from django.conf import settings
from .supabase_uploader import upload_image_to_supabase


class ImageHandler:
    """
    Classe responsável por processar imagens (redimensionamento).
    O upload é delegado para o módulo supabase_uploader.
    """
    
    def __init__(self):
        self.max_width = 400
        self.png_optimize = True
    
    def resize_image(self, image_file, max_width=None):
        """
        Redimensiona uma imagem mantendo a proporção.
        
        Args:
            image_file: Arquivo de imagem (PIL Image ou file-like object)
            max_width: Largura máxima (padrão: self.max_width)
            
        Returns:
            BytesIO: Buffer com a imagem redimensionada em PNG
        """
        try:
            if max_width is None:
                max_width = self.max_width
            
            # Abre a imagem
            if hasattr(image_file, 'read'):
                img = Image.open(image_file)
            else:
                img = image_file
            
            # Preserva o formato original ou garante compatibilidade com PNG
            original_format = img.format
            
            # Redimensiona apenas se necessário
            if img.width > max_width:
                print(f"--- IMAGE_HANDLER: Redimensionando de {img.width}px para {max_width}px ---")
                new_height = int(max_width * img.height / img.width)
                img = img.resize((max_width, new_height), Image.LANCZOS)
            else:
                print(f"--- IMAGE_HANDLER: Imagem já tem tamanho adequado ({img.width}px) ---")
            
            # Salva em buffer mantendo PNG
            buffer = BytesIO()
            img.save(buffer, format='PNG', optimize=self.png_optimize)
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            print(f"--- IMAGE_HANDLER: ERRO ao redimensionar imagem: {e} ---")
            raise e
    
    def process_and_upload_image(self, image_field):
        """
        Processa uma imagem (redimensiona) e faz upload para o Supabase.
        
        Args:
            image_field: Campo ImageField do Django
            
        Returns:
            str: URL pública da imagem ou None se não houver imagem
        """
        if not image_field or not hasattr(image_field, 'file'):
            return None
        
        try:
            # Obtém o nome do arquivo original
            filename = os.path.basename(image_field.name)
            
            # Garante que o arquivo tenha extensão PNG
            if not filename.lower().endswith('.png'):
                name_without_ext = os.path.splitext(filename)[0]
                filename = f"{name_without_ext}.png"
            
            # Redimensiona a imagem
            resized_buffer = self.resize_image(image_field.file)
            
            # Faz upload para Supabase usando o módulo dedicado
            public_url = upload_image_to_supabase(resized_buffer, filename)
            
            return public_url
            
        except Exception as e:
            print(f"--- IMAGE_HANDLER: ERRO no processamento da imagem: {e} ---")
            raise e
    
    def should_process_image(self, image_field):
        """
        Determina se uma imagem deve ser processada.
        
        Args:
            image_field: Campo ImageField do Django
            
        Returns:
            bool: True se deve processar, False caso contrário
        """
        return (
            not settings.DEBUG and  # Apenas em produção
            image_field and         # Tem imagem
            hasattr(image_field, 'file') and  # Tem arquivo
            hasattr(image_field.file, 'read')  # É um arquivo válido
        )


# Instância global para uso nos models
image_handler = ImageHandler()


def process_product_image(image_field):
    """
    Função helper para processar imagens de produtos.
    
    Args:
        image_field: Campo ImageField do produto
        
    Returns:
        str: URL pública da imagem ou None
    """
    if image_handler.should_process_image(image_field):
        return image_handler.process_and_upload_image(image_field)
    return None
