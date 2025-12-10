"""
Interface Gráfica e Geração de Memes
====================================

Este módulo implementa a interface gráfica do sistema de memes evolutivos usando Pygame.
Fornece uma interface visual para o usuário avaliar memes, visualizar o top 3, e acompanhar
a evolução do algoritmo através de gráficos de fitness.

Funcionalidades principais:
- Interface gráfica minimalista para avaliação de memes (notas 1-10)
- Exibição de imagens e reprodução de áudios
- Tabela dinâmica do top 3 memes
- Tela de resultados finais com visualização dos melhores memes
- Gráfico de evolução do fitness ao longo das gerações
- Modais de ajuda e visualização de gráficos
- Sistema de botões interativos com efeitos hover
"""

import pygame
import os
import math

# Paleta de cores minimalista
BG_COLOR = (250, 250, 252)  # Fundo suave
CARD_COLOR = (255, 255, 255)  # Cards brancos
TEXT_PRIMARY = (30, 30, 30)  # Texto escuro
TEXT_SECONDARY = (120, 120, 120)  # Texto secundário
ACCENT_BLUE = (59, 130, 246)  # Azul moderno
ACCENT_BLUE_HOVER = (37, 99, 235)  # Azul hover
ACCENT_GREEN = (34, 197, 94)  # Verde sucesso
ACCENT_RED = (239, 68, 68)  # Vermelho
ACCENT_GRAY = (156, 163, 175)  # Cinza
BORDER_COLOR = (229, 231, 235)  # Borda suave
SHADOW_COLOR = (0, 0, 0, 30)  # Sombra suave

def _scale_to_fit(surface, target_size):
    tw, th = target_size
    sw, sh = surface.get_size()
    scale = min(tw / sw, th / sh)
    new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
    scaled = pygame.transform.smoothscale(surface, new_size)
    x = (tw - new_size[0]) // 2
    y = (th - new_size[1]) // 2
    return scaled, (x, y)

