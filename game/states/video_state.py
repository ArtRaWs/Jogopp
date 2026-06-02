
import pygame
import os
from utils.game_state_manager import BaseState
from utils.constants import *
from utils.ui import draw_text


class VideoState(BaseState):

    def _asset_path(self, filename: str) -> str:
        """
        Resolve caminho para assets independente do diretório atual.
        Estrutura esperada: game/assets/<filename>
        """
        game_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(game_dir, "assets", filename)

    def enter(self, data: dict = None):
        self._done    = False
        self._t       = 0.0
        self._surface = None
        self._cap     = None

        # OpenCV é opcional. Se não estiver instalado, pula a cutscene.
        try:
            import cv2  # type: ignore
        except Exception as e:
            print(f"[VideoState] OpenCV (cv2) indisponível: {e}")
            self._ir_proximo()
            return

        # ── Vídeo ─────────────────────────────────────────────
        video_path = self._asset_path("video.mp4")
        self._cap   = cv2.VideoCapture(video_path)

        if not self._cap.isOpened():
            print(f"[VideoState] Não foi possível abrir {video_path}")
            self._ir_proximo()
            return

        self._fps_video = self._cap.get(cv2.CAP_PROP_FPS) or 30
        self._frame_dt  = 1.0 / self._fps_video
        self._acum_dt   = 0.0

        # ── Áudio ─────────────────────────────────────────────
        audio_path = self._asset_path("audio.mp3")
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[VideoState] Áudio não carregado: {e}")

        self._ler_frame()

    def _ler_frame(self):
        import cv2  # type: ignore
        ret, frame = self._cap.read()
        if not ret:
            self._ir_proximo()
            return

        # OpenCV usa BGR → converter para RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Redimensionar para a tela mantendo proporção
        fh, fw = frame.shape[:2]
        escala  = min(SCREEN_WIDTH / fw, SCREEN_HEIGHT / fh)
        nw      = int(fw * escala)
        nh      = int(fh * escala)
        frame   = cv2.resize(frame, (nw, nh))

        # Converter para Surface pygame
        self._surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        self._surf_x  = (SCREEN_WIDTH  - nw) // 2
        self._surf_y  = (SCREEN_HEIGHT - nh) // 2

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                self._ir_proximo()
            if e.type == pygame.MOUSEBUTTONDOWN:
                self._ir_proximo()

    def _ir_proximo(self):
        if self._done:
            return
        self._done = True
        if self._cap:
            self._cap.release()
        pygame.mixer.music.stop()
        self.go_to(STATE_PROLOGUE)

    def update(self, dt: float):
        if self._done:
            return
        self._t      += dt
        self._acum_dt += dt
        if self._acum_dt >= self._frame_dt:
            self._acum_dt -= self._frame_dt
            self._ler_frame()

    def draw(self, surface: pygame.Surface):
        surface.fill((0, 0, 0))
        if self._surface:
            surface.blit(self._surface, (self._surf_x, self._surf_y))

        # Dica de pular
        if self._t > 1.5:
            draw_text(surface, "[ ENTER ou clique para pular ]",
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 28,
                      size=FONT_TINY, color=(100, 100, 100),
                      center=True, shadow=False)

    def exit(self):
        if not self._done:
            if self._cap:
                self._cap.release()
            pygame.mixer.music.stop()