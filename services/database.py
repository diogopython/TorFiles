"""
Serviço de conexão com bancos de dados.
Gerencia conexões com MariaDB (metadados) e PostgreSQL (arquivos).
"""
import pymysql
import psycopg2
from contextlib import contextmanager
from config import Config


class MariaDBService:
    """Serviço para operações no MariaDB."""
    
    def __init__(self):
        self.config = Config.get_mariadb_config()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão com MariaDB."""
        if not self.config:
            raise ValueError("MARIADB_URL não configurada")
        
        conn = pymysql.connect(**self.config)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query, params=None, fetch=False, fetchone=False):
        """Executa uma query no MariaDB."""
        with self.get_connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params or ())
                if fetchone:
                    result = cursor.fetchone()
                elif fetch:
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = cursor.lastrowid
                return result
    
    def init_tables(self):
        """Inicializa as tabelas no MariaDB."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                code CHAR(5) UNIQUE NOT NULL,
                uuid CHAR(36) UNIQUE NOT NULL,
                filename VARCHAR(255) NOT NULL,
                description TEXT,
                file_hash CHAR(64) NOT NULL,
                downloads_remaining INT NOT NULL,
                download_limit INT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                status ENUM('active', 'paused', 'expired') DEFAULT 'active',
                has_password BOOLEAN DEFAULT FALSE,
                password_hash VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        ]
        
        # Criar índices separadamente
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_files_code ON files(code)",
            "CREATE INDEX IF NOT EXISTS idx_files_user_status ON files(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_files_expires ON files(expires_at)"
        ]
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                for query in queries:
                    cursor.execute(query)
                
                # Índices podem falhar se já existirem, ignorar erros
                for query in index_queries:
                    try:
                        cursor.execute(query)
                    except pymysql.err.OperationalError:
                        pass
                
                conn.commit()


class PostgresService:
    """Serviço para operações no PostgreSQL."""
    
    def __init__(self):
        self.dsn = Config.get_postgres_config()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão com PostgreSQL."""
        if not self.dsn:
            raise ValueError("POSTGRES_URL não configurada")
        
        conn = psycopg2.connect(self.dsn)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query, params=None, fetch=False, fetchone=False):
        """Executa uma query no PostgreSQL."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetchone:
                    result = cursor.fetchone()
                elif fetch:
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = None
                return result
    
    def init_tables(self):
        """Inicializa as tabelas no PostgreSQL."""
        query = """
        CREATE TABLE IF NOT EXISTS file_blobs (
            uuid UUID PRIMARY KEY,
            encrypted_data BYTEA NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
    
    def save_blob(self, uuid, encrypted_data):
        """Salva um arquivo criptografado no PostgreSQL."""
        query = "INSERT INTO file_blobs (uuid, encrypted_data) VALUES (%s, %s)"
        self.execute(query, (uuid, psycopg2.Binary(encrypted_data)))
    
    def get_blob(self, uuid):
        """Recupera um arquivo criptografado do PostgreSQL."""
        query = "SELECT encrypted_data FROM file_blobs WHERE uuid = %s"
        result = self.execute(query, (uuid,), fetchone=True)
        return result[0] if result else None
    
    def delete_blob(self, uuid):
        """Remove um arquivo do PostgreSQL."""
        query = "DELETE FROM file_blobs WHERE uuid = %s"
        self.execute(query, (uuid,))


# Instâncias globais
mariadb = MariaDBService()
postgres = PostgresService()
