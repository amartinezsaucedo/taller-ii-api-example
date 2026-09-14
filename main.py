
from functools import lru_cache
from io import StringIO
from typing import Optional

import pandas as pd
from datasets import load_dataset
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

app = FastAPI(
    title="Amazon Reviews Dataset API",
    description="Serves SetFit/amazon_reviews_multi_en for classroom use.",
    version="1.0.0",
)


@lru_cache(maxsize=1)
def get_dataframe() -> pd.DataFrame:
    ds = load_dataset("SetFit/amazon_reviews_multi_en")
    df = pd.concat(
        [ds[split].to_pandas() for split in ds.keys()],
        ignore_index=True,
    )
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    df = get_dataframe()
    return {
        "total_rows": len(df),
        "columns": list(df.columns),
        "label_distribution": df["label"].value_counts().sort_index().to_dict(),
    }


@app.get("/reviews")
def get_reviews(
    limit: int = Query(100, ge=1, le=1000, description="Max rows to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Rows to skip"),
    stars: Optional[int] = Query(None, ge=0, le=4, description="Filter by label (0-4)"),
):
    df = get_dataframe()
    if stars is not None:
        df = df[df["label"] == stars]
    if offset >= len(df):
        return {"total_matching": len(df), "returned": 0, "data": []}
    page = df.iloc[offset : offset + limit]
    return {
        "total_matching": len(df),
        "returned": len(page),
        "offset": offset,
        "limit": limit,
        "data": page.to_dict(orient="records"),
    }


@app.get("/reviews/sample")
def sample_reviews(
    n: int = Query(100, ge=1, le=5000, description="Sample size"),
    seed: int = Query(42, description="Random seed for reproducibility"),
):
    df = get_dataframe()
    if n > len(df):
        raise HTTPException(status_code=400, detail=f"n cannot exceed dataset size ({len(df)})")
    sample = df.sample(n=n, random_state=seed)
    return sample.to_dict(orient="records")


@app.get("/reviews/download")
def download_full_dataset():
    df = get_dataframe()
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=amazon_reviews_full.csv"},
    )
