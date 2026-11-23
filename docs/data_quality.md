# Data Quality – Olist Dataset

## 1. Objetivo

Documentar as regras de qualidade aplicadas durante a transformação dos dados da camada Bronze para Silver e durante a construção das métricas da camada Gold.

O processo utiliza PySpark para garantir padronização de tipos, consistência, rastreabilidade e preservação das informações originais.

As validações contemplam conversões de tipos, tratamento de duplicidades, preservação de valores nulos, tradução de categorias de produtos e construção de métricas logísticas.

## 2. Padronização de tipos

Foram realizadas conversões de tipos de dados conforme as características de cada tabela, utilizando recursos do PySpark.

- Colunas de datas convertidas para `TimestampType`.
- Colunas numéricas convertidas para `DoubleType`.
- Colunas inteiras convertidas para `LongType`, permitindo valores nulos.
- Valores incompatíveis com o tipo esperado são convertidos para `NULL`.
- Os registros afetados são preservados.
- Os valores inválidos identificados durante as conversões são contabilizados nos relatórios de qualidade.

As conversões utilizam operações tolerantes a erros, como `try_to_timestamp` e `try_cast`, evitando que valores incompatíveis interrompam a execução do pipeline.

## 3. Tratamento de duplicidades

Foram definidas chaves de identificação para verificar duplicidades nas tabelas.

| Tabela | Chave | Tratamento |
|---|---|---|
| Customers | customer_id | Remover duplicidades |
| Orders | order_id | Remover duplicidades |
| Order Items | order_id, order_item_id | Remover duplicidades |
| Payments | order_id, payment_sequential | Remover duplicidades |
| Reviews | review_id, order_id | Remover duplicidades |
| Products | product_id | Remover duplicidades |
| Sellers | seller_id | Remover duplicidades |
| Geolocation | Sem chave única definida | Preservar registros |
| Category Translation | product_category_name | Remover duplicidades |

**Regras adicionais:**

- Registros com chaves incompletas não são removidos.
- Registros duplicados são identificados considerando as chaves definidas para cada tabela.
- Quando há duplicidade, é selecionado um registro por meio de uma ordenação determinística baseada nos campos não pertencentes à chave.
- A implementação atual não garante a preservação da primeira ocorrência na ordem original do CSV, pois essa ordem não foi armazenada na camada Bronze.

**Resultado da execução:** nenhuma duplicidade foi identificada nas chaves verificadas durante os diagnósticos realizados.

## 4. Tratamento de valores nulos

Valores nulos são preservados quando representam informações ausentes ou situações legítimas do negócio.

Exemplos identificados:

- Pedidos não entregues podem não possuir data efetiva de entrega.
- Avaliações podem não possuir título ou comentário.
- Produtos podem não possuir categoria ou informações completas de dimensões físicas.
- Pedidos podem não possuir data de aprovação ou de envio.

Não são removidos registros exclusivamente pela presença de valores nulos.

A contagem de valores nulos é realizada utilizando funções nativas do PySpark e registrada nos relatórios de qualidade.

## 5. Tradução das categorias de produtos

A tabela de produtos é enriquecida utilizando o arquivo `product_category_name_translation.csv`, disponibilizado originalmente pelo dataset Olist.

**Transformação aplicada:**

- Relacionamento entre produtos e tabela de tradução utilizando `product_category_name`.
- Categoria original em português preservada.
- Coluna `product_category_name_english` adicionada.
- Relacionamento realizado por meio de `LEFT JOIN`.
- Produtos sem categoria original são preservados.

**Traduções complementares:**

Duas categorias não possuíam correspondência no arquivo original e receberam mapeamentos complementares:

| Categoria original | Categoria em inglês |
|---|---|
| pc_gamer | pc_gamer |
| portateis_cozinha_e_preparadores_de_alimentos | kitchen_and_food_preparers |

