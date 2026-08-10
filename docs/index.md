---
icon: material/office-building
---

# Python Build123d para Arquitetos e Engenheiros

Material de apoio para modelagem paramétrica com Python e Build123d, com foco em aplicações para arquitetura e engenharia.

## Objetivo

Este repositório reúne exemplos práticos para:

- criação de geometrias 2D e 3D
- modelagem por operações paramétricas
- exercícios com múltiplos pavimentos
- exportação e interoperabilidade de arquivos

## Pré-requisitos

- Python 3.12 ou superior
- Ambiente virtual Python (`.venv`)
- Dependências do projeto instaladas com `uv sync --dev`
- MkDocs Material e plugin `mkdocs-jupyter` para renderização dos notebooks

Comandos recomendados:

```bash
uv sync --dev
mkdocs serve -f mkdocs.yml
```

## Trilha sugerida

1. Comece por Modelagem no menu Google Colab.
2. Avance para Primitivas e Treliças.
3. Faça os exercícios de múltiplos pavimentos.
4. Finalize com os exemplos de exportação IFC.

## Conteúdo disponível

- Notebooks de modelagem em [Google Colab](tuto_colab_build/build123d_basic_gc.ipynb)
- Conceitos de apoio em [Apêndice](conceitos/matrizes_de_transformacao.md)
- Arquivos para download em [Downloads](down_files/down_files.md)

## Como executar localmente

```bash
mkdocs serve -f mkdocs.yml
```

Depois abra a URL exibida no terminal para navegar pela documentação.
