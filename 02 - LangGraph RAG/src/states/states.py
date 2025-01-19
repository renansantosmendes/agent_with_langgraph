from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from typing import Annotated, Literal, TypedDict
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from utils.utils import reduce_docs


class Router(TypedDict):
    """Classify user query."""

    logic: str
    type: Literal["more-info", "environmental", "general"]

from pydantic import BaseModel, Field

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, '1' or '0'"
    )

    @dataclass(kw_only=True)
    class InputState:
        """Represents the input state for the agent.

        This class defines the structure of the input state, which includes
        the messages exchanged between the user and the agent. It serves as
        a restricted version of the full State, providing a narrower interface
        to the outside world compared to what is maintained iternally.
        """

        messages: Annotated[list[AnyMessage], add_messages]

        """Messages track the primary execution state of the agent.

        Typically accumulates a pattern of Human/AI/Human/AI messages.

        Returns:
            A new list of messages with the messages from `right` merged into `left`.
            If a message in `right` has the same ID as a message in `left`, the
            message from `right` will replace the message from `left`."""

    # Primary agent state
    @dataclass(kw_only=True)
    class AgentState(InputState):
        """State of the retrieval graph / agent."""

        router: Router = field(default_factory=lambda: Router(type="general", logic=""))
        """The router's classification of the user's query."""
        steps: list[str] = field(default_factory=list)
        """A list of steps in the research plan."""
        documents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
        """Populated by the retriever. This is a list of documents that the agent can reference."""
        hallucination: GradeHallucinations = field(default_factory=lambda: GradeHallucinations(binary_score="0"))