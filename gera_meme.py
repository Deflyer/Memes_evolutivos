import pygame

def _scale_to_fit(surface, target_size):
    tw, th = target_size
    sw, sh = surface.get_size()
    scale = min(tw / sw, th / sh)
    new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
    scaled = pygame.transform.smoothscale(surface, new_size)
    x = (tw - new_size[0]) // 2
    y = (th - new_size[1]) // 2
    return scaled, (x, y)

def show_image_and_play_audio(image_path, audio_path, target_size=(640, 640)):
    pygame.init()
    # A linha abaixo deve vir ANTES de carregar e converter a imagem
    screen = pygame.display.set_mode(target_size)
    pygame.display.set_caption("Meme Player")

    # Agora você pode carregar a imagem e convertê-la
    image = pygame.image.load(image_path).convert_alpha()

    # Carregar áudio
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    nota = ""
    running = True
    while running:
        screen.fill((0, 0, 0))
        scaled, pos = _scale_to_fit(image, target_size)
        screen.blit(scaled, pos)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter finaliza nota
                    running = False
                elif event.key == pygame.K_BACKSPACE:  # apagar último dígito
                    nota = nota[:-1]
                elif event.unicode.isdigit():  # só aceita números
                    nota += event.unicode

    pygame.quit()
    return float(nota) if nota != "" else None

def avaliar_meme(image_path, audio_path, target_size=(640, 640)):
    nota = show_image_and_play_audio(image_path, audio_path, target_size)
    return nota