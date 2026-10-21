"""Testes da propria infraestrutura de verificacao."""

import os

from conftest import extrair, listar_fontes, RAIZ


def test_fontes_listadas():
    assert listar_fontes("nt"), "nenhuma NT em fontes/ (acervo ausente?)"
    assert listar_fontes("moc"), "nenhum MOC em fontes/ (acervo ausente?)"


def test_extrair_nao_escreve_no_repositorio():
    pdf = os.path.join(RAIZ, "fontes", "mdfe", "notas-tecnicas", "MDFe_NT_2026_001_v1.00.pdf")
    stdout_dir = RAIZ / "catalogo" / "nt" / "mdfe" / "stdout"
    antes = {p: p.stat().st_mtime for p in stdout_dir.glob("*")} if stdout_dir.exists() else {}
    dados = extrair(pdf, "nt")
    depois = {p: p.stat().st_mtime for p in stdout_dir.glob("*")} if stdout_dir.exists() else {}
    assert dados["nt"] == "2026.001"
    assert antes == depois, "a extracao de teste escreveu em catalogo/ do repositorio"


def test_guarda_de_fontes_detecta_alteracoes(tmp_path):
    """O guarda de somente-leitura precisa enxergar criacao, remocao e alteracao."""
    from conftest import diferencas_snapshot, snapshot_dir

    (tmp_path / "a.txt").write_text("um")
    (tmp_path / "b.txt").write_text("dois")
    antes = snapshot_dir(tmp_path)

    (tmp_path / "a.txt").write_text("UM")
    (tmp_path / "b.txt").unlink()
    (tmp_path / "c.txt").write_text("tres")
    criados, removidos, alterados = diferencas_snapshot(antes, snapshot_dir(tmp_path))

    assert (criados, removidos, alterados) == (["c.txt"], ["b.txt"], ["a.txt"])


def test_fontes_existem_no_snapshot():
    from conftest import snapshot_dir

    assert len(snapshot_dir(RAIZ / "fontes")) > 100, "acervo de fontes/ inesperadamente pequeno"
