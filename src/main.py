#!/usr/bin/env python
# coding: utf-8

"""
Main entry point for the Email Assistant application.

This module initializes all components and starts the application,
setting up the language models, memory store, graph workflow, and web interface.
"""

import argparse
import sys
import socket

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.store.memory import InMemoryStore

from src.app.interface import create_gradio_interface
from src.core.config import (
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    DEFAULT_PORT,
    validate_env_vars
)
from src.workflow.graph import create_workflow
from src.tools.memory import create_memory_tools
from src.core.models import Router
from src.utils.logger import EmailAssistantLogger, info


def setup_language_models():
    """
    Initialize and configure the language models.
    
    Returns:
        tuple: (llm, llm_router) - Language models for general use and structured output.
    """
    # Instantiate the Azure Chat Model
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME, 
        openai_api_version=AZURE_OPENAI_API_VERSION,   
        temperature=0, 
    )
    
    # Create a variant with structured output for the router
    llm_router = llm.with_structured_output(Router)
    
    return llm, llm_router


def setup_memory_store():
    """
    Initialize the memory store with embedding configuration.
    
    Returns:
        InMemoryStore: Configured memory store instance.
    """
    # Create an InMemoryStore with Azure OpenAI embeddings
    store = InMemoryStore(
        index={"embed": f"azure_openai:{AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME}"}
    )
    
    return store


def find_available_port(preferred_port):
    """
    Find an available port starting from the preferred port.
    
    Args:
        preferred_port: The port to try first.
        
    Returns:
        int: An available port.
        
    Raises:
        SystemExit: If no available port is found.
    """
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    if not is_port_in_use(preferred_port):
        return preferred_port
        
    # Try to find an available port
    for port_offset in range(1, 10):
        alternate_port = preferred_port + port_offset
        if not is_port_in_use(alternate_port):
            print(f"⚠️  Port {preferred_port} is in use, using port {alternate_port} instead.")
            return alternate_port
            
    print(f"❌ Error: Could not find an available port in range {preferred_port}-{preferred_port+9}.")
    print("Please specify a different port with the --port option.")
    sys.exit(1)


def main():
    """
    Main function that initializes and starts the Email Assistant application.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Email Assistant Application")
    parser.add_argument("--share", action="store_true", help="Create a shareable link (may require frpc download)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to run the Gradio app on")
    args = parser.parse_args()
    
    # Find an available port
    port = find_available_port(args.port)
    
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    validate_env_vars()
    
    # Set up logger
    logger = EmailAssistantLogger(log_dir="email_logs")
    info("Email Assistant application starting")
    
    # Set up language models
    llm, llm_router = setup_language_models()
    
    # Set up memory store
    store = setup_memory_store()
    
    # Create memory tools with namespacing
    memory_tools = create_memory_tools((
        "email_assistant", 
        "{langgraph_user_id}",
        "collection"
    ))
    
    # Create the workflow graph
    email_agent = create_workflow(llm, llm_router, store, memory_tools)
    
    # Create the Gradio interface
    demo = create_gradio_interface(email_agent, store, llm)
    
    # Launch the demo
    print(f"Starting Email Assistant at http://localhost:{port}")
    demo.launch(share=args.share, server_port=port)


if __name__ == "__main__":
    main()