Esses mapeamentos foram definidos manualmente para complementar a tabela original de tradução.

**Resultado da execução:**

- 32.951 produtos processados.
- 32.341 produtos com categoria original.
- 32.341 produtos com categoria traduzida.
- 610 produtos sem categoria original.
- Nenhuma categoria preenchida permaneceu sem tradução.

## 6. Regras de negócio – Entregas

Foi criada a tabela `fact_delivery_metrics` na camada Gold, com granularidade de um registro por pedido (`order_id`).

A tabela utiliza os dados da camada Silver e calcula indicadores relacionados ao prazo de entrega.

**Métricas calculadas:**

| Métrica | Descrição |
|---|---|
| delivery_days | Tempo entre a compra e a entrega efetiva, em dias |
| estimated_delivery_days | Prazo estimado entre a compra e a entrega prevista |
| delivery_variance_days | Diferença entre a data efetiva e a data estimada de entrega |
| delay_days | Quantidade de dias de atraso, considerando zero para entregas antecipadas |
| is_delivered_on_time | Indicador booleano de entrega no prazo |
| delivery_performance | Classificação do desempenho da entrega |

**Regras aplicadas:**

- Pedidos sem data efetiva de entrega não recebem métricas de prazo efetivo.
- Entregas antecipadas possuem variância negativa.
- Dias de atraso são limitados a zero quando a entrega ocorre antes da data estimada.
- Quando a variância de entrega é nula, `delay_days` também permanece nulo.
- `is_delivered_on_time` permanece nulo quando não existem as datas necessárias para a comparação.
- Pedidos com status diferente de `delivered` não são classificados como entregas concluídas.

**Classificações de desempenho:**

| Classificação | Regra |
|---|---|
| not_delivered | Pedido sem datas completas de entrega e sem inconsistência identificada |
| inconsistent_delivery_data | Pedido com status `delivered`, mas sem data efetiva de entrega |
| on_time_or_early | Entrega realizada até a data estimada |
| delayed | Entrega realizada após a data estimada |

## 7. Auditoria e rastreabilidade

Os relatórios de qualidade da camada Silver são armazenados em:

`data/silver/quality_reports/`

Os relatórios são gerados em formato JSON e registram indicadores encontrados durante a transformação, incluindo:

- Quantidade de registros antes e depois do tratamento.
- Quantidade de valores nulos por coluna.
- Quantidade de duplicidades removidas.
- Quantidade de registros com chaves incompletas.
- Quantidade de valores inválidos nas conversões.
- Indicadores relacionados às categorias de produtos sem correspondência na tradução.

A geração dos relatórios permite acompanhar os resultados das transformações e identificar possíveis problemas de qualidade ao longo da execução.

## 8. Resultados da validação

Com base nas execuções do pipeline e nos diagnósticos realizados:

| Indicador | Resultado |
|---|---:|
| Registros de pedidos | 99.441 |
| Registros de produtos | 32.951 |
| Registros de clientes | 99.441 |
| Registros de itens | 112.650 |
| Duplicidades nas chaves verificadas | 0 |
| Conversões inválidas | 0 |
| Produtos com categoria traduzida | 32.341 |
| Produtos sem categoria original | 610 |
| Categorias preenchidas sem tradução | 0 |

**Indicadores logísticos identificados**

- Pedidos entregues com datas completas: 96.476.
- Percentual de entregas no prazo ou antecipadas: 91,89%.
- Pedidos atrasados: 7.827.
- Tempo médio de entrega: 12,56 dias.
- Atraso médio entre pedidos atrasados: 9,55 dias.

**Classificação dos pedidos na camada Gold**

| Classificação | Quantidade |
|---|---:|
| on_time_or_early | 88.649 |
| delayed | 7.827 |
| not_delivered | 2.957 |
| inconsistent_delivery_data | 8 |
| **Total** | **99.441** |

**Pontos identificados para investigação**

