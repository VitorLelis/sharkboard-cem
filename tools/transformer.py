from typing import Dict, Tuple
import pandas as pd

POINTS = {
    1: 10,
    2: 8,
    3: 6,
    4: 5,
    5: 4,
    6: 3,
    7: 2,
    8: 1,
}

STROKES = ("FREE", "BREAST", "BACK", "FLY", "MEDLEY")
GENDERS = ("M", "F")

POSITION_COLUMNS = ["1º","2º","3º","4º","5º","6º","7º","8º"]


def add_points(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["points"] = sum(
        result[column] * POINTS[position]
        for position, column in enumerate(
            POSITION_COLUMNS,
            start=1,
        )
    )

    return result


def rank_trophy(df: pd.DataFrame) -> pd.DataFrame:
    result = add_points(df)

    sort_columns = [
        "points",
        *POSITION_COLUMNS,
    ]

    result = result.sort_values(
        by=sort_columns,
        ascending=[False] * len(sort_columns),
        kind="stable",
    ).reset_index(drop=True)

    result.insert(
        0,
        "position",
        range(1, len(result) + 1),
    )

    return result


def build_complete_swimmers(positions: Dict[Tuple[str, str], pd.DataFrame]) -> Dict[Tuple[str, str], pd.DataFrame]:
    complete = {}

    for gender in GENDERS:
        gender_positions = [
            positions[(gender, stroke)]
            for stroke in STROKES
        ]

        qualified_ids = None

        for trophy in gender_positions:
            swimmer_ids = set(trophy["swimmer_id"])

            if qualified_ids is None:
                qualified_ids = swimmer_ids
            else:
                qualified_ids &= swimmer_ids

        if not qualified_ids:
            complete[(gender, "COMPLETE")] = _empty_complete_dataframe()
            continue

        base = gender_positions[0]

        complete_df = base[
            base["swimmer_id"].isin(qualified_ids)
        ][
            [
                "swimmer_id",
                "name",
                "club",
                "gender",
            ]
        ].drop_duplicates()

        for column in POSITION_COLUMNS:
            complete_df[column] = 0

        for trophy in gender_positions:
            trophy_indexed = trophy.set_index("swimmer_id")

            for column in POSITION_COLUMNS:
                values = trophy_indexed[column]

                complete_df[column] += (
                    complete_df["swimmer_id"]
                    .map(values)
                    .fillna(0)
                    .astype(int)
                )

        complete[(gender, "COMPLETE")] = rank_trophy(
            complete_df
        )

    return complete


def calculate_rankings(positions: Dict[Tuple[str, str], pd.DataFrame]) -> Dict[Tuple[str, str], pd.DataFrame]:
    ranked = {}

    for gender in GENDERS:
        for stroke in STROKES:
            ranked[(gender, stroke)] = rank_trophy(
                positions[(gender, stroke)]
            )

    complete = build_complete_swimmers(ranked)

    ranked.update(complete)

    return ranked


def _empty_complete_dataframe() -> pd.DataFrame:

    return pd.DataFrame(
        columns=[
            "position",
            "swimmer_id",
            "name",
            "club",
            "gender",
            *POSITION_COLUMNS,
            "points",
        ]
    )