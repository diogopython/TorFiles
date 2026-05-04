# Deployment

## Requisitos

- Python 3.9+
- MariaDB 10.5+
- PostgreSQL 13+
- Servidor com suporte a Python (Vercel, Heroku, VPS)

## Variaveis de Ambiente

```bash
MARIADB_URL=mysql://user:password@host:3306/torfiles
POSTGRES_URL=postgresql://user:password@host:5432/torfiles

SECRET_KEY=chave-secreta-longa-e-aleatoria
ENCRYPTION_KEY=chave-base64-32-bytes
```

### Gerando Chaves

```python
import secrets
import base64

# SECRET_KEY
print(secrets.token_hex(32))

# ENCRYPTION_KEY
print(base64.b64encode(secrets.token_bytes(32)).decode())
```

## Deploy em VPS

### 1. Clonar Repositorio

```bash
git clone <repo>
cd secure-file-share/backend
```

### 2. Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar Variaveis

```bash
export MARIADB_URL="mysql://..."
export POSTGRES_URL="postgresql://..."
export SECRET_KEY="..."
```

### 4. Executar

**Desenvolvimento:**
```bash
python app.py
```

## Configuracao de Banco de Dados

### MariaDB

```sql
CREATE DATABASE secureshare CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'secureshare'@'%' IDENTIFIED BY 'senha';
GRANT ALL PRIVILEGES ON secureshare.* TO 'secureshare'@'%';
```

### PostgreSQL

```sql
CREATE DATABASE secureshare;
CREATE USER secureshare WITH PASSWORD 'senha';
GRANT ALL PRIVILEGES ON DATABASE secureshare TO secureshare;
```

As tabelas sao criadas automaticamente na primeira execucao.

## Proxy Reverso (Nginx)

```nginx
server {
    listen 80;
    server_name secureshare.example.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## SSL/HTTPS

### Certbot (Let's Encrypt)

```bash
certbot --nginx -d secureshare.example.com
```

## Tor Hidden Service

### torrc

```
HiddenServiceDir /var/lib/tor/secureshare/
HiddenServicePort 80 127.0.0.1:8000
```

### Obter Endereco .onion

```bash
cat /var/lib/tor/secureshare/hostname
```

## Monitoramento

### Logs

- Flask logs erros para stderr
- Configure log rotation no sistema

### Health Check

Crie um endpoint simples:

```python
@app.route('/health')
def health():
    return {'status': 'ok'}
```

## Backup

### MariaDB

```bash
mysqldump -u user -p secureshare > backup.sql
```

### PostgreSQL

```bash
pg_dump -U user secureshare > backup.sql
```

### Restauracao

```bash
mysql -u user -p secureshare < backup.sql
psql -U user secureshare < backup.sql
```