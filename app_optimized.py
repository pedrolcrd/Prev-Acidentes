import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import numpy as np
import os # Importar o módulo os
# import requests # Removido temporariamente devido a problemas na API do IBGE

# Configuração da página
st.set_page_config(page_title="Dashboard de Acidentes de Trânsito", layout="wide")

# --- Segurança da Informação (Placeholders) ---
# Autenticação Multifatorial (MFA):
# Em um ambiente de produção, isso seria integrado com um provedor de identidade (Auth0, Okta, AWS Cognito, etc.)
# Streamlit não possui MFA nativo. Seria necessário um proxy de autenticação ou integração via OAuth/OpenID Connect.
# Exemplo: if not st.session_state.get("authenticated"): st.stop() # Pararia a execução se não autenticado

# Registros Seguros e Auditáveis:
# Em produção, logs seriam enviados para um sistema centralizado (ELK Stack, Splunk, CloudWatch Logs).
# st.write("Logs de acesso e eventos importantes seriam registrados aqui para auditoria.")
# Exemplo: import logging; logging.basicConfig(filename="app_audit.log", level=logging.INFO)
# logging.info(f"User {user_id} accessed dashboard at {datetime.now()}")
# ----------------------------------------------

# Função para carregar dados
@st.cache_data
def load_data(selected_year):
    all_data = []
    # Usar os.path.join para compatibilidade com diferentes sistemas operacionais
    base_upload_path = "upload"
    
    file_names = {
        "acidentes": f"acidentes{selected_year}_todas_causas_tipos.csv",
        "datatran": f"datatran{selected_year}.csv"
    }
    
    for key, file_name in file_names.items():
        # Construir o caminho completo do arquivo
        file_path = os.path.join(base_upload_path, file_name)
        try:
            df = pd.read_csv(file_path, sep=";", encoding="latin1")
            all_data.append(df)
        except FileNotFoundError:
            st.warning(f"Arquivo {file_path} não encontrado. Pulando...")
        except Exception as e:
            st.error(f"Erro ao carregar {file_path}: {e}")
            
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# --- Removido temporariamente a função fetch_ibge_data() ---

# Título principal
st.title("🚗 Dashboard de Análise de Acidentes de Trânsito")
st.markdown("---")

# Seleção do Ano
current_year = 2023 # Ano padrão para exibição
available_years = [2020, 2021, 2022, 2023, 2024, 2025]
selected_year = st.sidebar.selectbox("Selecione o Ano dos Dados", available_years, index=available_years.index(current_year))

df = load_data(selected_year)

