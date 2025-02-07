from dataclasses import dataclass, field
from typing import Any, Optional, List, Annotated
import operator


@dataclass(kw_only=True)
class InputState:
    """Input state defines the interface between the graph and the user."""

    query: str
    "Product search query provided by the user."

    category: str
    "Product category (e.g., electronics, outdoors, etc.)"

    price_range: str = field(default="Any")
    "Desired price range for products"


@dataclass(kw_only=True)
class OverallState:
    """Overall state tracks all information throughout the research process."""

    query: str
    "Product search query provided by the user."

    category: str
    "Product category (e.g., electronics, outdoors, etc.)"

    price_range: str = field(default="Any")
    "Desired price range for products"

    product_research: List[str] = field(default_factory=list)
    "Product specifications and features from search results"

    review_data: List[str] = field(default_factory=list)
    "User reviews and feedback from various sources"

    expert_opinions: List[str] = field(default_factory=list)
    "Professional reviews and expert analysis"

    comparison_table: str = field(default=None)
    "Structured comparison table of top products"

    detailed_analysis: str = field(default=None)
    "In-depth analysis of top product options"

    final_recommendation: str = field(default=None)
    "Final product recommendations and buying advice"


@dataclass(kw_only=True)
class OutputState:
    """The response object for the end user."""

    comparison_table: str
    "Structured comparison table of top products"

    detailed_analysis: str
    "In-depth analysis of top product options"

    final_recommendation: str
    "Final product recommendations and buying advice"
