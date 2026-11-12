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
