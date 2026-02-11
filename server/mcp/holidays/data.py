"""Built-in holiday / special day database.

Turkiye + uluslararasi ozel gunler. Yeni gunler kolayca eklenebilir.
Tarih formati: (ay, gun). Yil bazli olanlar icin (yil, ay, gun).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SpecialDay:
    name: str
    date: tuple[int, int]  # (month, day)
    emoji: str
    category: str  # religious, national, international, commercial, awareness
    country: str | None  # None = international
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "month": self.date[0],
            "day": self.date[1],
            "emoji": self.emoji,
            "category": self.category,
            "country": self.country,
            "description": self.description,
        }


# ---- Turkiye ----

TR_HOLIDAYS = [
    SpecialDay("Yilbasi", (1, 1), "🎉", "international", "TR", "Yeni yil kutlamasi"),
    SpecialDay("Ogretmenler Gunu", (11, 24), "📚", "national", "TR", "Turkiye'de ogretmenler gunu"),
    SpecialDay("Ulusal Egemenlik ve Cocuk Bayrami", (4, 23), "🇹🇷", "national", "TR"),
    SpecialDay("Isci Bayrami", (5, 1), "⚒️", "national", "TR"),
    SpecialDay("Ataturk'u Anma, Genclik ve Spor Bayrami", (5, 19), "🇹🇷", "national", "TR"),
    SpecialDay("Zafer Bayrami", (8, 30), "🇹🇷", "national", "TR"),
    SpecialDay("Cumhuriyet Bayrami", (10, 29), "🇹🇷", "national", "TR"),
]

# ---- Uluslararasi ----

INTL_HOLIDAYS = [
    SpecialDay("Sevgililer Gunu", (2, 14), "❤️", "commercial", None, "Valentine's Day"),
    SpecialDay("Dunya Kadinlar Gunu", (3, 8), "💜", "awareness", None),
    SpecialDay("Anneler Gunu", (5, 11), "🌸", "commercial", None, "Mayis'in ikinci pazari (yaklasik)"),
    SpecialDay("Babalar Gunu", (6, 15), "👔", "commercial", None, "Haziran'in ucuncu pazari (yaklasik)"),
    SpecialDay("Dunya Cevre Gunu", (6, 5), "🌍", "awareness", None),
    SpecialDay("Dunya Muzik Gunu", (6, 21), "🎵", "awareness", None),
    SpecialDay("Halloween", (10, 31), "🎃", "commercial", None),
    SpecialDay("Black Friday", (11, 28), "🛒", "commercial", None, "Kasim'in dorduncu cumasi (yaklasik)"),
    SpecialDay("Noel", (12, 25), "🎄", "religious", None),
    SpecialDay("Dunya Saglik Gunu", (4, 7), "🏥", "awareness", None),
    SpecialDay("Dunya Gida Gunu", (10, 16), "🍎", "awareness", None),
    SpecialDay("Dunya Kitap Gunu", (4, 23), "📖", "awareness", None),
    SpecialDay("Dunya Su Gunu", (3, 22), "💧", "awareness", None),
    SpecialDay("Dunya Hayvanlar Gunu", (10, 4), "🐾", "awareness", None),
    SpecialDay("Dunya Cocuk Haklari Gunu", (11, 20), "👶", "awareness", None),
    SpecialDay("Dunya Spor Gunu", (4, 6), "🏅", "awareness", None),
    SpecialDay("Yilbasi Gecesi", (12, 31), "🥂", "international", None),
]

ALL_HOLIDAYS = TR_HOLIDAYS + INTL_HOLIDAYS
