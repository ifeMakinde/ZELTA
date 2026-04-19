# tests/test_nlp_scraper.py

import pytest
import aiohttp
from nlp.scraper import ZeltaNewsScraper


@pytest.fixture
async def scraper():
    async with aiohttp.ClientSession() as session:
        yield ZeltaNewsScraper(session=session)


@pytest.mark.asyncio
async def test_normalize_title(scraper):
    raw_title = "   BREAKING:  CBN Devalues Naira \n\n  "
    clean_title = scraper.normalize_title(raw_title)
    assert clean_title == "breaking: cbn devalues naira"


@pytest.mark.asyncio
async def test_is_relevant_campus_news(scraper):
    assert scraper.is_relevant("OAU management announces new tuition fee") is True
    assert scraper.is_relevant("ASUU strike update for students") is True


@pytest.mark.asyncio
async def test_is_relevant_macro_news(scraper):
    assert scraper.is_relevant("Inflation hits new high in Nigeria") is True
    assert scraper.is_relevant("How to cook jollof rice") is False  # Irrelevant


@pytest.mark.asyncio
async def test_build_absolute_url(scraper):
    base_url = "https://nairametrics.com"
    rel_link = "/2026/04/16/economy-update"

    abs_link = scraper.build_absolute_url(base_url, rel_link)
    assert abs_link == "https://nairametrics.com/2026/04/16/economy-update"