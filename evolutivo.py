import pandas as pd
import numpy as np
from gera_meme import avaliar_meme
from scipy.spatial.distance import cdist

tam_populacao = 5
num_geracoes = 5

# Carregar embeddings
df_imagens = pd.read_csv("image_embeddings.csv")
df_audios = pd.read_csv("audio_embeddings.csv")

# Converter embeddings para arrays numpy
emb_imagens = df_imagens.drop(columns=['filename']).values
emb_audios = df_audios.drop(columns=['filename']).values

def criar_meme_aleatorio():
    img_idx = np.random.randint(len(df_imagens))
    aud_idx = np.random.randint(len(df_audios))
    return img_idx, aud_idx

def cruzar_memes(parents):
    img_mean = np.mean([emb_imagens[p[0]] for p in parents], axis=0)
    aud_mean = np.mean([emb_audios[p[1]] for p in parents], axis=0)

    img_idx = np.argmin(cdist([img_mean], emb_imagens, metric='euclidean'))
    aud_idx = np.argmin(cdist([aud_mean], emb_audios, metric='euclidean'))
    print(img_idx)
    print(aud_idx)
    return img_idx, aud_idx


populacao = [criar_meme_aleatorio() for _ in range(tam_populacao)]

for geracao in range(num_geracoes):
    print(f"\n=== Geração {geracao+1} ===")
    avaliacoes = []

    for idx, (img_idx, aud_idx) in enumerate(populacao):
        print(aud_idx)
        print(img_idx)
        img_file = df_imagens.iloc[img_idx]['filename']
        aud_file = df_audios.iloc[aud_idx]['filename']
        print(f"Meme {idx+1} com img {img_file} e audio {aud_file}")
        nota = avaliar_meme("./imagens/" + img_file, "./audios/" +aud_file)
        avaliacoes.append((nota, (img_idx, aud_idx)))

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
