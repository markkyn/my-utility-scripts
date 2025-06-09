#!/usr/bin/env python3
"""
Script para converter todo o código fonte de um repositório para um arquivo Markdown único.

Uso:
    python repo_to_md.py <diretorio> -o <arquivo_saida.md> [-x <regex_pattern>]

Exemplos:
    python repo_to_md.py ./meu_projeto -o codigo_completo.md
    python repo_to_md.py ./meu_projeto -o codigo_completo.md -x "test_.*\.py|.*\.pyc"
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Set

class RepoToMarkdown:
    def __init__(self, ignore_patterns: List[str] = None):
        self.ignore_patterns = ignore_patterns or []
        
        # Padrões padrão para ignorar
        self.default_ignore = [
            r'\.git/.*',
            r'\.gitignore',
            r'__pycache__/.*',
            r'\.pyc$',
            r'\.pyo$',
            r'node_modules/.*',
            r'\.vscode/.*',
            r'\.idea/.*',
            r'\.DS_Store',
            r'\.env',
            r'\.log$',
            r'\.tmp$',
            r'\.cache/.*',
            r'dist/.*',
            r'build/.*',
            r'\.egg-info/.*',
            r'venv/.*',
            r'env/.*',
            r'\.venv/.*',
            r'\.pytest_cache/.*',
            r'\.coverage',
            r'coverage\.xml',
            r'\.nyc_output/.*',
            r'\.next/.*',
            r'\.nuxt/.*'
        ]
        
        # Extensões de código suportadas
        self.code_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'zsh',
            '.fish': 'fish',
            '.ps1': 'powershell',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'ini',
            '.sql': 'sql',
            '.r': 'r',
            '.R': 'r',
            '.m': 'matlab',
            '.pl': 'perl',
            '.lua': 'lua',
            '.vim': 'vim',
            '.dockerfile': 'dockerfile',
            '.Dockerfile': 'dockerfile',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.tex': 'latex',
            '.vue': 'vue',
            '.svelte': 'svelte',
            '.dart': 'dart',
            '.elm': 'elm',
            '.ex': 'elixir',
            '.exs': 'elixir',
            '.erl': 'erlang',
            '.hrl': 'erlang',
            '.clj': 'clojure',
            '.cljs': 'clojure',
            '.hs': 'haskell',
            '.lhs': 'haskell',
            '.ml': 'ocaml',
            '.mli': 'ocaml',
            '.fs': 'fsharp',
            '.fsx': 'fsharp',
            '.jl': 'julia',
            '.nim': 'nim',
            '.nims': 'nim',
            '.cr': 'crystal',
            '.zig': 'zig',
            '.v': 'v',
            '.sv': 'systemverilog',
            '.vhd': 'vhdl',
            '.vhdl': 'vhdl'
        }
    
    def should_ignore(self, file_path: str) -> bool:
        """Verifica se um arquivo deve ser ignorado baseado nos padrões regex."""
        all_patterns = self.default_ignore + self.ignore_patterns
        
        for pattern in all_patterns:
            if re.search(pattern, file_path):
                return True
        return False
    
    def get_language_from_extension(self, file_path: str) -> str:
        """Retorna a linguagem baseada na extensão do arquivo."""
        ext = Path(file_path).suffix.lower()
        return self.code_extensions.get(ext, 'text')
    
    def is_code_file(self, file_path: str) -> bool:
        """Verifica se o arquivo é um arquivo de código suportado."""
        ext = Path(file_path).suffix.lower()
        return ext in self.code_extensions
    
    def get_file_content(self, file_path: str) -> str:
        """Lê o conteúdo de um arquivo com tratamento de encoding."""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Erro ao ler {file_path}: {e}")
                return f"# Erro ao ler arquivo: {e}"
        
        return "# Arquivo não pôde ser decodificado"
    
    def scan_directory(self, directory: str) -> List[str]:
        """Escaneia o diretório e retorna lista de arquivos de código."""
        code_files = []
        
        for root, dirs, files in os.walk(directory):
            # Remove diretórios que devem ser ignorados
            dirs[:] = [d for d in dirs if not self.should_ignore(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                
                if not self.should_ignore(relative_path) and self.is_code_file(file_path):
                    code_files.append(file_path)
        
        return sorted(code_files)
    
    def generate_markdown(self, directory: str, output_file: str):
        """Gera o arquivo Markdown com todo o código do repositório."""
        print(f"Escaneando diretório: {directory}")
        code_files = self.scan_directory(directory)
        
        if not code_files:
            print("Nenhum arquivo de código encontrado!")
            return
        
        print(f"Encontrados {len(code_files)} arquivos de código")
        
        # Gera o conteúdo Markdown
        with open(output_file, 'w', encoding='utf-8') as f:
            # Cabeçalho
            repo_name = os.path.basename(os.path.abspath(directory))
            f.write(f"# Código Fonte - {repo_name}\n\n")
            f.write(f"Este documento contém todo o código fonte do repositório `{repo_name}`.\n\n")
            f.write(f"**Total de arquivos:** {len(code_files)}\n\n")
            
            # Índice
            f.write("## Índice\n\n")
            for file_path in code_files:
                relative_path = os.path.relpath(file_path, directory)
                anchor = relative_path.replace('/', '-').replace('.', '-').replace('_', '-').lower()
                f.write(f"- [{relative_path}](#{anchor})\n")
            f.write("\n---\n\n")
            
            # Conteúdo dos arquivos
            for i, file_path in enumerate(code_files, 1):
                relative_path = os.path.relpath(file_path, directory)
                language = self.get_language_from_extension(file_path)
                
                print(f"Processando ({i}/{len(code_files)}): {relative_path}")
                
                # Cabeçalho do arquivo
                f.write(f"## {relative_path}\n\n")
                f.write(f"**Caminho:** `{relative_path}`\n")
                f.write(f"**Linguagem:** {language}\n\n")
                
                # Conteúdo do arquivo
                content = self.get_file_content(file_path)
                f.write(f"```{language}\n")
                f.write(content)
                if not content.endswith('\n'):
                    f.write('\n')
                f.write("```\n\n")
                f.write("---\n\n")
        
        print(f"Arquivo Markdown gerado: {output_file}")
        print(f"Tamanho do arquivo: {os.path.getsize(output_file):,} bytes")

def main():
    parser = argparse.ArgumentParser(
        description="Converte todo o código fonte de um repositório para um arquivo Markdown único",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s ./meu_projeto -o codigo_completo.md
  %(prog)s ./meu_projeto -o codigo_completo.md -x "test_.*\.py"
  %(prog)s ./meu_projeto -o codigo_completo.md -x "test_.*\.py|.*\.pyc|temp/.*"
        """
    )
    
    parser.add_argument(
        'directory',
        help='Diretório do repositório a ser convertido'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Arquivo de saída (.md)'
    )
    
    parser.add_argument(
        '-x', '--exclude',
        action='append',
        help='Padrão regex para ignorar arquivos (pode ser usado múltiplas vezes)'
    )
    
    args = parser.parse_args()
    
    # Valida o diretório
    if not os.path.isdir(args.directory):
        print(f"Erro: Diretório '{args.directory}' não encontrado!")
        return 1
    
    # Valida o arquivo de saída
    if not args.output.endswith('.md'):
        print("Aviso: Arquivo de saída não tem extensão .md")
    
    # Cria o diretório de saída se não existir
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ignore_patterns = []
    if args.exclude:
        for pattern in args.exclude:
            ignore_patterns.extend(pattern.split('|'))
    
    converter = RepoToMarkdown(ignore_patterns)
    
    try:
        converter.generate_markdown(args.directory, args.output)
        print("Conversão concluída com sucesso!")
        return 0
    except Exception as e:
        print(f"Erro durante a conversão: {e}")
        return 1

if __name__ == "__main__":
    exit(main())