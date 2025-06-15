# /*********************************************************************************
# * Projeto:   Luz do Mundo
# * Script:    luz_do_mundo.py
# * Autor:     Carlos Henrique Tourinho Santana
# * Data:      15 de junho de 2025
# * GitHub:    https://github.com/henriquetourinho/luz-do-mundo
# *
# * Descrição:
# * Jogo de plataforma 2D com tema cristão, desenvolvido em Python com a
# * biblioteca padrão Tkinter. O projeto é 100% autônomo, sem a necessidade
# * de dependências externas ou arquivos de imagem, focando na jornada
# * simbólica da fé contra as adversidades.
# *********************************************************************************/

import tkinter as tk
from tkinter import simpledialog
import math
import random

# --- Constantes de Configuração do Jogo ---
LARGURA = 1000
ALTURA = 700
TITULO_JOGO = "Luz do Mundo - A Jornada Final (Versão Estável)"

# Dimensões dos objetos
PLAYER_W, PLAYER_H = 30, 40
ENEMY_W, ENEMY_H = 30, 30
GOAL_W, GOAL_H = 50, 70

# Configurações do Jogador
VELOCIDADE_MOVIMENTO = 5
FORCA_PULO = 18
GRAVIDADE = 1

# Configurações da Mecânica da Luz
RAIO_DA_LUZ = 150
FORCA_EMPURRAO_LUZ = 20

# --- ESTRUTURA DOS NÍVEIS COM CORES E TEMAS ---
LEVELS = [
    # Nível 1: Noite Escura
    {"nome": "Noite Escura", "bg_color": "#1c2a38", "tem_estrelas": True, "tem_trovao": True,
     "player_start": (30, 630), "goal_pos": (900, 100),
     "platforms": [[0, 680, 1000, 700], [150, 580, 400, 600], [500, 500, 750, 520], [800, 400, 1000, 420]],
     "enemies": [{"start_pos": (550, 470), "patrol_end": 720}]},
    # Nível 2: Amanhecer Tempestuoso
    {"nome": "Amanhecer Tempestuoso", "bg_color": "#483D8B", "tem_estrelas": True, "tem_trovao": True,
     "player_start": (30, 630), "goal_pos": (500, 100),
     "platforms": [[0, 680, 250, 700], [350, 600, 600, 620], [700, 680, 1000, 700], [400, 450, 550, 470], [100, 350, 300, 370], [450, 200, 550, 220]],
     "enemies": [{"start_pos": (400, 570), "patrol_end": 570}, {"start_pos": (750, 650), "patrol_end": 970}]},
    # Nível 3: Céu Aberto
    {"nome": "Céu Aberto", "bg_color": "#87CEEB", "tem_estrelas": False, "tem_trovao": False,
     "player_start": (80, 100), "goal_pos": (900, 620),
     "platforms": [[0, 150, 150, 170], [250, 250, 300, 270], [50, 350, 100, 370], [200, 450, 400, 470], [500, 550, 700, 570], [800, 680, 1000, 700]],
     "enemies": [{"start_pos": (250, 420), "patrol_end": 370}, {"start_pos": (520, 520), "patrol_end": 670}]},
    # Nível 4: O Encontro
    {"nome": "O Encontro no Céu", "bg_color": "#ADD8E6", "tem_estrelas": False, "tem_trovao": False,
     "player_start": (50, 630), "goal_pos": (850, 280),
     "platforms": [[0, 680, 1000, 700], [200, 550, 400, 570], [500, 450, 700, 470], [750, 350, 950, 370]],
     "enemies": []}
]


