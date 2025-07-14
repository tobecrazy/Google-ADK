import datetime
from typing import Dict, Optional

class InputHandler:
    def parse_input(self, user_input: str) -> Dict:
        """Parses the user input to extract travel information."""
        # This is a placeholder implementation. A more sophisticated NLP-based
        # parser will be implemented later.
        parts = user_input.split()
        return {
            "departure_city": parts[0],
            "destination": parts[1],
            "departure_date": parts[2] if len(parts) > 2 else str(datetime.date.today()),
            "duration": int(parts[3]) if len(parts) > 3 else 1,
            "budget": int(parts[4]) if len(parts) > 4 else 100,
        }
