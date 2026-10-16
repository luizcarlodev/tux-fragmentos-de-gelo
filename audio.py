from pathlib import Path
import pygame

_BASE_DIR = Path(__file__).resolve().parent
_MUSIC_DIR = _BASE_DIR / "assets" / "music"
_SOUNDS_DIR = _BASE_DIR / "assets" / "sounds"
_music_enabled = True
_sfx_enabled = True
_initialized = False
_sounds = {}
_current_music = None


def preparar():
    try:
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    except pygame.error:
        pass


def inicializar():
    global _initialized
    if _initialized:
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(16)
        files = {
            "jump": ("jump.wav", 0.55),
            "attack": ("attack.wav", 0.35),
            "player_hurt": ("player_hurt.wav", 0.45),
            "enemy_hit": ("enemy_hit.wav", 0.35),
            "enemy_die": ("enemy_die.wav", 0.40),
            "collect": ("collect.wav", 0.55),
            "boss_attack": ("boss_attack.wav", 0.68),
            "boss_impact": ("boss_impact.wav", 0.72),
            "boss_rain": ("boss_rain.wav", 0.48),
            "menu_move": ("menu_move.wav", 0.35),
            "menu_confirm": ("menu_confirm.wav", 0.30),
        }
        for name, (filename, volume) in files.items():
            path = _SOUNDS_DIR / filename
            try:
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(volume)
                _sounds[name] = sound
            except (pygame.error, OSError) as exc:
                print(f"[Áudio] Não foi possível carregar {filename}: {exc}")

        _initialized = True
        mudar_musica("normal")
    except pygame.error as exc:
        print(f"[Áudio] Áudio indisponível; o jogo continuará sem som: {exc}")



def mudar_musica(tipo):
    """Troca a trilha sem reiniciá-la a cada frame. Tipos: normal, boss, boss_climax."""
    global _current_music
    if not _initialized or not pygame.mixer.get_init():
        return

    trilhas = {
        "normal": "snow_theme.ogg",
        "boss": "boss_theme.ogg",
        "boss_climax": "boss_climax.ogg",
    }
    filename = trilhas.get(tipo, trilhas["normal"])
    if _current_music == tipo and pygame.mixer.music.get_busy():
        return

    path = _MUSIC_DIR / filename
    if not path.is_file():
        print(f"[Áudio] Trilha não encontrada: {path}; voltando à música normal.")
        tipo = "normal"
        path = _MUSIC_DIR / trilhas["normal"]
        if not path.is_file():
            return

    try:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(0.32 if _music_enabled else 0.0)
        pygame.mixer.music.play(-1)
        _current_music = tipo
    except pygame.error as exc:
        print(f"[Áudio] Não foi possível trocar a música: {exc}")

def tocar(name):
    if not _initialized or not _sfx_enabled:
        return
    sound = _sounds.get(name)
    if sound is not None:
        try:
            sound.play()
        except pygame.error:
            pass


def alternar_musica():
    global _music_enabled
    _music_enabled = not _music_enabled
    if _initialized:
        try:
            pygame.mixer.music.set_volume(0.32 if _music_enabled else 0.0)
        except pygame.error:
            pass
    return _music_enabled


def alternar_efeitos():
    global _sfx_enabled
    _sfx_enabled = not _sfx_enabled
    return _sfx_enabled



def tratar_tecla(event):
    if event.type != pygame.KEYDOWN:
        return False
    if event.key == pygame.K_F1:
        alternar_musica()
        return True
    if event.key == pygame.K_F2:
        alternar_efeitos()
        return True
    return False


def pausar_musica():
    if _initialized:
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            pass


def continuar_musica():
    if _initialized and _music_enabled:
        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            pass
