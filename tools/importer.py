from typing import Dict, Tuple
import pandas as pd

MIN_DISTANCES = {
    "FREE": 3,
    "BREAST": 2,
    "BACK": 2,
    "FLY": 2,
    "MEDLEY": 2,
}

STROKES = ("FREE", "BREAST", "BACK", "FLY", "MEDLEY")
GENDERS = ("M", "F")

POSITION_COLUMNS = ["1º","2º","3º","4º","5º","6º","7º","8º"]

def _load_results(connection, season: str) -> pd.DataFrame:
    query = """
        SELECT
            r.swimmer_id,
            s.name,
            s.club,
            s.gender,
            e.stroke,
            e.distance,
            r.position
        FROM results AS r
        INNER JOIN swimmers AS s
            ON s.id = r.swimmer_id
        INNER JOIN meets AS m
            ON m.id = r.meet_id
        INNER JOIN events AS e
            ON e.id = r.event_id
        WHERE m.season = %s
          AND m.tag = 'CEM'
          AND r.from_relay = FALSE
          AND e.stroke IN ('FREE', 'BREAST', 'BACK', 'FLY', 'MEDLEY')
          AND r.position IS NOT NULL
    """

    return pd.read_sql_query(
        query,
        connection,
        params=(season,),
    )


def _find_qualified_swimmers(results: pd.DataFrame) -> pd.DataFrame:
    distances = (
        results[
            [
                "swimmer_id",
                "name",
                "club",
                "gender",
                "stroke",
                "distance"
            ]
        ]
        .drop_duplicates()
        .groupby(
            [
                "swimmer_id",
                "name",
                "club",
                "gender",
                "stroke"
            ],
            as_index=False,
        )
        .agg(
            distance_count=("distance", "nunique"),
        )
    )

    distances["required_distances"] = distances["stroke"].map(
        MIN_DISTANCES
    )

    qualified = distances[
        distances["distance_count"] >= distances["required_distances"]
    ].copy()

    return qualified

def _calculate_scores(results: pd.DataFrame, qualified: pd.DataFrame) -> pd.DataFrame:
    qualified_keys = qualified[
        [
            "swimmer_id",
            "gender",
            "stroke"
        ]
    ].drop_duplicates()

    scoring_results = results.merge(
        qualified_keys,
        on=[
            "swimmer_id",
            "gender",
            "stroke"
        ],
        how="inner",
    )

    scoring_results = scoring_results[
        scoring_results["position"].between(1, 8)
    ].copy()

    if scoring_results.empty:
        return qualified.iloc[0:0].copy()

    scores = (
        scoring_results
        .groupby(
            [
                "swimmer_id",
                "name",
                "club",
                "gender",
                "stroke",
                "position"
            ],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "count"})
    )

    scores["position_column"] = scores["position"].map(
        dict(enumerate(POSITION_COLUMNS, start=1))
    )

    scores = scores.pivot_table(
        index=[
            "swimmer_id",
            "name",
            "club",
            "gender",
            "stroke"
        ],
        columns="position_column",
        values="count",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    for column in POSITION_COLUMNS:
        if column not in scores.columns:
            scores[column] = 0

    return scores[
        [
            "swimmer_id",
            "name",
            "club",
            "gender",
            "stroke",
            *POSITION_COLUMNS
        ]
    ]


def _build_empty_trophy_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "swimmer_id",
            "name",
            "club",
            "gender",
            "stroke",
            *POSITION_COLUMNS
        ]
    )


def import_positions(connection,season: int) -> Dict[Tuple[str, str], pd.DataFrame]:
    results = _load_results(connection, season)

    if results.empty:
        empty = _build_empty_trophy_dataframe()

        return {
            (gender, stroke): empty.copy()
            for gender in GENDERS
            for stroke in STROKES
        }

    qualified = _find_qualified_swimmers(results)

    scores = _calculate_scores(results,qualified)

    positions: Dict[Tuple[str, str], pd.DataFrame] = {}

    for gender in GENDERS:
        for stroke in STROKES:
            pos = scores[
                (scores["gender"] == gender)
                & (scores["stroke"] == stroke)
            ].copy()

            if pos.empty:
                pos = _build_empty_trophy_dataframe()
            else:
                pos = pos.sort_values(
                    by=POSITION_COLUMNS,
                    ascending=False,
                    kind="stable",
                ).reset_index(drop=True)

            positions[(gender, stroke)] = pos

    return positions