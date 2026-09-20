#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
OUTPUT_NAME = "montagem_todas_as_musicas_3x.mp3"


def natural_key(text: str) -> tuple[object, ...]:
    parts = re.split(r"(\d+)", text.casefold())
    key: list[object] = []
    for part in parts:
        if not part:
            continue
        key.append(int(part) if part.isdigit() else part)
    return tuple(key)


def leading_number_key(name: str) -> tuple[int, ...]:
    match = re.match(r"^(\d+(?:\.\d+)*)", name)
    if not match:
        return (sys.maxsize,)
    return tuple(int(part) for part in match.group(1).split("."))


def list_tracks(repo_root: Path, excluded_paths: set[Path] | None = None) -> list[Path]:
    excluded_paths = {path.resolve() for path in (excluded_paths or set())}
    tracks = [
        path
        for path in repo_root.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".mp3"
        and path.resolve() not in excluded_paths
    ]
    return sorted(
        tracks,
        key=lambda path: (leading_number_key(path.name), natural_key(path.name)),
    )


def expanded_tracks(tracks: list[Path]) -> list[Path]:
    return [track for track in tracks for _ in range(3)]


def validate_repetitions(tracks: list[Path]) -> None:
    expanded = expanded_tracks(tracks)
    expected_length = len(tracks) * 3
    if len(expanded) != expected_length:
        raise ValueError("A sequência expandida não possui 3 repetições por faixa.")

    for index, track in enumerate(tracks):
        start = index * 3
        group = expanded[start : start + 3]
        if group != [track, track, track]:
            raise ValueError(f"A faixa {track.name} não aparece 3 vezes em sequência.")


def estimated_output_size_bytes(tracks: list[Path]) -> int:
    return sum(track.stat().st_size for track in tracks) * 3


def ffconcat_escape(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace("'", r"\'")


def write_concat_file(tracks: list[Path], concat_path: Path) -> None:
    with concat_path.open("w", encoding="utf-8") as file:
        file.write("ffconcat version 1.0\n")
        for track in expanded_tracks(tracks):
            file.write(f"file '{ffconcat_escape(track.resolve())}'\n")


def ffmpeg_command(concat_path: Path, output: Path) -> list[str]:
    return [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
        "-c",
        "copy",
        str(output),
    ]


def run_ffmpeg(command: list[str]) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg não está instalado. Instale-o e execute o script novamente, "
            "ou use --dry-run para validar a ordem sem gerar o MP3."
        )
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Gera uma montagem MP3 com todas as músicas da raiz do repositório, "
            "repetindo cada faixa 3 vezes consecutivas."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida e imprime a ordem sem executar o ffmpeg.",
    )
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / OUTPUT_NAME),
        help="Caminho do arquivo MP3 de saída.",
    )
    args = parser.parse_args()

    output_path = Path(args.output).resolve()
    tracks = list_tracks(REPO_ROOT, excluded_paths={output_path})
    if not tracks:
        raise SystemExit("Nenhum arquivo .mp3/.MP3 foi encontrado na raiz do repositório.")

    validate_repetitions(tracks)

    print(f"Faixas encontradas: {len(tracks)}")
    print("Ordem utilizada:")
    for index, track in enumerate(tracks, start=1):
        print(f"{index:02d}. {track.name}")
    print(f"Total de entradas após repetir 3x: {len(tracks) * 3}")
    print(f"Tamanho estimado mínimo do áudio final: {estimated_output_size_bytes(tracks)} bytes")
    print(f"Arquivo de saída esperado: {output_path}")

    if args.dry_run:
        return 0

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".ffconcat",
        prefix="montagem_todas_as_musicas_3x_",
        delete=False,
    ) as temp_file:
        concat_path = Path(temp_file.name)

    try:
        write_concat_file(tracks, concat_path)
        command = ffmpeg_command(concat_path, output_path)
        print("Executando ffmpeg...")
        run_ffmpeg(command)
    finally:
        concat_path.unlink(missing_ok=True)

    print("Montagem gerada com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
