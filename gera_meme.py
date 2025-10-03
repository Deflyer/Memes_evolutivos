import pygame

def show_image_and_play_audio(image_path, audio_path):
    pygame.init()
    image = pygame.image.load(image_path)
    screen = pygame.display.set_mode(image.get_size())
    pygame.display.set_caption("Meme Player")

    # Carregar áudio
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    nota = ""  # armazena os dígitos que o usuário digitar
    running = True
    while running:
        screen.blit(image, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Captura teclas
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter finaliza nota
                    running = False
                elif event.key == pygame.K_BACKSPACE:  # apagar último dígito
                    nota = nota[:-1]
                elif event.unicode.isdigit():  # só aceita números
                    nota += event.unicode

        # Se o áudio terminar sem nota, também encerra
        if not pygame.mixer.music.get_busy():
            running = False

    pygame.quit()
    return nota if nota != "" else None


def avaliar_meme(image_path, audio_path):
    nota = show_image_and_play_audio(image_path, audio_path)
    return nota


nota = avaliar_meme(
    "/home/art/projetos/evolutivos/imagens/figurinha_2.jpg",
    "/home/art/projetos/evolutivos/audios/1-2-3-4-flamengo.mp3"
)

if nota:
    print(f"Você deu nota {nota} para o meme.")
else:
    print("Você não deu nota para o meme.")
