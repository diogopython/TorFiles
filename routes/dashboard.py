"""
Rotas do dashboard do usuário.
Gerenciamento de arquivos.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.file import File
from utils.helpers import login_required, get_current_user_id, format_timedelta
from config import Config

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Página principal do dashboard."""
    user_id = get_current_user_id()
    
    # Buscar todos os arquivos do usuário
    files = File.find_by_user(user_id)
    
    # Atualizar status de arquivos expirados
    for file in files:
        if file.status == 'active' and file.is_expired():
            file.update_status('expired')
    
    # Separar por status
    active_files = [f for f in files if f.status == 'active']
    paused_files = [f for f in files if f.status == 'paused']
    expired_files = [f for f in files if f.status == 'expired']
    
    # Adicionar tempo formatado
    for file in files:
        file.time_remaining_formatted = format_timedelta(file.time_remaining())
    
    return render_template('dashboard/index.html',
                           active_files=active_files,
                           paused_files=paused_files,
                           expired_files=expired_files,
                           active_count=len(active_files),
                           max_files=Config.MAX_ACTIVE_FILES)


@dashboard_bp.route('/dashboard/delete/<code>', methods=['POST'])
@login_required
def delete_file(code):
    """Remove um arquivo."""
    user_id = get_current_user_id()
    
    file = File.find_by_code(code)
    
    if not file or file.user_id != user_id:
        flash('Arquivo não encontrado.', 'error')
        return redirect(url_for('dashboard.index'))
    
    try:
        file.delete()
        flash('Arquivo removido com sucesso.', 'success')
    except Exception as e:
        flash('Erro ao remover arquivo.', 'error')
    
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/dashboard/pause/<code>', methods=['POST'])
@login_required
def pause_file(code):
    """Pausa um arquivo (bloqueia downloads)."""
    user_id = get_current_user_id()
    
    file = File.find_by_code(code)
    
    if not file or file.user_id != user_id:
        flash('Arquivo não encontrado.', 'error')
        return redirect(url_for('dashboard.index'))
    
    if file.status != 'active':
        flash('Este arquivo não pode ser pausado.', 'warning')
        return redirect(url_for('dashboard.index'))
    
    try:
        file.update_status('paused')
        flash('Arquivo pausado. Downloads bloqueados.', 'success')
    except Exception as e:
        flash('Erro ao pausar arquivo.', 'error')
    
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/dashboard/activate/<code>', methods=['POST'])
@login_required
def activate_file(code):
    """Reativa um arquivo pausado."""
    user_id = get_current_user_id()
    
    file = File.find_by_code(code)
    
    if not file or file.user_id != user_id:
        flash('Arquivo não encontrado.', 'error')
        return redirect(url_for('dashboard.index'))
    
    if file.status != 'paused':
        flash('Este arquivo não pode ser reativado.', 'warning')
        return redirect(url_for('dashboard.index'))
    
    # Verificar se não está expirado
    if file.is_expired():
        flash('Este arquivo já expirou e não pode ser reativado.', 'warning')
        file.update_status('expired')
        return redirect(url_for('dashboard.index'))
    
    # Verificar limite de arquivos ativos
    active_count = File.count_active_by_user(user_id)
    if active_count >= Config.MAX_ACTIVE_FILES:
        flash(f'Você atingiu o limite de {Config.MAX_ACTIVE_FILES} arquivos ativos.', 'warning')
        return redirect(url_for('dashboard.index'))
    
    try:
        file.update_status('active')
        flash('Arquivo reativado com sucesso.', 'success')
    except Exception as e:
        flash('Erro ao reativar arquivo.', 'error')
    
    return redirect(url_for('dashboard.index'))
