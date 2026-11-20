# Data Dictionary – Olist Dataset

## 1. Objetivo

Este documento apresenta o dicionário de dados do projeto Olist, descrevendo as tabelas utilizadas no pipeline, suas respectivas granularidades, chaves de identificação e principais atributos.

O objetivo é facilitar o entendimento dos dados disponíveis em cada camada da arquitetura, padronizar a interpretação das informações e documentar a estrutura das tabelas utilizadas nas transformações.

O projeto utiliza nove tabelas originais do dataset Olist e uma tabela derivada na camada Gold.

## 2. Visão geral das tabelas

| Tabela | Camada | Granularidade | Descrição |
|---|---|---|---|
| olist_customers_dataset | Bronze / Silver | Um registro por cliente | Informações dos clientes |
| olist_geolocation_dataset | Bronze / Silver | Um registro por localização geográfica | Coordenadas associadas a prefixos de CEP |
| olist_orders_dataset | Bronze / Silver | Um registro por pedido | Informações gerais dos pedidos |
| olist_order_items_dataset | Bronze / Silver | Um registro por item de pedido | Produtos associados a cada pedido |
| olist_order_payments_dataset | Bronze / Silver | Um registro por pagamento de pedido | Informações dos pagamentos |
| olist_order_reviews_dataset | Bronze / Silver | Um registro por avaliação de pedido | Avaliações realizadas pelos clientes |
| olist_products_dataset | Bronze / Silver | Um registro por produto | Características dos produtos |
| olist_sellers_dataset | Bronze / Silver | Um registro por vendedor | Informações dos vendedores |
| product_category_name_translation | Bronze / Silver | Uma categoria por registro | Tradução das categorias de produtos |
| fact_delivery_metrics | Gold | Um registro por pedido | Indicadores de desempenho das entregas |

## 3. Dicionário de dados – Tabelas originais

### 3.1. Customers – `olist_customers_dataset`

**Descrição:** contém informações de identificação e localização dos clientes da plataforma Olist.

**Granularidade:** um registro por cliente.

**Chave de identificação:** `customer_id`.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| customer_id | String | Identificador único do cliente |
| customer_unique_id | String | Identificador que representa unicamente o consumidor |
| customer_zip_code_prefix | String | Prefixo do CEP do cliente |
| customer_city | String | Cidade do cliente |
| customer_state | String | Estado do cliente |

### 3.2. Geolocation – `olist_geolocation_dataset`

**Descrição:** contém informações geográficas associadas aos prefixos de CEP brasileiros.

**Granularidade:** um registro por combinação de informações geográficas disponibilizadas na origem.

**Chave de identificação:** não possui chave única definida no projeto.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| geolocation_zip_code_prefix | String | Prefixo do CEP |
| geolocation_lat | Double | Latitude da localização |
| geolocation_lng | Double | Longitude da localização |
| geolocation_city | String | Cidade associada à localização |
| geolocation_state | String | Estado associado à localização |

### 3.3. Orders – `olist_orders_dataset`

**Descrição:** contém informações gerais dos pedidos realizados na plataforma.

**Granularidade:** um registro por pedido.

**Chave de identificação:** `order_id`.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| order_id | String | Identificador único do pedido |
| customer_id | String | Identificador do cliente associado ao pedido |
| order_status | String | Situação atual do pedido |
| order_purchase_timestamp | Timestamp | Data e hora da realização da compra |
| order_approved_at | Timestamp | Data e hora da aprovação do pagamento |
| order_delivered_carrier_date | Timestamp | Data e hora da entrega do pedido à transportadora |
| order_delivered_customer_date | Timestamp | Data e hora da entrega ao cliente |
| order_estimated_delivery_date | Timestamp | Data estimada para entrega ao cliente |

### 3.4. Order Items – `olist_order_items_dataset`

**Descrição:** contém os produtos associados aos pedidos, incluindo informações de preço, frete e vendedor.

**Granularidade:** um registro por item de pedido.

**Chave de identificação:** combinação de `order_id` e `order_item_id`.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| order_id | String | Identificador do pedido |
| order_item_id | Long | Número sequencial do item dentro do pedido |
| product_id | String | Identificador do produto |
| seller_id | String | Identificador do vendedor |
| shipping_limit_date | Timestamp | Data limite para envio do item |
| price | Double | Preço do produto |
| freight_value | Double | Valor do frete do item |

