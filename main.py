import os
import sys
import subprocess
from app.config import APP_NAME, ENVIRONMENT, DATABASE_URL

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    print(f"🏛️  {APP_NAME}")
    print(f"Ambiente: {ENVIRONMENT}")
    print(f"Banco de Dados: {DATABASE_URL}")
    print("\nPara iniciar o Painel Interativo com Mapa e Linha do Tempo, execute:")
    print("  streamlit run app/ui/app.py\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--ui":
        print("Iniciando interface gráfica Streamlit...")
        subprocess.run(["streamlit", "run", "app/ui/app.py"])


if __name__ == "__main__":
    main()
