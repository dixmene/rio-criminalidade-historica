import os
import sys
from dotenv import load_dotenv

# Garante suporte a UTF-8 no terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

def main():
    app_name = os.getenv("APP_NAME", "Daniel Systems")
    environment = os.getenv("ENVIRONMENT", "development")
    print(f"🚀 {app_name} iniciado com sucesso!")
    print(f"Ambiente: {environment}")

if __name__ == "__main__":
    main()
