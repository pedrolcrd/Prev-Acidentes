# Dashboard de Análise de Acidentes de Trânsito

Este projeto implementa um dashboard interativo para análise de dados de acidentes de trânsito utilizando Streamlit, XGBoost e integração com LLM Llama 3.1 via Ollama.

## 🚀 Funcionalidades

### Dashboard Interativo
- **Seleção de Ano:** Permite visualizar dados de acidentes por ano (2020-2025).
- **Mapa de calor de acidentes** por UF e tipo
- **Previsão de risco por horário** com gráficos de linha
- **Análise de causas principais** com gráficos de barras horizontais
- **Gráficos interativos** para acidentes por dia da semana e condições meteorológicas
- **Mapa de Densidade de Risco de Acidentes:** Visualização da densidade de acidentes com base no risco previsto.
- **Top 10 Trechos Críticos:** Tabela com os 10 trechos de rodovia com maior risco de acidentes.

### Machine Learning
- **Modelo XGBoost Classifier** para predição de risco de acidentes
- **Features utilizadas:**
  - Histórico de acidentes por km
  - Condições climáticas
  - Dia da semana/hora
  - Tipo de rodovia
  - Densidade de tráfego
- **Métricas:** AUC-ROC, Precision, Acurácia
- **Predição interativa** com sliders e seletores

### Integração com LLM
- **Llama 3.1 via Ollama** para análise contextual dos dados
- **Interface de chat** para perguntas sobre os dados
- **Respostas baseadas** no contexto dos dados carregados

## 🔒 Segurança da Informação (Considerações)

Para uma implementação completa de segurança em um ambiente de produção, as seguintes funcionalidades seriam consideradas:

- **Autenticação Multifatorial (MFA):**
  - **Implementação:** Requer integração com provedores de identidade externos (e.g., Auth0, Okta, AWS Cognito) ou a utilização de um proxy de autenticação. O Streamlit, por si só, não oferece MFA nativo.
  - **Considerações:** A complexidade da implementação de MFA pode variar dependendo da infraestrutura existente e dos requisitos de segurança da organização.

- **Registros Seguros e Auditáveis com Monitoramento Contínuo:**
  - **Implementação:** Os logs de acesso e eventos importantes (e.g., tentativas de login, alterações de dados, interações com o modelo de ML) seriam enviados para um sistema centralizado de gerenciamento de logs (e.g., ELK Stack, Splunk, AWS CloudWatch Logs).
  - **Monitoramento:** Ferramentas de monitoramento contínuo seriam configuradas para alertar sobre atividades suspeitas ou anomalias nos logs.
  - **Considerações:** A implementação de um sistema de log robusto e auditável é crucial para conformidade e detecção de incidentes de segurança.

**Nota:** As implementações acima são complexas e geralmente exigem uma infraestrutura de segurança dedicada, indo além do escopo de um projeto de dashboard simples. O código atual inclui apenas placeholders para demonstrar onde essas funcionalidades seriam consideradas.

## 📋 Pré-requisitos

### Python e Dependências
```bash
pip install streamlit pandas plotly xgboost scikit-learn requests ollama
```

### Ollama (para LLM)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Iniciar o serviço
ollama serve

# Baixar o modelo Llama 3.1
ollama pull llama3.1
```

## 🗂️ Estrutura dos Dados

O dashboard espera arquivos CSV com os seguintes padrões de nome e colunas principais:

- **Arquivos de Acidentes:** `acidentesYYYY_todas_causas_tipos.csv` (onde YYYY é o ano)
- **Arquivos DataTran:** `datatranYYYY.csv` (onde YYYY é o ano)

**Colunas principais esperadas:**
- `data_inversa`: Data do acidente
- `horario`: Hora do acidente
- `uf`: Unidade Federativa
- `km`: Quilômetro da rodovia
- `causa_acidente`: Causa do acidente
- `tipo_acidente`: Tipo do acidente
- `classificacao_acidente`: Classificação (com/sem vítimas)
- `condicao_metereologica`: Condições climáticas
- `tipo_pista`: Tipo da pista
- `dia_semana`: Dia da semana
- `latitude`: Latitude do acidente (formato com vírgula ou ponto)
- `longitude`: Longitude do acidente (formato com vírgula ou ponto)

## 🚀 Como Executar (Windows)

### 1. Organizar os Dados
Crie uma pasta chamada `upload` no mesmo diretório do `app_optimized.py` e coloque todos os arquivos CSV fornecidos dentro dela.

### 2. Instalar Dependências
Abra o Prompt de Comando (CMD) ou PowerShell no diretório do projeto e execute:
```cmd
pip install -r requirements.txt
```

### 3. Executar o Dashboard
No mesmo Prompt de Comando (CMD) ou PowerShell, execute:
```cmd
streamlit run app_optimized.py --server.port 8501 --server.address 0.0.0.0
```

### 4. Acessar no Navegador
Abra seu navegador e acesse:
```
http://localhost:8501
```

## 📊 Features do Dashboard

### 1. Visualizações Principais
- **Mapa de Calor:** Distribuição de acidentes por UF e tipo
- **Gráfico de Linha:** Risco de acidentes por horário do dia
- **Gráfico de Barras:** Top 10 causas de acidentes
- **Gráfico Pizza:** Distribuição por dia da semana
- **Gráfico de Barras:** Acidentes por condição meteorológica

### 2. Modelo de Machine Learning
- **Treinamento automático** do modelo XGBoost
- **Métricas de performance** (AUC-ROC, Acurácia)
- **Importância das features** visualizada
- **Predição interativa** com gauge de risco

### 3. Chat com LLM
- **Interface de texto** para perguntas
- **Contexto dos dados** fornecido automaticamente
- **Respostas baseadas** nos dados analisados

## 🔧 Configurações

### Arquivos de Dados
Os arquivos CSV devem estar na pasta `upload` no mesmo diretório do `app_optimized.py`.

### Parâmetros do Modelo
```python
model = xgb.XGBClassifier(
    objective=\'binary:logistic\',
    eval_metric=\'logloss\',
    use_label_encoder=False,
    random_state=42
)
```

## 📈 Métricas e KPIs

- **Total de Registros:** Número de acidentes analisados
- **AUC-ROC Score:** Performance do modelo de classificação
- **Acurácia:** Precisão das predições
- **Importância das Features:** Quais variáveis mais influenciam o risco

## 🛠️ Personalização

### Adicionar Novas Visualizações
```python
# Exemplo: Gráfico de acidentes por mês
monthly_data = df.groupby(\'mes\').size().reset_index(name=\'acidentes\')
fig_monthly = px.line(monthly_data, x=\'mes\', y=\'acidentes\', title=\'Acidentes por Mês\')
st.plotly_chart(fig_monthly, use_container_width=True)
```

### Modificar Features do ML
```python
# Adicionar novas features
features_for_ml = [\'km\', \'hora\', \'dia_semana_num\', \'nova_feature\']
```

## 🔍 Troubleshooting

### Problema: Ollama não conecta
**Solução:** Verificar se o serviço está rodando:
```cmd
ollama serve
```

### Problema: Dados não carregam
**Solução:** Verificar se os arquivos CSV estão na pasta `upload` e se o encoding está correto (`encoding=\'latin1\'`).

### Problema: Modelo não treina
**Solução:** Verificar se há dados suficientes:
```python
if len(X) > 10 and len(y) > 10:
    # Treinar modelo
```

