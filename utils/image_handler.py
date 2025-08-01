"""
Módulo para processamento e upload de imagens para o Supabase Storage.
Centraliza toda a lógica de manipulação de imagens do e-commerce.
"""

import os
from io import BytesIO
from datetime import datetime
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from supabase import create_client, Client


class ImageHandler:
    """
    Classe responsável por processar e fazer upload de imagens para o Supabase.
    """
    
    def __init__(self):
        self.max_width = 800
        self.jpeg_quality = 60
        self.bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
        self.supabase_url = os.getenv('AWS_S3_ENDPOINT_URL')
        self.supabase_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Valida as credenciais
        if not all([self.bucket_name, self.supabase_url, self.supabase_key]):
            raise Exception("Credenciais do Supabase não configuradas nas variáveis de ambiente.")
    
    def resize_image(self, image_file, max_width=None):
        """
        Redimensiona uma imagem mantendo a proporção.
        
        Args:
            image_file: Arquivo de imagem (PIL Image ou file-like object)
            max_width: Largura máxima (padrão: self.max_width)
            
        Returns:
            BytesIO: Buffer com a imagem redimensionada em JPEG
        """
        try:
            if max_width is None:
                max_width = self.max_width
            
            # Abre a imagem
            if hasattr(image_file, 'read'):
                img = Image.open(image_file)
            else:
                img = image_file
            
            # Converte para RGB se necessário (para garantir compatibilidade com JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensiona apenas se necessário
            if img.width > max_width:
                print(f"--- IMAGE_HANDLER: Redimensionando de {img.width}px para {max_width}px ---")
                new_height = int(max_width * img.height / img.width)
                img = img.resize((max_width, new_height), Image.LANCZOS)
            else:
                print(f"--- IMAGE_HANDLER: Imagem já tem tamanho adequado ({img.width}px) ---")
            
            # Salva em buffer
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=self.jpeg_quality, optimize=True)
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            print(f"--- IMAGE_HANDLER: ERRO ao redimensionar imagem: {e} ---")
            raise e
    
    def generate_file_path(self, filename):
        """
        Gera o caminho do arquivo no bucket seguindo a estrutura: produto_imagens/YYYY/MM/filename
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            str: Caminho completo no bucket
        """
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        return f"produto_imagens/{year}/{month}/{filename}"
    
    def upload_to_supabase(self, image_buffer, filename):
        """
        Faz upload de uma imagem para o Supabase Storage.
        
        Args:
            image_buffer: BytesIO com os dados da imagem
            filename: Nome do arquivo
            
        Returns:
            str: URL pública da imagem
        """
        try:
            # Inicializa cliente Supabase
            base_url = self.supabase_url.replace('/storage/v1', '')
            supabase = create_client(base_url, self.supabase_key)
            
            # Gera o caminho no bucket
            file_path = self.generate_file_path(filename)
            
            # Prepara os dados para upload
            image_buffer.seek(0)
            file_data = image_buffer.read()
            
            # Faz o upload
            result = supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": "image/jpeg"}
            )
            
            # Constrói URL pública
            public_url = f"{self.supabase_url}/object/public/{self.bucket_name}/{file_path}"
            
            print(f"--- IMAGE_HANDLER: Upload realizado com sucesso: {public_url} ---")
            return public_url
            
        except Exception as e:
            print(f"--- IMAGE_HANDLER: ERRO no upload para Supabase: {e} ---")
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
            
            # Redimensiona a imagem
            resized_buffer = self.resize_image(image_field.file)
            
            # Faz upload para Supabase
            public_url = self.upload_to_supabase(resized_buffer, filename)
            
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
