import asyncio
from typing import cast, Any, Literal
import json

from tavily import AsyncTavilyClient
from langchain_anthropic import ChatAnthropic
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel, Field

from agent.configuration import Configuration
from agent.state import InputState, OutputState, OverallState
from agent.utils import deduplicate_sources, format_sources, format_all_notes
from agent.prompts import (
    COMPARISON_PROMPT,
    ANALYSIS_PROMPT,
    RECOMENDATION_PROMPT,
)

# LLMs

rate_limiter = InMemoryRateLimiter(
    requests_per_second=4,
    check_every_n_seconds=0.1,
    max_bucket_size=10,  # Controls the maximum burst size.
)
claude_3_5_sonnet = ChatAnthropic(
    model="claude-3-5-sonnet-latest", temperature=0, rate_limiter=rate_limiter
)

# Search

tavily_async_client = AsyncTavilyClient()


class InputState(BaseModel):
    query: str = Field(description="Product search query")
    category: str = Field(description="Product category")
    price_range: str = Field(description="Price range for products", default="Any")


class OutputState(BaseModel):
    comparison_table: str = Field(description="Structured comparison table of products", default="")
    detailed_analysis: str = Field(description="Detailed analysis of top products", default="")
    final_recommendation: str = Field(description="Final product recommendations", default="")


class OverallState(InputState, OutputState):
    product_research: list[str] = Field(default_factory=list)
    review_data: list[str] = Field(default_factory=list)
    expert_opinions: list[str] = Field(default_factory=list)


async def research_products(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Execute product research using Tavily search.

    Performs concurrent searches for:
    1. Product specifications and features
    2. User reviews
    3. Expert opinions
    """
    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    max_search_results = configurable.max_search_results

    # Build search queries
    product_query = f"{state.query} specs features price {state.category} 2025"
    review_query = f"{state.query} user reviews reddit 2025"
    expert_query = f"{state.query} expert professional review 2025"

    # Execute concurrent searches
    search_tasks = [
        tavily_async_client.search(
            query,
            max_results=max_search_results,
            include_raw_content=True,
            topic="general",
        )
        for query in [product_query, review_query, expert_query]
    ]

    search_results = await asyncio.gather(*search_tasks)

    # Process results
    product_info = [r["content"] for r in search_results[0]["results"]]
    review_data = [r["content"] for r in search_results[1]["results"]]
    expert_opinions = [r["content"] for r in search_results[2]["results"]]

    return {
        "product_research": product_info,
        "review_data": review_data,
        "expert_opinions": expert_opinions,
    }


def generate_comparison(state: OverallState) -> dict[str, Any]:
    """Generate product comparison table"""
    context = "\n\n".join(
        [
            "\n".join(state.product_research or []),
            "\n".join(state.review_data or []),
            "\n".join(state.expert_opinions or []),
        ]
    )

    result = claude_3_5_sonnet.invoke(
        [
            {"role": "system", "content": COMPARISON_PROMPT},
            {
                "role": "user",
                "content": f"Create a comparison table for: {state.query}\n\nResearch:\n{context}",
            },
        ]
    )

    return {"comparison_table": str(result.content)}


def generate_analysis(state: OverallState) -> dict[str, Any]:
    """Generate detailed product analysis"""
    context = "\n\n".join(
        [
            "\n".join(state.product_research or []),
            "\n".join(state.review_data or []),
            "\n".join(state.expert_opinions or []),
        ]
    )

    result = claude_3_5_sonnet.invoke(
        [
            {"role": "system", "content": ANALYSIS_PROMPT},
            {
                "role": "user",
                "content": f"Analyze results for: {state.query}\n\nResearch:\n{context}",
            },
        ]
    )

    return {"detailed_analysis": str(result.content)}


def generate_recommendation(state: OverallState) -> dict[str, Any]:
    """Generate final recommendations"""
    result = claude_3_5_sonnet.invoke(
        [
            {"role": "system", "content": RECOMENDATION_PROMPT},
            {
                "role": "user",
                "content": f"Make recommendations for: {state.query}\nPrice range: {state.price_range}\n\nAnalysis:\n{state.detailed_analysis}",
            },
        ]
    )

    return {"final_recommendation": str(result.content)}


# Add nodes and edges
builder = StateGraph(
    OverallState,
    input=InputState,
    output=OutputState,
    config_schema=Configuration,
)

# Add nodes for product research workflow
builder.add_node("research_products", research_products)
builder.add_node("generate_comparison", generate_comparison)
builder.add_node("generate_analysis", generate_analysis)
builder.add_node("generate_recommendation", generate_recommendation)

# Add edges for linear workflow
builder.add_edge(START, "research_products")
builder.add_edge("research_products", "generate_comparison")
builder.add_edge("generate_comparison", "generate_analysis")
builder.add_edge("generate_analysis", "generate_recommendation")
builder.add_edge("generate_recommendation", END)

# Compile
graph = builder.compile()
