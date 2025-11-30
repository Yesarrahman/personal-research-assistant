"""
Coordinator Agent - Research Assistant System

This agent orchestrates the research workflow by:
- Analyzing user queries
- Creating research strategies
- Determining which sub-agents to invoke
- Managing the overall research flow
- Executing complete research workflows

Model: Gemini 2.5 Flash (fast coordination decisions)
"""

import logging
from google import generativeai as genai

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Orchestrates the multi-agent research workflow.
    Decides research strategy and coordinates sub-agents.
    """

    def __init__(self, researcher_agent=None, summarizer_agent=None):
        """
        Initialize coordinator with Gemini Flash model and sub-agents.

        Args:
            researcher_agent: ResearcherAgent instance (optional, can be set later)
            summarizer_agent: SummarizerAgent instance (optional, can be set later)
        """
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
        self.researcher = researcher_agent
        self.summarizer = summarizer_agent
        logger.info("Coordinator Agent initialized with Gemini 2.5 Flash-Lite")

    def set_agents(self, researcher_agent, summarizer_agent):
        """
        Set sub-agents after initialization (useful for avoiding circular imports).

        Args:
            researcher_agent: ResearcherAgent instance
            summarizer_agent: SummarizerAgent instance
        """
        self.researcher = researcher_agent
        self.summarizer = summarizer_agent
        logger.info("Sub-agents configured in Coordinator")

    def create_plan(self, query: str) -> dict:
        """
        Analyze query and create a research plan.

        Args:
            query: User's research question

        Returns:
            dict: Research plan with strategy and parameters
        """
        # Prompt for strategic planning
        planning_prompt = f"""
        You are a research coordinator. Analyze this research query and create a plan.
        
        Query: "{query}"
        
        Provide a structured research plan in the following format:
        
        STRATEGY: [Brief description of research approach]
        NUM_SOURCES: [Recommended number: 3-10]
        FOCUS_AREAS: [List 2-4 key aspects to research]
        SEARCH_TERMS: [List 3-5 optimized search terms]
        
        Be concise and strategic.
        """

        try:
            # Generate plan using Gemini
            response = self.model.generate_content(planning_prompt)
            plan_text = response.text

            # Parse response into structured format
            plan = self._parse_plan(plan_text)
            plan["original_query"] = query

            logger.info(f"Created research plan: {plan['strategy']}")
            return plan

        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            # Return default plan on error
            return {
                "strategy": "comprehensive web research",
                "num_sources": 5,
                "focus_areas": [query],
                "search_terms": [query],
                "original_query": query,
            }

    def orchestrate_research(self, query: str) -> dict:
        """
        Full orchestration: Plan → Research → Synthesize

        This is the main method that coordinates the entire workflow.

        Args:
            query: User's research question

        Returns:
            dict: Complete research results including plan, sources, and report
        """
        if not self.researcher or not self.summarizer:
            raise ValueError(
                "Sub-agents not configured. Call set_agents() first or pass them to __init__"
            )

        logger.info(f"Starting orchestrated research for: '{query}'")

        try:
            # Step 1: Create strategic plan
            logger.info("[1/3] Creating research plan...")
            plan = self.create_plan(query)
            logger.info(f"  ✓ Strategy: {plan['strategy']}")
            logger.info(f"  ✓ Target sources: {plan.get('num_sources', 5)}")

            # Step 2: Execute research using ResearcherAgent
            logger.info("[2/3] Executing web search...")
            search_results = self.researcher.search_web(
                query=query, num_results=plan.get("num_sources", 5)
            )
            logger.info(f"  ✓ Found {len(search_results)} sources")

            # Step 3: Synthesize findings using SummarizerAgent
            logger.info("[3/3] Synthesizing research...")
            final_report = self.summarizer.synthesize(
                query=query, sources=search_results, context=plan.get("focus_areas", [])
            )
            logger.info("  ✓ Synthesis complete")

            # Return complete results
            return {
                "success": True,
                "query": query,
                "plan": plan,
                "sources": search_results,
                "report": final_report,
                "num_sources": len(search_results),
            }

        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            return {"success": False, "query": query, "error": str(e)}

    def orchestrate_follow_up(self, query: str, previous_context: dict) -> dict:
        """
        Orchestrate follow-up research using previous context.

        Args:
            query: Follow-up question
            previous_context: Context from previous research (sources, query, etc.)

        Returns:
            dict: Follow-up research results
        """
        if not self.summarizer:
            raise ValueError("Summarizer agent not configured")

        logger.info(f"Orchestrating follow-up question: '{query}'")

        try:
            # Use previous sources with new synthesis
            previous_query = previous_context.get("query", "Unknown")
            sources = previous_context.get("sources", [])

            logger.info(f"Using {len(sources)} sources from previous research")

            # Re-synthesize with new focus
            refined_report = self.summarizer.synthesize(
                query=query,
                sources=sources,
                context=[f"Previous query: {previous_query}"],
            )

            return {
                "success": True,
                "query": query,
                "report": refined_report,
                "sources": sources,
                "is_follow_up": True,
                "num_sources": len(sources),
            }

        except Exception as e:
            logger.error(f"Follow-up orchestration error: {e}")
            return {"success": False, "query": query, "error": str(e)}

    def _parse_plan(self, plan_text: str) -> dict:
        """
        Parse the LLM's plan response into structured dict.

        Args:
            plan_text: Raw text response from LLM

        Returns:
            dict: Parsed plan components
        """
        plan = {"strategy": "", "num_sources": 5, "focus_areas": [], "search_terms": []}

        lines = plan_text.split("\n")

        for line in lines:
            line = line.strip()

            if line.startswith("STRATEGY:"):
                plan["strategy"] = line.split(":", 1)[1].strip()

            elif line.startswith("NUM_SOURCES:"):
                try:
                    num = line.split(":", 1)[1].strip()
                    # Extract first number found
                    import re

                    match = re.search(r"\d+", num)
                    if match:
                        plan["num_sources"] = min(int(match.group()), 10)
                except:
                    pass

            elif line.startswith("FOCUS_AREAS:"):
                areas = line.split(":", 1)[1].strip()
                plan["focus_areas"] = [a.strip() for a in areas.split(",")]

            elif line.startswith("SEARCH_TERMS:"):
                terms = line.split(":", 1)[1].strip()
                plan["search_terms"] = [t.strip() for t in terms.split(",")]

        return plan
