
# Resumo – GitHub Copilot, Educação, Modelos e Limitações (2026)

## 1. Planos do GitHub Copilot (com equivalência educacional)

| Plano | Custo | Público | Equivalência | Principais Capacidades | Limitações Principais |
|------|-------|--------|--------------|------------------------|-----------------------|
| Copilot Free | Gratuito | Usuário geral | – | Autocomplete básico, Chat limitado | Baixa cota mensal |
| Copilot Student | Gratuito | Estudantes verificados | Parcial do Pro | Autocomplete ilimitado, Chat em modo automático | Sem escolha manual de modelos premium |
| **Copilot Pro (Education)** | **Gratuito** | **Professores verificados** | **Copilot Pro pago** | Todas as funções Pro, acesso a modelos premium | Cota mensal de requests premium |
| Copilot Pro | Pago (US$10/mês) | Usuário individual | – | Igual ao Pro Educacional | Igual ao educacional |
| Copilot Pro+ | Pago (US$39/mês) | Usuário avançado | – | Mais modelos, maior cota premium | Custo elevado |

---

## 2. Aspectos importantes do plano educacional (fora da tabela)

- O plano **Copilot Pro Educacional (Professor)** é funcionalmente idêntico ao Copilot Pro pago.
- Não exige cartão de crédito após verificação.
- A verificação **expira** e precisa ser renovada periodicamente.
- O plano educacional prioriza ensino e pesquisa, mas **não remove limites de quota**.

---

## 3. GitHub Copilot × Microsoft Copilot (comparativo)

| Característica | GitHub Copilot | Microsoft Copilot |
|---------------|---------------|------------------|
| Foco | Programação | Produtividade geral |
| Ambiente | VS Code, IDEs | Web, Word, Excel, Windows |
| Conta usada | GitHub | Microsoft |
| Modelos | OpenAI, Anthropic, Google | Principalmente OpenAI |
| Código | ✅ | ❌ (limitado) |
| Imagens | ❌ | ✅ (web) |

### Complemento
- Copilot GitHub é um **assistente de desenvolvimento**.
- Microsoft Copilot é um **assistente de produtividade e pesquisa**.
- Eles **não compartilham quotas nem autenticação**.

---

## 4. Uso de outros modelos e conceito de requests premium

- Modelos avançados (Claude, Gemini, GPT avançados) consomem **requests premium**.
- Requests premium são uma **cota mensal**, não diária.
- Reset ocorre no **dia 1º de cada mês (UTC)**.

### Cotas típicas
- Student: ~50/mês
- Pro / Pro Educacional: ~300/mês
- Pro+: ~1500/mês

---

## 5. Consumo de requests premium por modelo

| Modelo | Tipo | Multiplicador |
|------|------|---------------|
| GPT-4.1 / GPT-5 mini | Incluído | 0× (não consome) |
| Claude Sonnet | Premium | 1× |
| Claude Sonnet (reasoning) | Premium | 1.25× |
| Claude Opus | Premium | ~10× |

### Explicação
- Um *multiplicador* indica quantos requests são consumidos por interação.
- Modelos como Claude Opus esgotam a cota rapidamente.

---

## 6. Limitações do Claude (via Copilot)

- Não é o Claude “nativo” da Anthropic.
- Não há acesso a ferramentas próprias da Anthropic.
- Contexto limitado pelo Copilot.
- Alto consumo de quota em tarefas longas.

---

## 7. Professor × Estudante

| Recurso | Professor | Estudante |
|-------|-----------|-----------|
| Copilot gratuito | ✅ | ✅ |
| Escolha manual de modelo | ✅ | ❌ |
| Claude Opus | ✅ | ❌ |
| Cota premium alta | ✅ | ❌ |
| Ideal para | Ensino & pesquisa | Aprendizado |

---

## 8. Como criar e verificar conta GitHub (passo a passo)

### Criar conta GitHub
1. Acesse https://github.com
2. Clique em **Sign up**
3. Crie conta com qualquer e-mail

### Verificação para Professor
1. Acesse https://education.github.com/teachers
2. Solicite verificação
3. Use e-mail institucional ou comprovante
4. Após aprovação, ative Copilot

### Verificação para Estudante
1. Acesse https://education.github.com/pack
2. Solicite GitHub Student Developer Pack
3. Use e-mail acadêmico ou comprovante
4. Copilot Student será ativado automaticamente

---

## 9. Outras limitações importantes

- Copilot **não gera imagens** dentro do VS Code.
- Não substitui revisão humana em código científico.
- Atingir a cota força fallback automático de modelo.
- Uso intensivo em aulas pode exigir planejamento de quota.

---

**Este documento pode ser livremente compartilhado com colegas para fins acadêmicos.**
