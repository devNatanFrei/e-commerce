"""
Módulo dedicado exclusivamente ao upload de imagens para o Supabase Storage.
Separado da lógica de processamento de imagens para melhor organização.
"""

import os
from datetime import datetime
from supabase import create_client, Client
from django.conf import settings


class SupabaseUploader:
    """
    Classe responsável exclusivamente pelo upload de arquivos para o Supabase Storage.
    """
    
    def __init__(self):
        self.bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
        self.supabase_url = os.getenv('AWS_S3_ENDPOINT_URL')
        self.supabase_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Valida as credenciais
        if not all([self.bucket_name, self.supabase_url, self.supabase_key]):
            raise Exception("Credenciais do Supabase não configuradas nas variáveis de ambiente.")
    
    def generate_file_path(self, filename, folder="produto_imagens"):
        """
        Gera o caminho do arquivo no bucket seguindo a estrutura: folder/YYYY/MM/filename
        
        Args:
            filename: Nome do arquivo
            folder: Pasta base (padrão: produto_imagens)
            
        Returns:
            str: Caminho completo no bucket
        """
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        return f"{folder}/{year}/{month}/{filename}"
    
    def upload_file(self, file_data, filename, content_type="image/png", folder="produto_imagens"):
        """
        Faz upload de um arquivo para o Supabase Storage.
        
        Args:
            file_data: Dados do arquivo (bytes ou BytesIO)
            filename: Nome do arquivo
            content_type: Tipo MIME do arquivo
            folder: Pasta base no bucket
            
        Returns:
            str: URL pública do arquivo
        """
        try:
            # Inicializa cliente Supabase
            base_url = self.supabase_url.replace('/storage/v1', '')
            supabase = create_client(base_url, self.supabase_key)
            
            # Gera o caminho no bucket
            file_path = self.generate_file_path(filename, folder)
            
            # Prepara os dados para upload
            if hasattr(file_data, 'read'):
                file_data.seek(0)
                file_bytes = file_data.read()
            else:
                file_bytes = file_data
            
            # Faz o upload
            result = supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
            
            # Constrói URL pública
            public_url = f"{self.supabase_url}/object/public/{self.bucket_name}/{file_path}"
            
            print(f"--- SUPABASE_UPLOADER: Upload realizado com sucesso: {public_url} ---")
            return public_url
            
        except Exception as e:
            print(f"--- SUPABASE_UPLOADER: ERRO no upload para Supabase: {e} ---")
            raise e
    
    def upload_image(self, image_data, filename):
        """
        Método específico para upload de imagens PNG.
        
        Args:
            image_data: Dados da imagem (bytes ou BytesIO)
            filename: Nome do arquivo (será convertido para .png se necessário)
            
        Returns:
            str: URL pública da imagem
        """
        # Garante que o arquivo tenha extensão PNG
        if not filename.lower().endswith('.png'):
            name_without_ext = os.path.splitext(filename)[0]
            filename = f"{name_without_ext}.png"
        
        return self.upload_file(
            file_data=image_data,
            filename=filename,
            content_type="image/png",
            folder="produto_imagens"
        )
    
    def delete_file(self, file_path):
        """
        Remove um arquivo do Supabase Storage.
        
        Args:
            file_path: Caminho do arquivo no bucket
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            base_url = self.supabase_url.replace('/storage/v1', '')
            supabase = create_client(base_url, self.supabase_key)
            
            result = supabase.storage.from_(self.bucket_name).remove([file_path])
            
            print(f"--- SUPABASE_UPLOADER: Arquivo removido: {file_path} ---")
            return True
            
        except Exception as e:
            print(f"--- SUPABASE_UPLOADER: ERRO ao remover arquivo: {e} ---")
            return False


# Instância global para uso em toda a aplicação
supabase_uploader = SupabaseUploader()


def upload_image_to_supabase(image_data, filename):
    """
    Função helper para upload de imagens.
    
    Args:
        image_data: Dados da imagem (bytes ou BytesIO)
        filename: Nome do arquivo
        
    Returns:
        str: URL pública da imagem
    """
    return supabase_uploader.upload_image(image_data, filename)


def delete_image_from_supabase(file_path):
    """
    Função helper para remoção de imagens.
    
    Args:
        file_path: Caminho do arquivo no bucket
        
    Returns:
        bool: True se removido com sucesso
    """
    return supabase_uploader.delete_file(file_path)
