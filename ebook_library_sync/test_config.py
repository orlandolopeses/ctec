#!/usr/bin/env python3
"""
Script de Teste e Verificação de Configuração

Execute este script ANTES da primeira sincronização para verificar
se tudo está configurado corretamente.
"""

import os
import json
import sys


def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"✓ {text}")


def print_error(text):
    """Imprime mensagem de erro"""
    print(f"✗ {text}")


def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"⚠ {text}")


def test_credentials(credentials_path):
    """Testa se as credenciais estão corretas"""
    print_header("TESTE 1: Arquivo de Credenciais")

    if not os.path.exists(credentials_path):
        print_error(f"Arquivo não encontrado: {credentials_path}")
        print("   Verifique se o caminho está correto.")
        return False

    print_success(f"Arquivo encontrado: {credentials_path}")

    try:
        with open(credentials_path, 'r') as f:
            creds = json.load(f)

        # Verificar campos essenciais
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [f for f in required_fields if f not in creds]

        if missing_fields:
            print_error(f"Campos faltando no JSON: {', '.join(missing_fields)}")
            return False

        print_success("Estrutura do JSON válida")
        print(f"   Tipo: {creds.get('type')}")
        print(f"   Projeto: {creds.get('project_id')}")
        print(f"   Email: {creds.get('client_email')}")

        if creds.get('type') != 'service_account':
            print_warning("Tipo de credencial diferente de 'service_account'")
            print("   Certifique-se de que é uma service account válida.")

        return True

    except json.JSONDecodeError:
        print_error("Arquivo JSON inválido ou corrompido")
        return False
    except Exception as e:
        print_error(f"Erro ao ler arquivo: {e}")
        return False


def test_imports():
    """Testa se as bibliotecas necessárias estão instaladas"""
    print_header("TESTE 2: Bibliotecas Python")

    required_packages = [
        ('google.oauth2', 'google-auth'),
        ('googleapiclient', 'google-api-python-client'),
    ]

    all_ok = True

    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print_success(f"{package_name} instalado")
        except ImportError:
            print_error(f"{package_name} NÃO instalado")
            print(f"   Execute: pip install {package_name}")
            all_ok = False

    return all_ok


def test_drive_connection(credentials_path, folder_id):
    """Testa conexão com Google Drive"""
    print_header("TESTE 3: Conexão com Google Drive")

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        print("   Autenticando...")

        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )

        service = build('drive', 'v3', credentials=credentials)

        print_success("Autenticação bem-sucedida")

        print("   Testando acesso à pasta...")

        # Tentar acessar a pasta
        folder = service.files().get(
            fileId=folder_id,
            fields='id, name, mimeType'
        ).execute()

        print_success(f"Pasta acessível: {folder.get('name')}")
        print(f"   ID: {folder.get('id')}")
        print(f"   Tipo: {folder.get('mimeType')}")

        if folder.get('mimeType') != 'application/vnd.google-apps.folder':
            print_warning("O ID fornecido não é de uma pasta!")
            return False

        # Testar listagem de arquivos
        print("   Testando listagem de arquivos...")
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            pageSize=5,
            fields='files(id, name, mimeType)'
        ).execute()

        files = results.get('files', [])
        print_success(f"Listagem bem-sucedida: {len(files)} item(ns) na pasta raiz")

        if files:
            print("   Primeiros itens encontrados:")
            for f in files[:3]:
                print(f"      - {f.get('name')} ({f.get('mimeType')})")

        return True

    except Exception as e:
        print_error(f"Erro ao conectar: {e}")
        return False


def test_sheets_connection(credentials_path):
    """Testa conexão com Google Sheets"""
    print_header("TESTE 4: Conexão com Google Sheets")

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        print("   Autenticando...")

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )

        service = build('sheets', 'v4', credentials=credentials)

        print_success("Autenticação com Sheets bem-sucedida")
        print_success("API do Google Sheets está acessível")

        return True

    except Exception as e:
        print_error(f"Erro ao conectar: {e}")
        return False


def main():
    """Função principal"""
    print_header("VERIFICAÇÃO DE CONFIGURAÇÃO - EBOOK LIBRARY SYNC")
    print("\nEste script irá verificar se tudo está configurado corretamente.")
    print("Execute antes da primeira sincronização!\n")

    # ========== CONFIGURAÇÕES - AJUSTE AQUI ==========
    CREDENTIALS_PATH = "/content/drive/MyDrive/0_Credentials/acessodriveorlando-44351dfb71f4.json"
    LIBRARY_FOLDER_ID = "0B9gSg9OIekOlajlGdWcxOWt0MlU"
    # ==================================================

    print(f"Configurações:")
    print(f"  Credenciais: {CREDENTIALS_PATH}")
    print(f"  Pasta da Biblioteca: {LIBRARY_FOLDER_ID}")

    # Executar testes
    tests_results = []

    tests_results.append(("Credenciais", test_credentials(CREDENTIALS_PATH)))
    tests_results.append(("Bibliotecas", test_imports()))

    # Só testar conexões se credenciais e bibliotecas estiverem OK
    if tests_results[0][1] and tests_results[1][1]:
        tests_results.append(("Google Drive", test_drive_connection(CREDENTIALS_PATH, LIBRARY_FOLDER_ID)))
        tests_results.append(("Google Sheets", test_sheets_connection(CREDENTIALS_PATH)))

    # Resumo
    print_header("RESUMO DOS TESTES")

    all_passed = True
    for test_name, result in tests_results:
        if result:
            print_success(f"{test_name}: PASSOU")
        else:
            print_error(f"{test_name}: FALHOU")
            all_passed = False

    print()

    if all_passed:
        print("=" * 70)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("=" * 70)
        print("\nVocê está pronto para executar a sincronização!")
        print("\nPróximos passos:")
        print("1. Execute o script: python ebook_sync.py")
        print("2. Ou use o notebook: Ebook_Library_Sync.ipynb")
        print("=" * 70)
        return 0
    else:
        print("=" * 70)
        print("❌ ALGUNS TESTES FALHARAM")
        print("=" * 70)
        print("\nCorreja os problemas acima antes de executar a sincronização.")
        print("Consulte o README.md para mais informações.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
