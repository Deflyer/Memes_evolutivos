"""
Algoritmo Evolutivo para Geração de Memes
==========================================

Este módulo implementa o algoritmo evolutivo que combina imagens e áudios para criar memes.
O algoritmo utiliza embeddings (representações numéricas) de imagens e áudios, aplicando
operações genéticas (mutação e crossover) para evoluir combinações baseadas nas avaliações
do usuário.

Funcionalidades principais:
- Criação de população inicial de memes aleatórios
- Mutação de embeddings (imagem e áudio) com diferentes estratégias
- Crossover entre memes para gerar novos indivíduos
- Seleção baseada em fitness (notas do usuário)
- Geração de novas populações com estratégia elitista
- Ajuste adaptativo da taxa de mutação baseado em estagnação
"""

import pandas as pd
import numpy as np
from gera_meme import avaliar_meme, show_results_screen
from scipy.spatial.distance import cdist
import random
tam_populacao = 10
num_geracoes = 100
incremento_mutacao = 0.02
taxa_mutacao_inicial = 0.2
taxa_mutacao_maxima = 0.5
taxa_mutacao = taxa_mutacao_inicial
limite_geracoes_estagnacao = 3
extincao = 0.1
melhores = []
df_imagens = pd.read_csv("image_embeddings.csv")
df_audios = pd.read_csv("audio_embeddings.csv")

emb_imagens = df_imagens.drop(columns=['filename']).values
emb_audios = df_audios.drop(columns=['filename']).values

# Estatísticas dos embeddings (baseadas na análise dos dados)
EMBEDDING_STATS = {
    'audio': {
        'std': 0.04,
        'min': -0.15,
        'max': 0.15,
        'p1': -0.12,
        'p99': 0.12
    },
    'image': {
        'std': 0.6,
        'min': -9.0,
        'max': 4.0,
        'p1': -2.5,
        'p99': 2.5
    }
}

def criar_meme_aleatorio():
    img_idx = np.random.randint(len(df_imagens))
    img_embedding = df_imagens.filter(like='dim_').iloc[img_idx].astype(float).values
    aud_idx = np.random.randint(len(df_audios))
    aud_embedding = df_audios.filter(like='dim_').iloc[aud_idx].astype(float).values
    return img_idx, aud_idx, img_embedding, aud_embedding

