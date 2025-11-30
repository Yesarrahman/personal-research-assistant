"""
Personal Research Assistant Agent - Main Entry Point
Capstone Project for Google AI Agents Intensive Course

This multi-agent system automates web research using:
- Coordinator Agent: Orchestrates workflow
- Researcher Agent: Performs web searches
- Summarizer Agent: Synthesizes findings

Author: Yesar Rahman
Date: November 2025
"""

import os
import sys
import logging
from dotenv import load_dotenv
from google import generativeai as genai
from datetime import datetime

# Import our custom agents and tools
from agents.coordinator import CoordinatorAgent
from agents.researcher import ResearcherAgent
from agents.summarizer import SummarizerAgent
from utils.session_manager import SessionManager

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# Color codes for terminal output (works on most terminals)
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class ResearchAssistantSystem:
    """
    Enhanced Personal Research Assistant with better UX.
    Manages agent lifecycle, session state, and workflow coordination.
    """

    def __init__(self):
        """Initialize the research assistant system with all agents."""
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}🚀 Personal Research Assistant Agent {Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

        # Validate API keys with helpful error messages
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            self._show_api_key_error()
            raise ValueError("GOOGLE_API_KEY not found")

        # Configure Gemini API
        try:
            genai.configure(api_key=self.api_key)
            print(f"{Colors.OKGREEN}✓ API key configured successfully{Colors.ENDC}")
        except Exception as e:
            self._show_api_configuration_error(e)
            raise

        # Initialize session manager for memory
        self.session_manager = SessionManager()

        # Initialize agents with progress indicators
        print(f"\n{Colors.OKCYAN}Initializing AI Agents...{Colors.ENDC}")

        try:
            # Initialize sub-agents first
            self.researcher = ResearcherAgent()
            print(f"{Colors.OKGREEN}  ✓ Researcher Agent ready{Colors.ENDC}")

            self.summarizer = SummarizerAgent()
            print(f"{Colors.OKGREEN}  ✓ Summarizer Agent ready{Colors.ENDC}")

            # Initialize coordinator and give it access to sub-agents
            self.coordinator = CoordinatorAgent()
            self.coordinator.set_agents(self.researcher, self.summarizer)
            print(f"{Colors.OKGREEN}  ✓ Coordinator Agent ready{Colors.ENDC}")

            print(
                f"\n{Colors.BOLD}{Colors.OKGREEN}🎉 All agents initialized successfully!{Colors.ENDC}\n"
            )

        except Exception as e:
            self._show_initialization_error(e)
            raise

    def research(
        self, query: str, session_id: str = None, mode: str = "detailed"
    ) -> dict:
        """
        Execute a research query through the multi-agent system.
        Now delegates to the Coordinator for full orchestration!

        Args:
            query: The research topic or question
            session_id: Optional session ID for conversation continuity
            mode: Output mode - 'detailed', 'brief', or 'summary-only'

        Returns:
            dict: Research results including summary, sources, and metadata
        """
        # Generate or retrieve session
        if not session_id:
            session_id = self.session_manager.create_session()

        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}📋 Research Query:{Colors.ENDC} {query}")
        print(f"{Colors.OKBLUE}🆔 Session ID:{Colors.ENDC} {session_id}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

        try:
            # LET THE COORDINATOR DO ALL THE ORCHESTRATION!
            results = self.coordinator.orchestrate_research(query)

            # Store in session for follow-up queries
            if results["success"]:
                self.session_manager.store(
                    session_id,
                    {
                        "query": query,
                        "plan": results["plan"],
                        "sources": results["sources"],
                        "report": results["report"],
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                # Add session info to results
                results["session_id"] = session_id
                results["mode"] = mode

            return results

        except Exception as e:
            self._show_research_error(e, query)
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "query": query,
            }

    def follow_up(self, query: str, session_id: str) -> dict:
        """
        Handle follow-up questions using previous research context.
        Now delegates to the Coordinator!

        Args:
            query: Follow-up question
            session_id: Previous session ID

        Returns:
            dict: Response with context from previous research
        """
        print(f"\n{Colors.OKCYAN}💬 Processing follow-up question...{Colors.ENDC}")

        # Retrieve previous context
        context = self.session_manager.retrieve(session_id)

        if not context:
            print(
                f"{Colors.WARNING}⚠ No previous context found. Starting new research...{Colors.ENDC}\n"
            )
            return self.research(query)

        print(
            f"{Colors.OKGREEN}✓ Using context from previous query: \"{context['query']}\"{Colors.ENDC}\n"
        )

        try:
            # LET THE COORDINATOR HANDLE FOLLOW-UPS!
            results = self.coordinator.orchestrate_follow_up(query, context)

            # Add session info
            results["session_id"] = session_id

            return results

        except Exception as e:
            self._show_research_error(e, query)
            return {"success": False, "error": str(e), "session_id": session_id}

    # Error handling methods with helpful troubleshooting

    def _show_api_key_error(self):
        """Display helpful error message for missing API key."""
        print(f"\n{Colors.FAIL}{'='*80}")
        print(f"❌ ERROR: Google API Key Not Found")
        print(f"{'='*80}{Colors.ENDC}\n")
        print(
            f"{Colors.WARNING}The GOOGLE_API_KEY environment variable is not set.{Colors.ENDC}\n"
        )
        print(f"{Colors.BOLD}How to fix:{Colors.ENDC}")
        print(f"  1. Create a .env file in the project root directory")
        print(f"  2. Add this line: GOOGLE_API_KEY=your_actual_api_key")
        print(
            f"  3. Get your API key from: {Colors.OKBLUE}https://ai.google.dev/{Colors.ENDC}\n"
        )
        print(
            f"{Colors.WARNING}Make sure .env is in your .gitignore file!{Colors.ENDC}\n"
        )

    def _show_api_configuration_error(self, error):
        """Display helpful error for API configuration issues."""
        print(f"\n{Colors.FAIL}{'='*80}")
        print(f"❌ ERROR: API Configuration Failed")
        print(f"{'='*80}{Colors.ENDC}\n")
        print(f"{Colors.WARNING}Error details: {str(error)}{Colors.ENDC}\n")
        print(f"{Colors.BOLD}Possible causes:{Colors.ENDC}")
        print(f"  • Invalid API key format")
        print(f"  • API key has been revoked")
        print(f"  • Network connectivity issues")
        print(f"  • API quota exceeded\n")
        print(f"{Colors.BOLD}How to fix:{Colors.ENDC}")
        print(
            f"  1. Verify your API key at: {Colors.OKBLUE}https://ai.google.dev/{Colors.ENDC}"
        )
        print(f"  2. Generate a new API key if needed")
        print(f"  3. Check your internet connection")
        print(f"  4. Review API usage quotas\n")

    def _show_initialization_error(self, error):
        """Display helpful error for agent initialization issues."""
        print(f"\n{Colors.FAIL}{'='*80}")
        print(f"❌ ERROR: Agent Initialization Failed")
        print(f"{'='*80}{Colors.ENDC}\n")
        print(f"{Colors.WARNING}Error details: {str(error)}{Colors.ENDC}\n")
        print(f"{Colors.BOLD}Possible causes:{Colors.ENDC}")
        print(f"  • Missing agent files (coordinator.py, researcher.py, summarizer.py)")
        print(f"  • Import errors in agent files")
        print(f"  • Model name not recognized by API\n")
        print(f"{Colors.BOLD}How to fix:{Colors.ENDC}")
        print(f"  1. Verify all files exist in agents/ directory")
        print(f"  2. Check for syntax errors in agent files")
        print(f"  3. Verify model names (gemini-1.5-flash, gemini-2.0-flash)")
        print(
            f"  4. Run: python -c 'from agents.coordinator import CoordinatorAgent'\n"
        )

    def _show_research_error(self, error, query):
        """Display helpful error for research failures."""
        print(f"\n{Colors.FAIL}{'='*80}")
        print(f"❌ ERROR: Research Failed")
        print(f"{'='*80}{Colors.ENDC}\n")
        print(f"{Colors.WARNING}Query: {query}{Colors.ENDC}")
        print(f"{Colors.WARNING}Error: {str(error)}{Colors.ENDC}\n")
        print(f"{Colors.BOLD}Possible causes:{Colors.ENDC}")
        print(f"  • API rate limit exceeded")
        print(f"  • Network timeout")
        print(f"  • Invalid model response")
        print(f"  • Search API issues\n")
        print(f"{Colors.BOLD}How to fix:{Colors.ENDC}")
        print(f"  1. Wait a moment and try again")
        print(f"  2. Check API rate limits")
        print(f"  3. Verify internet connection")
        print(f"  4. Try a simpler query\n")


def print_formatted_results(results: dict):
    """Enhanced result formatting with colors and multiple modes."""

    if not results["success"]:
        print(f"\n{Colors.FAIL}{'='*80}")
        print(f"❌ RESEARCH FAILED")
        print(f"{'='*80}{Colors.ENDC}\n")
        print(f"{Colors.WARNING}Error: {results['error']}{Colors.ENDC}\n")
        return

    # Header
    print(f"\n{Colors.HEADER}{'='*80}")
    print(f"{Colors.BOLD}📊 RESEARCH RESULTS{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

    # Query info
    print(f"{Colors.BOLD}📋 Query:{Colors.ENDC} {results['query']}")
    print(f"{Colors.OKBLUE}🆔 Session ID:{Colors.ENDC} {results['session_id']}")

    num_sources = results.get("num_sources", 0)
    if num_sources > 0:
        print(f"{Colors.OKGREEN}📚 Sources Analyzed:{Colors.ENDC} {num_sources}")

    if results.get("is_follow_up"):
        print(f"{Colors.OKCYAN}💬 Type:{Colors.ENDC} Follow-up question")

    # Research report
    print(f"\n{Colors.HEADER}{'-'*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}📄 RESEARCH SUMMARY{Colors.ENDC}")
    print(f"{Colors.HEADER}{'-'*80}{Colors.ENDC}\n")

    print(results["report"]["summary"])

    # Key findings (if available)
    if "key_findings" in results["report"] and results["report"]["key_findings"]:
        print(f"\n{Colors.HEADER}{'-'*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}🔑 KEY FINDINGS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'-'*80}{Colors.ENDC}\n")

        for i, finding in enumerate(results["report"]["key_findings"], 1):
            print(f"{Colors.OKGREEN}{i}.{Colors.ENDC} {finding}")

    # Sources (if available)
    if "sources" in results and results["sources"]:
        print(f"\n{Colors.HEADER}{'-'*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}📚 SOURCES{Colors.ENDC}")
        print(f"{Colors.HEADER}{'-'*80}{Colors.ENDC}\n")

        for i, source in enumerate(results["sources"][:5], 1):
            print(f"{Colors.OKCYAN}[{i}]{Colors.ENDC} {source['title']}")
            print(f"     {Colors.OKBLUE}{source['url']}{Colors.ENDC}\n")

    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")


def show_welcome_message():
    """Display welcome message with instructions."""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Welcome to Personal Research Assistant!{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    print(f"{Colors.OKCYAN}Features:{Colors.ENDC}")
    print(f"  • Multi-agent AI system powered by Google Gemini")
    print(f"  • Intelligent web search and synthesis")
    print(f"  • Context-aware follow-up questions")
    print(f"  • Session memory for continuous research\n")
    print(f"{Colors.OKCYAN}How to use:{Colors.ENDC}")
    print(f"  • Type your research question when prompted")
    print(f"  • Ask follow-up questions to dig deeper")
    print(f"  • Type 'quit', 'exit', or 'q' to exit\n")
    print(f"{Colors.WARNING}Note: This may take 10-30 seconds per query{Colors.ENDC}\n")


def main():
    """Main execution function with enhanced UX."""

    # Show welcome message
    show_welcome_message()

    # Initialize system
    try:
        system = ResearchAssistantSystem()
    except Exception as e:
        print(f"{Colors.FAIL}Failed to initialize system. Exiting.{Colors.ENDC}\n")
        sys.exit(1)

    # Interactive mode
    current_session = None
    query_count = 0

    while True:
        try:
            # Get user input
            print(f"{Colors.BOLD}{'─'*80}{Colors.ENDC}")
            query = input(f"{Colors.BOLD}💭 Your research query:{Colors.ENDC} ").strip()

            if not query:
                continue

            # Check for exit commands
            if query.lower() in ["quit", "exit", "q", "bye"]:
                print(
                    f"\n{Colors.OKGREEN}👋 Thank you for using Research Assistant!{Colors.ENDC}"
                )
                print(f"{Colors.OKCYAN}Total queries: {query_count}{Colors.ENDC}\n")
                break

            # Check if follow-up
            if current_session and query_count > 0:
                choice = (
                    input(
                        f"{Colors.OKCYAN}Is this a follow-up to previous query? (y/n):{Colors.ENDC} "
                    )
                    .strip()
                    .lower()
                )
                if choice == "y":
                    results = system.follow_up(query, current_session)
                else:
                    results = system.research(query)
                    current_session = results["session_id"]
            else:
                results = system.research(query)
                current_session = results["session_id"]

            query_count += 1
            print_formatted_results(results)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Interrupted by user.{Colors.ENDC}")
            print(f"{Colors.OKGREEN}👋 Goodbye!{Colors.ENDC}\n")
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}Unexpected error: {str(e)}{Colors.ENDC}\n")
            print(
                f"{Colors.WARNING}Please try again or type 'quit' to exit.{Colors.ENDC}\n"
            )


if __name__ == "__main__":
    main()
