"""Converte objetos do núcleo em JSON para o front-end."""
from datetime import date, datetime


def _data_hora(valor: datetime | None):
    return valor.isoformat() + "Z" if valor else None  # o banco guarda em UTC


def usuario(u) -> dict:
    return {"id": u.id, "nome": u.nome, "email": u.email, "idioma": u.idioma}


def jogo(v) -> dict:
    return {
        "id": v.id, "nome": v.nome, "ano": v.ano, "historia": v.historia,
        "capa_url": f"/capas/{v.capa}" if v.capa else None,
        "genero": {"id": v.genero_id, "nome": v.genero},
        "faixa_etaria": {"id": v.faixa_etaria_id, "descricao": v.faixa_etaria},
        "consoles": [{"id": i, "nome": n} for i, n in zip(v.console_ids, v.consoles)],
        "cadastrado_por": v.cadastrado_por, "cadastrado_em": _data_hora(v.cadastrado_em),
        "alterado_por": v.alterado_por,
        "excluido": v.excluido_em is not None, "excluido_em": _data_hora(v.excluido_em),
        "excluido_por": v.excluido_por,
        "nota_media": v.nota_media, "total_avaliacoes": v.total_avaliacoes,
    }


def avaliacao(a) -> dict:
    return {"usuario_id": a.usuario_id, "usuario": a.usuario, "nota": a.nota,
            "comentario": a.comentario, "criada_em": _data_hora(a.criada_em)}


def lancamento(l) -> dict:
    return {"id": l.id, "nome": l.nome, "plataformas": l.plataformas, "origem": l.origem, "capa_url": l.capa_url,
            "data_lancamento": l.data_lancamento.isoformat() if isinstance(l.data_lancamento, date) else None,
            "atualizado_em": _data_hora(l.atualizado_em)}


def referencias(r) -> dict:
    return {
        "generos": [{"id": g.id, "nome": g.nome} for g in r.generos],
        "faixas_etarias": [{"id": f.id, "descricao": f.descricao} for f in r.faixas_etarias],
        "consoles": [{"id": c.id, "nome": c.nome} for c in r.consoles],
    }