if not df.empty:
    # Sidebar com informações
    st.sidebar.header("📊 Informações dos Dados")
    st.sidebar.metric("Total de Registros", len(df))
    st.sidebar.metric("Ano Selecionado", selected_year)
    
    # Limpeza básica dos dados
    df.columns = df.columns.str.lower()
    
    # Conversões de data e hora
    if "data_inversa" in df.columns:
        df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")
        df["ano"] = df["data_inversa"].dt.year
        df["mes"] = df["data_inversa"].dt.month
        df["dia_semana_num"] = df["data_inversa"].dt.dayofweek
    
    if "horario" in df.columns:
        df["hora"] = pd.to_datetime(df["horario"], format="%H:%M:%S", errors="coerce").dt.hour
    
    # Preenchimento de valores NaN
    numeric_columns = ["km", "pessoas", "mortos", "feridos", "veiculos"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Adicionando colunas de latitude e longitude, se existirem
    if "latitude" in df.columns and "longitude" in df.columns:
        df["latitude"] = df["latitude"].str.replace(",", ".").astype(float)
        df["longitude"] = df["longitude"].str.replace(",", ".").astype(float)
    else:
        st.warning("Colunas \'latitude\' ou \'longitude\' não encontradas. O mapa de calor pode não funcionar.")

    # Layout em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Mapa de calor de acidentes por UF e tipo
        st.subheader("🔥 Mapa de Calor: Acidentes por UF e Tipo")
        if "uf" in df.columns and "tipo_acidente" in df.columns:
            heatmap_data = df.groupby(["uf", "tipo_acidente"]).size().unstack(fill_value=0)
            if not heatmap_data.empty:
                fig_heatmap = px.imshow(
                    heatmap_data, 
                    text_auto=True, 
                    aspect="auto",
                    color_continuous_scale="Reds",
                    title="Distribuição de Acidentes por UF e Tipo"
                )
                fig_heatmap.update_layout(height=400)
                st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        # 2. Previsão de risco por horário
        st.subheader("⏰ Risco de Acidentes por Horário")
        if "hora" in df.columns:
            risk_by_hour = df.groupby("hora").size().reset_index(name="acidentes")
            fig_risk = px.line(
                risk_by_hour, 
                x="hora", 
                y="acidentes",
                title="Número de Acidentes por Hora do Dia",
                markers=True
            )
            fig_risk.update_traces(line_color="#ff6b6b")
            fig_risk.update_layout(height=400)
            st.plotly_chart(fig_risk, use_container_width=True)

    # 3. Análise de causas principais
    st.subheader("📈 Principais Causas de Acidentes")
    if "causa_acidente" in df.columns:
        top_causes = df["causa_acidente"].value_counts().head(10)
        fig_causes = px.bar(
            x=top_causes.values,
            y=top_causes.index,
            orientation="h",
            title="Top 10 Causas de Acidentes",
            color=top_causes.values,
            color_continuous_scale="viridis"
        )
        fig_causes.update_layout(height=500)
        st.plotly_chart(fig_causes, use_container_width=True)

    # 4. Gráficos interativos adicionais
    col3, col4 = st.columns(2)
    
    with col3:
        # Acidentes por dia da semana
        if "dia_semana" in df.columns:
            st.subheader("📅 Acidentes por Dia da Semana")
            day_counts = df["dia_semana"].value_counts()
            fig_days = px.pie(
                values=day_counts.values,
                names=day_counts.index,
                title="Distribuição por Dia da Semana"
            )
            st.plotly_chart(fig_days, use_container_width=True)
    
    with col4:
        # Condições meteorológicas
        if "condicao_metereologica" in df.columns:
            st.subheader("🌤️ Condições Meteorológicas")
            weather_counts = df["condicao_metereologica"].value_counts().head(8)
            fig_weather = px.bar(
                x=weather_counts.index,
                y=weather_counts.values,
                title="Acidentes por Condição Meteorológica"
            )
            fig_weather.update_xaxes(tickangle=45)
            st.plotly_chart(fig_weather, use_container_width=True)

    # 5. Modelo de Machine Learning
    st.markdown("---")
    st.header("🤖 Modelo de Machine Learning: XGBoost Classifier")
    
    # Preparação dos dados para ML
    features_for_ml = []
    if "km" in df.columns:
        features_for_ml.append("km")
    if "hora" in df.columns:
        features_for_ml.append("hora")
    if "dia_semana_num" in df.columns:
        features_for_ml.append("dia_semana_num")
    
    # Encoding de variáveis categóricas
    if "condicao_metereologica" in df.columns:
        df["condicao_metereologica_encoded"] = pd.Categorical(df["condicao_metereologica"]).codes
        features_for_ml.append("condicao_metereologica_encoded")
    
    if "tipo_pista" in df.columns:
        df["tipo_pista_encoded"] = pd.Categorical(df["tipo_pista"]).codes
        features_for_ml.append("tipo_pista_encoded")
    
    # Criação da variável alvo
    if "classificacao_acidente" in df.columns:
        df["risco_alto"] = df["classificacao_acidente"].apply(
            lambda x: 1 if "Com Vítimas" in str(x) else 0
        )
        
        # Garantir que as colunas de latitude e longitude existam e não sejam nulas para o mapa de calor
        df_ml = df.dropna(subset=features_for_ml + ["latitude", "longitude", "risco_alto"])

        if features_for_ml and len(features_for_ml) > 0:
            # Preparação dos dados
            X = df_ml[features_for_ml]
            y = df_ml["risco_alto"]
            
            if len(X) > 10 and len(y) > 10:
                # Divisão treino/teste
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.3, random_state=42
                )
                
                # Treinamento do modelo
                model = xgb.XGBClassifier(
                    objective="binary:logistic",
                    eval_metric="logloss",
                    use_label_encoder=False,
                    random_state=42
                )
                
                try:
                    model.fit(X_train, y_train)
                    
                    # Predições
                    y_pred_proba = model.predict_proba(X)[:, 1] # Predição para todo o dataset
                    df["risco"] = pd.Series(y_pred_proba, index=df_ml.index) # Atribuir risco ao DataFrame original
                    df["risco"] = df["risco"].fillna(0) # Preencher NaN com 0 para evitar erros no mapa

                    # Métricas
                    auc_score = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
                    
                    col5, col6 = st.columns(2)
                    
                    with col5:
                        st.metric("AUC-ROC Score", f"{auc_score:.3f}")
                        st.metric("Acurácia", f"{model.score(X_test, y_test):.3f}")
                    
                    with col6:
                        # Importância das features
                        feature_importance = pd.DataFrame({
                            "feature": features_for_ml,
                            "importance": model.feature_importances_
                        }).sort_values("importance", ascending=False)
                        
                        fig_importance = px.bar(
                            feature_importance,
                            x="importance",
                            y="feature",
                            orientation="h",
                            title="Importância das Features"
                        )
                        st.plotly_chart(fig_importance, use_container_width=True)
                    
                    # Predição interativa
                    st.subheader("🎯 Predição de Risco Personalizada")
                    
                    col7, col8 = st.columns(2)
                    
                    with col7:
                        km_input = st.slider("Quilômetro da Rodovia", 0, 1000, 100)
                        hora_input = st.slider("Hora do Dia", 0, 23, 12)
                        dia_semana_input = st.selectbox("Dia da Semana", 
                                                      [0, 1, 2, 3, 4, 5, 6],
                                                      format_func=lambda x: ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][x])
                    
                    with col8:
                        # Predição
                        sample_data = {
                            "km": km_input,
                            "hora": hora_input,
                            "dia_semana_num": dia_semana_input
                        }
                        
                        if "condicao_metereologica_encoded" in features_for_ml:
                            sample_data["condicao_metereologica_encoded"] = 0
                        if "tipo_pista_encoded" in features_for_ml:
                            sample_data["tipo_pista_encoded"] = 0
                        
                        sample_df = pd.DataFrame([sample_data])
                        prediction_proba = model.predict_proba(sample_df)[:, 1][0]
                        
                        st.metric("Probabilidade de Acidente com Vítimas", f"{prediction_proba:.1%}")
                        
                        # Gauge chart
                        fig_gauge = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = prediction_proba * 100,
                            domain = {"x": [0, 1], "y": [0, 1]},
                            title = {"text": "Risco (%)"},
                            gauge = {
                                "axis": {"range": [None, 100]},
                                "bar": {"color": "darkblue"},
                                "steps": [
                                    {"range": [0, 25], "color": "lightgray"},
                                    {"range": [25, 50], "color": "yellow"},
                                    {"range": [50, 75], "color": "orange"},
                                    {"range": [75, 100], "color": "red"}
                                ],
                                "threshold": {
                                    "line": {"color": "red", "width": 4},
                                    "thickness": 0.75,
                                    "value": 90
                                }
                            }
                        ))
                        fig_gauge.update_layout(height=300)
                        st.plotly_chart(fig_gauge, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Erro no modelo ML: {e}")
            else:
                st.warning("Dados insuficientes para treinar o modelo.")
        else:
            st.warning("Features não encontradas para o modelo ML.")

    # Novo: Mapa de calor de densidade de acidentes
    st.markdown("---")
    st.header("🗺️ Mapa de Densidade de Risco de Acidentes")
    if "latitude" in df.columns and "longitude" in df.columns and "risco" in df.columns:
        # Filtrar dados com risco > 0 para o mapa de calor
        df_map = df[df["risco"] > 0].copy()
        if not df_map.empty:
            fig_density_map = px.density_mapbox(
                df_map,
                lat="latitude",
                lon="longitude",
                z="risco",
                radius=10,
                center=dict(lat=-14.235, lon=-51.925),
                zoom=3,
                mapbox_style="open-street-map",
                title="Mapa de Densidade de Risco de Acidentes"
            )
            fig_density_map.update_layout(height=600)
            st.plotly_chart(fig_density_map, use_container_width=True)

            st.subheader("🔝 Top 10 Trechos Críticos (por Risco)")
            top_10_risco = df_map.nlargest(10, "risco")
            if not top_10_risco.empty:
                st.dataframe(top_10_risco[["latitude", "longitude", "risco", "uf", "br", "km"]])
            else:
                st.info("Nenhum trecho com risco significativo encontrado para exibir.")
        else:
            st.info("Nenhum dado com risco > 0 para exibir no mapa de densidade.")
    else:
        st.warning("Colunas \'latitude\', \'longitude\' ou \'risco\' não disponíveis para o mapa de densidade.")

    # --- Removido temporariamente a seção de Integração com API do IBGE ---
    # st.markdown("---")
    # st.header("📊 Dados Complementares do IBGE")
    # ibge_data = fetch_ibge_data()
    # if ibge_data:
    #     st.success("Dados do IBGE carregados com sucesso!")
    #     st.json(ibge_data)
    # else:
    #     st.info("API do IBGE não disponível no momento.")

    # 7. Seção Ollama/LLM
    st.markdown("---")
    st.header("🧠 Integração com LLM (Llama 3.1 via Ollama)")
    
    st.info("""
    **Para usar a integração com Ollama:**
    1. Instale o Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
    2. Inicie o serviço: `ollama serve`
    3. Baixe o modelo: `ollama pull llama3.1`
    """)
    
    user_question = st.text_area(
        "Faça uma pergunta sobre os dados de acidentes:",
        "Quais são os principais fatores de risco para acidentes de trânsito?"
    )
    
    if st.button("🤖 Perguntar à LLM"):
        try:
            import ollama
            
            # Contexto dos dados para a LLM
            data_context = f"""
            Dados de acidentes de trânsito analisados:
            - Total de registros: {len(df)}
            - Principais causas: {df["causa_acidente"].value_counts().head(3).to_dict() if "causa_acidente" in df.columns else "N/A"}
            - Horários de maior risco: {df.groupby("hora").size().nlargest(3).to_dict() if "hora" in df.columns else "N/A"}
            """
            
            prompt = f"{data_context}\n\nPergunta: {user_question}\n\nResponda de forma concisa e baseada nos dados apresentados."
            
            response = ollama.chat(
                model="llama3.1",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            st.success("Resposta da LLM:")
            st.write(response["message"]["content"])
            
        except Exception as e:
            st.error(f"Erro ao conectar com Ollama: {e}")
            st.info("Certifique-se de que o Ollama está rodando e o modelo llama3.1 está disponível.")

else:
    st.error("❌ Não foi possível carregar os dados. Verifique os arquivos CSV.")

# Footer
st.markdown("---")
st.markdown("**Dashboard desenvolvido com Streamlit, XGBoost e Plotly** 🚀")

