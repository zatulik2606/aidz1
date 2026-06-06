import unittest

from src.dialog_store import get_thread_id, start_new_thread


class DialogStoreThreadTests(unittest.TestCase):
    def test_get_thread_id_is_stable_for_user(self) -> None:
        first = get_thread_id(111)
        second = get_thread_id(111)
        self.assertEqual(first, second)

    def test_start_new_thread_rotates_thread_id(self) -> None:
        first = start_new_thread(222)
        second = start_new_thread(222)
        self.assertNotEqual(first, second)
