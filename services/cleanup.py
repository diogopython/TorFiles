"""
Serviço de limpeza automática de arquivos.
Remove arquivos expirados e com downloads zerados.
"""
import threading
import time
from datetime import datetime
from config import Config


class CleanupWorker:
    """
    Worker para limpeza automática de arquivos expirados.
    
    Roda em uma thread separada e verifica periodicamente
    por arquivos que devem ser removidos.
    """
    
    def __init__(self):
        self.interval = Config.CLEANUP_INTERVAL
        self.running = False
        self.thread = None
    
    def _cleanup(self):
        """Executa a limpeza de arquivos expirados."""
        # Importamos aqui para evitar imports circulares
        from services.database import mariadb, postgres
        
        try:
            now = datetime.now()
            
            # Buscar arquivos expirados (por tempo ou downloads zerados)
            expired_files = mariadb.execute(
                """
                SELECT uuid FROM files 
                WHERE status != 'expired' 
                AND (expires_at < %s OR downloads_remaining <= 0)
                """,
                (now,),
                fetch=True
            )
            
            # Atualizar status para expirado
            mariadb.execute(
                """
                UPDATE files 
                SET status = 'expired' 
                WHERE status != 'expired' 
                AND (expires_at < %s OR downloads_remaining <= 0)
                """,
                (now,)
            )
            
            # Opcional: remover arquivos expirados há muito tempo (ex: 7 dias)
            # Isso libera espaço no PostgreSQL
            # old_expired = mariadb.execute(
            #     """
            #     SELECT uuid FROM files
            #     WHERE status = 'expired'
            #     AND expires_at < DATE_SUB(%s, INTERVAL 7 DAY)
            #     """,
            #     (now,),
            #     fetch=True
            # )
            #
            # for file in old_expired:
            #     postgres.delete_blob(file['uuid'])
            #     mariadb.execute("DELETE FROM files WHERE uuid = %s", (file['uuid'],))
            
        except Exception as e:
            # Log mínimo por privacidade
            print(f"Cleanup error: {type(e).__name__}")
    
    def _run(self):
        """Loop principal do worker."""
        while self.running:
            self._cleanup()
            time.sleep(self.interval)
    
    def start(self):
        """Inicia o worker em uma thread separada."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Para o worker."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)


# Instância global
cleanup_worker = CleanupWorker()
