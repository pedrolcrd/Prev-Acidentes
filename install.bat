@echo off

echo 🚗 Instalador do Dashboard de Acidentes de Trânsito
echo ==================================================

:: Verificar se Python está instalado
where python >nul 2>&1
if %errorlevel% ne 0 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8 ou superior.
    goto :eof
)

echo ✅ Python encontrado: %python --version%

:: Instalar dependências Python
echo 📦 Instalando dependências Python...
pip install -r requirements.txt

if %errorlevel% ne 0 (
    echo ❌ Erro ao instalar dependências Python.
    goto :eof
)

echo ✅ Dependências Python instaladas com sucesso!

:: Instruções para configurar Ollama
echo.
echo 🔧 Configuração do Ollama:
echo 1. Baixe e instale o Ollama para Windows em: https://ollama.ai/download
echo 2. Inicie o serviço Ollama (geralmente inicia automaticamente após a instalação).
echo 3. Abra o Prompt de Comando ou PowerShell e baixe o modelo Llama 3.1:
echo    ollama pull llama3.1
echo.

:: Verificar se os dados estão disponíveis
if exist "upload\*.csv" (
    echo ✅ Arquivos CSV encontrados na pasta 'upload\'
) else (
    echo ⚠️  Arquivos CSV não encontrados na pasta 'upload\'
    echo    Certifique-se de criar uma pasta 'upload' no mesmo diretório deste script e colocar os arquivos CSV nela.
)

echo.
echo 🚀 Para executar o dashboard:
echo    streamlit run app_optimized.py --server.port 8501 --server.address 0.0.0.0
echo.
echo 🌐 Acesse no navegador:
echo    http://localhost:8501
echo.
echo 📚 Para mais informações, consulte o README.md
echo.
echo ✨ Instalação concluída!

pause

