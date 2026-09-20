import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gerar_montagem_todas_as_musicas_3x as montagem


class MontagemTests(unittest.TestCase):
    def test_discover_tracks_orders_numeric_prefixes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for name in [
                "10. Dez.mp3",
                "2. Dois.mp3",
                "16.1 Dezesseis e um.mp3",
                "16. Dezesseis.mp3",
            ]:
                (root / name).write_bytes(b"")

            tracks = montagem.discover_tracks(root)

        self.assertEqual(
            [track.name for track in tracks],
            [
                "2. Dois.mp3",
                "10. Dez.mp3",
                "16. Dezesseis.mp3",
                "16.1 Dezesseis e um.mp3",
            ],
        )

    def test_validate_tracks_rejects_wrong_count(self):
        tracks = [Path(f"{index}. faixa.mp3") for index in range(1, 48)]

        with self.assertRaisesRegex(ValueError, "Esperadas 48 faixas MP3 na raiz"):
            montagem.validate_tracks(tracks)

    def test_split_sequence_creates_three_equal_parts_without_breaking_triplets(self):
        tracks = [Path(f"{index}. faixa.mp3") for index in range(1, 49)]

        parts = montagem.split_sequence(tracks, repeats=3, parts=3)

        self.assertEqual(len(parts), 3)
        self.assertEqual([len(part) for part in parts], [48, 48, 48])
        self.assertEqual(parts[0][:3], [tracks[0], tracks[0], tracks[0]])
        self.assertEqual(parts[1][:3], [tracks[16], tracks[16], tracks[16]])
        self.assertEqual(parts[2][:3], [tracks[32], tracks[32], tracks[32]])

    def test_validate_sequence_rejects_non_consecutive_triplets(self):
        tracks = [Path(f"{index}. faixa.mp3") for index in range(1, 49)]
        invalid_sequence = []
        for index, track in enumerate(tracks):
            if index == 0:
                invalid_sequence.extend([track, tracks[1], track])
            elif index == 1:
                invalid_sequence.extend([track, tracks[0], track])
            else:
                invalid_sequence.extend([track, track, track])

        with self.assertRaisesRegex(ValueError, "ordem/repetição 3x consecutiva"):
            montagem.validate_sequence(invalid_sequence, tracks)

    def test_validate_tracks_and_parts_accept_real_repository_flow(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index in range(1, 49):
                (root / f"{index}. faixa.mp3").write_bytes(b"")

            tracks = montagem.discover_tracks(root)
            montagem.validate_tracks(tracks)
            montagem.validate_parts(montagem.split_sequence(tracks), tracks)

    def test_validate_parts_rejects_split_triplet_between_parts(self):
        tracks = [Path(f"{index}. faixa.mp3") for index in range(1, 49)]
        parts = montagem.split_sequence(tracks)
        invalid_parts = [
            parts[0][:-1],
            [parts[0][-1], *parts[1]],
            parts[2],
        ]

        with self.assertRaisesRegex(ValueError, "não respeita a divisão esperada"):
            montagem.validate_parts(invalid_parts, tracks)

    def test_generate_parts_rejects_any_number_other_than_three(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index in range(1, 49):
                (root / f"{index}. faixa.mp3").write_bytes(b"")

            with self.assertRaisesRegex(ValueError, "exatamente 3 partes"):
                montagem.generate_parts(root, root / "saida", parts=2)

    def test_generate_parts_creates_three_expected_output_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index in range(1, 49):
                (root / f"{index}. faixa.mp3").write_bytes(b"")

            with patch.object(montagem, "concat_sequence_to_mp3") as concat_mock:
                outputs = montagem.generate_parts(root, root / "saida", parts=3)

        self.assertEqual(
            [output.name for output in outputs],
            [
                "montagem_todas_as_musicas_3x_parte_1.mp3",
                "montagem_todas_as_musicas_3x_parte_2.mp3",
                "montagem_todas_as_musicas_3x_parte_3.mp3",
            ],
        )
        self.assertEqual(concat_mock.call_count, 3)
        self.assertEqual([len(call.args[0]) for call in concat_mock.call_args_list], [48, 48, 48])


if __name__ == "__main__":
    unittest.main()
