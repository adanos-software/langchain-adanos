# LangChain Adanos

Adanos market sentiment research through a LangChain `BaseTool`, maintained by
[Adanos](https://adanos.org/) and built on the official
[Python SDK](https://github.com/adanos-software/adanos-python-sdk).

## Install

Version 0.1.0 is not yet published to PyPI. To test this checkout:

```sh
uv sync
```

Adanos is a commercial API with a free plan. Obtain your own key from
[Adanos](https://adanos.org/) and set `ADANOS_API_KEY` in your environment.
Free, Hobby and Professional plan permissions, retention and quotas are enforced
by the API. Each user retains their own account and limits. No shared key is used.

## Use

```python
from langchain_adanos import AdanosMarketSentimentTool

tool = AdanosMarketSentimentTool()
result = tool.invoke({
    "source": "news",
    "operation": "stock",
    "parameters": {"ticker": "AAPL"},
})
print(result)
```

Pass `tools=[tool]` to a LangChain agent. To use an explicit key, pass `api_key`
to the constructor, never in agent input. `ainvoke` is supported through
LangChain's standard thread-executor fallback. Import and construction make no
network calls. Each invocation closes its HTTP client, uses a 30-second timeout,
and performs no automatic retries or pagination.

## Sources and Operations

| Source | Operations |
| --- | --- |
| `reddit`, `x`, `news` | `stock`, `mentions`, `trending`, `trending_sectors`, `trending_countries`, `market_sentiment`, `compare`, `search`, `stats`, `health`, `explain` |
| `polymarket` | Same stock operations, except `explain` |
| `crypto` | Reddit crypto: `token`, `mentions`, `trending`, `market_sentiment`, `compare`, `search`, `stats`, `health` |
| `sentiment` | `analyze` supplied text |
| `status` | Root API `health` |

`parameters` uses SDK keyword names:

- `stock`, `mentions`, `explain`: `ticker`; crypto `token`/`mentions`: `symbol`.
- `compare`: a `tickers` list, or `symbols` for crypto.
- `search`: `query`; `analyze`: `text`.
- `trending`, sector/country trends and `mentions`: optional `limit`, `offset`.
- `search`: optional `limit`; stock `trending`: optional `type`.
- Reddit stock and crypto `mentions`: optional `include_inherited`.

For historical queries, provide both `from_` and `to` as inclusive UTC dates
(`YYYY-MM-DD`) within the account's retention, or omit both for the API default.
The deprecated `days` parameter is rejected. Search, explain, analyze, stats and
health do not accept dates. For example:

```python
result = tool.invoke({
    "source": "crypto",
    "operation": "token",
    "parameters": {"symbol": "BTC", "from_": "2026-09-20", "to": "2026-09-21"},
})
```

The example dates are fixed; select dates permitted by your account when running
it. Historical aggregates are not guaranteed point-in-time data for backtesting;
explanations describe current context.

Successful calls return `source`, `operation` and the SDK's unmodified `data`,
preserving zero and null values. Metrics from different sources are not combined
or normalized. Errors return `error` and a safe `message`, never neutral sentiment
or raw server errors. Check credentials, plan access, parameters and quota before
retrying. Invalid tool-schema arguments raise LangChain/Pydantic validation errors.

Mention text is untrusted third-party content, not agent instructions. Treat
results as research evidence, not investment advice or standalone trading signals.
See the [API reference](https://api.adanos.org/docs) for field definitions and
source-specific metrics.

## Development

```sh
uv sync --locked
uv run pytest --disable-socket --allow-unix-socket
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv build
uv run twine check dist/*
```

Tests use the installed SDK and mocked HTTP transport, including all 53 supported
source/operation pairs, error redaction, schema boundaries, synchronous and
asynchronous LangChain invocation, and the LangChain standard tool unit tests.
They require no API key, live API access or paid LLM.

## Publication

Follow [LangChain's integration publishing process](https://docs.langchain.com/oss/python/contributing/publish-langchain).
Publish the reviewed package on PyPI, then submit an Integration listing issue in
`langchain-ai/docs`. A maintainer starts their listing PR automation. Do not open
a manual integration-code or docs-listing PR in LangChain's repositories.

Before the first release, register a PyPI pending trusted publisher for project
`langchain-adanos`, GitHub owner `adanos-software`, repository `langchain-adanos`,
workflow `publish.yml`, and environment `pypi`. Configure that GitHub environment
with release approval. Publishing a version-matched GitHub release (for example,
`v0.1.0`) then runs validation and publishes through OIDC without storing a PyPI
token. After successful publication, update the installation instructions above.

MIT license. API service access is governed separately by Adanos terms.
