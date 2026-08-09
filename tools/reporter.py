from datetime import datetime
from pathlib import Path

from pandas import DataFrame
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (ParagraphStyle,getSampleStyleSheet)
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BLUE = colors.HexColor("#302578")
RED = colors.HexColor("#DC0B15")

POSITION_COLUMNS = ["1º","2º","3º","4º","5º","6º","7º","8º"]

def truncate_text(text: str, max_len: int) -> str:
    if not isinstance(text, str):
        text = str(text)

    return (
        text
        if len(text) <= max_len
        else text[: max_len - 3] + "..."
    )


def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="SmallGray",
            fontSize=7,
            textColor=colors.black,
        )
    )

    styles.add(
        ParagraphStyle(
            name="BigTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=20,
            textColor=RED,
            spaceAfter=4,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Subtitle",
            parent=styles["Heading2"],
            fontSize=13,
            leading=15,
            textColor=BLUE,
            spaceAfter=10,
        )
    )

    return styles


def _add_footer(story, styles):

    story.append(Spacer(1, 8))

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    story.append(
        Paragraph(
            f"Generated at {timestamp}",
            styles["SmallGray"],
        )
    )


def _add_table_style(
    table: Table,
    df: DataFrame,
    column_count: int,
    highlight_top: int,
    highlight_club: str
):
    table_style = TableStyle(
        [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                RED,
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, 0),
                "CENTER",
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, 0),
                10,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                6,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, 0),
                6,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.25,
                colors.gray,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "FONTSIZE",
                (0, 1),
                (-1, -1),
                9,
            ),
        ]
    )

    for position, row in enumerate(
        df.itertuples(),
        start=1,
    ):
        background = (
            colors.whitesmoke
            if position % 2 == 0
            else colors.white
        )

        table_style.add(
            "BACKGROUND",
            (0, position),
            (-1, position),
            background,
        )

        club = getattr(row, "club", "")

        if club == highlight_club:
            text_color = RED
        elif position <= highlight_top:
            text_color = BLUE
        else:
            text_color = colors.black

        for column in range(column_count):
            table_style.add(
                "TEXTCOLOR",
                (column, position),
                (column, position),
                text_color,
            )

            table_style.add(
                "FONTNAME",
                (column, position),
                (column, position),
                "Helvetica-Bold",
            )

    table.setStyle(table_style)


def _build_swimmer_table(df: DataFrame, club:str) -> Table:
    headers = [
        "POS",
        "NOME",
        "CLUBE",
        "1º",
        "2º",
        "3º",
        "4º",
        "5º",
        "6º",
        "7º",
        "8º",
        "PTS",
    ]

    data = [headers]

    for position, (_, row) in enumerate(
        df.iterrows(),
        start=1,
    ):
        data.append(
            [
                str(position),
                truncate_text(
                    row["name"],
                    25,
                ),
                truncate_text(
                    row["club"],
                    35,
                ),
                *[
                    str(row[column])
                    for column in POSITION_COLUMNS
                ],
                str(row["points"]),
            ]
        )

    col_widths = [
        1.0 * cm,
        5.0 * cm,
        6.5 * cm,
        0.8 * cm,
        0.8 * cm,
        0.8 * cm,
        0.8 * cm,
        0.8 * cm,
        0.8 * cm,
        0.8 * cm,
        0.8 * cm,
        1.2 * cm,
    ]

    table = Table(
        data,
        colWidths=col_widths,
        repeatRows=1,
    )

    _add_table_style(
        table=table,
        df=df,
        column_count=len(headers),
        highlight_top=10,
        highlight_club=club
    )

    return table


