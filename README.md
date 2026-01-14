# FIAP-8MLET-TechChallenge
Criação de uma API Pública para Consulta de Livros

## Link do deploy
http://techchallenge.ddns.net:8000/
Favor avisar antes de avaliar pois a vm permanece desligada quando não esta sendo usada.

## Link do vídeo
https://drive.google.com/file/d/12mCtSbBZ4kpggHY-_4XXW3-WbiH4zGOc/view?usp=sharing

# Book API - Documentação
## Descrição
Este projeto é uma API REST desenvolvida em FastAPI para consulta e gerenciamento de dados de livros extraídos do site books.toscrape.com. A aplicação permite:
- Autenticação JWT com tokens de acesso e refresh
- Consulta de livros por diversos critérios (título, categoria, preço, avaliação)
- Estatísticas sobre a coleção de livros
- Processo de scraping assíncrono para coleta de dados
- Documentação automática via Swagger UI e ReDoc

# Arquitetura do Sistema
## Estrutura de Pastas
book_api/
├── api/                          # Camada de apresentação (FastAPI)
│   ├── routes/                   # Endpoints organizados por módulo
│   │   ├── auth.py              # Rotas de autenticação
│   │   ├── books.py             # Rotas de livros
│   │   ├── categories.py        # Rotas de categorias
│   │   ├── health.py            # Health checks
│   │   ├── scraper_router.py    # Rotas de scraping
│   │   └── stats.py             # Rotas de estatísticas
│   └── main.py                  # Aplicação FastAPI principal
│
├── scripts/                      # Lógica de negócio e persistência
│   ├── auth.py                  # Autenticação e JWT
│   ├── crud.py                  # Operações de banco de dados
│   ├── database.py              # Configuração do banco
│   ├── models.py                # Modelos SQLAlchemy
│   ├── schemas.py               # Schemas Pydantic
│   └── scraper.py               # Web scraping
│
├── alembic/                      # Migrações de banco de dados
├── tests/                        # Testes automatizados
└── pyproject.toml               # Dependências com Poetry

## Pipeline
https://www.mermaidchart.com/d/0ba752fb-f731-4d33-91df-c9d91278babc

## Diagrama (arquitetura) visual do projeto
https://www.mermaidchart.com/d/95904e01-b8c9-4ef6-adde-25b570f53f51

## Tecnologias Utilizadas
- FastAPI: Framework web moderno e rápido
- PostgreSQL: Banco de dados relacional
- SQLAlchemy: ORM para Python
- Poetry: Gerenciamento de dependências
- Alembic: Migrações de banco de dados
- JWT: Autenticação por tokens
- BeautifulSoup4: Web scraping

# Instalação e Configuração
## Pré-requisitos
- Python 3.14 ou superior
- Poetry 1.7 ou superior
- PostgreSQL 12 ou superior
- Git

## Passo a Passo da Instalação
1. Clone o repositório
git clone <url-do-repositorio>
cd book_api

2. Instale as dependências com Poetry
poetry install

3. Configure o ambiente
Crie um arquivo .env na raiz do projeto:
### Banco de Dados PostgreSQL
DB_USER=postgres
DB_PASS=sua_senha_aqui
DB_NAME=book_api
DB_HOST=localhost
DB_PORT=5432

### Autenticação JWT
SECRET_KEY=sua_chave_secreta_super_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

### API
API_HOST=0.0.0.0
API_PORT=8000

4. Configure o banco de dados
### Crie o banco de dados no PostgreSQL
sudo -u postgres createdb book_api

### Execute as migrações
poetry run alembic upgrade head

5. Execute o scraper para popular o banco (opcional)
### Execute o scraper para coletar dados iniciais
poetry run python -m scripts.scraper

# Como Executar a Aplicação
## Ambiente de Desenvolvimento
### Ative o ambiente virtual do Poetry
poetry env activate

### Execute a aplicação com recarregamento automático
poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Verifique se está funcionando
## Acesse no seu navegador:
- API: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs
- Documentação ReDoc: http://localhost:8000/redoc

# Documentação da API
## Autenticação
Apenas os endpoints /api/v1/scraping/trigger, /api/v1/scraping/status e /api/v1/scraping/status/{job_id}/output requerem autenticação via Bearer Token.

### Login
POST /api/v1/login/
Content-Type: application/x-www-form-urlencoded

username=admin&password=secret

#### Resposta
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

### Refresh Token
POST /api/v1/refresh/
Content-Type: application/json

{
  "refresh_token": "seu_refresh_token_aqui"
}

## Livros
### Listar todos os livros
GET /api/v1/books/
Authorization: Bearer <access_token>

#### Parâmetros:
- skip: Número de registros para pular (padrão: 0)
- limit: Número máximo de registros (padrão: 100, máximo: 1000)

### Buscar livro por UPC
GET /api/v1/books/{upc}
Authorization: Bearer <access_token>

### Buscar livros
GET /api/v1/books/search/
Authorization: Bearer <access_token>

#### Parâmetros
- title: Busca parcial no título (case-insensitive)
- category: Filtra por categoria

### Livros mais bem avaliados
GET /api/v1/books/top-rated/
Authorization: Bearer <access_token>

#### Parâmetros:
- min_rating: Avaliação mínima (1-5, padrão: 4)

### Livros por faixa de preço
GET /api/v1/books/price-range/
Authorization: Bearer <access_token>

#### Parâmetros:
- min_price: Preço mínimo
- max_price: Preço máximo

## Categorias
### Listar categorias
GET /api/v1/categories/
Authorization: Bearer <access_token>

## Estatísticas
### Visão geral
GET /api/v1/stats/overview/
Authorization: Bearer <access_token>

#### Resposta
{
  "total_books": 1000,
  "average_price": 45.67,
  "rating_distribution": {
    "1": 50,
    "2": 100,
    "3": 200,
    "4": 400,
    "5": 250
  }
}

### Estatísticas por categoria
GET /api/v1/stats/categories/
Authorization: Bearer <access_token>

## Scraping
### Iniciar scraping
POST /api/v1/scraping/trigger/
Authorization: Bearer <access_token>

### Verificar status
GET /api/v1/scraping/status/{job_id}
Authorization: Bearer <access_token>

### Verificar output
GET /api/v1/scraping/status/{job_id}/output
Authorization: Bearer <access_token>

## Health Check
GET /api/v1/health/

## Exemplos de Chamadas API
1. Autenticação e Listagem de Livros
    1. Faça login
    curl -X POST "http://localhost:8000/api/v1/login/" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=secret"

    2. Use o token para listar livros
    curl -X GET "http://localhost:8000/api/v1/books/" \
    -H "Authorization: Bearer SEU_ACCESS_TOKEN"

2. Busca Avançada
Buscar livros sobre "python" na categoria "programming"
curl -X GET "http://localhost:8000/api/v1/books/search/?title=python&category=programming" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"

3. Estatísticas
Obter estatísticas gerais
curl -X GET "http://localhost:8000/api/v1/stats/overview/" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"

4. Scraping
# Iniciar scraping
curl -X POST "http://localhost:8000/api/v1/scraping/trigger/" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"

Verificar status (substitua {job_id} pelo ID retornado)
curl -X GET "http://localhost:8000/api/v1/scraping/status/{job_id}" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"

# Deploy em Produção
Para deploy em produção:
1. Altere a SECRET_KEY para uma chave segura e única
2. Configure HTTPS usando um proxy reverso (Nginx/Apache)
3. Use variáveis de ambiente para configurações sensíveis
4. Configure CORS apropriadamente no main.py
5. Use um process manager como Systemd ou Supervisor