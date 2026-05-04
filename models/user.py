"""
Modelo de usuário para operações no MariaDB.
"""
from services.database import mariadb
from services.crypto import crypto


class User:
    """Modelo de usuário."""
    
    def __init__(self, id=None, username=None, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at
    
    @classmethod
    def from_dict(cls, data):
        """Cria um User a partir de um dicionário."""
        if not data:
            return None
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password_hash=data.get('password_hash'),
            created_at=data.get('created_at')
        )
    
    @classmethod
    def find_by_id(cls, user_id):
        """Busca usuário por ID."""
        result = mariadb.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            fetchone=True
        )
        return cls.from_dict(result)
    
    @classmethod
    def find_by_username(cls, username):
        """Busca usuário por username."""
        result = mariadb.execute(
            "SELECT * FROM users WHERE username = %s",
            (username,),
            fetchone=True
        )
        return cls.from_dict(result)
    
    @classmethod
    def create(cls, username, password):
        """Cria um novo usuário."""
        # Verificar se username já existe
        existing = cls.find_by_username(username)
        if existing:
            raise ValueError("Username já existe")
        
        # Hash da senha com Argon2
        password_hash = crypto.hash_password(password)
        
        # Inserir no banco
        user_id = mariadb.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        
        return cls(id=user_id, username=username, password_hash=password_hash)
    
    def verify_password(self, password):
        """Verifica se a senha está correta."""
        return crypto.verify_password(self.password_hash, password)
    
    def to_dict(self):
        """Converte para dicionário (sem dados sensíveis)."""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': str(self.created_at) if self.created_at else None
        }
