#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from decimal import Decimal
from pathlib import Path

EXPECTED_TRACK_COUNT = 48
REPEATS_PER_TRACK = 3
DEFAULT_PARTS = 3
OUTPUT_BASENAME = "montagem_todas_as_musicas_3x"


def numeric_prefix_key(path: Path) -> tuple[Decimal, str]:
    match = re.match(r"^\s*(\d+(?:\.\d+)?)", path.name)
    if match:
        return Decimal(match.group(1)), path.name.casefold()
    return Decimal("Infinity"), path.name.casefold()


def discover_tracks(input_dir: Path) -> list[Path]:
    return sorted(
        [
            path
            for path in input_dir.iterdir()
            if path.is_file() and path.suffix.casefold() == ".mp3"
        ],
        key=numeric_prefix_key,
    )


def validate_tracks(
    tracks: list[Path],
    expected_count: int = EXPECTED_TRACK_COUNT,
    repeats: int = REPEATS_PER_TRACK,
) -> None:
    if len(tracks) != expected_count:
        raise ValueError(
            f"Esperadas {expected_count} faixas MP3 na raiz, mas foram encontradas {len(tracks)}."
        )

    validate_sequence(build_sequence(tracks, repeats=repeats), tracks, repeats=repeats)


def validate_sequence(
    sequence: list[Path],
    tracks: list[Path],
    repeats: int = REPEATS_PER_TRACK,
) -> None:
    expected_entries = len(tracks) * repeats
    if len(sequence) != expected_entries:
        raise ValueError(
            f"Sequência inválida: esperado {expected_entries} entradas, mas foram geradas {len(sequence)}."
        )

    counts = Counter(sequence)
    invalid_counts = {
        name: count for name, count in counts.items() if count != repeats
    }
    if invalid_counts:
        details = ", ".join(
            f"{path.name}={count}"
            for path, count in sorted(invalid_counts.items(), key=lambda item: item[0].name.casefold())
        )
        raise ValueError(f"Cada faixa deve aparecer {repeats} vezes. Contagens inválidas: {details}")

    for index, track in enumerate(tracks):
        start = index * repeats
        chunk = sequence[start : start + repeats]
        if len(chunk) != repeats or any(item != track for item in chunk):
            raise ValueError(
                "A ordem/repetição 3x consecutiva está incorreta em "
                f"{track.name} (posição {index + 1})."
            )


def validate_parts(
    parts: list[list[Path]],
    tracks: list[Path],
    repeats: int = REPEATS_PER_TRACK,
    expected_parts: int = DEFAULT_PARTS,
) -> None:
    if len(parts) != expected_parts:
        raise ValueError(f"Esperadas exatamente {expected_parts} partes, mas foram geradas {len(parts)}.")

    flattened = [item for part in parts for item in part]
    validate_sequence(flattened, tracks, repeats=repeats)


def build_sequence(tracks: list[Path], repeats: int = REPEATS_PER_TRACK) -> list[Path]:
    return [track for track in tracks for _ in range(repeats)]


def split_sequence(
    tracks: list[Path],
    repeats: int = REPEATS_PER_TRACK,
    parts: int = DEFAULT_PARTS,
) -> list[list[Path]]:
    if parts <= 0:
        raise ValueError("O número de partes deve ser maior que zero.")

    groups = [[track] * repeats for track in tracks]
    group_count = len(groups)
    base_size, remainder = divmod(group_count, parts)

    result: list[list[Path]] = []
    start = 0
    for part_index in range(parts):
        size = base_size + (1 if part_index < remainder else 0)
        selected_groups = groups[start : start + size]
        result.append([item for group in selected_groups for item in group])
        start += size

    return result


def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg"):
        return
    raise RuntimeError(
        "ffmpeg não encontrado no PATH. Instale o ffmpeg ou execute pelo workflow do GitHub Actions."
    )


def write_concat_list(sequence: list[Path], destination: Path) -> None:
    lines = []
    for path in sequence:
        escaped_path = path.resolve().as_posix().replace("'", "'\\''")
        lines.append(f"file '{escaped_path}'")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def concat_sequence_to_mp3(sequence: list[Path], output_file: Path) -> None:
    ensure_ffmpeg_available()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="ffmpeg-concat-") as temp_dir:
        concat_file = Path(temp_dir) / "concat.txt"
        write_concat_list(sequence, concat_file)

        command = [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-vn",
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(output_file),
        ]

        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or "stderr vazio"
            raise RuntimeError(
                f"Falha ao executar ffmpeg para gerar {output_file.name}: {stderr}"
            )


def generate_parts(
    input_dir: Path,
    output_dir: Path,
    expected_count: int = EXPECTED_TRACK_COUNT,
    repeats: int = REPEATS_PER_TRACK,
    parts: int = DEFAULT_PARTS,
) -> list[Path]:
    tracks = discover_tracks(input_dir)
    validate_tracks(tracks, expected_count=expected_count, repeats=repeats)

    if parts != DEFAULT_PARTS:
        raise ValueError("Esta automação foi configurada para gerar exatamente 3 partes.")

    split_parts = split_sequence(tracks, repeats=repeats, parts=parts)
    validate_parts(split_parts, tracks, repeats=repeats, expected_parts=parts)
    output_files: list[Path] = []
    for index, part_sequence in enumerate(split_parts, start=1):
        output_file = output_dir / f"{OUTPUT_BASENAME}_parte_{index}.mp3"
        concat_sequence_to_mp3(part_sequence, output_file)
        output_files.append(output_file)

    return output_files


def print_summary(tracks: list[Path], parts: list[list[Path]] | None = None) -> None:
    print(f"Faixas encontradas: {len(tracks)}")
    print(f"Entradas totais na sequência: {len(tracks) * REPEATS_PER_TRACK}")
    if parts is not None:
        for index, part in enumerate(parts, start=1):
            print(f"Parte {index}: {len(part)} entradas")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera a montagem das músicas repetindo cada faixa 3 vezes consecutivas."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Valida a ordem e a repetição 3x.")
    validate_parser.add_argument("--input-dir", default=".", help="Diretório com os MP3.")
    validate_parser.add_argument("--expected-count", type=int, default=EXPECTED_TRACK_COUNT)

    generate_parser = subparsers.add_parser(
        "generate", help="Gera a montagem dividida em exatamente 3 partes."
    )
    generate_parser.add_argument("--input-dir", default=".", help="Diretório com os MP3.")
    generate_parser.add_argument(
        "--output-dir",
        default="output/montagem_3_partes",
        help="Diretório de saída para as 3 partes geradas.",
    )
    generate_parser.add_argument("--expected-count", type=int, default=EXPECTED_TRACK_COUNT)
    generate_parser.add_argument("--parts", type=int, default=DEFAULT_PARTS)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir).resolve()
    tracks = discover_tracks(input_dir)

    if args.command == "validate":
        validate_tracks(tracks, expected_count=args.expected_count)
        parts = split_sequence(tracks)
        validate_parts(parts, tracks)
        print_summary(tracks, parts)
        return 0

    if args.command == "generate":
        output_dir = Path(args.output_dir).resolve()
        output_files = generate_parts(
            input_dir=input_dir,
            output_dir=output_dir,
            expected_count=args.expected_count,
            parts=args.parts,
        )
        parts = split_sequence(tracks)
        print_summary(tracks, parts)
        for output_file in output_files:
            print(f"Gerado: {output_file}")
        return 0

    raise ValueError(f"Comando inválido: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
