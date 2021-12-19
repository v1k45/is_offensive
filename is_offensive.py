#!/usr/bin/python3
import argparse
import asyncio
import json
import os
import typing
from dataclasses import dataclass
from itertools import islice

import httpx


@dataclass
class SearchResult:
    word: str
    is_offensive: typing.Optional[bool] = None
    error: typing.Optional[str] = None


class DictionaryClient(httpx.AsyncClient):
    BASE_URL = "https://dictionaryapi.com/api/v3/references/collegiate/json/"
    API_KEY = ""
    ERROR_WORD_NOT_FOUND = "Could find a word matching query."
    ERROR_REQUEST_FAILED = "Failed to perform the request."

    def __init__(self, *args, **kwargs):
        super().__init__(base_url=self.BASE_URL, *args, **kwargs)
        self.API_KEY = os.environ.get("DICTIONARY_API_KEY", "")

    async def search(self, word: str) -> SearchResult:
        """
        Search a word in the dictionary and returns the result based on first occurence.
        """
        result = SearchResult(word)
        try:
            response = await self.get(word, params={"key": self.API_KEY})
        except httpx.RequestError:
            result.error = self.ERROR_REQUEST_FAILED
            return result

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            # when the API Key is invalid, the API does not return a valid json.
            result.error = response.text
            return result

        # if the result is empty or invalid, treat the word as invalid.
        if not response_json or not isinstance(response_json[0], dict):
            result.error = self.ERROR_WORD_NOT_FOUND
        else:
            result.is_offensive = response_json[0]["meta"]["offensive"]

        return result

    def bulk_search(self, wordlist: typing.Iterable, limit: int = 50):
        """
        Search multiple words together.
        """
        words = [word.strip() for word in islice(wordlist, limit) if word.strip()]
        return asyncio.gather(*[self.search(word) for word in words])


async def file_search(wordlist: typing.Iterable):
    """
    Perform bulk word searches using text files.

    Parameters
    ----------
    wordlist: file
    """
    async with DictionaryClient() as client:
        try:
            results = await client.bulk_search(wordlist)
        except UnicodeDecodeError:
            print(
                "ERROR: Invalid file. Select a plaintext file with words separated by lines."
            )
            return

    offensive_word_count = 0
    inoffensive_word_count = 0
    errored_word_count = 0
    for result in results:
        if result.error:
            errored_word_count += 1
        elif result.is_offensive:
            offensive_word_count += 1
        else:
            inoffensive_word_count += 1

    print(f"Offensive word count: {offensive_word_count}")
    print(f"Inoffensive word count: {inoffensive_word_count}")
    print(f"Errored word count: {errored_word_count}")


async def interactive_search():
    """
    Start an interactive shell to search words.
    """

    async def shell():
        word = input("Enter a word to search: ").strip()
        if not word:
            return

        result = await client.search(word)
        if result.error:
            print(f"ERROR: {result.error}")
        else:
            print("yes" if result.is_offensive else "no")

    async with DictionaryClient() as client:
        while True:
            try:
                await shell()
            except KeyboardInterrupt:
                break


async def main():
    parser = argparse.ArgumentParser(description="Find out if a word is offensive.")
    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r"),
        help="File containg list of words to search",
        default=None,
    )
    args = parser.parse_args()

    if not DictionaryClient.API_KEY:
        print("API Key not found. Set DICTIONARY_API_KEY environment variable.")
        print('Run "export DICTIONARY_API_KEY=your-api-key-here" and retry.')
        return

    if args.file:
        await file_search(args.file)
    else:
        await interactive_search()


if __name__ == "__main__":
    asyncio.run(main())
