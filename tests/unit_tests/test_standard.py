import json
from unittest.mock import patch

import httpx
import pytest
from langchain_tests.unit_tests.tools import ToolsUnitTests

from langchain_adanos import AdanosMarketSentimentTool


class TestAdanosStandard(ToolsUnitTests):
    @property
    def tool_constructor(self):
        return AdanosMarketSentimentTool

    @property
    def tool_constructor_params(self):
        return {"api_key": "test-adanos-key"}

    @property
    def tool_invoke_params_example(self):
        return {
            "source": "reddit",
            "operation": "stock",
            "parameters": {"ticker": "AAPL"},
        }

    @property
    def init_from_env_params(self):
        return (
            {"ADANOS_API_KEY": "test-adanos-key"},
            {},
            {"api_key": "test-adanos-key"},
        )


@pytest.mark.asyncio
async def test_ainvoke_and_tool_call_message():
    tool = AdanosMarketSentimentTool(api_key="test-adanos-key")
    payload = {"ticker": "AAPL", "found": True, "sentiment_score": None}
    with patch.object(
        httpx.Client,
        "send",
        autospec=True,
        side_effect=lambda client, request, **kwargs: httpx.Response(
            200, json=payload, request=request
        ),
    ):
        result = await tool.ainvoke(
            {
                "name": tool.name,
                "type": "tool_call",
                "id": "test-call",
                "args": {
                    "source": "reddit",
                    "operation": "stock",
                    "parameters": {"ticker": "AAPL"},
                },
            }
        )
    assert result.tool_call_id == "test-call"
    assert json.loads(result.content)["data"] == payload


def test_untrusted_tool_arguments_do_not_trigger_network():
    tool = AdanosMarketSentimentTool(api_key="test-adanos-key")
    with patch.object(httpx.Client, "send") as send:
        with pytest.raises(ValueError):
            tool.invoke({"source": "crypto", "operation": "explain"})
    send.assert_not_called()


def test_serialization_and_schema_do_not_expose_key():
    tool = AdanosMarketSentimentTool(api_key="test-adanos-key")
    assert "test-adanos-key" not in json.dumps(tool.to_json())
    assert "api_key" not in tool.tool_call_schema.model_json_schema()["properties"]
