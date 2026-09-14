# Amazon Reviews Dataset API

A minimal FastAPI service that serves the `SetFit/amazon_reviews_multi_en`
dataset over HTTP

## Run locally

```bash
uv install
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs for interactive Swagger docs (auto-generated).

## Endpoints

| Endpoint              | Description                                      |
|------------------------|---------------------------------------------------|
| `GET /health`           | Liveness check                                    |
| `GET /stats`             | Row count + label distribution                     |
| `GET /reviews`            | Paginated rows (`limit`, `offset`, `stars` filter)   |
| `GET /reviews/sample`      | Random sample (`n`, `seed`)                          |
| `GET /reviews/download`     | Entire dataset as a downloadable CSV                 |

