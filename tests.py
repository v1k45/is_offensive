import unittest
from io import StringIO
from unittest import mock

import httpx

from is_offensive import (DictionaryClient, SearchResult, file_search,
                          interactive_search)


class SearchClientTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_search_word_parameters(self):
        client = DictionaryClient()
        client.get = mock.AsyncMock(return_value=httpx.Response(200))

        result = await client.search("hello")

        self.assertIsInstance(result, SearchResult)
        self.assertEqual(result.word, "hello")
        client.get.assert_awaited_once_with(
            "hello", params={"key": DictionaryClient.API_KEY}
        )

    async def test_search_word_error(self):
        client = DictionaryClient()
        client.get = mock.AsyncMock(return_value=httpx.Response(200, text="API error."))

        result = await client.search("hello")

        client.get.assert_awaited_once()
        self.assertEqual(result.error, "API error.")

    async def test_search_word_empty_results(self):
        client = DictionaryClient()
        client.get = mock.AsyncMock(return_value=httpx.Response(200, json=[]))

        result = await client.search("hello")
        client.get.assert_awaited_once()
        client.get.reset_mock()

        self.assertEqual(result.error, DictionaryClient.ERROR_WORD_NOT_FOUND)

        client.get = mock.AsyncMock(
            return_value=httpx.Response(200, json=["some-other-suggestion"])
        )

        result = await client.search("hello")
        client.get.assert_awaited_once()

        self.assertEqual(result.error, DictionaryClient.ERROR_WORD_NOT_FOUND)

    async def test_search_offensive_word(self):
        client = DictionaryClient()
        client.get = mock.AsyncMock(
            return_value=httpx.Response(200, json=[{"meta": {"offensive": True}}])
        )

        result = await client.search("idiot")
        client.get.assert_awaited_once()
        client.get.reset_mock()

        self.assertEqual(result.word, "idiot")
        self.assertTrue(result.is_offensive)
        self.assertIsNone(result.error)

        client.get = mock.AsyncMock(
            return_value=httpx.Response(200, json=[{"meta": {"offensive": False}}])
        )

        result = await client.search("smart")
        client.get.assert_awaited_once()
        client.get.reset_mock()

        self.assertEqual(result.word, "smart")
        self.assertFalse(result.is_offensive)
        self.assertIsNone(result.error)

    async def test_bulk_search(self):
        client = DictionaryClient()
        client.search = mock.AsyncMock(
            side_effect=[
                SearchResult("hello"),
                SearchResult("darkness"),
                SearchResult("my old friend"),
            ]
        )

        results = await client.bulk_search(
            StringIO("hello\ndarkness\n\nmy old friend\n")
        )

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].word, "hello")
        self.assertEqual(results[1].word, "darkness")
        self.assertEqual(results[2].word, "my old friend")

        client.search.assert_has_calls(
            [mock.call("hello"), mock.call("darkness"), mock.call("my old friend")]
        )


class CommandTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_interactive_search(self):
        input_mock = mock.patch(
            "builtins.input",
            side_effect=["hello", "idiot", "", "not a word", KeyboardInterrupt],
        )
        input_mock.start()

        search_mock_value = mock.AsyncMock(
            side_effect=[
                SearchResult("hello", is_offensive=False),
                SearchResult("idiot", is_offensive=True),
                SearchResult("not a word", error="word not found."),
            ]
        )
        with mock.patch(
            "is_offensive.DictionaryClient.search", search_mock_value
        ) as search_mock, mock.patch("builtins.print") as print_mock:
            await interactive_search()

        search_mock.assert_has_calls(
            [mock.call("hello"), mock.call("idiot"), mock.call("not a word")]
        )
        print_mock.assert_has_calls(
            [mock.call("no"), mock.call("yes"), mock.call("ERROR: word not found.")]
        )

        input_mock.stop()

    async def test_file_search(self):
        search_mock_value = mock.AsyncMock(
            return_value=[
                SearchResult("hello", is_offensive=False),
                SearchResult("idiot", is_offensive=True),
                SearchResult("not a word", error="word not found"),
                SearchResult("friend", is_offensive=False),
                SearchResult("suck", is_offensive=True),
            ]
        )
        with mock.patch(
            "is_offensive.DictionaryClient.bulk_search", search_mock_value
        ) as search_mock, mock.patch("builtins.print") as print_mock:
            wordlist = StringIO("\nhello\nidiot\nnot a word\nfriend\nsuck\n")
            await file_search(wordlist)

        search_mock.assert_awaited_once_with(wordlist)
        print_mock.assert_has_calls(
            [
                mock.call("Offensive word count: 2"),
                mock.call("Inoffensive word count: 2"),
                mock.call("Errored word count: 1"),
            ]
        )


if __name__ == "__main__":
    unittest.main()
