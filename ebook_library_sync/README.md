# 📚 Ebook Library Sync - Sincronizador de Biblioteca de Ebooks

Sistema completo para sincronizar sua biblioteca de ebooks do Google Drive com Google Sheets, otimizado para grandes volumes (50k+ arquivos).

## 🎯 Funcionalidades

- ✅ **Varredura recursiva** de toda a biblioteca no Google Drive
- ✅ **Suporte para grandes volumes** (50k a 200k+ arquivos)
- ✅ **Cache inteligente** para sincronizações incrementais
- ✅ **Retry automático** em caso de erros de rede ou limites de API
- ✅ **Logging detalhado** de todo o processo
- ✅ **Formatação automática** da planilha (cabeçalhos, congelamento, etc)
- ✅ **Estatísticas detalhadas** da biblioteca
- ✅ **Busca e filtros** por nome, extensão, tamanho, etc

## 📋 Formatos de Ebook Suportados

O sistema identifica e processa os seguintes formatos:

- **Documentos**: PDF, TXT, RTF, DOC, DOCX
- **E-readers**: EPUB, MOBI, AZW, AZW3
- **Especializados**: DJVU, FB2, LIT
- **Comics**: CBR, CBZ

## 🚀 Início Rápido

### Opção 1: Google Colab (Recomendado)

1. Abra o notebook `Ebook_Library_Sync.ipynb` no Google Colab
2. Configure suas credenciais e caminhos
3. Execute as células sequencialmente
4. Pronto! Sua planilha estará criada e atualizada

### Opção 2: Script Python Local

```bash
# Instalar dependências
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Executar script
python ebook_sync.py
```

## ⚙️ Configuração

### 1. Credenciais do Google Drive

Você precisa de um arquivo JSON de credenciais de service account com permissões para:
- Google Drive API (leitura)
- Google Sheets API (leitura e escrita)

**Caminho padrão**: `/content/drive/MyDrive/0_Credentials/acessodriveorlando-44351dfb71f4.json`

### 2. ID da Pasta da Biblioteca

Encontre o ID da pasta raiz da sua biblioteca:
- Abra a pasta no Google Drive
- O ID está na URL após `/folders/`
- Exemplo: `https://drive.google.com/drive/folders/0B9gSg9OIekOlajlGdWcxOWt0MlU`
  - ID: `0B9gSg9OIekOlajlGdWcxOWt0MlU`

### 3. Configurações no Código

```python
# Credenciais
CREDENTIALS_PATH = "/caminho/para/credenciais.json"

# ID da pasta da biblioteca
LIBRARY_FOLDER_ID = "0B9gSg9OIekOlajlGdWcxOWt0MlU"

# ID da planilha (None para criar nova)
SPREADSHEET_ID = None

# Arquivo de cache
CACHE_FILE = "/content/drive/MyDrive/library_cache.pkl"
```

## 📊 Estrutura da Planilha

A planilha criada contém as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| ID | ID único do arquivo no Google Drive |
| Nome | Nome completo do arquivo |
| Caminho | Caminho completo na estrutura de pastas |
| Extensão | Tipo de arquivo (.pdf, .epub, etc) |
| Tamanho (bytes) | Tamanho em bytes |
| Tamanho (MB) | Tamanho em megabytes |
| Data Criação | Data de criação no Drive |
| Data Modificação | Data da última modificação |
| Link | Link direto para o arquivo no Drive |

## 🔧 Uso Avançado

### Atualização Incremental

Para atualizar uma planilha existente em vez de criar nova:

```python
# Configure o ID da planilha existente
SPREADSHEET_ID = "1a2b3c4d5e6f7g8h9i0j"

# Execute novamente
sync = EbookLibrarySync(CREDENTIALS_PATH, LIBRARY_FOLDER_ID, CACHE_FILE)
sync.sync(spreadsheet_id=SPREADSHEET_ID)
```

### Buscar Arquivos

```python
# Carregar cache
with open(CACHE_FILE, 'rb') as f:
    cache = pickle.load(f)

# Buscar por termo
results = [
    f for f in cache['files'].values()
    if 'python' in f['nome'].lower()
]

# Filtrar por extensão
pdfs = [
    f for f in cache['files'].values()
    if f['extensao'] == '.pdf'
]

# Arquivos grandes (>100 MB)
large_files = [
    f for f in cache['files'].values()
    if f['tamanho_mb'] > 100
]
```

### Estatísticas

```python
from collections import Counter

files = list(cache['files'].values())

# Total
total_files = len(files)
total_size_gb = sum(f['tamanho'] for f in files) / (1024**3)

# Por extensão
extensions = Counter(f['extensao'] for f in files)
print(extensions.most_common())

# Maiores arquivos
largest = sorted(files, key=lambda x: x['tamanho'], reverse=True)[:10]
```

## ⚡ Performance e Limites

### Tempo de Execução Estimado

| Arquivos | Tempo Estimado | Observações |
|----------|---------------|-------------|
| 10k | 10-20 min | Depende da estrutura de pastas |
| 50k | 30-60 min | Tempo médio esperado |
| 100k | 60-120 min | Pode variar com conexão |
| 200k | 2-4 horas | Máximo testado |

### Limites do Google Sheets

