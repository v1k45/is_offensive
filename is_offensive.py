import asyncio
import json
import os

import httpx


class Config:
    BASE_URL = "https://dictionaryapi.com/api/v3/references/collegiate/json/"
    API_KEY = os.environ.get("DICTIONARY_API_KEY", "")
    ERROR_WORD_NOT_FOUND = "Could find a word matching query."
    ERROR_INVALID_API_KEY = "Invalid API Key."
    ERROR_REQUEST_FAILED = "Failed to perform the request."


async def search_word(word: str, client: httpx.AsyncClient) -> dict:
    """
    Search a word in the dictionary and returns the first result based on first occurence.
    """
    result = {"word": word, "is_offensive": None, "error": None}
    try:
        response = await client.get(word, params={"key": Config.API_KEY})
    except httpx.RequestError:
        result["error"] = Config.ERROR_REQUEST_FAILED
        return result

    try:
        response_json = response.json()
    except json.JSONDecodeError:
        # when the API Key is invalid, the API does not return a valid json.
        result["error"] = Config.ERROR_INVALID_API_KEY
        return result

    # if the result is empty, or the the list contains possible valid suggestions,
    # treat the word as invalid.
    if not response_json or isinstance(response_json[0], str):
        result["error"] = Config.ERROR_WORD_NOT_FOUND
    else:
        result["is_offensive"] = response_json[0]["meta"]["offensive"]

    return result


async def search_words(words: list[str]):
    async with httpx.AsyncClient(base_url=Config.BASE_URL) as client:
        results = await asyncio.gather(*[search_word(word, client) for word in words])
    print(results)


if __name__ == "__main__":
    asyncio.run(search_words(["suck", "idiot", "animal"]))
