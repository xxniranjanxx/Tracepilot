from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/raw/sample_incidents.csv")
OUTPUT_PATH = Path("data/processed/clean_incidents.csv")

REQUIRED_COLUMNS = {
    "short_description",
    "description",
    "resolution_notes",
    "priority",
    "resolution_category",
}

TEXT_COLUMNS = [
    "short_description",
    "description",
    "resolution_notes",
    "priority",
    "resolution_category",
]


def clean_text(value: object) -> str:
    """Remove unnecessary whitespace from a text value."""
    if pd.isna(value):
        return ""

    return " ".join(str(value).split())


def process_incidents() -> None:
    # 1. Read the source dataset
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    # 2. Validate the dataset structure
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    original_count = len(df)

    # 3. Remove records without essential information
    df = df.dropna(
        subset=["description", "resolution_notes"]
    ).copy()

    # 4. Clean text fields
    for column in TEXT_COLUMNS:
        df[column] = df[column].apply(clean_text)

    # 5. Remove records with empty technical descriptions
    df = df[
        (df["description"] != "")
        & (df["resolution_notes"] != "")
    ].copy()

    # 6. Standardise selected fields
    df["priority"] = df["priority"].str.strip().str.title()
    df["resolution_category"] = (
        df["resolution_category"].str.strip().str.title()
    )

    # 7. Remove duplicate records
    df = df.drop_duplicates(
        subset=[
            "short_description",
            "description",
            "resolution_notes",
        ]
    ).copy()

    # 8. Replace identifiers with synthetic IDs
    df.insert(
        0,
        "incident_id",
        [f"SYN-{number:05d}" for number in range(1, len(df) + 1)],
    )

    # 9. Save processed data
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Original records: {original_count}")
    print(f"Processed records: {len(df)}")
    print(f"Removed records: {original_count - len(df)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    process_incidents() 