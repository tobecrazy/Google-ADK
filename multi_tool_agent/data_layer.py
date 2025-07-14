from typing import Any, Dict, List, Optional

from google.generativeai import GenerativeModel
from google.generativeai.types import Tool

class DataLayer:
    """Manages interaction with the knowledge graph using provided tools.

    This class is responsible for creating, reading, updating, and deleting
    entities and relations within the knowledge graph. It uses a GenerativeModel
    to execute tool calls for these operations.
    """

    def __init__(self, model: GenerativeModel):
        """Initializes the DataLayer with a GenerativeModel instance.

        Args:
            model: An instance of GenerativeModel configured with the necessary tools.
        """
        self._model = model

    def create_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Creates new entities in the knowledge graph.

        Args:
            entities: A list of dictionaries, each representing an entity to create.
                      Each dictionary must have 'entityType', 'name', and 'observations'.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].create_entities(entities=entities)

    def create_relations(self, relations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Creates new relations between entities in the knowledge graph.

        Args:
            relations: A list of dictionaries, each representing a relation to create.
                       Each dictionary must have 'from', 'relationType', and 'to'.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].create_relations(relations=relations)

    def add_observations(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Adds new observations to existing entities in the knowledge graph.

        Args:
            observations: A list of dictionaries, each representing observations to add.
                          Each dictionary must have 'entityName' and 'contents'.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].add_observations(observations=observations)

    def delete_entities(self, entity_names: List[str]) -> Dict[str, Any]:
        """Deletes entities and their associated relations from the knowledge graph.

        Args:
            entity_names: A list of entity names to delete.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].delete_entities(entityNames=entity_names)

    def delete_observations(self, deletions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deletes specific observations from entities in the knowledge graph.

        Args:
            deletions: A list of dictionaries, each specifying observations to delete.
                       Each dictionary must have 'entityName' and 'observations'.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].delete_observations(deletions=deletions)

    def delete_relations(self, relations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deletes specific relations from the knowledge graph.

        Args:
            relations: A list of dictionaries, each specifying relations to delete.
                       Each dictionary must have 'from', 'relationType', and 'to'.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].delete_relations(relations=relations)

    def read_graph(self) -> Dict[str, Any]:
        """Reads the entire knowledge graph.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].read_graph()

    def search_nodes(self, query: str) -> Dict[str, Any]:
        """Searches for nodes in the knowledge graph based on a query.

        Args:
            query: The search query to match against entity names, types, and observation content.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].search_nodes(query=query)

    def open_nodes(self, names: List[str]) -> Dict[str, Any]:
        """Opens specific nodes in the knowledge graph by their names.

        Args:
            names: A list of entity names to retrieve.

        Returns:
            The result of the tool call.
        """
        return self._model.tools[0].open_nodes(names=names)
