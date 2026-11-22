# E-commerce Olist — Data Engineering Project

## 1. Visão Geral

Este projeto foi desenvolvido como solução para um desafio técnico de Engenharia de Dados, utilizando o dataset público de e-commerce brasileiro da Olist, disponibilizado no Kaggle.

O objetivo é construir uma plataforma de dados capaz de realizar a ingestão, transformação, organização e análise dos dados, desde os arquivos originais até uma estrutura analítica dimensional.

O projeto contempla duas frentes principais:

- **ETL local com Python:** processamento dos dados nas camadas RAW, Bronze, Silver e Gold, utilizando o VS Code.
- **Data Warehouse no Databricks:** construção de um modelo dimensional com tabelas fato e dimensões, consultas SQL e análises exploratórias orientadas ao negócio.

A solução busca demonstrar conhecimentos em Python, SQL, modelagem dimensional, qualidade de dados, processamento de dados e análise de informações de negócio.

## 2. Fonte de Dados

Foi utilizado o dataset [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data).

O conjunto contém informações de pedidos realizados na plataforma Olist, incluindo clientes, produtos, vendedores, pagamentos, avaliações, localização e logística.

Os arquivos utilizados são:

| Arquivo | Descrição |
|---|---|
| `olist_customers_dataset.csv` | Informações dos clientes |
| `olist_geolocation_dataset.csv` | Dados de geolocalização |
| `olist_orders_dataset.csv` | Informações dos pedidos |
| `olist_order_items_dataset.csv` | Itens associados aos pedidos |
| `olist_order_payments_dataset.csv` | Informações dos pagamentos |
| `olist_order_reviews_dataset.csv` | Avaliações dos pedidos |
| `olist_products_dataset.csv` | Cadastro de produtos |
| `olist_sellers_dataset.csv` | Cadastro de vendedores |
| `product_category_name_translation.csv` | Tradução dos nomes das categorias |

## 3. Arquitetura e Tecnologias

A solução utiliza uma arquitetura em camadas para organizar os dados progressivamente, separando a ingestão dos arquivos originais, as transformações e a disponibilização para análise.

### 3.1. Fluxo de processamento

```text
        Kaggle - Olist Dataset
                 |
                 v
              RAW
       Arquivos CSV originais
                 |
                 v
              BRONZE
      Dados ingeridos e organizados
                 |
                 v
              SILVER
       Dados tratados e padronizados
                 |
                 v
               GOLD
       Dados preparados para análise
                 |
                 v
       Databricks - Data Warehouse
                 |
                 v
         Modelo Dimensional
       Fatos + Dimensões + SQL
                 |
                 v
       Análises e Visualizações
```

### 3.2. Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Ingestão e transformação dos dados |
| Pandas | Manipulação de dados no processamento local |
| PyArrow / Parquet | Armazenamento dos dados em formato colunar |
| VS Code | Desenvolvimento e execução do ETL local |
| Databricks | Processamento analítico e construção do Data Warehouse |
| Apache Spark | Processamento distribuído e manipulação dos dados |
| SQL | Consultas, transformações e análises |
| Delta Lake | Armazenamento das tabelas analíticas no Databricks |
| Git e GitHub | Versionamento e documentação do projeto |

## 4. Estrutura do Repositório

```text
ecommerce-olist-data-platform/
│
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── src/
│   ├── ingestion/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── spark/
│
├── databricks/
│   ├── notebooks/
│   └── sql/
│       ├── gold/
│       └── validation/
│
├── analysis/
│   ├── images/
│   │   ├── vendas/
│   │   ├── logistica/
│   │   ├── satisfacao_cliente/
│   │   ├── financeiro/
│   │   └── clientes_pagamentos/
│   └── exploratory_data_analysis.md
│
├── tests/
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── data_quality.md
│   ├── dimensional_model.md
│   └── exploratory_data_analysis.md
│
├── main.py
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

**Observação:** os diretórios `data/` armazenam os dados processados localmente e não são versionados no GitHub, conforme as regras do `.gitignore`.

## 5. Como Executar o Projeto do Zero

### 5.1. Pré-requisitos

Para executar o ETL localmente, são necessários:

- Python compatível com as dependências do projeto.
- Visual Studio Code.
- Git.
- Dataset da Olist baixado do Kaggle.

### 5.2. Clonar o repositório

Abra o terminal e execute:

```bash
git clone https://github.com/MiMghtt/ecommerce-olist-data-platform.git

