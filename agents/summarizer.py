"""
Summarizer Agent - Research Assistant System

This agent synthesizes research findings into structured reports:
- Combines information from multiple sources
- Creates coherent summaries
- Formats citations properly
- Identifies key findings

Model: Gemini 1.5 Pro (high-quality synthesis)
"""

import logging
from google import generativeai as genai

logger = logging.getLogger(__name__)


class SummarizerAgent:
    """
    Synthesizes research findings into structured, well-cited reports.
    """

    def __init__(self):
        """Initialize summarizer with Gemini Pro model."""
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info("Summarizer Agent initialized with Gemini 2.5 Flash")

    def synthesize(self, query: str, sources: list, context: list = None) -> dict:
        """
        Synthesize research findings into a comprehensive report.

        Args:
            query: Original research query
            sources: List of search results with title, snippet, url
            context: Optional context from previous research

        Returns:
            dict: Structured report with summary, key findings, citations
        """
        logger.info(f"Synthesizing research for: '{query}'")

        if not sources:
            logger.warning("No sources provided for synthesis")
            return {
                "summary": "No sources available for research.",
                "key_findings": [],
                "citations": [],
            }

        try:
            # Create synthesis prompt
            synthesis_prompt = self._create_synthesis_prompt(query, sources, context)

            # Generate comprehensive summary
            response = self.model.generate_content(synthesis_prompt)
            report_text = response.text

            # Structure the report
            structured_report = self._structure_report(report_text, sources)

            logger.info("Research synthesis completed")
            return structured_report

        except Exception as e:
            logger.error(f"Error during synthesis: {e}")
            return {
                "summary": f"Error synthesizing research: {str(e)}",
                "key_findings": [],
                "citations": self._format_citations(sources),
            }

    def _create_synthesis_prompt(
        self, query: str, sources: list, context: list = None
    ) -> str:
        """
        Create a detailed prompt for research synthesis.

        Args:
            query: Research query
            sources: Search results
            context: Optional context

        Returns:
            str: Synthesis prompt
        """
        # Format sources for the prompt
        sources_text = ""
        for i, source in enumerate(sources, 1):
            sources_text += f"\n[Source {i}] {source['title']}\n"
            sources_text += f"URL: {source['url']}\n"
            sources_text += f"Content: {source['snippet']}\n"

        # Add context if provided
        context_text = ""
        if context:
            context_text = "\nAdditional Context:\n" + "\n".join(
                f"- {c}" for c in context
            )

        prompt = f"""
You are a research analyst creating a comprehensive report. Synthesize the following 
sources to answer this research query.

RESEARCH QUERY:
{query}

SOURCES:
{sources_text}
{context_text}

Create a comprehensive research report with:

1. EXECUTIVE SUMMARY (3-4 paragraphs)
   - Synthesize the main findings
   - Provide clear, factual information
   - Use an academic but accessible tone

2. KEY FINDINGS (5-7 bullet points)
   - List the most important discoveries
   - Be specific and evidence-based
   - Reference which sources support each finding

3. CONCLUSION (1 paragraph)
   - Summarize the implications
   - Suggest areas for further research if relevant

IMPORTANT:
- Be objective and balanced
- Cite sources naturally in the text [Source 1], [Source 2], etc.
- Do not make claims beyond what the sources support
- Focus on facts, not opinions
- Use clear, professional language

Begin your report:
"""
        return prompt

    def _structure_report(self, report_text: str, sources: list) -> dict:
        """
        Parse and structure the LLM's report into organized sections.

        Args:
            report_text: Raw report from LLM
            sources: Original sources for citations

        Returns:
            dict: Structured report
        """
        # Initialize report structure
        report = {
            "summary": "",
            "key_findings": [],
            "conclusion": "",
            "citations": self._format_citations(sources),
        }

        # Simple parsing - split by sections
        sections = report_text.split("\n\n")

        current_section = None
        summary_parts = []
        findings = []
        conclusion_parts = []

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Identify section headers
            if "EXECUTIVE SUMMARY" in section.upper() or "SUMMARY" in section.upper():
                current_section = "summary"
                continue
            elif "KEY FINDINGS" in section.upper() or "FINDINGS" in section.upper():
                current_section = "findings"
                continue
            elif "CONCLUSION" in section.upper():
                current_section = "conclusion"
                continue

            # Add content to appropriate section
            if current_section == "summary":
                summary_parts.append(section)
            elif current_section == "findings":
                # Extract bullet points
                lines = section.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and (
                        line.startswith("-")
                        or line.startswith("•")
                        or line[0].isdigit()
                    ):
                        # Remove bullet/number
                        clean_line = line.lstrip("-•0123456789. ").strip()
                        if clean_line:
                            findings.append(clean_line)
            elif current_section == "conclusion":
                conclusion_parts.append(section)
            else:
                # If no section identified yet, assume it's summary
                summary_parts.append(section)

        # Combine sections
        report["summary"] = "\n\n".join(summary_parts).strip()
        report["key_findings"] = findings[:7]  # Max 7 findings
        report["conclusion"] = "\n\n".join(conclusion_parts).strip()

        # If no structured findings found, extract from summary
        if not report["key_findings"]:
            report["key_findings"] = self._extract_findings_from_text(report["summary"])

        return report

    def _extract_findings_from_text(self, text: str) -> list:
        """
        Extract key findings from unstructured text using LLM.

        Args:
            text: Summary text

        Returns:
            list: Extracted findings
        """
        extraction_prompt = f"""
Extract 5 key findings from this research summary.
Format as a simple list.

Summary:
{text}

Key findings:
"""

        try:
            response = self.model.generate_content(extraction_prompt)
            findings_text = response.text

            findings = []
            for line in findings_text.split("\n"):
                line = line.strip()
                if line and (
                    line.startswith("-") or line.startswith("•") or line[0].isdigit()
                ):
                    clean = line.lstrip("-•0123456789. ").strip()
                    if clean:
                        findings.append(clean)

            return findings[:5]
        except:
            return []

    def _format_citations(self, sources: list) -> list:
        """
        Format sources as proper citations.

        Args:
            sources: List of search results

        Returns:
            list: Formatted citations
        """
        citations = []

        for i, source in enumerate(sources, 1):
            citation = {
                "number": i,
                "title": source["title"],
                "url": source["url"],
                "source_domain": source.get("source", ""),
                "apa_format": self._create_apa_citation(source),
            }
            citations.append(citation)

        return citations

    def _create_apa_citation(self, source: dict) -> str:
        """
        Create APA-style citation for a web source.

        Args:
            source: Source information

        Returns:
            str: APA formatted citation
        """
        # Simple APA format for web sources
        title = source["title"]
        url = source["url"]
        domain = source.get("source", "Unknown Source")

        # Format: Title. (n.d.). Retrieved from URL
        citation = f"{title}. (n.d.). {domain}. Retrieved from {url}"

        return citation
