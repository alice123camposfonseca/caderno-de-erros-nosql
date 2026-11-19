# caderno-de-erros-nosql
Caderno de erros inteligente com MongoDB (trabalho de BD NoSQL, UFU)

# Descrição do Sistema

O Caderno de Erros é uma aplicação voltada para estudantes que desejam
organizar, acompanhar e revisar os erros cometidos durante seus estudos.

A proposta do sistema é transformar erros cometidos em exercícios,
provas, listas de questões e outras atividades acadêmicas, 
permitindo que o estudante registre suas dificuldades
e acompanhe sua evolução ao longo do tempo.

O sistema permitirá o cadastro de erros associados a diferentes disciplinas
e assuntos, incluindo informações como descrição do erro, tipo de
dificuldade, nível de dificuldade, quantidade de vezes que o erro foi
cometido e palavras-chave relacionadas ao conteúdo.

Também será possível registrar revisões dos erros cadastrados,
informando a data da revisão, o resultado obtido e observações sobre
o desempenho do estudante.

A aplicação contará com funcionalidades de consulta e organização
dos erros, possibilitando a filtragem por disciplina, assunto,
tipo e dificuldade. Além disso, poderá auxiliar na identificação
de erros recorrentes e na priorização de conteúdos que precisam
ser revisados.

# Tecnologias Utilizadas

- Python: linguagem utilizada no desenvolvimento da aplicação.
- MongoDB Atlas: banco de dados NoSQL orientado a documentos,
  utilizado para armazenamento das informações.
- PyMongo: biblioteca responsável pela comunicação entre Python
  e MongoDB.
- python-dotenv: biblioteca utilizada para carregar variáveis
  de ambiente, como a string de conexão ao banco.
- Redis Stack: cache de login e estruturas probabilísticas.

# Redis: login e estatísticas de uso

Esta etapa adiciona Redis ao sistema sem substituir o MongoDB, que continua
como fonte persistente dos usuários e erros.

| Estrutura | Chave | Uso no projeto |
| --- | --- | --- |
| Cache com TTL | `auth:session:<token>` | Sessão do login por 30 minutos. |
| Bloom Filter | `users:emails` | Evita consultar o MongoDB para e-mails que certamente não existem. |
| HyperLogLog | `stats:unique-users:<data>` | Estima usuários únicos que fizeram login no dia. |
| Count-Min Sketch | `stats:login-frequency` e `stats:event-frequency` | Estima logins por usuário e eventos como cadastros e revisões. |

## Executar a etapa Redis

1. Copie `.env.example` para `.env` e preencha `MONGODB_URI`.
2. Crie/atualize os usuários de demonstração (todos usam a senha `senha123`):
   `python database/criar_usuarios.py`.
3. Instale as dependências: `pip install -r requirements.txt`.
4. Inicie o Redis Stack: `docker compose up -d`.
5. Inicie a API: `uvicorn api.main:app --reload`.

Faça `POST /auth/login` com `{"email":"ana@email.com","senha":"senha123"}`.
Use o token retornado como `Authorization: Bearer <token>` em `GET /auth/me`.
Após alguns logins, consulte `GET /stats/usage` para ver as estimativas.

## Interface com login

Com a API e o Redis em execução, inicie a interface com:

```powershell
streamlit run frontend/app.py
```

Ela abrirá uma tela de login. Entre com `ana@email.com` e `senha123`.
O token da sessão fica somente na sessão do navegador e o botão **Sair**
invalida a chave correspondente no Redis.

# Justificativa da Escolha do MongoDB

O MongoDB foi escolhido por ser um banco de dados NoSQL orientado
a documentos, permitindo armazenar informações em estruturas
semelhantes a JSON.
Essa característica é adequada ao Caderno de Erros, pois cada erro
pode possuir diferentes informações e quantidades de revisões.
A utilização de documentos embutidos permite armazenar o histórico
de revisões diretamente no documento correspondente ao erro,
facilitando a representação de informações relacionadas.
Além disso, a flexibilidade do MongoDB permite que novos campos
e funcionalidades sejam incorporados ao sistema conforme sua evolução,
sem exigir uma estrutura rígida de tabelas.

# Exemplos de Documentos

O script `database/criar_banco.py` realiza a criação do banco,
da coleção e a inserção de documentos de exemplo no MongoDB Atlas.
