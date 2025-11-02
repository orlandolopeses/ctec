#!/usr/bin/env python3
"""
Script de Sincronização de Biblioteca de Ebooks com Google Sheets
Otimizado para grandes volumes (50k+ arquivos)

Autor: Claude
Data: 2025-11-02
"""

import os
import json
import pickle
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
import logging

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERRO: Bibliotecas necessárias não instaladas!")
    print("Execute: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    raise


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ebook_sync.log')
    ]
)
logger = logging.getLogger(__name__)


class EbookLibrarySync:
    """Classe para sincronizar biblioteca de ebooks com Google Sheets"""

    # Limites da API do Google
    DRIVE_API_BATCH_SIZE = 1000  # Arquivos por requisição
    SHEETS_BATCH_SIZE = 10000     # Linhas por atualização (Google Sheets suporta até 10M células)
    MAX_RETRIES = 5
    RETRY_DELAY = 2  # segundos

    # Extensões de ebooks comuns
    EBOOK_EXTENSIONS = {
        '.pdf', '.epub', '.mobi', '.azw', '.azw3', '.djvu', '.fb2',
        '.txt', '.rtf', '.doc', '.docx', '.cbr', '.cbz', '.lit'
    }

    def __init__(self, credentials_path: str, library_folder_id: str,
                 cache_file: str = 'library_cache.pkl'):
        """
        Inicializa o sincronizador

        Args:
            credentials_path: Caminho para o arquivo JSON de credenciais
            library_folder_id: ID da pasta raiz da biblioteca no Drive
            cache_file: Arquivo para cache dos arquivos processados
        """
        self.credentials_path = credentials_path
        self.library_folder_id = library_folder_id
        self.cache_file = cache_file

        self.drive_service = None
        self.sheets_service = None
        self.cache = self._load_cache()

        logger.info("Inicializando EbookLibrarySync...")
        self._authenticate()

    def _authenticate(self):
        """Autentica com as APIs do Google Drive e Sheets"""
        try:
            logger.info(f"Autenticando com credenciais: {self.credentials_path}")

            # Escopos necessários
            SCOPES = [
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/spreadsheets'
            ]

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )

            # Construir serviços
            self.drive_service = build('drive', 'v3', credentials=credentials)
            self.sheets_service = build('sheets', 'v4', credentials=credentials)

            logger.info("✓ Autenticação bem-sucedida!")

        except Exception as e:
            logger.error(f"✗ Erro na autenticação: {e}")
            raise

    def _load_cache(self) -> Dict:
        """Carrega cache de arquivos processados anteriormente"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache = pickle.load(f)
                logger.info(f"Cache carregado: {len(cache.get('files', {}))} arquivos")
                return cache
            except Exception as e:
                logger.warning(f"Erro ao carregar cache: {e}")

        return {'files': {}, 'last_sync': None}

    def _save_cache(self):
        """Salva cache de arquivos processados"""
        try:
            self.cache['last_sync'] = datetime.now().isoformat()
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
            logger.info(f"Cache salvo: {len(self.cache['files'])} arquivos")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")

    def _retry_request(self, func, *args, **kwargs):
        """Executa requisição com retry em caso de erro"""
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except HttpError as e:
                if e.resp.status in [403, 429, 500, 503]:
                    wait_time = self.RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Erro {e.resp.status}, tentando novamente em {wait_time}s... (tentativa {attempt + 1}/{self.MAX_RETRIES})")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                logger.error(f"Erro na requisição: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    raise

        raise Exception(f"Falha após {self.MAX_RETRIES} tentativas")

    def _list_files_in_folder(self, folder_id: str, page_token: Optional[str] = None) -> Dict:
        """
        Lista arquivos em uma pasta do Drive (com paginação)

        Args:
            folder_id: ID da pasta
            page_token: Token para paginação

        Returns:
            Dicionário com arquivos e próximo page_token
        """
        query = f"'{folder_id}' in parents and trashed=false"

        # Campos que queremos retornar
        fields = "nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, parents)"

        try:
            results = self._retry_request(
                self.drive_service.files().list,
                q=query,
                pageSize=self.DRIVE_API_BATCH_SIZE,
                fields=fields,
                pageToken=page_token
            ).execute()

            return results

        except Exception as e:
            logger.error(f"Erro ao listar arquivos da pasta {folder_id}: {e}")
            return {'files': [], 'nextPageToken': None}

    def _get_folder_path(self, file_id: str, file_name: str, cache_paths: Dict[str, str]) -> str:
        """
        Obtém o caminho completo de um arquivo/pasta

        Args:
            file_id: ID do arquivo/pasta
            file_name: Nome do arquivo/pasta
            cache_paths: Cache de caminhos já resolvidos

        Returns:
            Caminho completo do arquivo
        """
        if file_id in cache_paths:
            return cache_paths[file_id]

        try:
            # Obter informações do arquivo para pegar o parent
            file_info = self._retry_request(
                self.drive_service.files().get,
                fileId=file_id,
                fields='parents'
            ).execute()

            parents = file_info.get('parents', [])

            if not parents or parents[0] == self.library_folder_id:
                # Chegamos na raiz
                cache_paths[file_id] = f"/{file_name}"
                return cache_paths[file_id]

            # Obter informações do parent
            parent_id = parents[0]
            parent_info = self._retry_request(
                self.drive_service.files().get,
                fileId=parent_id,
                fields='name, parents'
            ).execute()

            parent_name = parent_info.get('name', 'Unknown')
            parent_path = self._get_folder_path(parent_id, parent_name, cache_paths)

            full_path = f"{parent_path}/{file_name}"
            cache_paths[file_id] = full_path

            return full_path

        except Exception as e:
            logger.error(f"Erro ao obter caminho do arquivo {file_id}: {e}")
            return f"/ERROR/{file_name}"

    def scan_library(self, progress_callback=None) -> List[Dict]:
        """
        Escaneia toda a biblioteca recursivamente

        Args:
            progress_callback: Função para reportar progresso (opcional)

        Returns:
            Lista de dicionários com informações dos arquivos
        """
        logger.info("Iniciando varredura da biblioteca...")

        all_files = []
        folders_to_process = [self.library_folder_id]
        processed_folders = set()
        cache_paths = {}

        total_files = 0
        total_folders = 0

        while folders_to_process:
            current_folder_id = folders_to_process.pop(0)

            if current_folder_id in processed_folders:
                continue

            processed_folders.add(current_folder_id)
            total_folders += 1

            logger.info(f"Processando pasta {total_folders}... (arquivos encontrados: {total_files})")

            # Listar todos os arquivos da pasta com paginação
            page_token = None
            while True:
                results = self._list_files_in_folder(current_folder_id, page_token)
                files = results.get('files', [])

                for file_info in files:
                    file_id = file_info['id']
                    file_name = file_info['name']
                    mime_type = file_info['mimeType']

                    # Se for pasta, adicionar para processar depois
                    if mime_type == 'application/vnd.google-apps.folder':
                        folders_to_process.append(file_id)
                        continue

                    # Verificar se é um ebook
                    extension = Path(file_name).suffix.lower()
                    if extension not in self.EBOOK_EXTENSIONS:
                        continue

                    # Obter caminho completo
                    file_path = self._get_folder_path(file_id, file_name, cache_paths)

                    # Extrair informações
                    file_data = {
                        'id': file_id,
                        'nome': file_name,
                        'caminho': file_path,
                        'extensao': extension,
                        'tamanho': int(file_info.get('size', 0)),
                        'tamanho_mb': round(int(file_info.get('size', 0)) / (1024 * 1024), 2),
                        'data_criacao': file_info.get('createdTime', ''),
                        'data_modificacao': file_info.get('modifiedTime', ''),
                        'link': file_info.get('webViewLink', ''),
                        'mime_type': mime_type
                    }

                    all_files.append(file_data)
                    total_files += 1

                    if progress_callback and total_files % 100 == 0:
                        progress_callback(total_files, total_folders)

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

                # Pequeno delay para não sobrecarregar a API
                time.sleep(0.1)

        logger.info(f"✓ Varredura concluída: {total_files} ebooks em {total_folders} pastas")

        return all_files

    def create_or_update_spreadsheet(self, files_data: List[Dict],
                                     spreadsheet_id: Optional[str] = None,
                                     sheet_name: str = "Biblioteca de Ebooks") -> str:
        """
        Cria ou atualiza planilha com os dados dos arquivos

        Args:
            files_data: Lista com dados dos arquivos
            spreadsheet_id: ID da planilha existente (se None, cria nova)
            sheet_name: Nome da aba

        Returns:
            ID da planilha
        """
        logger.info(f"{'Atualizando' if spreadsheet_id else 'Criando'} planilha...")

        # Criar planilha se não existir
        if not spreadsheet_id:
            spreadsheet_id = self._create_spreadsheet(sheet_name)

        # Preparar dados para a planilha
        headers = [
            'ID', 'Nome', 'Caminho', 'Extensão', 'Tamanho (bytes)',
            'Tamanho (MB)', 'Data Criação', 'Data Modificação', 'Link'
        ]

        rows = [headers]
        for file_data in files_data:
            row = [
                file_data['id'],
                file_data['nome'],
                file_data['caminho'],
                file_data['extensao'],
                file_data['tamanho'],
                file_data['tamanho_mb'],
                file_data['data_criacao'],
                file_data['data_modificacao'],
                file_data['link']
            ]
            rows.append(row)

        # Atualizar planilha em lotes
        self._update_sheet_in_batches(spreadsheet_id, sheet_name, rows)

        # Formatar planilha
        self._format_spreadsheet(spreadsheet_id, sheet_name, len(rows))

        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        logger.info(f"✓ Planilha atualizada: {spreadsheet_url}")

        return spreadsheet_id

    def _create_spreadsheet(self, title: str) -> str:
        """Cria nova planilha"""
        try:
            spreadsheet = {
                'properties': {
                    'title': f'{title} - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                }
            }

            spreadsheet = self._retry_request(
                self.sheets_service.spreadsheets().create,
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()

            spreadsheet_id = spreadsheet.get('spreadsheetId')
            logger.info(f"✓ Planilha criada: {spreadsheet_id}")

            return spreadsheet_id

        except Exception as e:
            logger.error(f"✗ Erro ao criar planilha: {e}")
            raise

    def _update_sheet_in_batches(self, spreadsheet_id: str, sheet_name: str, rows: List[List]):
        """Atualiza planilha em lotes para evitar timeout"""
        total_rows = len(rows)
        logger.info(f"Atualizando planilha com {total_rows} linhas...")

        try:
            # Limpar planilha existente
            self._retry_request(
                self.sheets_service.spreadsheets().values().clear,
                spreadsheetId=spreadsheet_id,
                range=sheet_name,
                body={}
            ).execute()

            # Atualizar em lotes
            for i in range(0, total_rows, self.SHEETS_BATCH_SIZE):
                batch = rows[i:i + self.SHEETS_BATCH_SIZE]
                end_row = min(i + self.SHEETS_BATCH_SIZE, total_rows)

                logger.info(f"Atualizando linhas {i+1} a {end_row}...")

                body = {
                    'values': batch
                }

                self._retry_request(
                    self.sheets_service.spreadsheets().values().update,
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A{i+1}",
                    valueInputOption='RAW',
                    body=body
                ).execute()

                # Pequeno delay entre lotes
                time.sleep(0.5)

            logger.info(f"✓ {total_rows} linhas atualizadas com sucesso!")

        except Exception as e:
            logger.error(f"✗ Erro ao atualizar planilha: {e}")
            raise

    def _format_spreadsheet(self, spreadsheet_id: str, sheet_name: str, num_rows: int):
        """Formata a planilha (cabeçalho em negrito, congelar primeira linha, etc)"""
        try:
            # Obter ID da aba
            spreadsheet = self._retry_request(
                self.sheets_service.spreadsheets().get,
                spreadsheetId=spreadsheet_id
            ).execute()

            sheet_id = None
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break

            if not sheet_id:
                logger.warning("Sheet ID não encontrado para formatação")
                return

            requests = [
                # Congelar primeira linha (cabeçalho)
                {
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': sheet_id,
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        },
                        'fields': 'gridProperties.frozenRowCount'
                    }
                },
                # Formatar cabeçalho (negrito)
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {
                                    'bold': True
                                },
                                'backgroundColor': {
                                    'red': 0.9,
                                    'green': 0.9,
                                    'blue': 0.9
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                    }
                },
                # Auto-resize colunas
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 9
                        }
                    }
                }
            ]

            body = {
                'requests': requests
            }

            self._retry_request(
                self.sheets_service.spreadsheets().batchUpdate,
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()

            logger.info("✓ Planilha formatada com sucesso!")

        except Exception as e:
            logger.error(f"⚠ Erro ao formatar planilha (não crítico): {e}")

    def sync(self, spreadsheet_id: Optional[str] = None) -> str:
        """
        Executa sincronização completa

        Args:
            spreadsheet_id: ID da planilha existente (se None, cria nova)

        Returns:
            ID da planilha
        """
        start_time = time.time()

        logger.info("=" * 60)
        logger.info("INICIANDO SINCRONIZAÇÃO DA BIBLIOTECA")
        logger.info("=" * 60)

        # Escanear biblioteca
        def progress(files, folders):
            logger.info(f"Progresso: {files} ebooks em {folders} pastas")

        files_data = self.scan_library(progress_callback=progress)

        if not files_data:
            logger.warning("Nenhum ebook encontrado!")
            return None

        # Atualizar cache
        self.cache['files'] = {f['id']: f for f in files_data}
        self._save_cache()

        # Criar/atualizar planilha
        spreadsheet_id = self.create_or_update_spreadsheet(files_data, spreadsheet_id)

        # Estatísticas
        elapsed_time = time.time() - start_time
        total_size_gb = sum(f['tamanho'] for f in files_data) / (1024 ** 3)

        logger.info("=" * 60)
        logger.info("SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info(f"Total de ebooks: {len(files_data)}")
        logger.info(f"Tamanho total: {total_size_gb:.2f} GB")
        logger.info(f"Tempo decorrido: {elapsed_time:.2f} segundos")
        logger.info(f"URL da planilha: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        logger.info("=" * 60)

        return spreadsheet_id


def main():
    """Função principal para teste"""
    # Configurações (ajuste conforme necessário)
    CREDENTIALS_PATH = "/content/drive/MyDrive/0_Credentials/acessodriveorlando-44351dfb71f4.json"
    LIBRARY_FOLDER_ID = "0B9gSg9OIekOlajlGdWcxOWt0MlU"

    # Criar sincronizador
    sync = EbookLibrarySync(
        credentials_path=CREDENTIALS_PATH,
        library_folder_id=LIBRARY_FOLDER_ID
    )

    # Executar sincronização
    spreadsheet_id = sync.sync()

    print(f"\n✓ Sincronização concluída!")
    print(f"Planilha: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")


if __name__ == "__main__":
    main()