### 3.5. Order Payments – `olist_order_payments_dataset`

**Descrição:** contém informações dos pagamentos realizados para os pedidos.

**Granularidade:** um registro por pagamento associado a um pedido.

**Chave de identificação:** combinação de `order_id` e `payment_sequential`.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| order_id | String | Identificador do pedido |
| payment_sequential | Long | Sequência do pagamento dentro do pedido |
| payment_type | String | Tipo de pagamento utilizado |
| payment_installments | Long | Quantidade de parcelas |
| payment_value | Double | Valor do pagamento |

### 3.6. Order Reviews – `olist_order_reviews_dataset`

**Descrição:** contém as avaliações realizadas pelos clientes sobre os pedidos.

**Granularidade:** um registro por avaliação associada a um pedido.

**Chave de identificação:** combinação de `review_id` e `order_id`.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| review_id | String | Identificador da avaliação |
| order_id | String | Identificador do pedido avaliado |
| review_score | Long | Nota atribuída pelo cliente |
| review_comment_title | String | Título do comentário |
| review_comment_message | String | Texto do comentário |
| review_creation_date | Timestamp | Data de criação da avaliação |
| review_answer_timestamp | Timestamp | Data e hora da resposta à avaliação |

### 3.7. Products – `olist_products_dataset`

**Descrição:** contém informações e características físicas dos produtos comercializados na plataforma.

**Granularidade:** um registro por produto.

**Chave de identificação:** `product_id`.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| product_id | String | Identificador único do produto |
| product_category_name | String | Categoria original do produto em português |
| product_name_lenght | Long | Quantidade de caracteres do nome do produto |
| product_description_lenght | Long | Quantidade de caracteres da descrição |
| product_photos_qty | Long | Quantidade de fotos do produto |
| product_weight_g | Double | Peso do produto em gramas |
| product_length_cm | Double | Comprimento do produto em centímetros |
| product_height_cm | Double | Altura do produto em centímetros |
| product_width_cm | Double | Largura do produto em centímetros |
| product_category_name_english | String | Categoria do produto traduzida para inglês |

**Observação:** a coluna `product_category_name_english` é adicionada durante o enriquecimento da tabela na camada Silver. Ela não faz parte do arquivo original de produtos.

### 3.8. Sellers – `olist_sellers_dataset`

**Descrição:** contém informações de identificação e localização dos vendedores da plataforma.

**Granularidade:** um registro por vendedor.

**Chave de identificação:** `seller_id`.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| seller_id | String | Identificador único do vendedor |
| seller_zip_code_prefix | String | Prefixo do CEP do vendedor |
| seller_city | String | Cidade do vendedor |
| seller_state | String | Estado do vendedor |

### 3.9. Category Translation – `product_category_name_translation`

**Descrição:** contém o relacionamento entre os nomes originais das categorias de produtos em português e suas respectivas traduções para inglês.

**Granularidade:** uma categoria por registro.

**Chave de identificação:** `product_category_name`.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| product_category_name | String | Nome original da categoria em português |
| product_category_name_english | String | Nome traduzido da categoria em inglês |

**Observação:** durante a transformação Silver, foram adicionados dois mapeamentos complementares para categorias ausentes no arquivo original:

| Categoria original | Categoria em inglês |
|---|---|
| pc_gamer | pc_gamer |
| portateis_cozinha_e_preparadores_de_alimentos | kitchen_and_food_preparers |

## 4. Dicionário de dados – Camada Gold

### 4.1. Fact Delivery Metrics – `fact_delivery_metrics`

**Descrição:** tabela analítica que reúne informações dos pedidos e indicadores relacionados ao desempenho das entregas.

**Granularidade:** um registro por pedido.

**Chave de identificação:** `order_id`.