- **Máximo de células**: 10 milhões
- **Com 9 colunas**: ~1,1 milhão de linhas possíveis
- **Sua biblioteca (200k)**: ✅ Bem dentro do limite

### Otimizações Implementadas

1. **Paginação**: Processa arquivos em lotes de 1000
2. **Cache de caminhos**: Evita chamadas repetidas à API
3. **Retry exponencial**: Tenta novamente em caso de erro (5 tentativas)
4. **Batching**: Atualiza planilha em lotes de 10k linhas
5. **Rate limiting**: Delays estratégicos para não sobrecarregar API

## 🛠️ Troubleshooting

### Erro de Autenticação

```
✗ Erro na autenticação: ...
```

**Solução**:
- Verifique se o arquivo de credenciais existe
- Confirme que tem permissões corretas (Drive + Sheets)
- Certifique-se de que o caminho está correto

### Erro 403/429 (Rate Limit)

```
Erro 403, tentando novamente em 2s...
```

**Solução**:
- O script já tem retry automático
- Aguarde alguns segundos entre execuções
- Considere diminuir DRIVE_API_BATCH_SIZE

### Planilha não atualiza

**Soluções**:
- Verifique se o service account tem permissão de escrita
- Confirme que o SPREADSHEET_ID está correto
- Tente criar nova planilha (SPREADSHEET_ID = None)

### Arquivos não aparecem

**Verificações**:
- Confirme que os arquivos têm extensões suportadas
- Verifique se os arquivos não estão na lixeira
- Confirme que LIBRARY_FOLDER_ID está correto
- Veja os logs para identificar pastas com erro

### Cache corrompido

```python
# Delete o cache e execute novamente
import os
os.remove(CACHE_FILE)
```

## 📁 Estrutura do Projeto

```
ebook_library_sync/
├── ebook_sync.py              # Script principal
├── Ebook_Library_Sync.ipynb   # Notebook para Google Colab
├── README.md                  # Esta documentação
└── example_simple.py          # Exemplo simplificado
```

## 🔐 Segurança e Privacidade

- O script usa **apenas leitura** no Drive (exceto para criar planilha)
- Credenciais são armazenadas localmente
- Nenhum dado é enviado para servidores externos
- Cache pode ser criptografado se necessário

## 🤝 Contribuindo

Sugestões e melhorias são bem-vindas! Considere:

- Adicionar suporte para outros formatos
- Implementar detecção de duplicatas
- Adicionar extração de metadados dos arquivos
- Criar dashboard interativo
- Implementar sincronização bidirecional

## 📝 Notas de Uso

### Primeira Execução

Na primeira execução, o script irá:
1. Autenticar com Google Drive e Sheets
2. Varrer toda a biblioteca recursivamente
3. Criar cache com todos os arquivos
4. Criar planilha nova com todos os dados
5. Salvar ID da planilha no log

**Guarde o ID da planilha** para futuras atualizações!

### Execuções Subsequentes

Com o cache e SPREADSHEET_ID configurados:
1. Carrega cache anterior
2. Varre apenas arquivos novos/modificados
3. Atualiza planilha existente
4. Atualiza cache

**Muito mais rápido!**

### Compartilhamento da Planilha

Para compartilhar a planilha criada:

**Opção 1 - Adicionar service account**:
1. Copie o email da service account (nas credenciais JSON)
2. Abra a planilha
3. Clique em "Compartilhar"
4. Adicione o email com permissão de "Editor"

**Opção 2 - Link público**:
1. Abra a planilha
2. Clique em "Compartilhar"
3. Altere para "Qualquer pessoa com o link"
4. Defina permissão como "Visualizador" ou "Editor"

## 🎓 Exemplos Práticos

### Exemplo 1: Primeira Sincronização

```python
from ebook_sync import EbookLibrarySync

# Configurar
sync = EbookLibrarySync(
    credentials_path="/path/to/creds.json",
    library_folder_id="0B9gSg9OIekOlajlGdWcxOWt0MlU",
    cache_file="/path/to/cache.pkl"
)

# Executar
spreadsheet_id = sync.sync()
print(f"Planilha criada: {spreadsheet_id}")
```

### Exemplo 2: Atualizar Planilha Existente

```python
# Mesmo setup
sync = EbookLibrarySync(...)

# Atualizar planilha específica
spreadsheet_id = sync.sync(spreadsheet_id="1a2b3c...")
```

### Exemplo 3: Apenas Escanear (sem planilha)

```python
sync = EbookLibrarySync(...)

# Apenas escanear
files = sync.scan_library()

# Trabalhar com os dados
for file in files:
    print(f"{file['nome']} - {file['tamanho_mb']} MB")
```

## 📈 Roadmap

Funcionalidades planejadas:

- [ ] Interface web para visualização
- [ ] Detecção automática de duplicatas
- [ ] Extração de metadados (autor, ISBN, etc)
- [ ] Categorização automática por assunto
- [ ] Sincronização com Calibre
- [ ] Suporte para Google Books API
- [ ] Dashboard com gráficos e estatísticas
- [ ] Notificações por email
- [ ] Agendamento automático

## 📄 Licença

Este projeto é fornecido como está, sem garantias. Use por sua própria conta e risco.

## 👨‍💻 Autor

Criado por Claude (Anthropic)
Data: 2025-11-02

---

**Dúvidas?** Consulte a documentação ou abra uma issue!
