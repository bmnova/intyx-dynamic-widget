"""Sports data source — football-data.org (free tier, API key required).

Free registration at https://www.football-data.org/client/register gives access
to top competitions (Premier League, La Liga, Bundesliga, Serie A, Ligue 1,
Champions League, etc.).

Set FOOTBALL_DATA_API_KEY in environment to enable sports tools.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import requests

from server.config import FOOTBALL_DATA_API_KEY

logger = logging.getLogger(__name__)

FOOTBALL_BASE = "https://api.football-data.org/v4"

# Common competition codes (free tier)
COMPETITIONS = {
    "PL": "Premier League",
    "PD": "La Liga",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "FL1": "Ligue 1",
    "CL": "UEFA Champions League",
    "WC": "FIFA World Cup",
    "EC": "UEFA European Championship",
    "BSA": "Brasileirão",
    "PPL": "Primeira Liga",
    "ELC": "Championship",
    "DED": "Eredivisie",
}


def _headers() -> dict[str, str]:
    return {"X-Auth-Token": FOOTBALL_DATA_API_KEY or ""}


class SportsSource:
    """Fetches football fixture and standings data from football-data.org."""

    @staticmethod
    def fetch_fixtures(competition: str = "PL", days_from_today: int = 3) -> dict[str, Any]:
        """Fetch upcoming/today's fixtures for a competition."""
        if not FOOTBALL_DATA_API_KEY:
            return {"error": "FOOTBALL_DATA_API_KEY not configured", "matches": []}

        today = date.today()
        date_to = today + timedelta(days=max(0, days_from_today))

        try:
            resp = requests.get(
                f"{FOOTBALL_BASE}/competitions/{competition.upper()}/matches",
                params={
                    "dateFrom": today.isoformat(),
                    "dateTo": date_to.isoformat(),
                    "status": "SCHEDULED,LIVE,IN_PLAY,PAUSED",
                },
                headers=_headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("football-data.org fixtures error for: %s", competition)
            raise

        matches = data.get("matches", [])
        competition_info = data.get("competition", {})
        return {
            "competition": competition_info.get("name", competition.upper()),
            "date_from": today.isoformat(),
            "date_to": date_to.isoformat(),
            "total_matches": len(matches),
            "matches": [
                {
                    "id": m.get("id"),
                    "utc_date": m.get("utcDate"),
                    "status": m.get("status"),
                    "matchday": m.get("matchday"),
                    "home_team": m.get("homeTeam", {}).get("shortName") or m.get("homeTeam", {}).get("name"),
                    "away_team": m.get("awayTeam", {}).get("shortName") or m.get("awayTeam", {}).get("name"),
                    "score": {
                        "home": m.get("score", {}).get("fullTime", {}).get("home"),
                        "away": m.get("score", {}).get("fullTime", {}).get("away"),
                    },
                    "venue": m.get("venue"),
                }
                for m in matches
            ],
        }

    @staticmethod
    def fetch_standings(competition: str = "PL") -> dict[str, Any]:
        """Fetch current standings table for a competition."""
        if not FOOTBALL_DATA_API_KEY:
            return {"error": "FOOTBALL_DATA_API_KEY not configured", "standings": []}

        try:
            resp = requests.get(
                f"{FOOTBALL_BASE}/competitions/{competition.upper()}/standings",
                headers=_headers(),
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("football-data.org standings error for: %s", competition)
            raise

        standings_groups = data.get("standings", [])
        competition_info = data.get("competition", {})
        season_info = data.get("season", {})

        # Most leagues have one "TOTAL" table; CL has groups
        tables = []
        for group in standings_groups:
            tables.append(
                {
                    "type": group.get("type"),
                    "group": group.get("group"),
                    "table": [
                        {
                            "position": row.get("position"),
                            "team": row.get("team", {}).get("shortName") or row.get("team", {}).get("name"),
                            "played": row.get("playedGames"),
                            "won": row.get("won"),
                            "draw": row.get("draw"),
                            "lost": row.get("lost"),
                            "goals_for": row.get("goalsFor"),
                            "goals_against": row.get("goalsAgainst"),
                            "goal_diff": row.get("goalDifference"),
                            "points": row.get("points"),
                            "form": row.get("form"),
                        }
                        for row in group.get("table", [])
                    ],
                }
            )

        return {
            "competition": competition_info.get("name", competition.upper()),
            "season": f"{season_info.get('startDate', '')[:4]}/{season_info.get('endDate', '')[:4]}",
            "standings": tables,
        }

    @staticmethod
    def list_competitions() -> dict[str, Any]:
        """Return the list of supported competition codes."""
        return {
            "competitions": [
                {"code": code, "name": name}
                for code, name in COMPETITIONS.items()
            ]
        }