cd ecommerce-olist-data-platform
```

### 5.3. Configurar o ambiente Python

Crie um ambiente virtual:

**Windows PowerShell:**

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 5.4. Baixar e organizar os dados

Faça o download do dataset no Kaggle:

[Download — Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data)

Extraia os arquivos CSV e organize-os no diretório de dados RAW, conforme esperado pelo pipeline:

```text
data/
└── raw/
    ├── olist_customers_dataset.csv
    ├── olist_geolocation_dataset.csv
    ├── olist_orders_dataset.csv
    ├── olist_order_items_dataset.csv
    ├── olist_order_payments_dataset.csv
    ├── olist_order_reviews_dataset.csv
    ├── olist_products_dataset.csv
    ├── olist_sellers_dataset.csv
    └── product_category_name_translation.csv
```

### 5.5. Executar o ETL local

Com o ambiente virtual ativado, execute:

```bash
python src/main.py
```

O pipeline realiza o processamento dos arquivos pelas camadas definidas no projeto:

1. **RAW:** disponibilização dos arquivos originais.
2. **Bronze:** ingestão e organização inicial dos dados.
3. **Silver:** aplicação de transformações, padronização de tipos e tratamento dos dados.
4. **Gold:** construção de dados preparados para consumo analítico.

Ao final da execução, os dados processados são organizados nos respectivos diretórios de saída.

### 5.6. Validar a execução

Após o processamento, verifique:

- Se os arquivos foram carregados corretamente.
- Se as saídas das camadas foram geradas.
- Se os arquivos Silver estão disponíveis em formato Parquet.
- Se os testes e verificações de qualidade foram executados conforme implementados no projeto.

**Importante:** os dados não são disponibilizados no repositório GitHub. É necessário baixar os arquivos originais e executar o pipeline localmente para reproduzir o processamento.

## 6. Decisões de Modelagem

O projeto utiliza uma abordagem dimensional para disponibilizar os dados de forma organizada e facilitar consultas analíticas.

O modelo foi construído no Databricks, utilizando tabelas fato e dimensões.

### 6.1. Tabelas dimensão

| Tabela | Descrição |
|---|---|
| `dim_customer` | Dados dos clientes e identificação única |
| `dim_product` | Informações dos produtos e categorias |
| `dim_seller` | Informações dos vendedores |
| `dim_location` | Informações geográficas |
| `dim_date` | Dimensão calendário para análises temporais |

### 6.2. Tabelas fato

| Tabela | Granularidade | Descrição |
|---|---|---|
| `fact_sales` | Um registro por item do pedido | Informações comerciais, produtos, valores e vendedores |
| `fact_payments` | Um registro por pagamento do pedido | Meios de pagamento, parcelas e valores |
| `fact_delivery_metrics` | Um registro por pedido | Indicadores e datas relacionados à entrega |

### 6.3. Principais decisões

**Granularidade das tabelas fato**

Cada tabela fato possui uma granularidade própria:

- `fact_sales`: cada linha representa um item de pedido, identificado pela combinação de `order_id` e `order_item_id`.
- `fact_payments`: cada linha representa um registro de pagamento, identificado pela combinação de `order_id` e `payment_sequential`.
- `fact_delivery_metrics`: cada linha representa um pedido.

Essa separação evita misturar diferentes níveis de detalhe nas análises.

**Identificação dos clientes**

Foi utilizada a identificação `customer_unique_id` para análises de recorrência, pois um mesmo cliente pode aparecer associado a diferentes registros de `customer_id`.

**Dimensão calendário**

A `dim_date` permite realizar análises temporais a partir das datas associadas aos eventos de negócio.

**Separação entre vendas e pagamentos**

As informações comerciais dos itens e os registros de pagamento foram mantidos em tabelas fato distintas, respeitando suas respectivas granularidades e evitando duplicações em agregações.

## 7. Regras de Qualidade dos Dados

Foram realizadas verificações de qualidade ao longo do processamento, considerando aspectos estruturais e de consistência dos dados.

As verificações contemplam:

- **Tipos de dados:** conversão e padronização dos tipos de colunas.
- **Duplicidade:** identificação e tratamento de registros duplicados conforme as regras aplicadas às tabelas.
- **Valores nulos:** identificação de campos sem preenchimento.
- **Consistência:** investigação de divergências entre status dos pedidos e informações de datas.
- **Integridade das informações:** validação das relações utilizadas na construção das tabelas analíticas.

Durante a análise, também foram investigadas inconsistências presentes nos dados originais, especialmente relacionadas a pedidos com status de entrega e datas de entrega ausentes ou divergentes.

As regras, verificações e resultados estão detalhados em [Qualidade dos Dados](docs/data_quality.md).

## 8. Análises e Gráficos

Após a construção do modelo analítico, foram desenvolvidas análises exploratórias para responder a dez perguntas de negócio, distribuídas em cinco áreas.

As consultas SQL e visualizações foram desenvolvidas no Databricks.

| Área | Pergunta 1 | Pergunta 2 |
|---|---|---|
| Vendas | Quais são as 10 categorias com maior receita? | Como a receita total varia mês a mês? |
| Logística | Qual o tempo médio de entrega por estado? | Qual a porcentagem de pedidos entregues com atraso? |
| Satisfação do cliente | Como se distribuem as notas de 1 a 5? | Pedidos atrasados têm nota média menor que os entregues no prazo? |
| Financeiro | Qual a receita por categoria e sua participação no total? | Qual o valor médio do frete por estado do cliente? |
| Clientes e pagamentos | Qual a porcentagem de clientes que compraram mais de uma vez? | Quais os meios de pagamento mais usados? |

### Principais resultados

- **Vendas:** Health & Beauty apresentou a maior receita, com aproximadamente R$ 1,26 milhão.
- **Logística:** 8,11% dos pedidos entregues com datas válidas foram classificados como atrasados.
- **Satisfação:** pedidos atrasados apresentaram nota média de 2,57, contra 4,29 para pedidos entregues no prazo.
- **Financeiro:** as três categorias com maior receita concentraram 25,76% da receita de produtos.
- **Clientes:** 3,05% dos clientes compradores realizaram mais de uma compra.
- **Pagamentos:** o cartão de crédito representou 73,92% dos registros de pagamento.

### Relatório e visualizações

O relatório completo, incluindo as conclusões, critérios de análise e gráficos, está disponível em:

[Análise Exploratória de Dados](docs/exploratory_data_analysis.md)

Os notebooks utilizados nas análises estão organizados em databricks/notebooks/.

## 9. Premissas e Limitações

### Premissas

- O dataset da Olist representa os dados disponibilizados para o período e escopo da base pública.
- A receita de produtos considera o campo `price`, sem incluir o valor do frete.
- As análises de recorrência utilizam `customer_unique_id` como identificador do cliente.
- Os cálculos de atraso consideram pedidos entregues com datas efetivas e estimadas disponíveis.
- As análises respeitam a granularidade de cada tabela fato.

### Limitações

- O dataset é histórico e não representa necessariamente a operação atual da Olist.
- A qualidade e a completude das análises dependem das informações disponibilizadas nos arquivos originais.
- Foram identificadas inconsistências em alguns registros, principalmente relacionadas a status e datas de entrega.
- A tabela `fact_sales` possui granularidade por item, enquanto `fact_payments` possui granularidade por pagamento. Comparações entre essas tabelas exigem agregação adequada para evitar duplicidades.
- A análise de recorrência considera clientes com pedidos representados na `fact_sales`, não necessariamente todos os clientes cadastrados na base original.
- Os resultados de estados com baixo volume de pedidos podem apresentar maior sensibilidade a variações na amostra.

## 10. Dependências

As bibliotecas e versões utilizadas no processamento local estão especificadas no arquivo:

[`requirements.txt`](requirements.txt)

Para instalar as dependências:

```bash
pip install -r requirements.txt
```

## 11. Documentação Complementar

A documentação técnica do projeto está organizada na pasta [`docs/`](docs/).

| Documento | Conteúdo |
|---|---|
| [Arquitetura](docs/architecture.md) | Arquitetura da solução e fluxo de processamento |
| [Dicionário de Dados](docs/data_dictionary.md) | Descrição das tabelas, campos e tipos de dados |
| [Qualidade dos Dados](docs/data_quality.md) | Regras, validações e verificações de qualidade |
| [Modelo Dimensional](docs/dimensional_model.md) | Estrutura das dimensões e tabelas fato |
| [Análise Exploratória](docs/exploratory_data_analysis.md) | Perguntas de negócio, resultados e gráficos |

## 12. Uso de Ferramentas de Inteligência Artificial

Durante o desenvolvimento deste projeto, foi utilizada a ferramenta **ChatGPT (OpenAI)** como apoio ao desenvolvimento técnico e à documentação.

A ferramenta foi utilizada como suporte nas seguintes atividades:

- **Desenvolvimento:** auxílio na revisão e compreensão de consultas SQL e códigos Python.
- **Modelagem de dados:** apoio na discussão das decisões de modelagem dimensional e na definição da granularidade das tabelas fato.
- **Qualidade dos dados:** auxílio na interpretação de inconsistências identificadas.
- **Análise exploratória:** apoio na organização das conclusões.
- **Documentação:** auxílio na organização e redação dos arquivos Markdown, incluindo README, documentação técnica e relatório de análise exploratória.

## 13. Repositório

**GitHub:** [ecommerce-olist-data-platform](https://github.com/MiMghtt/ecommerce-olist-data-platform)

## 14. Autora

**Linkedin:** [Michelle Marighetti](https://www.linkedin.com/in/mi-marighetti/)

