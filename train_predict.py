import xgboost as xgb
import pandas as pd
from sklearn.metrics import roc_auc_score

# 1. Carregar dados processados
df = pd.read_parquet("data/processed/acc_features.parquet")

# 2. Preparar X e y (exemplo: binário se houve acidente)
y = (df['causa'].isNotNull()).astype(int)
X = df[['latitude','longitude','dia_semana','hora']]

# 3. Treinar modelo
dtrain = xgb.DMatrix(X, label=y)
model = xgb.train({"objective":"binary:logistic"}, dtrain)

# 4. Predições e métricas
preds = model.predict(dtrain)
print("AUC-ROC:", roc_auc_score(y, preds))

# 5. Salvar predições simples
df['risco'] = preds
df.to_csv("reports/predicoes.txt", sep='\t', index=False)