class LuzDoMundo:
    def __init__(self, master, nome_jogador):
        self.master = master
        self.master.title(TITULO_JOGO)
        self.canvas = tk.Canvas(master, width=LARGURA, height=ALTURA)
        self.canvas.pack()

        self.nome_jogador = nome_jogador
        self.inicializar_estado()
        self.iniciar_jogo()

    def inicializar_estado(self):
        """Inicializa ou reseta todas as variáveis de estado do jogo."""
        self.teclas_pressionadas = {}
        self.velocidade = {'x': 0, 'y': 0}
        self.em_chao = False
        self.current_level_index = 0
        self.game_over_flag = False
        self.venceu_flag = False
        self.tempo_decorrido = 0
        self.jogador = None
        self.objetivo_final = None
        self.plataformas = []
        self.inimigos = []
        self.estado_inimigos = {}
        self.level_info = {}
        self.texto_cronometro = None
        self.texto_nome = None

    def iniciar_jogo(self):
        self.carregar_nivel(self.current_level_index)
        self.vincular_eventos()
        self.game_loop()

    def reiniciar_jogo(self):
        self.inicializar_estado()
        self.iniciar_jogo()

    def limpar_nivel_anterior(self):
        self.canvas.delete("all")

    def carregar_nivel(self, level_index):
        self.limpar_nivel_anterior()
        self.level_info = LEVELS[level_index]

        self.canvas.config(bg=self.level_info["bg_color"])
        if self.level_info["tem_estrelas"]:
            self.criar_fundo_estrelado()

        self.criar_hud()

        platform_color = "#FFFFFF" if "Céu" in self.level_info["nome"] else "#7f8c8d"
        for p_coords in self.level_info["platforms"]:
            plataforma = self.criar_plataforma_texturizada(*p_coords, color=platform_color)
            self.plataformas.append(plataforma)

        for e_data in self.level_info["enemies"]:
            pos, end = e_data["start_pos"], e_data["patrol_end"]
            inimigo = self.criar_inimigo(pos[0], pos[1])
            self.inimigos.append(inimigo)
            self.estado_inimigos[inimigo] = {'velocidade': 2, 'limite_esquerda': pos[0], 'limite_direita': end}

        p_start = self.level_info["player_start"]
        self.jogador = self.criar_jogador(p_start[0], p_start[1])

        g_pos = self.level_info["goal_pos"]
        if level_index == len(LEVELS) - 1:
            self.objetivo_final = self.criar_cristo(g_pos[0], g_pos[1])
        else:
            self.objetivo_final = self.criar_farol(g_pos[0], g_pos[1])

    # --- Funções de Desenho e UI ---
    def criar_hud(self):
        self.texto_nome = self.canvas.create_text(10, 10, anchor="nw", text=f"Jogador: {self.nome_jogador}", font=("Arial", 14, "bold"), fill="white")
        self.texto_cronometro = self.canvas.create_text(LARGURA - 10, 10, anchor="ne", text="Tempo: 0s", font=("Arial", 14, "bold"), fill="white")

    def criar_fundo_estrelado(self):
        for _ in range(100):
            x, y = random.randint(0, LARGURA), random.randint(0, ALTURA)
            tamanho, cor = random.randint(1, 3), random.choice(["#FFFFFF", "#E0E0E0", "#C0C0C0"])
            self.canvas.create_oval(x, y, x + tamanho, y + tamanho, fill=cor, outline="")
    
    def criar_plataforma_texturizada(self, x1, y1, x2, y2, color="#7f8c8d"):
        cor_detalhe = "#616a6b" if color == "#7f8c8d" else "#E0E0E0"
        base = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        for x in range(int(x1), int(x2), 20): self.canvas.create_line(x, y1, x, y2, fill=cor_detalhe)
        return base

    def criar_jogador(self, x, y):
        p = self.canvas.create_rectangle(x, y, x + PLAYER_W, y + PLAYER_H, fill="#f1c40f", outline="")
        self.canvas.create_rectangle(x + 5, y + 5, x + PLAYER_W - 5, y + PLAYER_H - 5, fill="#f9e79f", outline="")
        return p

    def criar_inimigo(self, x, y):
        e = self.canvas.create_rectangle(x, y, x + ENEMY_W, y + ENEMY_H, fill="#c0392b", outline="")
        self.canvas.create_oval(x + 7, y + 10, x + 12, y + 15, fill="#e74c3c", outline="")
        self.canvas.create_oval(x + 18, y + 10, x + 23, y + 15, fill="#e74c3c", outline="")
        return e

    def criar_farol(self, x, y):
        return self.canvas.create_rectangle(x, y, x + GOAL_W, y + GOAL_H, fill="#f1c40f", outline="")

    def criar_cristo(self, x, y):
        self.canvas.create_rectangle(x, y, x + 50, y + 100, fill="white", outline="")
        self.canvas.create_oval(x + 15, y - 25, x + 35, y, fill="#fdebd0", outline="")
        self.canvas.create_line(x, y + 30, x - 30, y + 10, fill="white", width=8)
        return self.canvas.create_rectangle(x - 30, y - 25, x + 50, y + 100, outline="", fill=None)

    def proximo_nivel(self):
        self.current_level_index += 1
        if self.current_level_index < len(LEVELS):
            self.carregar_nivel(self.current_level_index)
        else:
            self.vencer_jogo()
        return True

    def efeito_trovao(self):
        flash = self.canvas.create_rectangle(0, 0, LARGURA, ALTURA, fill="white", outline="")
        self.master.after(100, lambda: self.canvas.winfo_exists() and self.canvas.delete(flash))

    def vincular_eventos(self):
        self.master.bind("<KeyPress>", self.tecla_pressionada)
        self.master.bind("<KeyRelease>", self.tecla_liberada)
        self.canvas.focus_set()

    def tecla_pressionada(self, evento):
        tecla = evento.keysym.lower()
        self.teclas_pressionadas[tecla] = True
        if (self.game_over_flag or self.venceu_flag) and tecla == 'r':
            self.reiniciar_jogo()
            return
        if tecla == 'p':
            self.proximo_nivel()
            return
        if tecla == 'x': self.brilhar_luz()
        if tecla == 'space' and self.em_chao:
            self.velocidade['y'] = -FORCA_PULO
            self.em_chao = False

    def tecla_liberada(self, evento):
        self.teclas_pressionadas[evento.keysym.lower()] = False

    def atualizar_movimento_jogador(self):
        if not self.jogador: return
        move_esquerda = self.teclas_pressionadas.get('a', False) or self.teclas_pressionadas.get('left', False)
        move_direita = self.teclas_pressionadas.get('d', False) or self.teclas_pressionadas.get('right', False)
        if move_esquerda and not move_direita: self.velocidade['x'] = -VELOCIDADE_MOVIMENTO
        elif move_direita and not move_esquerda: self.velocidade['x'] = VELOCIDADE_MOVIMENTO
        else: self.velocidade['x'] = 0

    def brilhar_luz(self):
        if not self.jogador or not self.canvas.winfo_exists() or not self.canvas.coords(self.jogador): return
        coords = self.canvas.coords(self.jogador)
        centro_jogador_x = coords[0] + PLAYER_W / 2
        centro_jogador_y = coords[1] + PLAYER_H / 2
        efeito_luz = self.canvas.create_oval(centro_jogador_x - RAIO_DA_LUZ, centro_jogador_y - RAIO_DA_LUZ, centro_jogador_x + RAIO_DA_LUZ, centro_jogador_y + RAIO_DA_LUZ, fill="#f1c40f", outline="", stipple="gray50")
        self.master.after(150, lambda: self.canvas.winfo_exists() and self.canvas.delete(efeito_luz))
        for inimigo in self.inimigos:
            if not self.canvas.coords(inimigo): continue
            icoords = self.canvas.coords(inimigo)
            centro_inimigo_x = icoords[0] + ENEMY_W / 2
            centro_inimigo_y = icoords[1] + ENEMY_H / 2
            distancia = math.sqrt((centro_jogador_x - centro_inimigo_x)**2 + (centro_jogador_y - centro_inimigo_y)**2)
            if distancia < RAIO_DA_LUZ:
                vetor_x, vetor_y = centro_inimigo_x - centro_jogador_x, centro_inimigo_y - centro_jogador_y
                norma = math.sqrt(vetor_x**2 + vetor_y**2)
                if norma > 0: self.canvas.move(inimigo, (vetor_x/norma) * FORCA_EMPURRAO_LUZ, (vetor_y/norma) * FORCA_EMPURRAO_LUZ)

    def atualizar_fisica_e_colisoes(self):
        coords = self.canvas.coords(self.jogador)
        if not self.jogador or not self.canvas.winfo_exists() or not coords: return

        self.velocidade['y'] += GRAVIDADE
        self.canvas.move(self.jogador, self.velocidade['x'], self.velocidade['y'])
        self.em_chao = False
        
        coords = self.canvas.coords(self.jogador)
        if not coords: return

        px1, py1, px2, py2 = coords
        
        objetos_colisao = self.plataformas + self.inimigos
        for obj in objetos_colisao:
            obj_coords = self.canvas.coords(obj)
            if not obj_coords: continue
            
            plat_x1, plat_y1, plat_x2, plat_y2 = obj_coords
            if px2 > plat_x1 and px1 < plat_x2 and py2 > plat_y1 and py1 < plat_y2:
                if self.velocidade['y'] > 0 and (py2 - self.velocidade['y']) <= plat_y1:
                    self.canvas.coords(self.jogador, px1, plat_y1 - PLAYER_H, px1 + PLAYER_W, plat_y1)
                    self.velocidade['y'] = 0
                    self.em_chao = True
                    return

    def checar_estado_jogo(self):
        coords = self.canvas.coords(self.jogador)
        if not self.jogador or not coords: return False
        
        px1, py1, px2, py2 = coords

        if py1 > ALTURA: return self.game_over()
        
        objetivo_coords = self.canvas.coords(self.objetivo_final)
        if not self.objetivo_final or not objetivo_coords: return False

        gx1, gy1, gx2, gy2 = objetivo_coords
        if px2 > gx1 and px1 < gx2 and py2 > gy1 and py1 < gy2: return self.proximo_nivel()

        return False

    def atualizar_inimigos(self):
        for inimigo, estado in self.estado_inimigos.items():
            coords = self.canvas.coords(inimigo)
            if not self.canvas.winfo_exists() or not coords: continue
            
            if coords[0] <= estado['limite_esquerda'] or (coords[0] + ENEMY_W) >= estado['limite_direita']:
                estado['velocidade'] *= -1
            self.canvas.move(inimigo, estado['velocidade'], 0)
    
    def game_over(self):
        if self.game_over_flag: return True
        self.game_over_flag = True
        self.limpar_nivel_anterior()
        self.canvas.config(bg="#1C1C1C")
        self.canvas.create_text(LARGURA / 2, ALTURA / 2 - 40, text="A escuridão venceu...", font=("Arial", 40, "bold"), fill="red")
        self.canvas.create_text(LARGURA / 2, ALTURA / 2 + 20, text=f"Tempo final: {int(self.tempo_decorrido)} segundos", font=("Arial", 20), fill="white")
        self.canvas.create_text(LARGURA / 2, ALTURA / 2 + 60, text="Pressione 'R' para reiniciar a jornada.", font=("Arial", 18, "bold"), fill="white")
        return True

    def vencer_jogo(self):
        if self.venceu_flag: return True
        self.venceu_flag = True
        self.limpar_nivel_anterior()
        self.canvas.config(bg=self.level_info["bg_color"])
        self.criar_cristo(LARGURA / 2 - 25, ALTURA / 2 - 50)
        self.canvas.create_text(LARGURA / 2, ALTURA / 2 + 80, text=f"{self.nome_jogador}, sua jornada está completa!", font=("Arial", 25, "bold"), fill="white")
        self.canvas.create_text(LARGURA / 2, ALTURA / 2 + 120, text=f"Tempo total: {int(self.tempo_decorrido)} segundos", font=("Arial", 18), fill="white")
        self.canvas.create_text(LARGURA / 2, ALTURA / 2 + 160, text="Pressione 'R' para jogar novamente.", font=("Arial", 16, "bold"), fill="white")
        return True

    def game_loop(self):
        if not self.game_over_flag and not self.venceu_flag:
            if self.level_info.get("tem_trovao", False) and random.random() < 0.002:
                self.efeito_trovao()

            self.atualizar_movimento_jogador()
            self.atualizar_inimigos()
            self.atualizar_fisica_e_colisoes()
            
            if self.checar_estado_jogo():
                return
            
            # Atualiza o cronômetro
            self.tempo_decorrido += 16 / 1000
            if self.texto_cronometro and self.canvas.winfo_exists():
                self.canvas.itemconfig(self.texto_cronometro, text=f"Tempo: {int(self.tempo_decorrido)}s")

            self.master.after(16, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    # Pede o nome do jogador
    nome = simpledialog.askstring("Nome do Jogador", "Qual é o seu nome, nobre aventureiro?", parent=root)
    if not nome:
        nome = "Aventureiro(a)"

    root.deiconify()
    
    jogo = LuzDoMundo(root, nome_jogador=nome)
    root.mainloop()