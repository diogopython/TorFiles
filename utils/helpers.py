"""
Funções auxiliares gerais.
"""
from datetime import timedelta
from functools import wraps
from flask import session, redirect, url_for, flash


def format_timedelta(td):
    """
    Formata um timedelta para exibição amigável.
    
    Args:
        td: timedelta object
    
    Returns:
        str: Tempo formatado (ex: "2 dias, 3 horas")
    """
    if not td or td.total_seconds() <= 0:
        return "Expirado"
    
    total_seconds = int(td.total_seconds())
    
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    
    parts = []
    
    if days > 0:
        parts.append(f"{days} {'dia' if days == 1 else 'dias'}")
    if hours > 0:
        parts.append(f"{hours} {'hora' if hours == 1 else 'horas'}")
    if minutes > 0 and days == 0:  # Só mostra minutos se < 1 dia
        parts.append(f"{minutes} {'minuto' if minutes == 1 else 'minutos'}")
    
    if not parts:
        return "Menos de 1 minuto"
    
    return ", ".join(parts[:2])  # Máximo 2 partes


def format_file_size(size_bytes):
    """
    Formata tamanho de arquivo para exibição.
    
    Args:
        size_bytes: Tamanho em bytes
    
    Returns:
        str: Tamanho formatado (ex: "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def login_required(f):
    """
    Decorator que exige autenticação.
    Redireciona para login se não autenticado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id():
    """Retorna o ID do usuário atual ou None."""
    return session.get('user_id')


def expiration_options():
    """
    Retorna opções de expiração para formulários.
    
    Returns:
        list: Lista de tuplas (valor_horas, label)
    """
    return [
        (1, "1 hora"),
        (6, "6 horas"),
        (12, "12 horas"),
        (24, "1 dia"),
        (72, "3 dias"),
        (168, "1 semana"),
        (720, "1 mês"),
        (2160, "3 meses"),
        (4320, "6 meses"),
        (8760, "1 ano"),
    ]
