#!/usr/bin/env python3
"""
Exemplo Simplificado de Uso do Ebook Library Sync

Este script mostra como usar o sincronizador de forma simples e direta.
"""

from ebook_sync import EbookLibrarySync
import sys


def main():
    print("=" * 70)
    print("📚 SINCRONIZADOR DE BIBLIOTECA DE EBOOKS")
    print("=" * 70)
    print()

    # ========== CONFIGURAÇÕES - AJUSTE AQUI ==========

    # IMPORTANTE: Ajuste estes valores para sua configuração
    CREDENTIALS_PATH = "/content/drive/MyDrive/0_Credentials/acessodriveorlando-44351dfb71f4.json"
    LIBRARY_FOLDER_ID = "0B9gSg9OIekOlajlGdWcxOWt0MlU"
    CACHE_FILE = "/content/drive/MyDrive/library_cache.pkl"

    # Se você já tem uma planilha e quer atualizar, coloque o ID aqui
    # Deixe como None para criar uma nova planilha
    SPREADSHEET_ID = None  # Exemplo: "1a2b3c4d5e6f7g8h9i0j"

    # ==================================================

    try:
        # Verificar configurações
        print("⚙️  Verificando configurações...")
        import os

        if not os.path.exists(CREDENTIALS_PATH):
            print(f"❌ ERRO: Arquivo de credenciais não encontrado!")
            print(f"   Caminho: {CREDENTIALS_PATH}")
            print(f"   Verifique se o caminho está correto.")
            sys.exit(1)

        print(f"✓ Credenciais: {CREDENTIALS_PATH}")
        print(f"✓ ID da Biblioteca: {LIBRARY_FOLDER_ID}")
        print(f"✓ Cache: {CACHE_FILE}")
        print()

        # Criar instância do sincronizador
        print("🔐 Autenticando...")
        sync = EbookLibrarySync(
            credentials_path=CREDENTIALS_PATH,
            library_folder_id=LIBRARY_FOLDER_ID,
            cache_file=CACHE_FILE
        )
        print()

        # Executar sincronização
        print("🚀 Iniciando sincronização...")
        print("   (Isso pode levar alguns minutos para bibliotecas grandes)")
        print()

        spreadsheet_id = sync.sync(spreadsheet_id=SPREADSHEET_ID)

        if spreadsheet_id:
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

            print()
            print("=" * 70)
            print("🎉 SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 70)
            print()
            print(f"📊 Sua planilha está disponível em:")
            print(f"   {spreadsheet_url}")
            print()
            print("💡 Dicas:")
            print()
            print("1. Salve o ID da planilha para futuras atualizações:")
            print(f'   SPREADSHEET_ID = "{spreadsheet_id}"')
            print()
            print("2. Para atualizar a mesma planilha no futuro:")
            print("   - Configure SPREADSHEET_ID no início do script")
            print("   - Execute novamente")
            print()
            print("3. O cache foi salvo e futuras sincronizações serão mais rápidas!")
            print()
            print("=" * 70)
        else:
            print()
            print("⚠️  AVISO: Nenhum ebook encontrado na biblioteca.")
            print("    Verifique se o ID da pasta está correto.")
            print()

    except KeyboardInterrupt:
        print()
        print("⚠️  Sincronização interrompida pelo usuário.")
        print("   O cache parcial foi salvo e pode ser usado na próxima execução.")
        sys.exit(0)

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO DURANTE A SINCRONIZAÇÃO")
        print("=" * 70)
        print()
        print(f"Detalhes do erro: {e}")
        print()
        print("Possíveis soluções:")
        print("1. Verifique se o arquivo de credenciais está correto")
        print("2. Confirme que o ID da pasta da biblioteca está correto")
        print("3. Certifique-se de ter conexão com a internet")
        print("4. Tente novamente em alguns minutos (pode ser limite de API)")
        print()
        print("Para mais ajuda, consulte o README.md")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
