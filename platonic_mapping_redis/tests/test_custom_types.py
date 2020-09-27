import dataclasses
import json
from dataclasses import dataclass, asdict
from typing import NewType

import pytest

from platonic_mapping_redis.mapping import RedisDBMutableMapping
from typecasts import DefaultTypecasts

CountryCode = NewType('CountryCode', str)


@dataclass
class Country:
    """Some data about country."""

    name: str
    capital: str


class CountryByCode(RedisDBMutableMapping[CountryCode, Country]):
    """Store country properties by ISO code."""


@DefaultTypecasts.register(Country, bytes)
def country_to_bytes(country: Country) -> bytes:
    """Convert Country to bytes."""
    return json.dumps(asdict(country)).encode()


@DefaultTypecasts.register(bytes, Country)
def bytes_to_country(raw_country: bytes) -> Country:
    return Country(**json.loads(raw_country))


@pytest.fixture
def countries() -> CountryByCode:
    countries = CountryByCode()

    countries[CountryCode('US')] = Country(
        name='United States of America',
        capital='Washington D. C.'
    )

    countries.update({
        CountryCode('AU'): Country(name='Australia', capital='Canberra'),
#        'RU': 'b',
    })

    return countries


def test_get(countries: CountryByCode):
    assert countries[
        CountryCode('US')
    ].name == 'United States of America'


def test_iter(countries: CountryByCode):
    assert set(iter(countries)) == {
        CountryCode('US'),
        CountryCode('AU'),
    }