def draw_rounded_rect(surface, color, rect, radius):
    """Desenha um retângulo com bordas arredondadas"""
    x, y, w, h = rect
    
    # Verificar se pygame suporta border_radius
    try:
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    except TypeError:
        # Fallback para pygame antigo
        pygame.draw.rect(surface, color, rect)
        # Desenhar círculos nos cantos para simular bordas arredondadas
        for corner_x, corner_y in [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]:
            pygame.draw.circle(surface, color, (corner_x, corner_y), radius)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, radius=12, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.radius = radius
        self.icon = icon
        # Usar fonte diferente de Arial e menor
        try:
            # Tentar Calibri primeiro, depois Verdana, depois padrão
            self.font = pygame.font.SysFont("Calibri", 20, bold=True)
        except:
            try:
                self.font = pygame.font.SysFont("Verdana", 20, bold=True)
            except:
                try:
                    self.font = pygame.font.SysFont("Tahoma", 20, bold=True)
                except:
                    self.font = pygame.font.Font(None, 20)
        
    def draw(self, screen):
        # Desenhar sombra suave
        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, 
                                 self.rect.width, self.rect.height)
        try:
            pygame.draw.rect(screen, (0, 0, 0, 20), shadow_rect, border_radius=self.radius)
        except:
            pass
        
        # Desenhar botão com bordas arredondadas
        draw_rounded_rect(screen, self.current_color, self.rect, self.radius)
        
        # Desenhar borda sutil
        try:
            pygame.draw.rect(screen, BORDER_COLOR, self.rect, 1, border_radius=self.radius)
        except:
            pygame.draw.rect(screen, BORDER_COLOR, self.rect, 1)
        
        # Desenhar texto ou ícone
        if self.icon:
            # Botão circular para ícone
            try:
                icon_font = pygame.font.SysFont("Calibri", 22, bold=True)
            except:
                try:
                    icon_font = pygame.font.SysFont("Verdana", 22, bold=True)
                except:
                    icon_font = pygame.font.Font(None, 22)
            icon_surface = icon_font.render(self.icon, True, TEXT_PRIMARY)
            icon_rect = icon_surface.get_rect(center=self.rect.center)
            screen.blit(icon_surface, icon_rect)
        else:
            # Se o texto for muito curto (como "?"), usar fonte ligeiramente maior
            if len(self.text) <= 2:
                try:
                    text_font = pygame.font.SysFont("Calibri", 22, bold=True)
                except:
                    try:
                        text_font = pygame.font.SysFont("Verdana", 22, bold=True)
                    except:
                        text_font = pygame.font.Font(None, 22)
            else:
                text_font = self.font
            
            # Cor do texto baseada na cor do botão
            if self.current_color == CARD_COLOR:
                text_color = TEXT_PRIMARY
            else:
                text_color = (255, 255, 255)
            
            text_surface = text_font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
    
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)
    
    def handle_hover(self, pos):
        if self.is_hovered(pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def load_thumbnail(image_path, size=(80, 80)):
    """Carrega uma miniatura da imagem"""
    try:
        img = pygame.image.load(image_path)
        img = pygame.transform.smoothscale(img, size)
        return img
    except:
        # Retorna uma imagem padrão se não conseguir carregar
        default = pygame.Surface(size)
        default.fill(ACCENT_GRAY)
        return default

def draw_top3_table(screen, top3_memes, font, small_font, x, y, width, height):
    """Desenha uma tabela minimalista com os top 3 memes e miniaturas"""
    # Card principal com bordas arredondadas
    card_rect = pygame.Rect(x, y, width, height)
    draw_rounded_rect(screen, CARD_COLOR, card_rect, 16)
    try:
        pygame.draw.rect(screen, BORDER_COLOR, card_rect, 1, border_radius=16)
    except:
        pygame.draw.rect(screen, BORDER_COLOR, card_rect, 1)
    
    # Cabeçalho
    header_rect = pygame.Rect(x + 10, y + 10, width - 20, 35)
    try:
        header_font = pygame.font.SysFont("Calibri", 22, bold=True)
    except:
        try:
            header_font = pygame.font.SysFont("Verdana", 22, bold=True)
        except:
            header_font = pygame.font.Font(None, 22)
    header_text = header_font.render("Top 3 Memes", True, TEXT_PRIMARY)
    screen.blit(header_text, (x + 20, y + 15))
    
    # Linhas da tabela
    row_height = (height - 55) // 3
    thumbnail_size = 45  # Reduzido para caber na linha
    
    for i, meme_info in enumerate(top3_memes[:3]):
        row_y = y + 50 + i * row_height
        row_rect = pygame.Rect(x + 10, row_y, width - 20, row_height - 5)
        
        # Cor de fundo alternada
        if i % 2 == 0:
            draw_rounded_rect(screen, BG_COLOR, row_rect, 8)
        else:
            draw_rounded_rect(screen, CARD_COLOR, row_rect, 8)
        
        if meme_info:
            # Posição com símbolo (substituindo emojis)
            pos_symbols = ["1st", "2nd", "3rd"]
            pos_text = small_font.render(pos_symbols[i] if i < 3 else f"#{i+1}", True, TEXT_PRIMARY)
            screen.blit(pos_text, (x + 20, row_y + row_height//2 - 8))
            
            # Miniatura da imagem (menor para caber na linha)
            img_path = "./imagens/" + meme_info.get('img_file', '')
            thumbnail = load_thumbnail(img_path, (thumbnail_size, thumbnail_size))
            thumb_rect = pygame.Rect(x + 65, row_y + (row_height - thumbnail_size)//2, thumbnail_size, thumbnail_size)
            screen.blit(thumbnail, thumb_rect)
            try:
                pygame.draw.rect(screen, BORDER_COLOR, thumb_rect, 1, border_radius=4)
            except:
                pygame.draw.rect(screen, BORDER_COLOR, thumb_rect, 1)
            
            # Nome do arquivo de áudio (truncado, ajustado para o novo layout)
            filename = os.path.basename(meme_info.get('aud_file', 'N/A'))
            if len(filename) > 18:
                filename = filename[:15] + "..."
            file_text = small_font.render(filename, True, TEXT_PRIMARY)
            screen.blit(file_text, (x + 120, row_y + 8))
            
            # Nota com destaque (ajustado)
            nota = meme_info.get('nota', 0)
            nota_bg = pygame.Rect(x + width - 85, row_y + (row_height - 25)//2, 70, 25)
            draw_rounded_rect(screen, ACCENT_GREEN, nota_bg, 6)
            try:
                nota_font = pygame.font.SysFont("Calibri", 14, bold=True)
            except:
                try:
                    nota_font = pygame.font.SysFont("Verdana", 14, bold=True)
                except:
                    nota_font = pygame.font.Font(None, 14)
            nota_text = nota_font.render(f"{nota:.1f}", True, (255, 255, 255))
            nota_rect = nota_text.get_rect(center=nota_bg.center)
            screen.blit(nota_text, nota_rect)

def draw_help_modal(screen, width, height):
    """Desenha o modal de ajuda"""
    modal_width = 500
    modal_height = 400
    modal_x = (width - modal_width) // 2
    modal_y = (height - modal_height) // 2
    
    # Overlay escuro
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Card do modal
    modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
    draw_rounded_rect(screen, CARD_COLOR, modal_rect, 20)
    try:
        pygame.draw.rect(screen, BORDER_COLOR, modal_rect, 2, border_radius=20)
    except:
        pygame.draw.rect(screen, BORDER_COLOR, modal_rect, 2)
    
    # Título
    try:
        title_font = pygame.font.SysFont("Calibri", 28, bold=True)
    except:
        try:
            title_font = pygame.font.SysFont("Verdana", 28, bold=True)
        except:
            title_font = pygame.font.Font(None, 28)
    
    try:
        text_font = pygame.font.SysFont("Calibri", 16)
    except:
        try:
            text_font = pygame.font.SysFont("Verdana", 16)
        except:
            text_font = pygame.font.Font(None, 16)
    
    title = title_font.render("Como Jogar", True, TEXT_PRIMARY)
    screen.blit(title, (modal_x + 30, modal_y + 30))
    
    # Conteúdo
    instrucoes = [
        "1. Observe a imagem e ouça o áudio",
        "2. Classifique o meme de 1 a 10",
        "3. Use 'Pular' para não avaliar",
        "4. Veja o Top 3 memes no canto superior",
        "5. O algoritmo evolui os memes baseado",
        "   nas suas avaliações"
    ]
    
    y_offset = modal_y + 80
    for instrucao in instrucoes:
        text = text_font.render(instrucao, True, TEXT_SECONDARY)
        screen.blit(text, (modal_x + 30, y_offset))
        y_offset += 35
    
    # Botão fechar
    close_rect = pygame.Rect(modal_x + modal_width - 50, modal_y + 20, 30, 30)
    draw_rounded_rect(screen, ACCENT_RED, close_rect, 6)
    close_font = pygame.font.Font(None, 24)
    close_text = close_font.render("×", True, (255, 255, 255))
    close_text_rect = close_text.get_rect(center=close_rect.center)
    screen.blit(close_text, close_text_rect)
    
    return close_rect

def draw_fitness_modal(screen, fitness_history, width, height):
    """Desenha o modal com o gráfico de fitness"""
    modal_width = 900
    modal_height = 600
    modal_x = (width - modal_width) // 2
    modal_y = (height - modal_height) // 2
    
    # Overlay escuro
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Card do modal
    modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
    draw_rounded_rect(screen, CARD_COLOR, modal_rect, 20)
    try:
        pygame.draw.rect(screen, BORDER_COLOR, modal_rect, 2, border_radius=20)
    except:
        pygame.draw.rect(screen, BORDER_COLOR, modal_rect, 2)
    
    # Desenhar gráfico dentro do modal
    if fitness_history and len(fitness_history) > 0:
        graph_x = modal_x + 20
        graph_y = modal_y + 60
        graph_width = modal_width - 40
        graph_height = modal_height - 100
        draw_fitness_graph(screen, fitness_history, graph_x, graph_y, graph_width, graph_height)
    else:
        # Mensagem se não houver dados
        try:
            text_font = pygame.font.SysFont("Calibri", 18)
        except:
            text_font = pygame.font.Font(None, 18)
        no_data_text = text_font.render("Nenhum dado de fitness disponível", True, TEXT_SECONDARY)
        text_rect = no_data_text.get_rect(center=(modal_x + modal_width // 2, modal_y + modal_height // 2))
        screen.blit(no_data_text, text_rect)
    
    # Botão fechar
    close_rect = pygame.Rect(modal_x + modal_width - 50, modal_y + 20, 30, 30)
    draw_rounded_rect(screen, ACCENT_RED, close_rect, 6)
    close_font = pygame.font.Font(None, 24)
    close_text = close_font.render("×", True, (255, 255, 255))
    close_text_rect = close_text.get_rect(center=close_rect.center)
    screen.blit(close_text, close_text_rect)
    
    return close_rect

def show_image_and_play_audio(image_path, audio_path, top3_memes=None, target_size=(1200, 800)):
    pygame.init()
    screen = pygame.display.set_mode(target_size)
    pygame.display.set_caption("Memes Evolutivos")

    # Carregar imagem
    try:
        image = pygame.image.load(image_path).convert_alpha()
    except:
        image = pygame.Surface((400, 400))
        image.fill(ACCENT_GRAY)
        try:
            error_font = pygame.font.SysFont("Calibri", 20)
        except:
            try:
                error_font = pygame.font.SysFont("Verdana", 20)
            except:
                error_font = pygame.font.Font(None, 20)
        error_text = error_font.render("Imagem não encontrada", True, TEXT_PRIMARY)
        text_rect = error_text.get_rect(center=(200, 200))
        image.blit(error_text, text_rect)

    # Carregar áudio
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
    except:
        print(f"Erro ao carregar áudio: {audio_path}")
    
    # Fontes (diferentes de Arial)
    try:
        title_font = pygame.font.SysFont("Calibri", 38, bold=True)
    except:
        try:
            title_font = pygame.font.SysFont("Verdana", 38, bold=True)
        except:
            title_font = pygame.font.Font(None, 38)
    
    try:
        subtitle_font = pygame.font.SysFont("Calibri", 20, bold=True)
    except:
        try:
            subtitle_font = pygame.font.SysFont("Verdana", 20, bold=True)
        except:
            subtitle_font = pygame.font.Font(None, 20)
    
    try:
        font = pygame.font.SysFont("Calibri", 28)
    except:
        try:
            font = pygame.font.SysFont("Verdana", 28)
        except:
            font = pygame.font.Font(None, 28)
    
    try:
        small_font = pygame.font.SysFont("Calibri", 16)
    except:
        try:
            small_font = pygame.font.SysFont("Verdana", 16)
        except:
            small_font = pygame.font.Font(None, 16)
    
    # Área da imagem (lado esquerdo)
    image_area = pygame.Rect(30, 100, 480, 480)
    
    # Área da tabela top 3 (canto superior direito)
    table_area = pygame.Rect(540, 100, 640, 240)
    
    # Botões de classificação (1-10) - em 2 linhas: 1-5 na primeira, 6-10 na segunda
    buttons = []
    button_width = 60
    button_height = 45
    button_spacing = 8
    start_x = 540
    start_y = 380
    
    # Primeira linha: botões 1-5
    for i in range(1, 6):
        x = start_x + (i - 1) * (button_width + button_spacing)
        y = start_y
        
        # Todos os botões com cor cinza
        btn_color = ACCENT_GRAY
        btn_hover = (107, 114, 128)
        
        buttons.append(Button(x, y, button_width, button_height, str(i), 
                              btn_color, btn_hover, radius=10))
    
    # Segunda linha: botões 6-10
    for i in range(6, 11):
        x = start_x + (i - 6) * (button_width + button_spacing)
        y = start_y + button_height + button_spacing
        
        # Todos os botões com cor cinza
        btn_color = ACCENT_GRAY
        btn_hover = (107, 114, 128)
        
        buttons.append(Button(x, y, button_width, button_height, str(i), 
                              btn_color, btn_hover, radius=10))
    
    # Botões de ação em 3 linhas verticais, um em cada
    action_button_width = 180
    action_button_height = 45
    action_button_spacing = 10
    action_start_x = 540
    action_start_y = 490  # Começa após os botões de nota
    
    # Botão de encerrar (primeira linha)
    encerrar_button = Button(action_start_x, action_start_y, action_button_width, action_button_height, 
                            "Encerrar", ACCENT_RED, (220, 38, 38), radius=10)
    
    # Botão de pular (segunda linha)
    pular_button = Button(action_start_x, action_start_y + action_button_height + action_button_spacing, 
                         action_button_width, action_button_height, "Pular", ACCENT_GRAY, (107, 114, 128), radius=10)
    
    # Botão de repetir áudio (terceira linha)
    repetir_audio_button = Button(action_start_x, action_start_y + 2 * (action_button_height + action_button_spacing), 
                                  action_button_width, action_button_height, "Repetir Audio", ACCENT_BLUE, ACCENT_BLUE_HOVER, radius=10)
    
    # Botão de ajuda (circular com texto) - mantém posição original
    ajuda_button = Button(1150, 20, 40, 40, "?", CARD_COLOR, ACCENT_BLUE, radius=20)
    
    nota_selecionada = None
    running = True
    encerrar_programa = False
    show_help = False
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Preencher fundo minimalista
        screen.fill(BG_COLOR)
        
        # Título principal "Memes Evolutivos"
        title_text = title_font.render("Memes Evolutivos", True, TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(600, 50))
        screen.blit(title_text, title_rect)
        
        # Card da imagem com bordas arredondadas
        image_card = pygame.Rect(image_area.x - 10, image_area.y - 10, 
                                image_area.width + 20, image_area.height + 20)
        draw_rounded_rect(screen, CARD_COLOR, image_card, 16)
        try:
            pygame.draw.rect(screen, BORDER_COLOR, image_card, 1, border_radius=16)
        except:
            pygame.draw.rect(screen, BORDER_COLOR, image_card, 1)
        
        # Desenhar imagem
        scaled, pos = _scale_to_fit(image, (image_area.width, image_area.height))
        screen.blit(scaled, (image_area.x + pos[0], image_area.y + pos[1]))
        
        # Desenhar tabela top 3
        if top3_memes:
            draw_top3_table(screen, top3_memes, subtitle_font, small_font, 
                          table_area.x, table_area.y, table_area.width, table_area.height)
        
        # Título dos botões de classificação
        subtitle = subtitle_font.render("Classifique o meme:", True, TEXT_SECONDARY)
        screen.blit(subtitle, (540, 350))
        
        # Desenhar botões de classificação
        for button in buttons:
            button.handle_hover(mouse_pos)
            button.draw(screen)
        
        # Desenhar botões de ação
        encerrar_button.handle_hover(mouse_pos)
        encerrar_button.draw(screen)
        
        pular_button.handle_hover(mouse_pos)
        pular_button.draw(screen)
        
        # Botão de ajuda
        ajuda_button.handle_hover(mouse_pos)
        ajuda_button.draw(screen)
        
        # Botão de repetir áudio
        repetir_audio_button.handle_hover(mouse_pos)
        repetir_audio_button.draw(screen)
        
        # Mostrar nota selecionada (ajustado para nova posição)
        if nota_selecionada:
            nota_bg = pygame.Rect(730, 490, 320, 40)
            draw_rounded_rect(screen, ACCENT_GREEN, nota_bg, 8)
            nota_text = subtitle_font.render(f"Nota selecionada: {nota_selecionada}/10", True, (255, 255, 255))
            nota_rect = nota_text.get_rect(center=nota_bg.center)
            screen.blit(nota_text, nota_rect)
        
        # Modal de ajuda
        close_rect = None
        if show_help:
            close_rect = draw_help_modal(screen, target_size[0], target_size[1])
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                encerrar_programa = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    if show_help and close_rect:
                        # Verificar se clicou no botão fechar do modal
                        if close_rect.collidepoint(mouse_pos):
                            show_help = False
                        continue
                    
                    # Verificar botão de ajuda
                    if ajuda_button.is_clicked(mouse_pos):
                        show_help = True
                        continue
                    
                    # Verificar botão de repetir áudio
                    if repetir_audio_button.is_clicked(mouse_pos):
                        try:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(audio_path)
                            pygame.mixer.music.play()
                        except:
                            print(f"Erro ao repetir áudio: {audio_path}")
                        continue
                    
                    # Verificar botões de classificação
                    for i, button in enumerate(buttons):
                        if button.is_clicked(mouse_pos):
                            nota_selecionada = i + 1
                            running = False
                            break
                    
                    # Verificar botão de encerrar
                    if encerrar_button.is_clicked(mouse_pos):
                        running = False
                        # Não encerrar imediatamente, mas marcar para mostrar tela de resultados
                        encerrar_programa = "show_results"
                    
                    # Verificar botão de pular
                    if pular_button.is_clicked(mouse_pos):
                        running = False
                        nota_selecionada = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and show_help:
                    show_help = False
        
        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.quit()
    
    return nota_selecionada, encerrar_programa

def draw_fitness_graph(screen, fitness_data, x, y, width, height):
    """Desenha um gráfico de fitness evolutivo"""
    if not fitness_data or len(fitness_data) == 0:
        return
    
    # Margens do gráfico
    margin_left = 60
    margin_right = 20
    margin_top = 40
    margin_bottom = 50
    
    graph_x = x + margin_left
    graph_y = y + margin_top
    graph_width = width - margin_left - margin_right
    graph_height = height - margin_top - margin_bottom
    
    # Fundo do gráfico
    graph_rect = pygame.Rect(graph_x, graph_y, graph_width, graph_height)
    draw_rounded_rect(screen, CARD_COLOR, graph_rect, 8)
    try:
        pygame.draw.rect(screen, BORDER_COLOR, graph_rect, 1, border_radius=8)
    except:
        pygame.draw.rect(screen, BORDER_COLOR, graph_rect, 1)
    
    # Calcular valores min/max
    min_fitness = min(fitness_data)
    max_fitness = max(fitness_data)
    range_fitness = max_fitness - min_fitness if max_fitness != min_fitness else 1
    
    # Adicionar padding de 10% acima e abaixo (mínimo de 0.5 para garantir visibilidade)
    padding = max(range_fitness * 0.1, 0.5)
    y_min = max(0, min_fitness - padding)
    y_max = max_fitness + padding
    y_range = y_max - y_min if y_max != y_min else 1
    
    # Desenhar linhas de grade
    try:
        grid_font = pygame.font.SysFont("Calibri", 12)
    except:
        grid_font = pygame.font.Font(None, 12)
    
    num_grid_lines = 5
    for i in range(num_grid_lines + 1):
        y_pos = graph_y + graph_height - (i * graph_height / num_grid_lines)
        value = y_min + (i * y_range / num_grid_lines)
        
        # Linha de grade
        pygame.draw.line(screen, BORDER_COLOR, 
                        (graph_x, y_pos), 
                        (graph_x + graph_width, y_pos), 1)
        
        # Label do eixo Y
        label_text = grid_font.render(f"{value:.1f}", True, TEXT_SECONDARY)
        screen.blit(label_text, (graph_x - 50, y_pos - 8))
    
    # Desenhar linha do gráfico
    if len(fitness_data) >= 1:
        points = []
        if len(fitness_data) == 1:
            # Se houver apenas um ponto, desenhar no centro
            x_pos = graph_x + graph_width / 2
            y_pos = graph_y + graph_height - ((fitness_data[0] - y_min) / y_range * graph_height)
            points.append((x_pos, y_pos))
        else:
            # Múltiplos pontos
            for i, fitness in enumerate(fitness_data):
                x_pos = graph_x + (i * graph_width / (len(fitness_data) - 1))
                y_pos = graph_y + graph_height - ((fitness - y_min) / y_range * graph_height)
                points.append((x_pos, y_pos))
        
        # Desenhar linha conectando os pontos (se houver mais de um)
        if len(points) > 1:
            pygame.draw.lines(screen, ACCENT_BLUE, False, points, 3)
        
        # Desenhar pontos
        for point in points:
            pygame.draw.circle(screen, ACCENT_BLUE, (int(point[0]), int(point[1])), 5)
            pygame.draw.circle(screen, (255, 255, 255), (int(point[0]), int(point[1])), 2)
    
    # Labels dos eixos
    try:
        axis_font = pygame.font.SysFont("Calibri", 14, bold=True)
    except:
        axis_font = pygame.font.Font(None, 14)
    
    # Eixo Y
    y_label = axis_font.render("Nota Média", True, TEXT_PRIMARY)
    y_label_rotated = pygame.transform.rotate(y_label, 90)
    screen.blit(y_label_rotated, (x + 10, y + height // 2 - 40))
    
    # Eixo X
    x_label = axis_font.render("Geração", True, TEXT_PRIMARY)
    screen.blit(x_label, (x + width // 2 - 40, y + height - 30))
    
    # Título do gráfico
    try:
        title_font = pygame.font.SysFont("Calibri", 18, bold=True)
    except:
        title_font = pygame.font.Font(None, 18)
    title = title_font.render("Evolução do Fitness", True, TEXT_PRIMARY)
    screen.blit(title, (x + 20, y + 10))
    
    # Estatísticas
    stats_text = [
        f"Melhor: {max_fitness:.2f}",
        f"Média: {sum(fitness_data)/len(fitness_data):.2f}",
        f"Pior: {min_fitness:.2f}"
    ]
    for i, stat in enumerate(stats_text):
        stat_surface = grid_font.render(stat, True, TEXT_SECONDARY)
        screen.blit(stat_surface, (x + width - 120, y + 15 + i * 15))

def show_results_screen(top3_memes, fitness_history=None, target_size=(1200, 800)):
    """Tela de resultados mostrando o top 3 memes e gráfico de fitness"""
    pygame.init()
    screen = pygame.display.set_mode(target_size)
    pygame.display.set_caption("Memes Evolutivos - Resultados")
    
    # Fontes
    try:
        title_font = pygame.font.SysFont("Calibri", 48, bold=True)
    except:
        try:
            title_font = pygame.font.SysFont("Verdana", 48, bold=True)
        except:
            title_font = pygame.font.Font(None, 48)
    
    try:
        subtitle_font = pygame.font.SysFont("Calibri", 24, bold=True)
    except:
        try:
            subtitle_font = pygame.font.SysFont("Verdana", 24, bold=True)
        except:
            subtitle_font = pygame.font.Font(None, 24)
    
    try:
        text_font = pygame.font.SysFont("Calibri", 18)
    except:
        try:
            text_font = pygame.font.SysFont("Verdana", 18)
        except:
            text_font = pygame.font.Font(None, 18)
    
    # Calcular start_y (sem gráfico sempre visível, então sempre 120)
    start_y = 120
    card_height = 350  # Altura dos cards dos memes
    
    # Botões para visualizar cada meme do top 3 (logo abaixo dos cards)
    view_buttons = []
    meme_previews = []
    
    # Carregar previews dos memes
    for i, meme_info in enumerate(top3_memes[:3]):
        if meme_info:
            img_path = "./imagens/" + meme_info.get('img_file', '')
            aud_path = "./audios/" + meme_info.get('aud_file', '')
            try:
                preview_img = pygame.image.load(img_path)
                preview_img = pygame.transform.smoothscale(preview_img, (200, 200))
            except:
                preview_img = pygame.Surface((200, 200))
                preview_img.fill(ACCENT_GRAY)
            
            meme_previews.append({
                'img': preview_img,
                'img_path': img_path,
                'aud_path': aud_path,
                'nota': meme_info.get('nota', 0),
                'filename': os.path.basename(meme_info.get('aud_file', 'N/A'))
            })
            
            # Botão para visualizar (ajustado para ficar abaixo dos cards)
            button_y = start_y + card_height + 10  # 10px de espaçamento após o card
            x_pos = 150 + i * 300  # Mesma posição X dos cards
            view_buttons.append(Button(x_pos + 50, button_y, 150, 40, f"Ver #{i+1}", 
                                      ACCENT_BLUE, ACCENT_BLUE_HOVER, radius=10))
    
    # Botão para ver gráfico de fitness (abaixo dos botões "Ver", com mais espaçamento)
    ver_grafico_button = None
    if fitness_history and len(fitness_history) > 0:
        ver_grafico_y = start_y + card_height + 70  # 70px abaixo dos cards (após os botões "Ver" que têm 40px de altura)
        ver_grafico_button = Button(200, ver_grafico_y, 200, 50, "Ver Gráfico", ACCENT_BLUE, ACCENT_BLUE_HOVER, radius=10)
    
    # Botão de fechar (ao lado do botão "Ver Gráfico", na mesma linha)
    fechar_y = start_y + card_height + 70  # Mesma altura do botão "Ver Gráfico"
    fechar_button = Button(500, fechar_y, 200, 50, "Fechar", ACCENT_RED, (220, 38, 38), radius=10)
    
    running = True
    encerrar_programa = False
    show_graph = False
    show_help = False
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Preencher fundo
        screen.fill(BG_COLOR)
        
        # Título
        title_text = title_font.render("Top 3 Memes - Resultados Finais", True, TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(600, 30))
        screen.blit(title_text, title_rect)
        
        # Exibir os 3 memes (ajustado para ficar abaixo do gráfico)
        for i, preview in enumerate(meme_previews):
            x_pos = 150 + i * 300
            
            # Card do meme
            card_rect = pygame.Rect(x_pos, start_y, 250, 350)
            draw_rounded_rect(screen, CARD_COLOR, card_rect, 16)
            try:
                pygame.draw.rect(screen, BORDER_COLOR, card_rect, 1, border_radius=16)
            except:
                pygame.draw.rect(screen, BORDER_COLOR, card_rect, 1)
            
            # Posição/Medalha
            positions = ["1st", "2nd", "3rd"]
            pos_text = subtitle_font.render(positions[i], True, TEXT_PRIMARY)
            screen.blit(pos_text, (x_pos + 20, start_y + 20))
            
            # Imagem do meme
            img_rect = pygame.Rect(x_pos + 25, start_y + 50, 200, 200)
            screen.blit(preview['img'], img_rect)
            try:
                pygame.draw.rect(screen, BORDER_COLOR, img_rect, 1, border_radius=8)
            except:
                pygame.draw.rect(screen, BORDER_COLOR, img_rect, 1)
            
            # Nome do arquivo
            filename = preview['filename']
            if len(filename) > 25:
                filename = filename[:22] + "..."
            file_text = text_font.render(filename, True, TEXT_SECONDARY)
            screen.blit(file_text, (x_pos + 25, start_y + 270))
            
            # Nota
            nota_bg = pygame.Rect(x_pos + 25, start_y + 300, 200, 40)
            draw_rounded_rect(screen, ACCENT_GREEN, nota_bg, 8)
            nota_text = subtitle_font.render(f"Nota: {preview['nota']:.1f}/10", True, (255, 255, 255))
            nota_rect = nota_text.get_rect(center=nota_bg.center)
            screen.blit(nota_text, nota_rect)
        
        # Botões de visualizar
        for i, button in enumerate(view_buttons):
            button.handle_hover(mouse_pos)
            button.draw(screen)
        
        # Botão para ver gráfico
        if ver_grafico_button:
            ver_grafico_button.handle_hover(mouse_pos)
            ver_grafico_button.draw(screen)
        
        # Botão de fechar
        fechar_button.handle_hover(mouse_pos)
        fechar_button.draw(screen)
        
        # Instruções (ajustado)
        instrucao_y = fechar_y + 70  # 70px abaixo dos botões de ação
        instrucoes_texto = "Clique em 'Ver' para visualizar o meme, 'Ver Gráfico' para ver a evolução, ou 'Fechar' para encerrar"
        instrucao = text_font.render(instrucoes_texto, True, TEXT_SECONDARY)
        screen.blit(instrucao, (200, instrucao_y))
        
        # Modal de gráfico de fitness
        graph_close_rect = None
        if show_graph and fitness_history:
            graph_close_rect = draw_fitness_modal(screen, fitness_history, target_size[0], target_size[1])
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                encerrar_programa = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    if show_graph and graph_close_rect:
                        # Verificar se clicou no botão fechar do modal de gráfico
                        if graph_close_rect.collidepoint(mouse_pos):
                            show_graph = False
                        continue
                    
                    # Verificar botão para ver gráfico
                    if ver_grafico_button and ver_grafico_button.is_clicked(mouse_pos):
                        show_graph = True
                        continue
                    
                    # Verificar botões de visualizar
                    for i, button in enumerate(view_buttons):
                        if button.is_clicked(mouse_pos) and i < len(meme_previews):
                            preview = meme_previews[i]
                            # Mostrar o meme em tela cheia temporariamente
                            should_quit = show_meme_fullscreen(screen, preview['img_path'], preview['aud_path'])
                            if should_quit:
                                running = False
                                encerrar_programa = True
                            # Restaurar título da janela
                            pygame.display.set_caption("Memes Evolutivos - Resultados")
                            break
                    
                    # Verificar botão de fechar
                    if fechar_button.is_clicked(mouse_pos):
                        running = False
                        encerrar_programa = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_graph:
                        show_graph = False
        
        pygame.display.flip()

    pygame.quit()
    return encerrar_programa

def show_meme_fullscreen(screen, image_path, audio_path):
    """Mostra um meme em tela cheia temporariamente (sem fechar pygame)"""
    pygame.display.set_caption("Visualizando Meme")
    
    # Carregar imagem - verificar se o caminho existe
    image = None
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(image_path):
            # Tentar caminho alternativo sem ./
            alt_path = image_path.replace("./imagens/", "imagens/")
            if os.path.exists(alt_path):
                image_path = alt_path
            else:
                # Tentar caminho absoluto
                alt_path2 = os.path.join(os.getcwd(), "imagens", os.path.basename(image_path))
                if os.path.exists(alt_path2):
                    image_path = alt_path2
                else:
                    raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
        
        # Carregar a imagem
        image = pygame.image.load(image_path).convert()
        print(f"Imagem carregada com sucesso: {image_path}, tamanho: {image.get_size()}")
        
    except Exception as e:
        print(f"Erro ao carregar imagem: {image_path}, erro: {e}")
        # Criar imagem de erro
        image = pygame.Surface((400, 400))
        image.fill(ACCENT_GRAY)
        try:
            error_font = pygame.font.SysFont("Calibri", 18)
        except:
            error_font = pygame.font.Font(None, 18)
        error_text = error_font.render("Erro ao carregar", True, TEXT_PRIMARY)
        error_text2 = error_font.render("imagem", True, TEXT_PRIMARY)
        text_rect = error_text.get_rect(center=(200, 190))
        text_rect2 = error_text2.get_rect(center=(200, 210))
        image.blit(error_text, text_rect)
        image.blit(error_text2, text_rect2)
    
    # Carregar áudio
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Erro ao carregar áudio: {audio_path}, erro: {e}")
    
    # Botão de voltar
    voltar_button = Button(500, 700, 200, 50, "Voltar", ACCENT_GRAY, (107, 114, 128), radius=10)
    
    running = True
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        screen.fill(BG_COLOR)
        
        # Card da imagem (desenhar primeiro para ficar atrás)
        image_area = pygame.Rect(100, 100, 1000, 600)
        image_card = pygame.Rect(image_area.x - 10, image_area.y - 10, 
                                image_area.width + 20, image_area.height + 20)
        draw_rounded_rect(screen, CARD_COLOR, image_card, 16)
        try:
            pygame.draw.rect(screen, BORDER_COLOR, image_card, 1, border_radius=16)
        except:
            pygame.draw.rect(screen, BORDER_COLOR, image_card, 1)
        
        # Desenhar imagem centralizada (depois do card)
        scaled, pos = _scale_to_fit(image, (image_area.width, image_area.height))
        screen.blit(scaled, (image_area.x + pos[0], image_area.y + pos[1]))
        
        # Botão voltar
        voltar_button.handle_hover(mouse_pos)
        voltar_button.draw(screen)
        
        # Instruções
        try:
            text_font = pygame.font.SysFont("Calibri", 18)
        except:
            text_font = pygame.font.Font(None, 18)
        instrucao = text_font.render("Pressione ESC ou clique em 'Voltar' para retornar", 
                                    True, TEXT_SECONDARY)
        screen.blit(instrucao, (350, 760))
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return True  # Indica que deve encerrar
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if voltar_button.is_clicked(mouse_pos):
                        running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.display.flip()
    
    pygame.mixer.music.stop()
    return False  # Retorna normalmente sem encerrar

def avaliar_meme(image_path, audio_path, top3_memes=None, target_size=(1200, 800)):
    nota, encerrar = show_image_and_play_audio(image_path, audio_path, top3_memes, target_size)
    return nota, encerrar