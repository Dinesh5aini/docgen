# from pydantic import BaseModel
# from typing import List

# class UserInput(BaseModel):
#     project_title: str
#     primary_objective: str
#     problem_solves: str
#     abstract : str
#     problem_audience_facing: str
#     resources_available: str
#     risk_or_constraints: str
#     functional_requirements: str
#     technologies: List[str]
#     er_or_dataflow_diagram: str
#     components : List[str] 
#     development_methodology: str
#     testing_strategy: str
#     limitations: str
#     future_enhancements: str

# class DocumentSection(BaseModel):
#     section_id: str  # e.g., "1.1.2"
#     title: str
#     content: str
#     summary: str     # 2-3 sentence summary for context
#     depends_on: List[str]  # e.g., ["1.1.1"]

# class Document(BaseModel):
#     doc_id: str
#     sections: List[DocumentSection]
#     formatting: dict = {}  # To store font/styles later

from dataclasses import dataclass
from typing import List, Dict, Optional

# Instead of Pydantic models, we'll use dataclasses for Flask
# This will help with serialization and validation

@dataclass
class UserInput:
    project_title: str
    primary_objective: str
    problem_solves: str
    abstract: str
    problem_audience_facing: str
    resources_available: str
    risk_or_constraints: str
    functional_requirements: str
    technologies: List[str]
    er_or_dataflow_diagram: str
    components: List[str]
    development_methodology: str
    testing_strategy: str
    limitations: str
    future_enhancements: str

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            project_title=data.get("project_title", ""),
            primary_objective=data.get("primary_objective", ""),
            problem_solves=data.get("problem_solves", ""),
            abstract=data.get("abstract", ""),
            problem_audience_facing=data.get("problem_audience_facing", ""),
            resources_available=data.get("resources_available", ""),
            risk_or_constraints=data.get("risk_or_constraints", ""),
            functional_requirements=data.get("functional_requirements", ""),
            technologies=data.get("technologies", []),
            er_or_dataflow_diagram=data.get("er_or_dataflow_diagram", ""),
            components=data.get("components", []),
            development_methodology=data.get("development_methodology", ""),
            testing_strategy=data.get("testing_strategy", ""),
            limitations=data.get("limitations", ""),
            future_enhancements=data.get("future_enhancements", "")
        )


@dataclass
class DocumentSection:
    section_id: str  # e.g., "1.1.2"
    title: str
    content: str
    summary: str     # 2-3 sentence summary for context
    depends_on: List[str]  # e.g., ["1.1.1"]

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            section_id=data.get("section_id", ""),
            title=data.get("title", ""),
            content=data.get("content", ""),
            summary=data.get("summary", ""),
            depends_on=data.get("depends_on", [])
        )


@dataclass
class Document:
    doc_id: str
    sections: List[DocumentSection]
    formatting: Dict = None  # To store font/styles later

    def __post_init__(self):
        if self.formatting is None:
            self.formatting = {}

    @classmethod
    def from_dict(cls, data: Dict):
        doc_sections = [
            DocumentSection.from_dict(section) 
            for section in data.get("sections", [])
        ]
        
        return cls(
            doc_id=data.get("doc_id", ""),
            sections=doc_sections,
            formatting=data.get("formatting", {})
        )