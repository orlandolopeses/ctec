# 🚀 Guia Rápido - Ebook Library Sync

Comece a usar o sincronizador em 3 passos simples!

## Passo 1: Abra o Notebook no Google Colab

1. Acesse [Google Colab](https://colab.research.google.com/)
2. Clique em **File > Upload notebook**
3. Faça upload do arquivo `Ebook_Library_Sync.ipynb`

## Passo 2: Configure suas Credenciais

No notebook, encontre a seção **"Passo 2: Configuração"** e ajuste:

```python
# Caminho para suas credenciais
CREDENTIALS_PATH = "/content/drive/MyDrive/0_Credentials/acessodriveorlando-44351dfb71f4.json"

# ID da sua pasta de biblioteca (está na URL da pasta)
LIBRARY_FOLDER_ID = "0B9gSg9OIekOlajlGdWcxOWt0MlU"
```

### Como encontrar o ID da pasta?

1. Abra sua pasta de biblioteca no Google Drive
2. Veja a URL no navegador:
   ```
   https://drive.google.com/drive/folders/0B9gSg9OIekOlajlGdWcxOWt0MlU
   ```
3. O ID é a parte final: `0B9gSg9OIekOlajlGdWcxOWt0MlU`

## Passo 3: Execute!

Execute as células do notebook em ordem:

1. **Montar Drive**: Autorize o acesso ao seu Drive
2. **Instalar bibliotecas**: Aguarde a instalação
3. **Configurar**: Suas configurações já estão prontas
4. **Executar sincronização**: Inicie o processo!

## ⏱️ Quanto tempo vai demorar?

| Arquivos | Tempo Aproximado |
|----------|------------------|
| 1-10k | 5-15 minutos |
| 10-50k | 15-45 minutos |
| 50-100k | 45-90 minutos |
| 100k+ | 1-3 horas |

## ✅ Pronto!

Quando terminar, você verá:

```
🎉 SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!
📊 Sua planilha está disponível em:
   https://docs.google.com/spreadsheets/d/[ID-DA-SUA-PLANILHA]
```

**IMPORTANTE**: Salve o ID da planilha para futuras atualizações!

## 🔄 Atualizar a Planilha Depois

Para atualizar a mesma planilha (muito mais rápido):

1. Configure o ID da planilha:
   ```python
   SPREADSHEET_ID = "cole-o-id-aqui"
   ```
2. Execute novamente!

O cache fará com que apenas arquivos novos/modificados sejam processados.

## ❓ Problemas?

### Erro de autenticação
- Verifique se o caminho das credenciais está correto
- Confirme que as credenciais têm permissões para Drive e Sheets

### Nenhum arquivo encontrado
- Confirme que o ID da pasta está correto
- Verifique se existem arquivos com extensões de ebook na pasta

### Demora muito
- É normal para bibliotecas grandes!
- O processo pode ser pausado e retomado
- Use o cache para sincronizações futuras mais rápidas

## 📚 Quer saber mais?

Consulte o **README.md** completo para:
- Uso avançado
- Busca e filtros
- Estatísticas detalhadas
- Troubleshooting completo
- Exemplos de código

---

**Boa sincronização!** 📚✨
