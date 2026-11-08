def test_saude_responde_ok(cliente):
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_front_end_local_pode_chamar_a_api(cliente):
    resposta = cliente.get("/saude", headers={"Origin": "http://localhost:5173"})
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"
