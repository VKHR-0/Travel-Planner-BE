from dataclasses import dataclass

import httpx


ARTIC_BASE_URL = "https://api.artic.edu/api/v1"


class ArticClientError(Exception):
    pass


class ArticArtworkNotFoundError(ArticClientError):
    pass


@dataclass(slots=True)
class ArticArtwork:
    external_id: int
    title: str
    artist_title: str | None
    image_id: str | None


class ArticClient:
    def __init__(self, base_url: str = ARTIC_BASE_URL, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def get_artwork(self, external_id: int) -> ArticArtwork:
        url = f"{self._base_url}/artworks/{external_id}"

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url)

        if response.status_code == 404:
            raise ArticArtworkNotFoundError(f"Artwork {external_id} was not found")

        if response.status_code >= 400:
            raise ArticClientError(
                f"Art Institute API request failed with status {response.status_code}"
            )

        payload = response.json()
        data = payload.get("data")
        if not data or not data.get("id") or not data.get("title"):
            raise ArticArtworkNotFoundError(f"Artwork {external_id} was not found")

        return ArticArtwork(
            external_id=int(data["id"]),
            title=data["title"],
            artist_title=data.get("artist_title"),
            image_id=data.get("image_id"),
        )
