# Memes Evolutivos 

Sistema de geração evolutiva de memes que combina imagens e áudios usando algoritmos genéticos. O sistema aprende com as avaliações do usuário para evoluir e criar memes cada vez melhores. Projeto da Disciplina SSC0713 - Sistemas Evolutivos e Aplicados à Robótica. 

Participantes do grupo:
- Artur De Vlieger Lima - 13671574
- Pedro Augusto Monteiro Delgado - 13672766

[Assista ao vídeo de demonstração do projeto!](https://youtu.be/sqUDYaDMBGc)

## Sobre o Projeto

Este projeto implementa um algoritmo evolutivo que utiliza **embeddings** (representações numéricas) de imagens e áudios para criar combinações de memes. O algoritmo evolui baseado nas avaliações do usuário, aplicando conceitos de algoritmos genéticos como mutação, crossover e seleção natural.

### Conceito Principal

Cada meme é representado por um par de embeddings:
- **Embedding de Imagem**: Representação numérica das características visuais
- **Embedding de Áudio**: Representação numérica das características sonoras

O algoritmo evolui esses embeddings através de:
1. **Mutação**: Modifica aleatoriamente valores dos embeddings
2. **Crossover**: Combina características de dois memes "pais" para criar um "filho"
3. **Seleção**: Memes com melhores avaliações têm maior chance de se reproduzir

## Como Funciona

### 1. Inicialização
- O sistema carrega embeddings pré-calculados de imagens e áudios
- Cria uma população inicial de memes aleatórios (combinações imagem + áudio)

### 2. Ciclo Evolutivo

Para cada geração:

1. **Avaliação**: O usuário avalia cada meme de 1 a 10
2. **Cálculo de Fitness**: A nota do usuário é o fitness do meme
3. **Seleção**: Os melhores memes são selecionados para reprodução
4. **Reprodução**: 
   - **Crossover**: Combina embeddings de dois memes pais
   - **Mutação**: Aplica mutações aleatórias nos embeddings resultantes
5. **Mapeamento**: Encontra a imagem e áudio reais mais próximos dos embeddings gerados
6. **Nova Geração**: Cria nova população com os memes gerados

### 3. Estratégias Evolutivas

#### Mutação
- **Substituição**: Substitui um valor do embedding por um aleatório
- **Multiplicação**: Multiplica um valor por um fator (0.95 a 1.05)
- **Adição**: Adiciona um incremento pequeno ao valor

A taxa de mutação é ajustada dinamicamente:
- Aumenta quando o algoritmo detecta estagnação
- Limita-se a um máximo para evitar mutações excessivas

#### Crossover

Seleciona uma das duas formas abaixo
- **Média**: Calcula a média dos embeddings dos pais
- **Seleção Aleatória**: Escolhe aleatoriamente valores de cada pai

#### Seleção
- **Estratégia Elitista**: O melhor meme sempre se reproduz, gerando metade da população de filhos  com o restante da população
- **Seleção Proporcional**: Outros memes têm chance de reprodução proporcional à sua nota em relação ao total

## Estrutura do Projeto

```
Memes_evolutivos-master/
├── evolutivo.py          # Algoritmo evolutivo principal
├── gera_meme.py          # Interface gráfica (Pygame)
├── images.py             # Script para coletar imagens (opcional)
├── sons.py               # Script para coletar sons (opcional)
├── image_embeddings.csv  # Embeddings das imagens
├── audio_embeddings.csv  # Embeddings dos áudios
├── imagens/              # Pasta com imagens
└── audios/               # Pasta com áudios
```

## Como Usar

### Pré-requisitos

```bash
pip install pygame pandas numpy scipy
```

### Execução

```bash
python evolutivo.py
```

### Interface do Usuário

1. **Avaliação de Memes**:
   - Observe a imagem e ouça o áudio
   - Classifique o meme de 1 a 10 usando os botões, recomenda-se começar com notas baixas e só dar uma nota maior quando um meme superar sua maior nota até agora
   - Use "Pular" para não avaliar um meme
   - Veja o Top 3 memes atualizados em tempo real

2. **Tela de Resultados**:
   - Após clicar em "Encerrar", visualize os Top 3 memes finais
   - Clique em "Ver Gráfico" para ver a evolução do fitness
   - Clique em "Ver #N" para visualizar um meme em tela cheia

3. **Gráfico de Evolução**:
   - Mostra a evolução da nota média ao longo das gerações
   - Exibe estatísticas: melhor, média e pior fitness
   - Acessível via botão "Ver Gráfico" na tela de resultados

## Detalhes Técnicos

### Embeddings

Os embeddings são representações vetoriais de alta dimensão que capturam características semânticas:
- **Imagens**: Embeddings extraídos de modelos de deep learning (CLIP)
- **Áudios**: Embeddings extraídos de modelos de deep learning (CLAP)

O código para extração de embeddings encontra-se no colab abaixo

[link do colab](https://colab.research.google.com/drive/1m1YuceUPp6aGf2UE9lVKAijuvFT6Wyb2?usp=sharing)

### Operações Genéticas

#### Mutação de Embeddings
```python
# Tipos de mutação aplicados:
- Substituir: embedding[i] = valor_aleatório
- Multiplicar: embedding[i] *= fator (0.95-1.05)
- Somar: embedding[i] += incremento_pequeno
```

#### Crossover
```python
# Estratégia 1: Média
filho = (pai1 + pai2) / 2

# Estratégia 2: Seleção aleatória
filho[i] = escolha_aleatória(pai1[i], pai2[i])
```

#### Mapeamento para Arquivos Reais
Após gerar novos embeddings, o sistema encontra os arquivos reais mais próximos usando distância euclidiana:
```python
distância = ||embedding_gerado - embedding_arquivo||
arquivo_escolhido = arquivo_com_menor_distância
```
Aqui, mutação pode causar a escolha do segundo ou terceiro amis próximo ao invés do primeiro


### Parâmetros do Algoritmo

- **Tamanho da População**: 10 memes por geração
- **Número de Gerações**: 100 (ou até o usuário encerrar)
- **Taxa de Mutação Inicial**: 0.2 (20%)
- **Taxa de Mutação Máxima**: 0.5 (50%)
- **Limite de Estagnação**: 3 gerações sem melhoria

## Visualizações

### Tabela Top 3
- Exibida durante a classificação
- Atualizada em tempo real
- Mostra posição, miniatura, nome do áudio e nota

### Gráfico de Fitness
- Linha temporal da evolução
- Eixo X: Gerações
- Eixo Y: Nota média
- Estatísticas: melhor, média e pior fitness

## Scripts Auxiliares

### `images.py`
Script para coletar imagens do Pinterest:
```bash
python images.py
```
- Busca imagens por termo
- Faz scroll automático
- Baixa imagens em alta resolução

### `sons.py`
Script para coletar sons do Myinstants:
```bash
python sons.py
```
- Navega no site Myinstants
- Coleta URLs de sons
- Baixa arquivos MP3 automaticamente

**Nota**: Estes scripts são opcionais e usados apenas para criar o dataset inicial ou adicionar mais sons. Ainda é preciso gerar os embeddings com o código presente n ogoogle colab linkado acima.








