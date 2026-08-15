"""Conserta o `.venv` depois que a pasta do projeto foi movida ou renomeada.

## O problema

Um virtualenv grava **caminhos absolutos** em dois lugares. Renomeie ou mova a
pasta do projeto e os dois apontam para o vazio:

1. **`Lib/site-packages/__editable__.*.pth`** — o caminho de `src/` do install
   editable. Quebra `import adaptive_offers` e, com ele, `adaptive-offers serve`,
   a CLI e o dashboard.
2. **`Scripts/*.exe`** — cada console script do pip embute o caminho absoluto do
   `python.exe` do venv. Quebra `streamlit`, `mlflow`, `uvicorn`, `pytest` e até
   o `pip`, com a mensagem:
   `Fatal error in launcher: Unable to create process using '...'`

O sintoma é traiçoeiro porque **`python -m <modulo>` continua funcionando** (não
passa pelo launcher) e **`pytest` passa** (o pyproject injeta `src` no path). Dá
para achar que está tudo bem e descobrir na hora da demo que não está.

## Uso

    python scripts\\fix_venv_paths.py            # mostra o que faria (dry-run)
    python scripts\\fix_venv_paths.py --apply    # aplica

O patch dos `.exe` é feito **byte a byte, preservando o tamanho do arquivo**: só
roda se o caminho antigo e o novo tiverem exatamente o mesmo comprimento (o caso
de `grupo-64` → `grupo-74`). Se os tamanhos diferirem, o script se recusa a
tocar nos executáveis e manda reinstalar os pacotes — porque mexer no tamanho
corromperia os offsets do payload embutido.

Se este script não resolver, o caminho seguro é recriar o ambiente:

    Remove-Item -Recurse -Force .venv
    python -m venv .venv
    .\\.venv\\Scripts\\Activate.ps1
    pip install -e ".[dev,bi]"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENV = PROJECT_ROOT / ".venv"


def find_stale_pth() -> list[tuple[Path, str, str]]:
    """Arquivos .pth cujo conteúdo não aponta para a pasta atual do projeto."""
    out = []
    site_packages = VENV / "Lib" / "site-packages"
    expected = str(PROJECT_ROOT / "src")
    for pth in site_packages.glob("__editable__*.pth"):
        current = pth.read_text(encoding="utf-8").strip()
        # .pth de import hook (começa com "import") não carrega caminho simples
        if current.startswith("import"):
            continue
        if current != expected:
            out.append((pth, current, expected))
    return out


def find_stale_exes() -> tuple[list[Path], bytes, bytes]:
    """Launchers que embutem um python.exe diferente do que está no venv."""
    scripts = VENV / "Scripts"
    correct = str(scripts / "python.exe").encode("utf-8")
    stale: list[Path] = []
    wrong = b""

    for exe in sorted(scripts.glob("*.exe")):
        blob = exe.read_bytes()
        if correct in blob:
            continue
        # procura um caminho de python.exe embutido que NÃO seja o correto
        marker = rb"\.venv\Scripts\python.exe"
        idx = blob.find(marker)
        if idx == -1:
            continue  # binário de verdade (python.exe, ruff.exe), não é launcher
        start = blob.rfind(b"#!", 0, idx)
        if start == -1:
            start = blob.rfind(b"\x00", 0, idx) + 1
        else:
            start += 2
        embedded = blob[start : idx + len(marker)]
        if not wrong:
            wrong = embedded
        stale.append(exe)

    return stale, wrong, correct


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--apply", action="store_true", help="aplica as correções")
    args = parser.parse_args()

    if not VENV.exists():
        print(f"[erro] .venv não encontrado em {VENV}")
        return 1

    print(f"projeto : {PROJECT_ROOT}")
    print(f"venv    : {VENV}\n")

    problems = 0

    # --- 1. arquivos .pth ---------------------------------------------------
    stale_pth = find_stale_pth()
    if stale_pth:
        problems += len(stale_pth)
        print(f"[.pth] {len(stale_pth)} arquivo(s) com caminho obsoleto:")
        for pth, current, expected in stale_pth:
            print(f"   {pth.name}")
            print(f"     atual   : {current}")
            print(f"     correto : {expected}")
        if args.apply:
            for pth, _, expected in stale_pth:
                pth.write_text(expected + "\n", encoding="utf-8")
            print("   -> corrigido\n")
        else:
            print("   -> rode com --apply (ou: pip install -e . --no-deps)\n")
    else:
        print("[.pth] ok\n")

    # --- 2. launchers .exe --------------------------------------------------
    stale_exes, wrong, correct = find_stale_exes()
    if stale_exes:
        problems += len(stale_exes)
        print(f"[.exe] {len(stale_exes)} launcher(s) apontando para o python errado:")
        print(f"   embutido: {wrong.decode('utf-8', 'replace')}")
        print(f"   correto : {correct.decode('utf-8', 'replace')}")
        print(f"   exemplos: {', '.join(e.name for e in stale_exes[:8])}"
              f"{' …' if len(stale_exes) > 8 else ''}")

        if len(wrong) != len(correct):
            print("\n   [!] Os caminhos têm TAMANHOS DIFERENTES — não dá para corrigir")
            print("       in-place sem corromper os executáveis. Reinstale os pacotes:")
            print('       python -m pip install --force-reinstall --no-deps streamlit mlflow uvicorn pytest pip')
            return 1

        if args.apply:
            for exe in stale_exes:
                blob = exe.read_bytes()
                patched = blob.replace(wrong, correct)
                if len(patched) != len(blob):
                    print(f"   [!] {exe.name}: tamanho mudaria — pulado")
                    continue
                exe.write_bytes(patched)
            print("   -> corrigido\n")
        else:
            print("   -> rode com --apply\n")
    else:
        print("[.exe] ok\n")

    if problems == 0:
        print("Nada a corrigir: o .venv está consistente com a pasta atual.")
    elif args.apply:
        print(f"{problems} problema(s) corrigido(s). Valide com:")
        print("   python -c \"import adaptive_offers; print('OK')\"")
        print("   streamlit --version")
        print("   mlflow --version")
    return 0


if __name__ == "__main__":
    sys.exit(main())