- Oito pedidos possuem status `delivered` sem data efetiva de entrega.
- Foram identificados valores extremos nos prazos de entrega e nas diferenças entre datas estimadas e efetivas.
- Os valores extremos são preservados até investigação, sem exclusão automática.

## 9. Limitações e próximas validações

As regras implementadas nesta versão contemplam conversões de tipos, duplicidades por chaves definidas, preservação de valores nulos, tradução de categorias e construção de métricas logísticas.

Ainda devem ser aprofundadas as validações de domínio e consistência, incluindo:

- Preços e valores negativos.
- Notas de avaliação fora do intervalo esperado.
- Coordenadas geográficas fora dos limites válidos.
- Datas incompatíveis com a sequência do processo de compra e entrega.
- Integridade referencial entre as tabelas.
- Validação de unicidade e consistência das chaves de negócio.

---

# 10. Validação do Modelo Dimensional — Databricks

## 10.1. Objetivo

Complementar as validações realizadas durante o processamento Bronze e Silver com testes específicos da camada Gold, implementada no Databricks utilizando SQL e Delta Lake.

As validações contemplam:

- Volumetria das dimensões e tabelas fato.
- Unicidade das chaves de negócio.
- Granularidade das tabelas fato.
- Integridade referencial entre fatos e dimensões.
- Consistência das regras de classificação de entrega.
- Identificação de exceções e inconsistências de negócio.

Os scripts SQL estão disponíveis no diretório:

`databricks/sql/validation/`

## 10.2. Validação de volumetria

Foram verificadas as quantidades de registros das oito tabelas que compõem o modelo dimensional.

| Tabela | Registros |
|---|---:|
| dim_customer | 99.441 |
| dim_product | 32.951 |
| dim_seller | 3.095 |
| dim_location | 19.015 |
| dim_date | 799 |
| fact_sales | 112.650 |
| fact_payments | 103.886 |
| fact_delivery_metrics | 99.441 |

**Resultado:** as quantidades de registros correspondem aos resultados obtidos durante a construção do modelo dimensional.

**Script:** `01_row_counts.sql`

## 10.3. Validação de granularidade e unicidade

Foram verificadas as chaves de negócio das três tabelas fato.

| Tabela fato | Chave de negócio | Registros | Chaves distintas | Duplicidades |
|---|---|---:|---:|---:|
| fact_sales | order_id + order_item_id | 112.650 | 112.650 | 0 |
| fact_payments | order_id + payment_sequential | 103.886 | 103.886 | 0 |
| fact_delivery_metrics | order_id | 99.441 | 99.441 | 0 |

**Resultado:** nenhuma duplicidade foi identificada nas chaves de negócio verificadas.

As três tabelas respeitam suas respectivas granularidades:

- Vendas: um registro por item de pedido.
- Pagamentos: um registro por pagamento.
- Entregas: um registro por pedido.

**Script:** `02_grain_checks.sql`

## 10.4. Integridade referencial

Foram verificadas as correspondências entre as chaves substitutas das tabelas fato e suas respectivas dimensões.

### fact_sales

| Relacionamento | Registros sem correspondência |
|---|---:|
| Cliente | 0 |
| Produto | 0 |
| Vendedor | 0 |
| Data da compra | 0 |

### fact_payments

| Relacionamento | Registros sem correspondência |
|---|---:|
| Cliente | 0 |
| Data da compra | 0 |

### fact_delivery_metrics

| Relacionamento | Resultado |
|---|---:|
| Cliente sem dimensão | 0 |
| Data da compra nula | 0 |
| Data de entrega nula | 2.965 |

As datas de entrega nulas foram preservadas, pois podem representar pedidos cancelados ou não entregues, além dos oito pedidos entregues com inconsistência na data.

**Resultado:** não foram identificadas referências inválidas nas verificações de integridade executadas.

**Script:** `03_referential_integrity.sql`

