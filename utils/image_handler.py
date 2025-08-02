from PIL import Image
from io import BytesIO
import os

class ImageHandler:
    """
    Classe responsável por processar imagens (redimensionamento).
    O upload é delegado para o módulo supabase_uploader.
    """
    
    def __init__(self):
        self.max_width = 250  
        self.png_optimize = True
        self.quality = 85  
    
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
            
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            
            if img.width > max_width:
                print(f"--- IMAGE_HANDLER: Redimensionando de {img.width}px para {max_width}px ---")
                new_height = int(max_width * img.height / img.width)
                img = img.resize((max_width, new_height), Image.LANCZOS)
            else:
                print(f"--- IMAGE_HANDLER: Imagem já tem tamanho adequado ({img.width}px) ---")
            
           
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
          
            filename = os.path.basename(image_field.name)
            
        
            if not filename.lower().endswith('.png'):
                name_without_ext = os.path.splitext(filename)[0]
                filename = f"{name_without_ext}.png"
            
          
            resized_buffer = self.resize_image(image_field.file)
            
  
            from .supabase_uploader import supabase_uploader
            public_url = supabase_uploader.upload_file(
                file_data=resized_buffer,
                filename=filename,
                content_type="image/png",
                folder="produto_imagens"
            )
            
            return public_url
            
        except Exception as e:
            print(f"--- IMAGE_HANDLER: ERRO no processamento da imagem: {e} ---")
            raise e



image_handler = ImageHandler()


def process_product_image(image_field):
    """
    Função auxiliar para processar imagens de produto.
    Utiliza a instância global do ImageHandler.
    
    Args:
        image_field: Campo ImageField do Django
        
    Returns:
        str: URL pública da imagem ou None se não houver imagem
    """
    return image_handler.process_and_upload_image(image_field)