def mutate(embedding, embedding_type):
    if random.random() < taxa_mutacao:
        # Fazer uma cópia para não modificar o original
        embedding_mutado = embedding.copy()
        
        # Obter estatísticas do tipo de embedding
        stats = EMBEDDING_STATS[embedding_type]
        
        # Número de elementos a serem mutados (entre 1 e 5% do tamanho do embedding)
        num_mutacoes = random.randint(1, max(1, len(embedding) // 20))
        
        for _ in range(num_mutacoes):
            # Escolher um índice aleatório para mutar
            idx = random.randint(0, len(embedding) - 1)
            
            # Permitir que mais de um tipo de mutação ocorra ao mesmo tempo
            tipos_mutacao = ['substituir', 'multiplicar', 'somar']
            # Escolhe aleatoriamente quais mutações aplicar (pelo menos uma)
            mutacoes_a_aplicar = [tipo for tipo in tipos_mutacao if random.random() < taxa_mutacao/3]
            if not mutacoes_a_aplicar:
                mutacoes_a_aplicar = [random.choice(tipos_mutacao)]
                
            for tipo_mutacao in mutacoes_a_aplicar:
                if tipo_mutacao == 'substituir':
                    embedding_mutado[idx] = random.uniform(stats['min'], stats['max'])
                elif tipo_mutacao == 'multiplicar':
                    fator = random.uniform(0.95, 1.05)
                    embedding_mutado[idx] *= fator
                elif tipo_mutacao == 'somar':
                    incremento = random.uniform(-stats['std']*0.05, stats['std']*0.05)
                    embedding_mutado[idx] += incremento
        
        return embedding_mutado
    
    return embedding

def cruzar_memes(parents):
    # Cruzamento de genes, ou a média, ou partes aleatórias dos genes dos pais
    if(random.random() < 0.5):
        img_mean = np.mean([parents[0][2], parents[1][2]], axis=0)
        aud_mean = np.mean([parents[0][3], parents[1][3]], axis=0)
    else:
        img_mean = np.array([random.choice([a, b]) for a, b in zip(parents[0][2], parents[1][2])])
        aud_mean = np.array([random.choice([a, b]) for a, b in zip(parents[0][3], parents[1][3])])
    
    # Aplicar mutações seguras com tipos específicos
    img_mean = mutate(img_mean, embedding_type='image')
    aud_mean = mutate(aud_mean, embedding_type='audio')

    img_dists = cdist([img_mean], emb_imagens, metric='euclidean')[0]
    sorted_indices = np.argsort(img_dists)
    if random.random() < taxa_mutacao and len(sorted_indices) > 1:  
        img_idx = sorted_indices[1]
    else:
        img_idx = sorted_indices[0]
    aud_dists = cdist([aud_mean], emb_audios, metric='euclidean')[0]
    sorted_indices = np.argsort(aud_dists)
    if random.random() < taxa_mutacao and len(sorted_indices) > 1:
        aud_idx = sorted_indices[1]
    else:
        aud_idx = sorted_indices[0]
    
    return img_idx, aud_idx, img_mean, aud_mean


def gerar_nova_populacao(avaliacoes):
    avaliacoes.sort(key=lambda x: x[0], reverse=True)
    melhores.append(avaliacoes[0])
    indices = list(range(len(avaliacoes)))
    notas = np.array([a[0] for a in avaliacoes])
    dados_pais = [(a[1], a[2], a[3], a[4]) for a in avaliacoes]
    pesos = (notas + 1e-8) / np.sum(notas + 1e-8)

    top1_indice = indices[0]
    restantes_indices = indices[1:]
    pesos_restantes = pesos[1:]
    pesos_restantes = pesos_restantes / np.sum(pesos_restantes)

    nova_populacao = []
    casais_usados = set()

    # Primeira metade: Top 1 se casa com os outros
    while len(nova_populacao) < tam_populacao // 2:
        parceiro_indice = np.random.choice(restantes_indices, p=pesos_restantes)
        casal = tuple(sorted((top1_indice, parceiro_indice)))

        if casal not in casais_usados:
            casais_usados.add(casal)
            
            pai1 = dados_pais[top1_indice]
            pai2 = dados_pais[parceiro_indice]
            
            filho = cruzar_memes([pai1, pai2])
            nova_populacao.append(filho)

    # Segunda metade: Casais aleatórios entre os restantes
    while len(nova_populacao) < tam_populacao:
        # Garante que há pelo menos dois indivíduos para formar um casal
        if len(restantes_indices) < 2:
            break

        # Seleciona dois pais de forma aleatória e sem repetição entre os restantes
        try:
            pais_indices = np.random.choice(restantes_indices, 2, replace=False, p=pesos_restantes)
        except ValueError:
            # Se a soma dos pesos for 0 faz aleatório uniforme
            pais_indices = np.random.choice(restantes_indices, 2, replace=False)
            
        casal = tuple(sorted(pais_indices))
        
        if casal not in casais_usados:
            casais_usados.add(casal)
            
            pai1 = dados_pais[pais_indices[0]]
            pai2 = dados_pais[pais_indices[1]]
            
            filho = cruzar_memes([pai1, pai2])
            nova_populacao.append(filho)
            
    return nova_populacao

def obter_top3_memes(dicionario_notas):
    """Retorna os top 3 memes com suas informações"""
    if not dicionario_notas:
        return []
    
    # Criar lista de memes com suas notas
    memes_com_notas = []
    for (img_idx, aud_idx), nota in dicionario_notas.items():
        # Ignorar apenas memes pulados (None)
        if nota is not None:
            try:
                img_file = df_imagens.iloc[img_idx]['filename']
                aud_file = df_audios.iloc[aud_idx]['filename']
                memes_com_notas.append({
                    'nota': nota,
                    'img_idx': img_idx,
                    'aud_idx': aud_idx,
                    'img_file': img_file,
                    'aud_file': aud_file
                })
            except (IndexError, KeyError):
                # Se houver erro ao acessar os dados, pular este meme
                continue
    
    # Ordenar por nota (maior primeiro) e pegar top 3
    memes_com_notas.sort(key=lambda x: x['nota'], reverse=True)
    return memes_com_notas[:3]

if __name__ == "__main__":
    populacao = [criar_meme_aleatorio() for _ in range(tam_populacao)]

    dicionario_notas = {}
    fitness_history = []
    geracoes_sem_melhora = 0
    melhor_fitness_global = -1.0
    encerrar_programa = False
    
    for geracao in range(num_geracoes):
        if encerrar_programa:
            print("Programa encerrado pelo usuário.")
            break
            
        print(f"\n=== Geração {geracao + 1}/{num_geracoes} ===")
        quant_repet = 0
        avaliacoes = []
        notas = []
        
        # Obter top 3 memes para mostrar na interface
        top3_memes = obter_top3_memes(dicionario_notas)
        
        for idx, (img_idx, aud_idx, img_emb, aud_emb) in enumerate(populacao):
            if encerrar_programa:
                break
                
            meme_id = (img_idx, aud_idx)

            if meme_id in dicionario_notas:
                nota = dicionario_notas[meme_id]
                quant_repet +=1
                print(f"Meme {idx+1} (cacheado) - Nota: {nota}")
            else:
                img_file = df_imagens.iloc[img_idx]['filename']
                aud_file = df_audios.iloc[aud_idx]['filename']
                print(f"Meme {idx+1} com img {img_file} e audio {aud_file}")
                
                # Atualizar top 3 antes de mostrar
                top3_memes = obter_top3_memes(dicionario_notas)
                
                nota, encerrar = avaliar_meme("./imagens/" + img_file, "./audios/" + aud_file, top3_memes)
                
                if encerrar:
                    if encerrar == "show_results":
                        # Calcular fitness parcial da geração atual antes de mostrar resultados
                        if notas and len(notas) > 0:
                            notas_parciais = np.array(notas, dtype=float)
                            fitness_parcial = notas_parciais.mean()
                            fitness_history.append(fitness_parcial)
                        
                        # Mostrar tela de resultados com gráfico de fitness
                        top3_final = obter_top3_memes(dicionario_notas)
                        encerrar_programa = show_results_screen(top3_final, fitness_history)
                    else:
                        encerrar_programa = True
                    break
                
                if nota is not None:
                    dicionario_notas[meme_id] = nota
                    print(f"Nota atribuída: {nota}")
                else:
                    print("Meme pulado (sem nota)")
                    # Marcar como pulado para não mostrar novamente
                    dicionario_notas[meme_id] = None
                    # Atribuir nota mínima para manter a população estável
                    nota = 0.0
                    dicionario_notas[meme_id] = 0.0
            
            # Adicionar à avaliação (mesmo que seja 0.0 se foi pulado)
            if nota is not None:
                notas.append(nota)
                avaliacoes.append([nota, img_idx, aud_idx, img_emb, aud_emb])
        
        if encerrar_programa:
            break
        
        if not avaliacoes:
            print("Nenhuma avaliação válida nesta geração. Pulando...")
            continue
            
        notas_np_array = np.array(notas, dtype=float) 
        fitness_atual = notas_np_array.mean()
        fitness_history.append(fitness_atual)
        
        print(f"Fitness médio da geração: {fitness_atual:.2f}")

        populacao = gerar_nova_populacao(avaliacoes)

        if fitness_atual <= melhor_fitness_global + 0.01:
            geracoes_sem_melhora += 1
        else:
            melhor_fitness_global = fitness_atual
            geracoes_sem_melhora = 0
        
        # Se a estabilização for detectada por X gerações consecutivas
        if geracoes_sem_melhora >= limite_geracoes_estagnacao or quant_repet >= tam_populacao/2:
            taxa_mutacao += incremento_mutacao * max(geracoes_sem_melhora,1)
            taxa_mutacao = min(taxa_mutacao, taxa_mutacao_maxima)
            geracoes_sem_melhora = 0
            print(f"Taxa de mutação ajustada para: {taxa_mutacao:.2f}")
    
    # Mostrar top 3 final (se não foi mostrado na tela de resultados)
    if not encerrar_programa:
        print("\n=== TOP 3 MEMES FINAIS ===")
        top3_final = obter_top3_memes(dicionario_notas)
        for i, meme in enumerate(top3_final):
            print(f"{i+1}. {meme['img_file']} + {meme['aud_file']} - Nota: {meme['nota']:.2f}")
        
        # Mostrar gráfico de fitness no final se não foi mostrado
        if fitness_history:
            print("\n=== HISTÓRICO DE FITNESS ===")
            print(f"Melhor fitness: {max(fitness_history):.2f}")
            print(f"Fitness médio: {sum(fitness_history)/len(fitness_history):.2f}")
            print(f"Pior fitness: {min(fitness_history):.2f}")