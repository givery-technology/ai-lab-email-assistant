#!/usr/bin/env python
# coding: utf-8

"""
LangGraph workflow definition for the Email Assistant application.

This module defines the graph structure for the email processing workflow,
connecting triage and response components into a coherent flow.
"""

from langgraph.graph import StateGraph, START, END
from src.core.models import State
from src.workflow.triage import triage_router
from src.workflow.response import setup_response_agent


def create_workflow(llm, llm_router, store, memory_tools):
    """
    Create the main workflow graph for the email assistant.
    
    This function defines the workflow as a state graph with nodes for triage
    and response, connected with appropriate edges.
    
    Args:
        llm: Language model for the response agent.
        llm_router: Language model with structured output for the triage router.
        store: Memory store for the workflow.
        memory_tools: Memory management tools.
        
    Returns:
        StateGraph: The compiled workflow graph ready for execution.
    """
    # Set up the response agent
    response_agent = setup_response_agent(llm, memory_tools, store)
    
    # Create triage router with provided dependencies
    def triage_with_deps(state, config, store):
        return triage_router(state, config, store, llm_router)
    
    # Create the state graph with our State definition
    email_graph = StateGraph(State)
    
    # Add nodes to the graph
    email_graph.add_node("triage_router", triage_with_deps)
    email_graph.add_node("response_agent", response_agent)
    
    # Define the graph's edges
    email_graph.add_edge(START, "triage_router")
    
    # Compile and return the graph
    return email_graph.compile(store=store)