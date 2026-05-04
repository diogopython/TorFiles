"""
Rotas de upload de arquivos.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.file import File
from utils.validators import (
    validate_file, validate_description, validate_download_limit,
    validate_expiration, validate_password, sanitize_input
)
from utils.helpers import login_required, expiration_options, get_current_user_id
from config import Config

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def form():
    """Página e processamento de upload."""
    user_id = get_current_user_id()
    
    # Verificar limite de arquivos ativos
    active_count = File.count_active_by_user(user_id)
    if active_count >= Config.MAX_ACTIVE_FILES:
        flash(f'Você atingiu o limite de {Config.MAX_ACTIVE_FILES} arquivos ativos. '
              'Apague ou aguarde a expiração de algum arquivo.', 'warning')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Obter arquivo
        file = request.files.get('file')
        
        # Validar arquivo
        valid, error = validate_file(file)
        if not valid:
            flash(error, 'error')
            return render_template('upload/form.html', 
                                   expiration_options=expiration_options(),
                                   active_count=active_count,
                                   max_files=Config.MAX_ACTIVE_FILES)
        
        # Obter outros campos
        description = sanitize_input(request.form.get('description', '').strip())
        password = request.form.get('password', '').strip() or None
        download_limit = request.form.get('download_limit', '10')
        expires_hours = request.form.get('expires_hours', '24')
        
        # Validar descrição
        valid, error = validate_description(description)
        if not valid:
            flash(error, 'error')
            return render_template('upload/form.html',
                                   expiration_options=expiration_options(),
                                   active_count=active_count,
                                   max_files=Config.MAX_ACTIVE_FILES)
        
        # Validar limite de downloads
        valid, error = validate_download_limit(download_limit)
        if not valid:
            flash(error, 'error')
            return render_template('upload/form.html',
                                   expiration_options=expiration_options(),
                                   active_count=active_count,
                                   max_files=Config.MAX_ACTIVE_FILES)
        
        # Validar expiração
        valid, error = validate_expiration(expires_hours)
        if not valid:
            flash(error, 'error')
            return render_template('upload/form.html',
                                   expiration_options=expiration_options(),
                                   active_count=active_count,
                                   max_files=Config.MAX_ACTIVE_FILES)
        
        # Validar senha opcional (se fornecida)
        if password:
            valid, error = validate_password(password)
            if not valid:
                flash(f'Senha de download: {error}', 'error')
                return render_template('upload/form.html',
                                       expiration_options=expiration_options(),
                                       active_count=active_count,
                                       max_files=Config.MAX_ACTIVE_FILES)
        
        try:
            # Ler dados do arquivo
            file_data = file.read()
            
            # Criar arquivo
            new_file = File.create(
                user_id=user_id,
                filename=file.filename,
                file_data=file_data,
                description=description,
                password=password,
                download_limit=int(download_limit),
                expires_hours=int(expires_hours)
            )
            
            flash(f'Arquivo enviado com sucesso! Código: {new_file.code}', 'success')
            return redirect(url_for('dashboard.index'))
        
        except Exception as e:
            flash('Erro ao enviar arquivo. Tente novamente.', 'error')
            return render_template('upload/form.html',
                                   expiration_options=expiration_options(),
                                   active_count=active_count,
                                   max_files=Config.MAX_ACTIVE_FILES)
    
    return render_template('upload/form.html',
                           expiration_options=expiration_options(),
                           active_count=active_count,
                           max_files=Config.MAX_ACTIVE_FILES)
