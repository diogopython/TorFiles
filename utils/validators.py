"""
Validadores para inputs e arquivos.
"""
import re
from config import Config


def validate_username(username):
    """
    Valida um username.
    
    Regras:
    - 3 a 50 caracteres
    - Apenas letras, números e underscore
    - Deve começar com letra
    """
    if not username:
        return False, "Username é obrigatório"
    
    if len(username) < 3:
        return False, "Username deve ter pelo menos 3 caracteres"
    
    if len(username) > 50:
        return False, "Username deve ter no máximo 50 caracteres"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username deve começar com letra e conter apenas letras, números e underscore"
    
    return True, None


def validate_password(password):
    """
    Valida uma senha.
    
    Regras:
    - Mínimo 8 caracteres
    - Pelo menos uma letra e um número
    """
    if not password:
        return False, "Senha é obrigatória"
    
    if len(password) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres"
    
    if not re.search(r'[a-zA-Z]', password):
        return False, "Senha deve conter pelo menos uma letra"
    
    if not re.search(r'\d', password):
        return False, "Senha deve conter pelo menos um número"
    
    return True, None


def validate_file(file):
    """
    Valida um arquivo de upload.
    
    Verifica:
    - Extensão permitida
    - Tamanho máximo
    """
    if not file or not file.filename:
        return False, "Arquivo é obrigatório"
    
    # Verificar extensão
    filename = file.filename.lower()
    extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    
    if extension not in Config.ALLOWED_EXTENSIONS:
        allowed = ', '.join(Config.ALLOWED_EXTENSIONS)
        return False, f"Tipo de arquivo não permitido. Aceitos: {allowed}"
    
    # Verificar tamanho (Flask já faz isso, mas verificamos aqui também)
    file.seek(0, 2)  # Vai para o final
    size = file.tell()
    file.seek(0)  # Volta para o início
    
    if size > Config.MAX_CONTENT_LENGTH:
        max_mb = Config.MAX_CONTENT_LENGTH / (1024 * 1024)
        return False, f"Arquivo muito grande. Máximo: {max_mb:.0f}MB"
    
    return True, None


def validate_code(code):
    """
    Valida um código de 5 dígitos.
    """
    if not code:
        return False, "Código é obrigatório"
    
    if len(code) != 5:
        return False, "Código deve ter 5 caracteres"
    
    if not re.match(r'^[A-Za-z0-9]+$', code):
        return False, "Código inválido"
    
    return True, None


def validate_description(description):
    """
    Valida uma descrição.
    """
    if description and len(description) > 1000:
        return False, "Descrição deve ter no máximo 1000 caracteres"
    
    return True, None


def validate_download_limit(limit):
    """
    Valida limite de downloads.
    """
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        return False, "Limite de downloads inválido"
    
    if limit < 1:
        return False, "Limite de downloads deve ser pelo menos 1"
    
    if limit > 1000:
        return False, "Limite de downloads deve ser no máximo 1000"
    
    return True, None


def validate_expiration(hours):
    """
    Valida tempo de expiração em horas.
    """
    try:
        hours = int(hours)
    except (TypeError, ValueError):
        return False, "Tempo de expiração inválido"
    
    if hours < 1:
        return False, "Tempo de expiração deve ser pelo menos 1 hora"
    
    # Máximo de 1 ano
    if hours > 8760:
        return False, "Tempo de expiração deve ser no máximo 1 ano"
    
    return True, None


def sanitize_input(text):
    """
    Sanitiza input de texto.
    Remove caracteres potencialmente perigosos.
    """
    if not text:
        return text
    
    # Remove caracteres de controle
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Escapa HTML básico
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text.strip()
