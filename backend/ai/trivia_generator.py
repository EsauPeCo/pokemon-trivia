"""
Pokemon trivia question generator using Gemini AI
"""

import json
import random
from typing import Dict, Any, Optional, List
from .gemini_client import GeminiClient
from .prompts.trivia_prompts import TriviaPrompts


class TriviaGenerator:
    """
    Generates Pokemon trivia questions using Gemini AI and prompt templates
    """

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize trivia generator

        Args:
            gemini_client: Pre-configured GeminiClient instance
        """
        self.gemini_client = gemini_client or GeminiClient()
        self.prompts = TriviaPrompts()

    def generate_question(
        self,
        pokemon_data: Dict[Any, Any],
        question_type: str = "general",
        difficulty: str = "medium",
        focus: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a trivia question for a specific Pokemon

        Args:
            pokemon_data: Pokemon data from database
            question_type: Type of question (basic_info, stats, moves, evolution, general)
            difficulty: Question difficulty (easy, medium, hard)
            focus: Optional focus area for general questions

        Returns:
            Generated trivia question as dictionary
        """
        try:
            # Prepare Pokemon data string for prompt
            pokemon_info = self._format_pokemon_data(pokemon_data)

            # Get the appropriate prompt
            prompt_kwargs = {"difficulty": difficulty}

            # For general questions, always provide a focus (default if none provided)
            if question_type == "general":
                prompt_kwargs["focus"] = focus or "general Pokemon knowledge"

            prompt = self.prompts.get_prompt(
                question_type, pokemon_info, **prompt_kwargs
            )

            # Generate response using Gemini
            response = self.gemini_client.generate_response(prompt)

            # Parse JSON response
            question_data = self._parse_response(response)

            # Add metadata
            question_data["pokemon_id"] = pokemon_data.get("id")
            question_data["pokemon_name"] = pokemon_data.get("name")
            question_data["generated_at"] = self._get_timestamp()

            return question_data

        except Exception as e:
            raise RuntimeError(f"Failed to generate trivia question: {str(e)}")

    def generate_random_question(
        self, pokemon_data: Dict[Any, Any], difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a random trivia question with random type and difficulty

        Args:
            pokemon_data: Pokemon data from database
            difficulty: Optional specific difficulty, otherwise random

        Returns:
            Generated trivia question as dictionary
        """
        # Random question type
        question_types = self.prompts.get_available_types()
        question_type = random.choice(question_types)

        # Random difficulty if not specified
        if not difficulty:
            difficulties = ["easy", "medium", "hard"]
            difficulty = random.choice(difficulties)

        # Random focus for general questions
        focus = None
        if question_type == "general":
            focus_options = [
                "appearance and design",
                "habitat and behavior",
                "lore and background",
                "competitive usage",
                "type effectiveness",
            ]
            focus = random.choice(focus_options)

        return self.generate_question(
            pokemon_data,
            question_type=question_type,
            difficulty=difficulty,
            focus=focus,
        )

    def generate_multiple_questions(
        self,
        pokemon_list: List[Dict[Any, Any]],
        count: int = 5,
        difficulty: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple trivia questions from a list of Pokemon

        Args:
            pokemon_list: List of Pokemon data
            count: Number of questions to generate
            difficulty: Optional difficulty filter

        Returns:
            List of generated trivia questions
        """
        if not pokemon_list:
            raise ValueError("Pokemon list cannot be empty")

        questions = []
        selected_pokemon = random.sample(pokemon_list, min(count, len(pokemon_list)))

        for pokemon in selected_pokemon:
            try:
                question = self.generate_random_question(pokemon, difficulty)
                questions.append(question)
            except Exception as e:
                print(
                    f"Failed to generate question for {pokemon.get('name', 'Unknown')}: {e}"
                )
                continue

        return questions

    def _format_pokemon_data(self, pokemon_data: Dict[Any, Any]) -> str:
        """
        Format Pokemon data into a readable string for prompts

        Args:
            pokemon_data: Raw Pokemon data

        Returns:
            Formatted Pokemon information string
        """
        # Extract key information for the prompt
        info = {
            "name": pokemon_data.get("name", "Unknown"),
            "id": pokemon_data.get("id", "Unknown"),
            "types": pokemon_data.get("types", []),
            "height": pokemon_data.get("height", "Unknown"),
            "weight": pokemon_data.get("weight", "Unknown"),
            "abilities": pokemon_data.get("abilities", []),
            "stats": pokemon_data.get("stats", {}),
            "moves": pokemon_data.get("moves", [])[
                :10
            ],  # Limit moves for prompt length
        }

        # Format as readable text
        formatted = f"""
Name: {info['name']}
ID: #{info['id']}
Types: {', '.join(info['types']) if info['types'] else 'Unknown'}
Height: {info['height']}
Weight: {info['weight']}
Abilities: {', '.join(info['abilities']) if info['abilities'] else 'None'}
Base Stats: {info['stats'] if info['stats'] else 'Not available'}
Sample Moves: {', '.join(info['moves']) if info['moves'] else 'None'}
""".strip()

        return formatted

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Gemini response and extract JSON

        Args:
            response: Raw response from Gemini

        Returns:
            Parsed question data
        """
        try:
            # Try to find JSON in the response
            response = response.strip()

            # Remove markdown formatting if present
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]

            # Parse JSON
            question_data = json.loads(response)

            # Validate required fields
            required_fields = [
                "question",
                "options",
                "correct_answer",
                "difficulty",
                "category",
            ]
            for field in required_fields:
                if field not in question_data:
                    raise ValueError(f"Missing required field: {field}")

            return question_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Gemini: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse response: {e}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()

    def set_temperature(self, temperature: float):
        """Update Gemini client temperature"""
        self.gemini_client.set_temperature(temperature)
