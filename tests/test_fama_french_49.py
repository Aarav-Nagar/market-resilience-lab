from datetime import date

from market_resilience_lab.adapters.fama_french_49 import (
    IndustryReturnMonth,
    build_momentum_observations,
    parse_value_weighted_monthly,
)


def _archive_with_monthly_table() -> bytes:
    from io import BytesIO
    from zipfile import ZipFile

    assets = [f"Ind{number:02d}" for number in range(1, 50)]
    header = "," + ",".join(assets)
    rows = [header]
    for index in range(15):
        year = 2020 + (index // 12)
        month = (index % 12) + 1
        value = "-99.99" if index == 2 else str(index + 1)
        rows.append(f"{year}{month:02d}," + ",".join([value] * 49))
    text = "\n".join(
        ["created by a provider", "", "  Average Value Weighted Returns -- Monthly", *rows, ""]
    )
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("49_Industry_Portfolios.csv", text)
    return buffer.getvalue()


def test_parser_converts_percentages_and_missing_sentinel() -> None:
    months = parse_value_weighted_monthly(_archive_with_monthly_table())

    assert len(months) == 15
    assert months[0].as_of.isoformat() == "2020-01-31"
    assert months[0].returns["Ind01"] == 0.01
    assert months[2].returns["Ind01"] is None


def test_observation_builder_excludes_incomplete_momentum_windows() -> None:
    months = parse_value_weighted_monthly(_archive_with_monthly_table())

    rows = build_momentum_observations(months)

    # Both possible formation months include the missing third-month return.
    assert rows == []


def test_observation_builder_uses_lagged_history_and_next_month_label() -> None:
    months = []
    for index in range(14):
        year = 2020 + (index // 12)
        month = (index % 12) + 1
        as_of = date(year, month, 28)
        months.append(IndustryReturnMonth(as_of=as_of, returns={"Industry": 0.01}))

    rows = build_momentum_observations(months)

    assert len(rows) == 1
    assert rows[0]["as_of"] == "2021-01-28"
    assert rows[0]["label_end"] == "2021-02-28"
    assert rows[0]["label_return"] == 0.01
    assert rows[0]["feature__mom_12_1"] > 0.12
