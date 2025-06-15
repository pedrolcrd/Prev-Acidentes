import requests
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import dayofweek, hour

spark = SparkSession.builder.appName("PipelineAccidentes").getOrCreate()

# 1. Carregar CSVs
_df_acc_ = spark.read.csv("data/raw/acidentes*.csv", header=True, inferSchema=True)

# 2. Consumir API IBGE (frota e população)
url = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/633"
    "/periodos/2023|2024|2025/variaveis/615|616?localidades=N1[all]"
)
resp = requests.get(url)
ibge_json = resp.json()
# Ajuste o parsing conforme estrutura da resposta do IBGE:
pdf = pd.json_normalize(
    ibge_json, record_path=['resultados', 0, 'series'],
    meta=[['resultados', 0, 'serie', 'localidade', 'nome'],
          ['resultados', 0, 'serie', 'variavel', 'id']]
)
# Converter para Spark DataFrame
df_ibge = spark.createDataFrame(pdf)

# 3. Limpeza simples
df = _df_acc_.dropna(subset=["latitude", "longitude", "timestamp"])

# 4. Feature Engineering
df = df.withColumn("dia_semana", dayofweek("timestamp")) \
       .withColumn("hora", hour("timestamp"))

# 5. Join com IBGE
# Supondo que a coluna 'localidade.nome' em df_ibge corresponde à região da rodovia
df_feat = df.join(df_ibge, df.region == df_ibge['nome'], how='left')

# 6. Gravar arquivo parquet
(df_feat
 .select("latitude", "longitude", "dia_semana", "hora", "causa", "frota", "populacao")
 .write.mode("overwrite").parquet("data/processed/acc_features.parquet"))


from pyspark.sql import SparkSession
from pyspark.sql.functions import dayofweek, hour

spark = SparkSession.builder.appName("PipelineAccidentes").getOrCreate()

# 1. Carregar CSVs
df = spark.read.csv("data/raw/acidentes*.csv", header=True, inferSchema=True)

# 2. Limpeza simples
df = df.dropna(subset=["latitude","longitude","timestamp"])

# 3. Feature Engineering
df = df.withColumn("dia_semana", dayofweek("timestamp")) \
       .withColumn("hora", hour("timestamp"))

# 4. Gravar arquivo parquet para downstream
(df
 .select("latitude","longitude","dia_semana","hora","causa")
 .write.mode("overwrite").parquet("data/processed/acc_features.parquet"))