## 10.5. Regras de negócio — Classificação de entregas

A classificação da tabela `fact_delivery_metrics` foi ajustada para considerar o status original do pedido, além das datas efetivas e estimadas de entrega.

| Classificação | Quantidade de pedidos |
|---|---:|
| delivered_on_time | 88.644 |
| delivered_delayed | 7.826 |
| delivery_data_inconsistent | 8 |
| canceled | 625 |
| not_delivered | 2.338 |
| **Total** | **99.441** |

### Indicadores de desempenho

Considerando exclusivamente os pedidos com status `delivered`:

| Indicador | Resultado |
|---|---:|
| Pedidos entregues | 96.478 |
| Entregues no prazo | 88.644 |
| Entregues com atraso | 7.826 |
| Entregues sem data de entrega | 8 |
| Percentual no prazo, entre pedidos entregues | 91,88% |
| Percentual com atraso, entre pedidos entregues | 8,12% |

Os percentuais consideram os 96.470 pedidos entregues com data efetiva, excluindo os oito registros inconsistentes.

### Regras implementadas

- Pedidos cancelados recebem a classificação `canceled`.
- Pedidos com status `delivered` e sem data efetiva recebem `delivery_data_inconsistent`.
- Pedidos entregues até a data estimada recebem `delivered_on_time`.
- Pedidos entregues após a data estimada recebem `delivered_delayed`.
- Os demais pedidos recebem `not_delivered`.

**Script:** `04_delivery_quality.sql`

## 10.6. Exceções identificadas no modelo dimensional

Durante as verificações, foram identificadas as seguintes ocorrências:

| Ocorrência | Quantidade | Tratamento |
|---|---:|---|
| Clientes sem correspondência geográfica | 278 | Preservados com `location_sk` nulo |
| Vendedores sem correspondência geográfica | 7 | Preservados com `location_sk` nulo |
| Pedidos entregues sem registro de pagamento | 1 | Preservado sem criação artificial de pagamento |
| Pedidos entregues sem data efetiva | 8 | Classificados como `delivery_data_inconsistent` |

Essas ocorrências foram preservadas para manter a rastreabilidade e evitar alterações artificiais nos dados de origem.

## 10.7. Análise de valores financeiros

Foram identificados os seguintes totais nas tabelas fato:

| Indicador | Valor |
|---|---:|
| Vendas + frete | R$ 15.843.553,24 |
| Pagamentos | R$ 16.008.872,12 |
| Diferença | R$ 165.318,88 |

Os valores ainda não foram conciliados.

As tabelas possuem granularidades diferentes e representam conceitos de negócio distintos. Uma investigação adicional é necessária para identificar as causas da diferença antes de utilizar esses indicadores como valores financeiros equivalentes.

## 10.8. Conclusão das validações da Gold

A camada Gold apresentou os resultados esperados nas verificações de volumetria, granularidade e integridade referencial realizadas.

As tabelas fato preservam suas respectivas chaves de negócio e granularidades, evitando duplicidades decorrentes de relacionamentos entre dados de diferentes níveis de detalhe.

As exceções identificadas foram documentadas e preservadas, mantendo a rastreabilidade dos dados.

Os scripts de criação e validação do modelo dimensional estão versionados no repositório para permitir reprodução, auditoria e manutenção da solução.

---

## Documentação complementar

Para obter uma visão completa da plataforma e do contexto das validações realizadas, consulte também:

- [Arquitetura da Plataforma](architecture.md) — explica o fluxo de ingestão, transformação e disponibilização dos dados.
- [Dicionário de Dados](data_dictionary.md) — apresenta a estrutura e a descrição dos campos utilizados nas validações.
- [Modelo Dimensional](dimensional_model.md) — detalha a organização das tabelas da camada analítica.
- [Análise Exploratória](exploratory_data_analysis.md) — apresenta as consultas e análises utilizadas para investigar os dados.
