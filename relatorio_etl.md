# Relatório do Processo ETL - Dados dos Deputados Federais

## Introdução

Este documento descreve o processo de Extração, Transformação e Carga (ETL) de dados públicos dos deputados federais brasileiros, obtidos através da API de Dados Abertos da Câmara dos Deputados. O objetivo principal foi coletar, tratar e armazenar informações sobre os parlamentares da 56ª legislatura (2019-2023) e suas despesas durante o ano de 2022.

## Arquitetura da Solução
O processo foi implementado em Python utilizando as seguintes tecnologias:

**Linguagem**: Python

**Bibliotecas principais:**

- requests para consumo da API

- pandas para manipulação de dados

- sqlalchemy para conexão com bancos de dados

- dotenv para gerenciamento de variáveis de ambiente

- logging para registro de atividades

**Armazenamento:**

- MySQL (prioritário, configurável via variáveis de ambiente)

- SQLite (fallback local)

## **Desafios e Soluções**
#### **Páginas múltiplas:**

**Desafio:** A API retorna dados paginados

**Solução:** Implementação de função verificar_proxima_pagina e loop while para coletar todos os dados

#### **Dados incompletos:**

**Desafio:** A API para verificar despesas não retornava todos os dados do período escolhido

**Solução:** Após alguns testes, foi identificado que era necessário colocar além do período, o id da legislatura para ter todos os dados

####  **Estrutura aninhada dos dados:**

**Desafio:** JSON com vários níveis de aninhamento

**Solução:** Desnormalização em tabelas relacionadas

#### **Confiabilidade da conexão:**

**Desafio:** Possíveis falhas na conexão com MySQL

**Solução:** Implementação de fallback para SQLite local

####  **Monitoramento do processo:**

Desafio: Rastreabilidade das operações

Solução: Sistema de logging abrangente

## Fluxo do Processo ETL

#### **1. Configuração Inicial**
**Variáveis de ambiente:** Carregadas do arquivo .env para configurações sensíveis

**Logging:** Configurado para registrar todas as operações em arquivo e console

**Conexão com banco de dados:**

- Tentativa de conexão MySQL primeiro

- Fallback para SQLite local se MySQL não estiver disponível

#### **2. Extração de Dados**
Foram coletados dados de três endpoints principais da API:

**Lista de Deputados:**

- Requisição inicial filtrada pela 56ª legislatura

- Paginação automática para coletar todos os registros

**Detalhes dos Deputados:**

Para cada deputado, foram feitas requisições individuais

**Dados coletados em três categorias:**

- Informações pessoais

- Último status parlamentar

- Dados do gabinete

**Despesas dos Deputados:**

- Coletadas para cada deputado individualmente

- Filtradas por ano (2022) e legislatura (56ª)

- Paginação automática para todas as despesas

#### **3. Transformação de Dados**
Os principais tratamentos realizados foram:

**Normalização de dados:**

- Separação das informações em tabelas relacionadas:

- deputados_detalhado (dados pessoais)

- deputados_ultimo_status (informações parlamentares)

- deputados_ultimo_gabinete (dados do gabinete)

- deputados_despesas (gastos parlamentares)

**Limpeza de dados:**

- Remoção de campos não utilizados (redeSocial, urlWebsite)

- Adição de chaves estrangeiras para relacionamento entre tabelas

**Tratamento de paginação:**

- Implementação de lógica para percorrer todas as páginas disponíveis

#### **4. Carga de Dados**
Os dados foram persistidos em um banco de dados relacional com as seguintes tabelas:

**deputados:**

- Lista básica de todos os deputados do período selecionado

| Nome da coluna   | Descrição                                  |
|------------------|--------------------------------------------|
| id               | ID único do deputado                       |
| uri              | Link onde há os dados do deputado          |
| nome             | Nome de campanha do deputado               |
| siglaPartido     | Partido que o deputado era filiado         |
| uriPartido       | Link onde há os dados do partido           |
| siglaUf          | Estado que o deputado representa           |
| idLegislatura    | ID da legislatura do período               |
| urlFoto          | Link para visualizar a foto do deputado    |


**deputados_detalhado:**

- Informações pessoais dos deputados

| Nome da coluna      | Descrição                                  |
|---------------------|--------------------------------------------|
| id                  | ID único do deputado                       |
| uri                 | Link para os dados completos do deputado   |
| nomeCivil           | Nome civil completo do deputado            |
| cpf                 | Número do CPF do deputado                  |
| sexo                | Gênero do deputado (masculino/feminino)    |
| dataNascimento      | Data de nascimento do deputado             |
| dataFalecimento     | Data de falecimento (quando aplicável)     |
| ufNascimento        | Unidade Federativa de nascimento           |
| municipioNascimento | Município de nascimento do deputado        |
| escolaridade        | Nível de escolaridade do deputado          |

**deputados_ultimo_status:**

- Situação parlamentar mais recente

