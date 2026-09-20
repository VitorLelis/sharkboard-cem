from typing import Dict, Tuple
import pandas as pd

STROKES = (
    "FREE",
    "BREAST",
    "BACK",
    "FLY",
    "MEDLEY",
    "COMPLETE",
)

GENDERS = ("M", "F")

POSITION_COLUMNS = ["1º","2º","3º","4º","5º","6º","7º","8º"]


def calculate_club_ranking(ranks: Dict[Tuple[str, str], pd.DataFrame]) -> pd.DataFrame:
    club_results = []

    for gender in GENDERS:
        for stroke in STROKES:
            rank = ranks.get((gender, stroke))

            if rank is None or rank.empty:
                continue

            top_10 = rank.head(10).copy()

            for _, swimmer in top_10.iterrows():
                club = swimmer["club"]

                club_results.append(
                    {
                        "club": club,
                        "points": swimmer["points"],
                        "1º": swimmer["1º"],
                        "2º": swimmer["2º"],
                        "3º": swimmer["3º"],
                        "4º": swimmer["4º"],
                        "5º": swimmer["5º"],
                        "6º": swimmer["6º"],
                        "7º": swimmer["7º"],
                        "8º": swimmer["8º"],
                    }
                )

    if not club_results:
        return _empty_club_dataframe()

    results = pd.DataFrame(club_results)

    results = (
        results
        .groupby("club", as_index=False)
        .agg(
            {
                "points": "sum",
                "1º": "sum",
                "2º": "sum",
                "3º": "sum",
                "4º": "sum",
                "5º": "sum",
                "6º": "sum",
                "7º": "sum",
                "8º": "sum",
            }
        )
    )

    sort_columns = [
        "points",
        *POSITION_COLUMNS,
    ]

    results = results.sort_values(
        by=sort_columns,
        ascending=[False] * len(sort_columns),
        kind="stable",
    ).reset_index(drop=True)

    results.insert(
        0,
        "position",
        range(1, len(results) + 1),
    )

    return results


def _empty_club_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "position",
            "club",
            *POSITION_COLUMNS,
            "points",
        ]
    )