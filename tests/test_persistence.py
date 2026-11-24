import tempfile
import unittest
from pathlib import Path

from persistence import SQLiteStateStore


class SQLiteStateStoreTests(unittest.TestCase):
    def test_round_trips_state_per_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "state.db"
            first = SQLiteStateStore(database, profile_id="first")
            second = SQLiteStateStore(database, profile_id="second")

            first.save({"learner_profile": {"level": "Beginner"}})
            second.save({"learner_profile": {"level": "Advanced"}})

            self.assertEqual(
                first.load(),
                {"learner_profile": {"level": "Beginner"}}
            )
            self.assertEqual(
                second.load(),
                {"learner_profile": {"level": "Advanced"}}
            )

    def test_missing_profile_returns_none(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteStateStore(Path(directory) / "state.db")
            self.assertIsNone(store.load())

    def test_round_trips_video_transcript_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteStateStore(Path(directory) / "state.db")
            chunks = [{"text": "local transcript", "start": "00:00"}]

            store.save_video_transcript("video-hash", "tiny", chunks)

            self.assertEqual(
                store.load_video_transcript("video-hash", "tiny"),
                chunks
            )
            self.assertIsNone(
                store.load_video_transcript("other-video", "tiny")
            )


if __name__ == "__main__":
    unittest.main()
