from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import sessionmaker

from app.adaptadores.persistencia.modelos import Base, ConsoleModelo, FaixaEtariaModelo, GeneroModelo

GENEROS = ["Ação", "Aventura", "RPG", "Esporte", "Corrida", "Luta", "Estratégia",
           "Simulação", "Quebra-cabeça", "Terror", "Plataforma", "Tiro"]
FAIXAS = ["Livre", "10 anos", "12 anos", "14 anos", "16 anos", "18 anos"]
CONSOLES = ["PC", "Atari 2600", "NES", "Super Nintendo", "Mega Drive", "Nintendo 64",
            "PlayStation", "PlayStation 2", "PlayStation 3", "PlayStation 4", "PlayStation 5",
            "Xbox", "Xbox 360", "Xbox One", "Xbox Series", "GameCube", "Wii", "Nintendo Switch",
            "Game Boy", "Nintendo DS", "PSP"]


def criar_fabrica_de_sessoes(url: str):
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    motor = create_engine(url, connect_args=args, pool_pre_ping=True)
    return motor, sessionmaker(bind=motor, expire_on_commit=False)


def preparar_banco(motor, fabrica) -> None:
    """Cria as tabelas e os dados fixos (gêneros, faixas etárias, consoles) se faltarem."""
    Base.metadata.create_all(motor)
    _adicionar_colunas_novas(motor)
    with fabrica() as s:
        for modelo, campo, valores in (
            (GeneroModelo, "nome", GENEROS),
            (FaixaEtariaModelo, "descricao", FAIXAS),
            (ConsoleModelo, "nome", CONSOLES),
        ):
            if s.scalar(select(modelo.id).limit(1)) is None:
                s.add_all(modelo(**{campo: v}) for v in valores)
        s.commit()


def _adicionar_colunas_novas(motor) -> None:
    """Migração leve: bancos criados em versões antigas ganham as colunas que surgiram depois.

    (Quando o sistema tiver dados reais, trocar por migrações versionadas com Alembic.)
    """
    colunas = {c["name"] for c in inspect(motor).get_columns("lancamento")}
    if "capa_url" not in colunas:
        with motor.begin() as conexao:
            conexao.execute(text("ALTER TABLE lancamento ADD COLUMN capa_url VARCHAR(300)"))
