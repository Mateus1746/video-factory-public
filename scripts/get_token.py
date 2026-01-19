import os
import json
import glob
from google_auth_oauthlib.flow import InstalledAppFlow

# Escopos necessários para upload
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    # Encontrar o arquivo client_secret
    files = glob.glob("client_secret*.json")
    if not files:
        print("❌ Erro: Arquivo 'client_secret_....json' não encontrado na pasta.")
        return

    client_secrets_file = files[0]
    print(f"🔑 Usando arquivo: {client_secrets_file}")

    # Iniciar fluxo de autenticação
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
    creds = flow.run_local_server(port=0)

    # Criar o JSON final para o GitHub Secret
    secret_json = {
        "type": "authorized_user",
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token"
    }

    print("\n\n✅ SUCESSO! Copie o conteúdo abaixo e cole no GitHub Secret 'GDRIVE_CREDENTIALS_JSON':\n")
    print(json.dumps(secret_json, indent=2))
    print("\n---------------------------------------------------")

if __name__ == '__main__':
    main()
