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

## 10. Documentação complementar

Para mais detalhes sobre a estrutura e as regras do projeto, consulte:

- [Data Dictionary](data_dictionary.md): descrição das tabelas, colunas, tipos e granularidade.
- [Architecture](architecture.md): descrição arquitetura e escopo do projeto.