import pandas as pd
import numpy as np
from gera_meme import avaliar_meme
from scipy.spatial.distance import cdist
import random
tam_populacao = 5
num_geracoes = 5
taxa_mutacao = 0.1

# Carregar embeddings
df_imagens = pd.read_csv("image_embeddings.csv")
df_audios = pd.read_csv("audio_embeddings.csv")

# Converter embeddings para arrays numpy
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
    print(len(parents[0][2]))
    print(type(parents[0][2][0]))
    print((parents[0][2][1]))
    print(len(parents[1][2]))
    print("abacate")
    # Cruzamento de genes, ou a média, ou partes aleatórias dos genes dos pais
    if(random.random() < 0.5):
        img_mean = np.mean([parents[0][2], parents[1][2]], axis=0)
        print(len(img_mean))
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
    
    print(f"Imagem selecionada: {img_idx}")
    print(f"Audio selecionado: {aud_idx}")
    return img_idx, aud_idx, img_mean, aud_mean

populacao = [criar_meme_aleatorio() for _ in range(tam_populacao)]

for geracao in range(num_geracoes):
    print(f"\n=== Geração {geracao+1} ===")
    avaliacoes = []

    for idx, (img_idx, aud_idx, img_emb, aud_emb) in enumerate(populacao):
        print(aud_idx)
        print(img_idx)
        print((img_emb[0]))
        print(type(img_emb[0]))
        img_file = df_imagens.iloc[img_idx]['filename']
        aud_file = df_audios.iloc[aud_idx]['filename']
        print(f"Meme {idx+1} com img {img_file} e audio {aud_file}")
        nota = avaliar_meme("./imagens/" + img_file, "./audios/" +aud_file)
        avaliacoes.append((nota, (img_idx, aud_idx, img_emb, aud_emb)))

    avaliacoes.sort(key=lambda x: float(x[0]), reverse=True)
    top = [ind for __, ind in avaliacoes[:tam_populacao // 2]]

    nova_pop = []
    while len(nova_pop) < tam_populacao:
        pais = np.random.choice(len(top), 2, replace=False)
        print(f"pais da cria  {pais}")
        filho = cruzar_memes([top[pais[0]], top[pais[1]]])
        nova_pop.append(filho)

    populacao = nova_pop

print("\nAlgoritmo finalizado.")
