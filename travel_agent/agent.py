from google.adk.agents import Agent

class TravelAgent(Agent):
    def __call__(self, prompt: str) -> str:
        """
        This is the root agent for the travel agent application.
        It takes a prompt and returns a simple response.
        """
        return f"Hello from the travel agent! You said: {prompt}"

root_agent = TravelAgent(
    name="travel_agent",
    description="A simple travel agent.",
    model="gemini-2.0-flash"
)