| Nome da coluna      | Descrição                                  |
|---------------------|--------------------------------------------|
| id                  | ID do registro de status                   |
| uri                 | Link para os dados completos do status     |
| nome                | Último nome de campanha do deputado        |
| siglaPartido        | Último partido que o deputado representou  |
| uriPartido          | Link para os dados do partido no status    |
| siglaUf             | Último UF de representação do deputado     |
| idLegislatura       | ID da última legislatura do deputado       |
| urlFoto             | Link da última foto registrada do deputado |
| email               | Email oficial ( Apenas se em atividade )   |
| data                | Data da última atualização do status       |
| nomeEleitoral       | Nome eleitoral utilizado                   |
| situacao            | Situação atual do mandato                  |
| condicaoEleitoral   | Condição eleitoral atual                   |
| descricaoStatus     | Observações para o último stauts           |
| id_deputado         | ID do deputado (chave estrangeira)         |

**deputados_ultimo_gabinete:**

Dados do gabinete do deputado ( Apenas para os que ainda estão em atividade )

| Nome da coluna | Descrição                          |
|----------------|------------------------------------|
| nome           | Nome do gabinete                   |
| predio         | Prédio onde está localizado        |
| sala           | Número da sala                     |
| andar          | Andar onde está situado            |
| telefone       | Telefone de contato do gabinete    |
| email          | Email oficial do gabinete          |
| id_deputado    | ID do deputado (chave estrangeira) |

### deputados_despesas:

Registros de gastos parlamentares em 2022

| Nome da coluna        | Descrição                                  |
|-----------------------|--------------------------------------------|
| ano                   | Ano da despesa                             |
| mes                   | Mês da despesa                             |
| tipoDespesa           | Tipo de despesa realizada                  |
| codDocumento          | Código do documento fiscal                 |
| tipoDocumento         | Tipo do documento fiscal                   |
| codTipoDocumento      | Código do tipo de documento                |
| dataDocumento         | Data de emissão do documento               |
| numDocumento          | Número do documento fiscal                 |
| valorDocumento        | Valor total do documento                   |
| urlDocumento          | URL do documento digitalizado              |
| nomeFornecedor        | Nome do fornecedor/beneficiário            |
| cnpjCpfFornecedor     | CNPJ/CPF do fornecedor                     |
| valorLiquido          | Valor líquido da despesa                   |
| valorGlosa            | Valor glosado (não reembolsado)            |
| numRessarcimento      | Número do ressarcimento                    |
| codLote               | Código do lote de pagamento                |
| parcela               | Número da parcela (quando aplicável)       |
| id_deputado           | ID do deputado (chave estrangeira)         |

#### **5. View para Acesso Simplificado aos Dados**

Para facilitar o acesso aos dados dos deputados, foi criada uma view chamada `deputados_completo` que combina informações das tabelas `deputados`, `deputados_detalhado`, `deputados_ultimo_status` e `deputados_ultimo_gabinete`. Esta view permite consultar todos os dados relevantes dos deputados em uma única consulta, simplificando a análise e visualização dos dados.

**Definição da View:**

```sql
CREATE VIEW `deputados_completo` AS
    SELECT 
        `dep`.`id` AS `id`,
        `dep`.`nome` AS `nomeCampanha`,
        `dep`.`siglaPartido` AS `siglaPartido`,
        `dep`.`siglaUf` AS `siglaUf`,
        `dep`.`urlFoto` AS `urlFoto`,
        `dep_det`.`nomeCivil` AS `nomeCivil`,
        `dep_det`.`cpf` AS `cpf`,
        `dep_det`.`sexo` AS `sexo`,
        `dep_det`.`dataNascimento` AS `dataNascimento`,
        `dep_det`.`dataFalecimento` AS `dataFalecimento`,
        `dep_det`.`ufNascimento` AS `ufNascimento`,
        `dep_det`.`municipioNascimento` AS `municipioNascimento`,
        `dep_det`.`escolaridade` AS `escolaridade`,
        `dep_ult`.`siglaPartido` AS `ultimoPartido`,
        `dep_ult`.`situacao` AS `situacao`,
        `dep_ult`.`condicaoEleitoral` AS `condicaoEleitoral`,
        `dep_ult`.`data` AS `ultimoStatus`,
        `dep_gab`.`predio` AS Prédio,
        dep_gab.sala AS Sala,
        dep_gab.andar AS Andar,
        dep_gab.telefone AS Telefone,
        dep_gab.email AS Email
    FROM
        (((deputados dep
        JOIN deputados_detalhado dep_det ON ((dep.id = dep_det.id)))
        JOIN deputados_ultimo_status dep_ult ON ((dep.id = dep_ult.id)))
        JOIN deputados_ultimo_gabinete dep_gab ON ((dep.id = dep_gab.id_deputado)))
```

Esta view é utilizada pelo dashboard para exibir informações completas sobre os deputados, permitindo uma análise mais eficiente dos dados. Ela combina informações pessoais, status parlamentar e dados de contato em uma única consulta, eliminando a necessidade de múltiplos joins para acessar essas informações.

# Conclusão
O processo ETL desenvolvido demonstra uma abordagem robusta para coleta e organização de dados públicos. A solução implementada:

- É flexível (permite configuração via ambiente)

- É resiliente (com fallback para banco local)

- Produz dados estruturados e relacionais

- Gera logs detalhados para auditoria

- Pode ser facilmente estendido para outros períodos ou tipos de dados

### Os dados resultantes estão prontos para análise, podendo ser utilizados para pesquisas acadêmicas, jornalismo de dados ou transparência pública. A arquitetura proposta serve como base para futuros projetos de coleta de dados governamentais.