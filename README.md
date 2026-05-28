Um jogo em Python + Pygame com narrativa, seleção de herói, batalhas com “quiz” de Python e cutscene em vídeo.

Requisitos





Python 3.10+ (recomendado)



pygame



opencv-python (necessário para a cutscene de vídeo)

Instalação

No PowerShell (ou terminal), dentro da pasta do projeto:

pip install pygame opencv-python

Como executar

Rode a partir da pasta game/:

cd game
python main.py

Cutscene (vídeo)

Para o vídeo tocar, coloque os arquivos exatamente aqui:





game/assets/video.mp4



game/assets/audio.mp3

Observação: os nomes/imports são case-sensitive no código. Se seus arquivos estiverem como AUDIO.MP3 ou VIDEO.MP4, renomeie para audio.mp3 e video.mp4.

Controles durante o vídeo:





ENTER / ESPAÇO / ESC: pular



Clique do mouse: pular

Controles do jogo





Mouse: clicar em botões / escolhas



ENTER / ESPAÇO: avançar diálogos/telas (quando disponível)



ESC: fechar painéis (ex.: status no mapa) / voltar (quando aplicável)



R: tentar novamente (na tela de Game Over)

Estrutura do projeto

game/
├── main.py
├── classes/
│   ├── Personagem.py
│   ├── Heroi.py
│   ├── vilao.py
├── data/
│   └── perguntas.py
├── states/
│   ├── intro_state.py
│   ├── hero_select_state.py
│   ├── video_state.py
│   ├── prologue_state.py
│   ├── battle_state.py
│   ├── map_state.py
│   ├── shop_state.py
│   ├── levelup_state.py
│   ├── game_over_state.py
│   └── victory_state.py
├── utils/
│   ├── constants.py
│   ├── game_state_manager.py
│   └── ui.py
└── assets/
    ├── video.mp4
    └── audio.mp3
        artraws.png
        drakon.png
        fundo1.png
        inicio.png
        luna.png
        sentinela.png
