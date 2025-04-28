def parse_schema(gemini_response: str) -> list:
    """Convert Gemini's schema JSON string to a list of sections."""
    import json
    import logging
    
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    try:
        # Log the response for debugging
        logger.debug(f"Raw Gemini response: {gemini_response}")
        
        # Attempt to extract JSON from the response
        # Sometimes AI responses include markdown or text before/after the JSON
        import re
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```|(\{[\s\S]*\})', gemini_response)
        
        if json_match:
            json_str = json_match.group(1) or json_match.group(2)
            logger.debug(f"Extracted JSON: {json_str}")
            return json.loads(json_str)
        else:
            logger.debug("No JSON pattern found in response")
            parsed_data = json.loads(gemini_response)
            return parsed_data.get("sections", parsed_data)
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        logger.error(f"Response that failed to parse: {gemini_response}")
        
        # More comprehensive fallback
        return [
            {"section_id": "1.1", "title": "Introduction", "keywords": ["objective", "problem"]},
            {"section_id": "2.1", "title": "Problem Statement", "keywords": ["challenges", "context"]},
            {"section_id": "3.1", "title": "Requirements", "keywords": ["functional", "non-functional"]},
            {"section_id": "4.1", "title": "Design", "keywords": ["architecture", "components"]},
            {"section_id": "5.1", "title": "Implementation", "keywords": ["code", "modules"]},
            {"section_id": "6.1", "title": "Testing", "keywords": ["validation", "results"]},
            {"section_id": "7.1", "title": "Conclusion", "keywords": ["summary", "future work"]}
        ]