def _build_club_table(df: DataFrame, club:str) -> Table:
    headers = [
        "POS",
        "CLUBE",
        "PONTOS",
    ]

    data = [headers]

    for position, (_, row) in enumerate(
        df.iterrows(),
        start=1,
    ):
        data.append(
            [
                str(position),
                truncate_text(
                    row["club"],
                    40,
                ),
                str(row["points"]),
            ]
        )

    col_widths = [
        1.0 * cm,
        8.0 * cm,
        3.0 * cm,
    ]

    table = Table(
        data,
        colWidths=col_widths,
        repeatRows=1,
    )

    _add_table_style(
        table=table,
        df=df,
        column_count=len(headers),
        highlight_top=8,
        highlight_club=club
    )

    return table


def _add_cover(
    story,
    styles,
    logo_path: str,
    season: str,
):
    path = Path(logo_path)

    if path.exists():
        logo = Image(str(path))

        logo.drawHeight = 6 * cm
        logo.drawWidth = 6 * cm
        logo.hAlign = "CENTER"

        story.append(
            Spacer(
                1,
                4 * cm,
            )
        )

        story.append(logo)

        story.append(
            Spacer(
                1,
                2 * cm,
            )
        )

    title_style = ParagraphStyle(
        name="CoverTitle",
        parent=styles["Heading1"],
        fontSize=24,
        leading=28,
        alignment=1,
        textColor=RED,
        spaceAfter=12,
    )

    story.append(
        Paragraph(
            "CEM",
            title_style,
        )
    )

    subtitle_style = ParagraphStyle(
        name="CoverSubtitle",
        parent=styles["Heading2"],
        fontSize=20,
        leading=20,
        alignment=1,
        textColor=BLUE,
        spaceAfter=10,
    )

    story.append(
        Paragraph(
            season,
            subtitle_style,
        )
    )

    story.append(
        Spacer(
            1,
            8 * cm,
        )
    )

    footer_style = ParagraphStyle(
        name="CoverFooter",
        parent=styles["Normal"],
        fontSize=14,
        alignment=1,
        textColor=colors.gray,
    )

    story.append(
        Paragraph(
            'Feito por '
            '<a href="https://github.com/VitorLelis">'
            'Vitor Lelis'
            '</a>',
            footer_style,
        )
    )

def generate_report(
    ranks: DataFrame,
    club_ranking: DataFrame,
    output_path: str,
    season: str,
    logo_path: str,
    highlight_club: str,
):

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1 * cm,
    )

    styles = _get_styles()
    story = []

    _add_cover(
        story=story,
        styles=styles,
        logo_path=logo_path,
        season=season,
    )

    trophy_titles = {
        "FREE": "CEM - Natação Livre",
        "BREAST": "CEM - Bruços",
        "BACK": "CEM - Costas",
        "FLY": "CEM - Mariposa",
        "IM": "CEM - Estilos",
        "COMPLETE": "CEM - Nadador Completo",
    }

    gender_names = {
        "M": "Masculino",
        "F": "Feminino",
    }

    trophy_order = [
        ("M", "FREE"),
        ("F", "FREE"),
        ("M", "BREAST"),
        ("F", "BREAST"),
        ("M", "BACK"),
        ("F", "BACK"),
        ("M", "FLY"),
        ("F", "FLY"),
        ("M", "IM"),
        ("F", "IM"),
        ("M", "COMPLETE"),
        ("F", "COMPLETE"),
    ]

    for gender, stroke in trophy_order:
        df = ranks.get(
            (gender, stroke)
        )

        if df is None:
            continue

        story.append(PageBreak())

        story.append(
            Paragraph(
                trophy_titles[stroke],
                styles["BigTitle"],
            )
        )

        story.append(
            Paragraph(
                gender_names[gender],
                styles["Subtitle"],
            )
        )

        story.append(
            _build_swimmer_table(df, highlight_club)
        )

        _add_footer(
            story,
            styles,
        )

    story.append(PageBreak())

    story.append(
        Paragraph(
            "CEM - Clubes",
            styles["BigTitle"],
        )
    )

    story.append(
        Paragraph(
            "Ranking dos clubes",
            styles["Subtitle"],
        )
    )

    story.append(
        _build_club_table(
            club_ranking, highlight_club
        )
    )

    _add_footer(
        story,
        styles,
    )

    doc.build(story)