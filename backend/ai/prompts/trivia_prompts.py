"""
Prompt templates for Pokemon trivia question generation
"""

from typing import Dict, Any


class TriviaPrompts:
    """Collection of prompt templates for generating Pokemon trivia questions"""
    
    BASE_SYSTEM_PROMPT = """
You are a Pokemon trivia expert. Generate engaging, accurate trivia questions based on the provided Pokemon data.
Follow these rules:
1. Create exactly one question per request
2. Include 4 multiple choice options (A, B, C, D)
3. Mark the correct answer clearly
4. Use official Pokemon names and data
5. Make questions challenging but fair
6. Vary difficulty levels appropriately
7. Return response in valid JSON format
"""

    BASIC_INFO_PROMPT = """
{system_prompt}

Based on this Pokemon data, create a trivia question about basic information (name, type, generation, etc.):

Pokemon Data:
{pokemon_data}

Return your response in this exact JSON format:
{{
    "question": "Your question here",
    "options": {{
        "A": "Option A",
        "B": "Option B", 
        "C": "Option C",
        "D": "Option D"
    }},
    "correct_answer": "A",
    "difficulty": "easy|medium|hard",
    "category": "basic_info",
    "explanation": "Brief explanation of the answer"
}}
"""

    STATS_PROMPT = """
{system_prompt}

Based on this Pokemon data, create a trivia question about stats, abilities, or battle-related information:

Pokemon Data:
{pokemon_data}

Return your response in this exact JSON format:
{{
    "question": "Your question here",
    "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C", 
        "D": "Option D"
    }},
    "correct_answer": "A",
    "difficulty": "easy|medium|hard",
    "category": "stats_abilities",
    "explanation": "Brief explanation of the answer"
}}
"""

    MOVES_PROMPT = """
{system_prompt}

Based on this Pokemon data, create a trivia question about moves, movesets, or battle techniques:

Pokemon Data:
{pokemon_data}

Return your response in this exact JSON format:
{{
    "question": "Your question here",
    "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
    }},
    "correct_answer": "A", 
    "difficulty": "easy|medium|hard",
    "category": "moves",
    "explanation": "Brief explanation of the answer"
}}
"""

    EVOLUTION_PROMPT = """
{system_prompt}

Based on this Pokemon data, create a trivia question about evolution chains, evolution methods, or related Pokemon:

Pokemon Data:
{pokemon_data}

Return your response in this exact JSON format:
{{
    "question": "Your question here",
    "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
    }},
    "correct_answer": "A",
    "difficulty": "easy|medium|hard", 
    "category": "evolution",
    "explanation": "Brief explanation of the answer"
}}
"""

    GENERAL_PROMPT = """
{system_prompt}

Based on this Pokemon data, create an interesting trivia question about any aspect of this Pokemon:

Pokemon Data:
{pokemon_data}

Question Focus: {focus}
Difficulty: {difficulty}

Return your response in this exact JSON format:
{{
    "question": "Your question here",
    "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
    }},
    "correct_answer": "A",
    "difficulty": "{difficulty}",
    "category": "general",
    "explanation": "Brief explanation of the answer"
}}
"""

    @classmethod
    def get_prompt(cls, prompt_type: str, pokemon_data: Dict[Any, Any], **kwargs) -> str:
        """
        Get a formatted prompt template
        
        Args:
            prompt_type: Type of prompt (basic_info, stats, moves, evolution, general)
            pokemon_data: Pokemon data to include in prompt
            **kwargs: Additional parameters for specific prompts
            
        Returns:
            Formatted prompt string
        """
        system_prompt = cls.BASE_SYSTEM_PROMPT
        
        prompt_templates = {
            "basic_info": cls.BASIC_INFO_PROMPT,
            "stats": cls.STATS_PROMPT, 
            "moves": cls.MOVES_PROMPT,
            "evolution": cls.EVOLUTION_PROMPT,
            "general": cls.GENERAL_PROMPT
        }
        
        if prompt_type not in prompt_templates:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        template = prompt_templates[prompt_type]
        
        # Format the template with common parameters
        formatted_prompt = template.format(
            system_prompt=system_prompt,
            pokemon_data=pokemon_data,
            **kwargs
        )
        
        return formatted_prompt
    
    @classmethod
    def get_available_types(cls) -> list:
        """Get list of available prompt types"""
        return ["basic_info", "stats", "moves", "evolution", "general"] 