import os
import json
from typing import Dict, Tuple
from collections import deque
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Configure the Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class SchemaGenerator:
    """
    Handles the generation of a JSON-based document schema using Gemini.
    """

    @staticmethod
    def generate_schema(user_input: dict) -> str:
        """
        Generates a JSON schema for the technical document structure based on user input.
        """
        prompt = f"""
        Generate a detailed schema for a technical document titled **"{user_input.get("project_title", "Technical Document")}"**.

            Below is the user-provided context. Use it to structure the document:

        ### User Input:
            {SchemaGenerator._format_user_input(user_input)}

        ### IMPORTANT - RESPONSE FORMAT REQUIREMENTS:
        - You MUST return ONLY valid JSON without any other text.
        - The JSON must have a "sections" array.
        - Each section must include: section_id, title, keywords (as array), depends_on (as array).
        - The response must be pure JSON with no markdown formatting.
        - Example structure:

        {{
          "sections": [
            {{
              "section_id": "1.1",
              "title": "Introduction",
              "keywords": ["objective", "problem", "audience"],
              "depends_on": []
            }},
            {{
              "section_id": "2.1",
              "title": "Background",
              "keywords": ["context", "prior work"],
              "depends_on": ["1.1"]
            }}
          ]
        }}
            """

        # Use a more structured generation approach
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature = 0.1,  # Lower temperature for more deterministic output
                response_mime_type =  "application/json"  # Request JSON output specifically
            )
        )

        return response.text.strip()

    @staticmethod
    def _format_user_input(user_input: dict) -> str:
        """
        Formats the user input into a readable form inside the prompt.
        """
        fields = [
            ("Primary Objective", "primary_objective"),
            ("Problem it Solves", "problem_solves"),
            ("Abstract", "abstract"),
            ("Target Audience Pain Points", "problem_audience_facing"),
            ("Resources Available", "resources_available"),
            ("Risks/Constraints", "risk_or_constraints"),
            ("Functional Requirements", "functional_requirements"),
            ("Technologies", "technologies"),
            ("Design Diagrams Needed", "er_or_dataflow_diagram"),
            ("System Components", "components"),
            ("Development Methodology", "development_methodology"),
            ("Testing Strategy", "testing_strategy"),
            ("Limitations", "limitations"),
            ("Future Enhancements", "future_enhancements"),
        ]

        return "\n".join(
            f"**{title}**: {user_input.get(key) or '[Infer based on context]'}"
            for title, key in fields
        )


class DocumentGenerator:
    """
    Handles detailed section-wise generation of the document using context tracking.
    """

    def __init__(self, project_context: Dict):
        self.project_context = {
            **project_context,
            "generated_sections": deque(maxlen=10),
            "full_summary": ""
        }

    def generate_section(self, section_data: Dict) -> Tuple[str, str]:
        """
        Generates content and a summary for a single section.

        Args:
            section_data: Dictionary containing section_id, title, keywords, depends_on.

        Returns:
            Tuple of (content, summary)
        """
        prompt = self._build_prompt(section_data)

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )

        try:
            result = json.loads(response.text)
            content = result["content"]
            summary = result["summary"]

            self._update_context(section_data["section_id"], summary)

            return content, summary

        except json.JSONDecodeError:
            return self._fallback_generation(section_data)

    def _build_prompt(self, section_data: Dict) -> str:
        """
        Constructs the prompt to generate a specific section considering its dependencies and context.
        """
        dependencies = "\n".join(
            f"- {dep}: {self._get_summary_for(dep)}"
            for dep in section_data.get("depends_on", [])
        ) or "None"

        return f"""
        **Project Overview**:
        {self.project_context['abstract']}

        **Technical Foundation**:
        - Objectives: {self.project_context['primary_objective']}
        - Technologies: {", ".join(self.project_context['technologies'])}
        - Key Requirements: {self.project_context['functional_requirements']}

        **Current Task**:
        Section: {section_data['title']} ({section_data['section_id']})
        Dependent Sections:
        {dependencies}

        **Recent Summaries (Last 3 Sections)**:
        {self._get_recent_sections(3)}

        **Instructions**:
        1. Write detailed technical content.
        2. Include a 2–4 sentence summary.
        3. Focus on technical accuracy and logical flow.

        **Keywords**: {", ".join(section_data['keywords'])}

        **Output Format (JSON)**:
        {{
            "content": "Full detailed text...",
            "summary": "Concise technical summary..."
        }}
        """

    def _update_context(self, section_id: str, summary: str):
        """
        Updates the context with newly generated section summaries.
        """
        self.project_context["generated_sections"].append((section_id, summary))
        self.project_context["full_summary"] = "\n".join(
            [f"{sid}: {summ}" for sid, summ in self.project_context["generated_sections"]]
        )

    def _get_summary_for(self, section_id: str) -> str:
        """
        Fetches the summary for a specific section ID.
        """
        for sid, summ in self.project_context["generated_sections"]:
            if sid == section_id:
                return summ
        return "[Not generated yet]"

    def _get_recent_sections(self, n: int) -> str:
        """
        Returns formatted text for the last 'n' sections.
        """
        return "\n".join(
            f"{sid}: {summ}"
            for sid, summ in list(self.project_context["generated_sections"])[-n:]
        )

    def _fallback_generation(self, section_data: Dict) -> Tuple[str, str]:
        """
        Backup simple generation if JSON response fails.
        """
        content_prompt = f"""
        Write technical content for {section_data['title']} based on keywords and project context:
        Context: {self.project_context['full_summary']}
        Keywords: {section_data['keywords']}
        """
        content = client.models.generate_content(model="gemini-2.0-flash", contents = content_prompt).text.strip()

        summary_prompt = f"""
        Summarize this section in 2–4 technical sentences:
        {content}
        """
        summary = client.models.generate_content(model="gemini-2.0-flash", contents = summary_prompt).text.strip()

        self._update_context(section_data["section_id"], summary)

        return content, summary