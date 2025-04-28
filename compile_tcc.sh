#!/bin/bash

# Instalar dependências do LaTeX (se necessário)
# sudo apt-get install texlive-full

# Compilar o documento
pdflatex tcc.tex
bibtex tcc
pdflatex tcc.tex
pdflatex tcc.tex

# Limpar arquivos temporários
rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot

echo "Compilação concluída. O arquivo tcc.pdf foi gerado." 