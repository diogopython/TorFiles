"""
Gerador de códigos únicos de 5 dígitos.
Gera códigos não previsíveis para compartilhamento de arquivos.
"""
import secrets
import string
from services.database import mariadb


class CodeGenerator:
    """Gera códigos únicos de 5 dígitos alfanuméricos."""
    
    # Caracteres permitidos (sem caracteres confusos como 0/O, 1/l/I)
    CHARSET = string.ascii_uppercase.replace('O', '').replace('I', '') + \
              string.digits.replace('0', '').replace('1', '')
    
    def generate(self, max_attempts=100):
        """
        Gera um código único de 5 caracteres.
        
        Verifica no banco de dados se o código já existe.
        """
        for _ in range(max_attempts):
            code = ''.join(secrets.choice(self.CHARSET) for _ in range(5))
            
            # Verificar se já existe
            result = mariadb.execute(
                "SELECT 1 FROM files WHERE code = %s",
                (code,),
                fetchone=True
            )
            
            if not result:
                return code
        
        raise ValueError("Não foi possível gerar um código único após várias tentativas")


# Instância global
code_generator = CodeGenerator()
