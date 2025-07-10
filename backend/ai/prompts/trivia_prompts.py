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

    MULTIPLE_QUESTIONS_SYSTEM_PROMPT = """
You are a Pokemon trivia expert. Generate engaging, accurate trivia questions based on the provided Pokemon data.
Follow these rules:
1. Create exactly the requested number of questions per request
2. Include 4 multiple choice options (A, B, C, D) for each question
3. Mark the correct answer clearly for each question
4. Use official Pokemon names and data
5. Make questions challenging but fair
6. Ensure all questions have the same difficulty level as requested
7. Make questions diverse and avoid repetition
8. Return response in valid JSON format
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

    MULTIPLE_QUESTIONS_PROMPT = """
{system_prompt}

Based on this Pokemon data, create exactly 5 trivia questions about this Pokemon.
All questions should have the same difficulty level and follow the same configuration.

Pokemon Data:
{pokemon_data}

Question Type: {question_type}
Difficulty: {difficulty}
{focus_line}

Requirements:
- Generate exactly 5 unique questions about this Pokemon
- All questions must be {difficulty} difficulty
- Questions should be diverse and cover different aspects within the {question_type} category
- Each question should have 4 multiple choice options (A, B, C, D)
- Avoid repetitive or very similar questions

Return your response in this exact JSON format:
{{
    "questions": [
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
            "category": "{question_type}",
            "explanation": "Brief explanation of the answer"
        }},
        {{
            "question": "Your second question here",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "B",
            "difficulty": "{difficulty}",
            "category": "{question_type}",
            "explanation": "Brief explanation of the answer"
        }},
        {{
            "question": "Your third question here",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "C",
            "difficulty": "{difficulty}",
            "category": "{question_type}",
            "explanation": "Brief explanation of the answer"
        }},
        {{
            "question": "Your fourth question here",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "D",
            "difficulty": "{difficulty}",
            "category": "{question_type}",
            "explanation": "Brief explanation of the answer"
        }},
        {{
            "question": "Your fifth question here",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "difficulty": "{difficulty}",
            "category": "{question_type}",
            "explanation": "Brief explanation of the answer"
        }}
    ]
}}
"""

    @classmethod
    def get_prompt(cls, prompt_type: str, pokemon_data: Dict[Any, Any], **kwargs) -> str:
        """
        Get a formatted prompt template
        
        Args:
            prompt_type: Type of prompt (basic_info, stats, moves, evolution, general, multiple_questions)
            pokemon_data: Pokemon data to include in prompt
            **kwargs: Additional parameters for specific prompts
            
        Returns:
            Formatted prompt string
        """
        # Choose the appropriate system prompt
        if prompt_type == "multiple_questions":
            system_prompt = cls.MULTIPLE_QUESTIONS_SYSTEM_PROMPT
        else:
            system_prompt = cls.BASE_SYSTEM_PROMPT
        
        prompt_templates = {
            "basic_info": cls.BASIC_INFO_PROMPT,
            "stats": cls.STATS_PROMPT, 
            "moves": cls.MOVES_PROMPT,
            "evolution": cls.EVOLUTION_PROMPT,
            "general": cls.GENERAL_PROMPT,
            "multiple_questions": cls.MULTIPLE_QUESTIONS_PROMPT
        }
        
        if prompt_type not in prompt_templates:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        template = prompt_templates[prompt_type]
        
        # Handle special formatting for multiple_questions prompt
        if prompt_type == "multiple_questions":
            focus_line = ""
            if kwargs.get("focus"):
                focus_line = f"Question Focus: {kwargs['focus']}"
            
            formatted_prompt = template.format(
                system_prompt=system_prompt,
                pokemon_data=pokemon_data,
                focus_line=focus_line,
                **kwargs
            )
        else:
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