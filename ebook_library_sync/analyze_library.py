#!/usr/bin/env python3
"""
Análise de Dados da Biblioteca de Ebooks

Este script mostra exemplos de como analisar os dados da sua biblioteca
após a sincronização.
"""

import pickle
import os
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime


def load_cache(cache_file):
    """Carrega cache de arquivos"""
    if not os.path.exists(cache_file):
        print(f"❌ Cache não encontrado: {cache_file}")
        print("Execute a sincronização primeiro!")
        return None

    try:
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)
        return cache
    except Exception as e:
        print(f"❌ Erro ao carregar cache: {e}")
        return None


def format_size(bytes_size):
    """Formata tamanho em bytes para formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0


def analyze_general_stats(files):
    """Estatísticas gerais"""
    print("\n" + "=" * 70)
    print(" 📊 ESTATÍSTICAS GERAIS")
    print("=" * 70)

    total_files = len(files)
    total_size = sum(f['tamanho'] for f in files)

    print(f"\n📚 Total de ebooks: {total_files:,}")
    print(f"💾 Tamanho total: {format_size(total_size)}")
    print(f"📏 Tamanho médio: {format_size(total_size / total_files if total_files > 0 else 0)}")

    # Maior e menor
    if files:
        largest = max(files, key=lambda x: x['tamanho'])
        smallest = min(files, key=lambda x: x['tamanho'])

        print(f"\n📦 Maior arquivo:")
        print(f"   {largest['nome']} - {format_size(largest['tamanho'])}")
        print(f"\n📄 Menor arquivo:")
        print(f"   {smallest['nome']} - {format_size(smallest['tamanho'])}")


def analyze_by_extension(files):
    """Análise por extensão/formato"""
    print("\n" + "=" * 70)
    print(" 📚 ANÁLISE POR FORMATO")
    print("=" * 70)

    # Contar por extensão
    extensions = Counter(f['extensao'] for f in files)

    # Tamanho por extensão
    size_by_ext = defaultdict(int)
    for f in files:
        size_by_ext[f['extensao']] += f['tamanho']

    print(f"\n{'Formato':<10} {'Quantidade':<15} {'% Total':<10} {'Tamanho Total':<15}")
    print("-" * 70)

    total_files = len(files)

    for ext, count in extensions.most_common():
        percentage = (count / total_files) * 100
        size = size_by_ext[ext]
        print(f"{ext:<10} {count:<15,} {percentage:>6.2f}%    {format_size(size):<15}")


def analyze_by_folder(files):
    """Análise por pasta"""
    print("\n" + "=" * 70)
    print(" 📁 TOP 20 PASTAS COM MAIS EBOOKS")
    print("=" * 70)

    # Agrupar por pasta
    folder_counts = defaultdict(int)
    for f in files:
        folder = str(Path(f['caminho']).parent)
        folder_counts[folder] += 1

    # Top 20
    top_folders = sorted(folder_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    print(f"\n{'Quantidade':<12} Pasta")
    print("-" * 70)

    for folder, count in top_folders:
        # Truncar caminho se muito longo
        display_folder = folder if len(folder) <= 55 else folder[:52] + "..."
        print(f"{count:<12,} {display_folder}")


def analyze_by_size_range(files):
    """Análise por faixa de tamanho"""
    print("\n" + "=" * 70)
    print(" 📊 DISTRIBUIÇÃO POR TAMANHO")
    print("=" * 70)

    # Definir faixas (em MB)
    ranges = [
        ("< 1 MB", 0, 1),
        ("1-5 MB", 1, 5),
        ("5-10 MB", 5, 10),
        ("10-50 MB", 10, 50),
        ("50-100 MB", 50, 100),
        ("> 100 MB", 100, float('inf'))
    ]

    range_counts = defaultdict(int)
    total_files = len(files)

    for f in files:
        size_mb = f['tamanho_mb']
        for label, min_size, max_size in ranges:
            if min_size <= size_mb < max_size:
                range_counts[label] += 1
                break

    print(f"\n{'Faixa':<15} {'Quantidade':<15} {'% Total':<10}")
    print("-" * 70)

    for label, _, _ in ranges:
        count = range_counts[label]
        percentage = (count / total_files * 100) if total_files > 0 else 0
        print(f"{label:<15} {count:<15,} {percentage:>6.2f}%")


def analyze_largest_files(files, top_n=20):
    """Top N maiores arquivos"""
    print("\n" + "=" * 70)
    print(f" 📦 TOP {top_n} MAIORES ARQUIVOS")
    print("=" * 70)

    largest = sorted(files, key=lambda x: x['tamanho'], reverse=True)[:top_n]

    print(f"\n{'#':<4} {'Tamanho':<12} Nome do Arquivo")
    print("-" * 70)

    for i, f in enumerate(largest, 1):
        name = f['nome']
        # Truncar nome se muito longo
        if len(name) > 50:
            name = name[:47] + "..."
        print(f"{i:<4} {format_size(f['tamanho']):<12} {name}")


def search_files(files, search_term, case_sensitive=False):
    """Busca arquivos por termo"""
    print("\n" + "=" * 70)
    print(f" 🔍 BUSCA: '{search_term}'")
    print("=" * 70)

    if not case_sensitive:
        search_term = search_term.lower()

    results = []
    for f in files:
        name = f['nome'] if case_sensitive else f['nome'].lower()
        if search_term in name:
            results.append(f)

    print(f"\n✓ Encontrados {len(results)} resultado(s)")

    if results:
        print(f"\n{'Tamanho':<12} Nome")
        print("-" * 70)

        for f in results[:50]:  # Mostrar primeiros 50
            name = f['nome']
            if len(name) > 55:
                name = name[:52] + "..."
            print(f"{format_size(f['tamanho']):<12} {name}")

        if len(results) > 50:
            print(f"\n... e mais {len(results) - 50} resultado(s)")


def analyze_by_date(files):
    """Análise por data de modificação"""
    print("\n" + "=" * 70)
    print(" 📅 ARQUIVOS MAIS RECENTES")
    print("=" * 70)

    # Filtrar arquivos com data
    files_with_date = [f for f in files if f.get('data_modificacao')]

    if not files_with_date:
        print("\n⚠ Nenhum arquivo com informação de data.")
        return

    # Ordenar por data (mais recentes primeiro)
    sorted_files = sorted(
        files_with_date,
        key=lambda x: x['data_modificacao'],
        reverse=True
    )[:20]

    print(f"\n{'Data':<20} {'Tamanho':<12} Nome")
    print("-" * 70)

    for f in sorted_files:
        try:
            date_str = f['data_modificacao'][:10]  # Pegar apenas data (YYYY-MM-DD)
        except:
            date_str = "N/A"

        name = f['nome']
        if len(name) > 40:
            name = name[:37] + "..."

        print(f"{date_str:<20} {format_size(f['tamanho']):<12} {name}")


def main():
    """Função principal"""
    print("=" * 70)
    print(" 📊 ANÁLISE DE BIBLIOTECA DE EBOOKS")
    print("=" * 70)

    # Configuração
    CACHE_FILE = "/content/drive/MyDrive/library_cache.pkl"

    # Carregar dados
    cache = load_cache(CACHE_FILE)
    if not cache or not cache.get('files'):
        print("\n❌ Nenhum dado encontrado no cache.")
        print("Execute a sincronização primeiro: python ebook_sync.py")
        return

    files = list(cache['files'].values())
    last_sync = cache.get('last_sync', 'N/A')

    print(f"\n✓ Cache carregado: {len(files):,} arquivos")
    print(f"✓ Última sincronização: {last_sync}")

    # Menu de análises
    print("\n" + "=" * 70)
    print(" EXECUTANDO TODAS AS ANÁLISES")
    print("=" * 70)

    # Executar análises
    analyze_general_stats(files)
    analyze_by_extension(files)
    analyze_by_size_range(files)
    analyze_by_folder(files)
    analyze_largest_files(files, top_n=20)
    analyze_by_date(files)

    # Exemplos de busca
    print("\n" + "=" * 70)
    print(" 🔍 EXEMPLOS DE BUSCA")
    print("=" * 70)
    print("\nPara buscar arquivos, edite este script e chame:")
    print("  search_files(files, 'python')")
    print("  search_files(files, '.pdf')")
    print("  search_files(files, 'programming', case_sensitive=False)")

    # Buscar por termo específico (exemplo)
    # Descomente e ajuste conforme necessário:
    # search_files(files, 'python')

    print("\n" + "=" * 70)
    print(" ✓ ANÁLISE CONCLUÍDA!")
    print("=" * 70)
    print("\nPara análises personalizadas, edite este script e adicione suas próprias funções.")
    print("Consulte o README.md para mais exemplos.\n")


if __name__ == "__main__":
    main()
