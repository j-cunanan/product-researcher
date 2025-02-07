# Product Researcher Agent

Product Researcher Agent searches the web for information about user-supplied products and returns structured analysis, comparisons, and recommendations.

## 🚀 Quickstart with LangGraph server

Set API keys for the LLM of choice (Anthropic is set by default in `src/agent/graph.py`) and [Tavily API](https://tavily.com/):
```
cp .env.example .env
```

Clone the repository and launch the assistant [using the LangGraph server](https://langchain-ai.github.io/langgraph/cloud/reference/cli/#dev):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/j-cunanan/product-researcher.git
cd product-researcher
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
```

## How it works

Product Researcher Agent follows a multi-step research and analysis workflow:

   - **Research Phase**: The system performs comprehensive product research:
     - Executes concurrent web searches via [Tavily API](https://tavily.com/) for:
       1. Product specifications and features
       2. User reviews and feedback
       3. Expert opinions and professional reviews
     - Retrieves up to `max_search_results` results per search type
   - **Analysis Phase**: After research is complete, the system:
     - Generates a structured comparison table of top products
     - Provides detailed analysis of top options
     - Creates final recommendations and buying advice
   - **Output Phase**: The system delivers three main components:
     - Comparison table with key features, pros, and cons
     - Detailed analysis of top options with market overview
     - Final recommendations including top pick, premium, and budget options

## Configuration

The configuration for Product Researcher Agent is defined in the `src/agent/configuration.py` file: 
* `max_search_queries`: int = 3 # Max search queries per product
* `max_search_results`: int = 3 # Max search results per query
* `comparison_table`: bool = True # Whether to include comparison table
* `detailed_analysis`: bool = True # Whether to include detailed analysis
* `final_recommendation`: bool = True # Whether to include final recommendation

## Inputs 

The user inputs are: 

```
* query: str - Product search query
* category: str - Product category (e.g., electronics, outdoors)
* price_range: Optional[str] - Desired price range (defaults to "Any")
```

## Output Format

The system provides structured output in three main sections:

1. **Comparison Table**: A markdown-formatted table comparing 3-5 top products, including:
   - Model name
   - Price
   - Rating
   - Key features
   - Pros and cons

2. **Detailed Analysis**:
   - Market overview and trends
   - Analysis of top options
   - Key decision factors
   - Price-performance analysis

3. **Final Recommendations**:
   - Top recommendation with justification
   - Premium option
   - Budget option
   - Specialized recommendations
   - Usage/buying tips

## Evaluation

Prior to engaging in any optimization, it is important to establish a baseline performance. This repository includes:

1. A dataset consisting of a list of companies and the expected structured information to be extracted for each company.
2. An evaluation script that can be used to evaluate the agent on this dataset.

### Set up

Make sure you have the LangSmith CLI installed:

```shell
pip install langsmith
```

And set your API key:

```shell
export LANGSMITH_API_KEY=<your_langsmith_api_key>
export ANTHROPIC_API_KEY=<your_anthropic_api_key>
```

### Evaluation metric

A score between 0 and 1 is assigned to each extraction result by an LLM model that acts
as a judge.

The model assigns the score based on how closely the extracted information matches the expected information.

### Get the dataset

Create a new dataset in LangSmith using the code in the `eval` folder:

```shell
python eval/create_dataset.py
```

### Run the evaluation

To run the evaluation, you can use the `run_eval.py` script in the `eval` folder. This will create a new experiment in LangSmith for the dataset you created in the previous step.

```shell
python eval/run_eval.py --experiment-prefix "My custom prefix" --agent-url http://localhost:2024
```
