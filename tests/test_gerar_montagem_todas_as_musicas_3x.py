import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
