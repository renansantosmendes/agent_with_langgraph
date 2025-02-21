from langchain.tools.retriever import create_retriever_tool

from agentic_rag.content_manager.web_content_manager import retriever

retriever_tool = create_retriever_tool(
    retriever=retriever,
    name="retrieve_blog_posts",
    description="Search and return information about Lilian Weng blog posts on LLM agents, "
                "prompt engineering, and adversarial attacks on LLMs.",
)

tools = [retriever_tool]