**Origem:** `olist_orders_dataset`, da camada Silver.

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| order_id | String | Identificador único do pedido |
| customer_id | String | Identificador do cliente |
| order_status | String | Situação do pedido |
| order_purchase_timestamp | Timestamp | Data e hora da compra |
| order_delivered_customer_date | Timestamp | Data e hora da entrega efetiva ao cliente |
| order_estimated_delivery_date | Timestamp | Data estimada para entrega |
| delivery_days | Double | Quantidade de dias entre a compra e a entrega efetiva |
| estimated_delivery_days | Double | Quantidade de dias entre a compra e a data estimada de entrega |
| delivery_variance_days | Double | Diferença, em dias, entre a entrega efetiva e a estimada |
| delay_days | Double | Quantidade de dias de atraso, limitada a zero para entregas antecipadas |
| is_delivered_on_time | Boolean | Indicador de entrega no prazo ou antecipada |
| delivery_performance | String | Classificação do desempenho da entrega |

**Regras das métricas:**

- `delivery_days`: diferença entre a data efetiva de entrega e a data da compra.
- `estimated_delivery_days`: diferença entre a data estimada e a data da compra.
- `delivery_variance_days`: diferença entre a data efetiva e a data estimada.
- `delay_days`: recebe zero quando a entrega ocorre antecipadamente ou no prazo; quando atrasada, recebe a quantidade de dias de atraso. Permanece nulo quando a variância não pode ser calculada.
- `is_delivered_on_time`: recebe `true` quando a entrega ocorre até a data estimada e `false` quando ocorre depois. Permanece nulo quando faltam datas necessárias para a comparação.

**Valores possíveis de `delivery_performance`:**

| Valor | Descrição |
|---|---|
| not_delivered | Pedido sem datas completas de entrega e sem inconsistência identificada |
| inconsistent_delivery_data | Pedido com status `delivered`, mas sem data efetiva de entrega |
| on_time_or_early | Entrega realizada no prazo ou antecipadamente |
| delayed | Entrega realizada após a data estimada |

## 5. Tipos de dados por camada

O pipeline utiliza diferentes representações dos dados conforme a etapa de processamento.

| Camada | Formato de armazenamento | Características |
|---|---|---|
| Source | CSV | Arquivos originais do dataset |
| RAW | Conforme implementação de ingestão | Dados extraídos da origem |
| Bronze | Parquet | Dados persistidos sem conversões de tipos de negócio |
| Silver | Parquet | Dados tratados, tipados e enriquecidos |
| Gold | Parquet | Dados organizados para análise e consumo |

Na camada Bronze, os campos são mantidos como strings durante a leitura dos arquivos CSV, conforme a implementação atual.

Na camada Silver, são realizadas conversões de tipos conforme as regras definidas para cada tabela.

A camada Gold utiliza os dados tratados da Silver para construir métricas analíticas.

## 6. Relacionamentos entre as tabelas

Os principais relacionamentos disponíveis no dataset são:

| Tabela de origem | Coluna | Tabela relacionada | Coluna |
|---|---|---|---|
| Customers | customer_id | Orders | customer_id |
| Orders | order_id | Order Items | order_id |
| Orders | order_id | Order Payments | order_id |
| Orders | order_id | Order Reviews | order_id |
| Order Items | product_id | Products | product_id |
| Order Items | seller_id | Sellers | seller_id |
| Products | product_category_name | Category Translation | product_category_name |
| Orders | order_id | Fact Delivery Metrics | order_id |

Esses relacionamentos representam as associações lógicas entre as tabelas e permitem a construção de análises integradas sobre clientes, pedidos, produtos, pagamentos, vendedores e entregas.

## 7. Observações e limitações

- Os tipos apresentados representam os tipos lógicos esperados após as transformações da camada Silver, e não necessariamente os tipos físicos dos arquivos CSV originais.
- A coluna `product_category_name_english` é criada durante o enriquecimento da tabela de produtos.
- A tabela de geolocalização não possui uma chave única definida na implementação atual.
- A tabela `fact_delivery_metrics` é derivada da tabela de pedidos e possui granularidade de um registro por pedido.
- As descrições e regras documentadas devem acompanhar futuras alterações nos esquemas e transformações do pipeline.

## 8. Documentação complementar

Para mais detalhes sobre a estrutura e as regras do projeto, consulte:

- [Data Quality](data_quality.md): regras de qualidade, conversões, duplicidades e validações.
- [Architecture](architecture.md): descrição arquitetura e escopo do projeto.