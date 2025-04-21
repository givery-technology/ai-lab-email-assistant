#!/usr/bin/env python
# coding: utf-8

"""
Response agent functionality for the Email Assistant application.

This module handles generating appropriate responses for emails that require
a reply, using LLM-based agents with memory capabilities.
"""

from langgraph.prebuilt import create_react_agent
from src.core.prompts import agent_system_prompt_memory
from src.core.config import USER_PROFILE
from src.memory.manager import get_agent_instructions
from src.tools.actions import write_email, schedule_meeting, check_calendar_availability
from src.utils.logger import log_agent_action


def create_prompt_function(store):
    """
    Create a prompt generation function for the response agent.
    
    This function returns another function that will be used by the
    react agent to generate appropriate system prompts for each request.
    
    Args:
        store: Memory store for retrieving prompt instructions.
        
    Returns:
        function: A function that generates prompts based on current state.
    """
    def create_prompt(state, config, store):
        """
        Generate a prompt for the response agent based on the current state.
        
        Args:
            state: Current application state.
            config: Configuration object with user settings.
            store: Memory store for retrieving prompt instructions.
            
        Returns:
            list: A list of formatted messages to serve as the agent's prompt.
        """
        # Get user ID from config for memory namespacing
        user_id = config['configurable']['langgraph_user_id']
        
        # Get agent instructions from memory
        prompt = get_agent_instructions(store, user_id)
        
        # Create a user profile string from the background info
        user_profile = USER_PROFILE["user_profile_background"]
        
        # Format the system prompt with instructions and user profile
        return [
            {
                "role": "system", 
                "content": agent_system_prompt_memory.format(
                    instructions=prompt,
                    profile=user_profile,  # Add the missing profile parameter
                    **USER_PROFILE
                )
            }
        ] + state['messages']
    
    return create_prompt


def setup_response_agent(llm, memory_tools, store):
    """
    Set up the response agent with tools and prompt function.
    
    Args:
        llm: Language model for the agent.
        memory_tools: Memory management tools.
        store: Memory store instance.
        
    Returns:
        callable: The configured response agent.
    """
    # Unpack memory tools
    manage_memory_tool, search_memory_tool = memory_tools
    
    # Combine all tools
    tools = [
        write_email, 
        schedule_meeting,
        check_calendar_availability,
        manage_memory_tool,
        search_memory_tool
    ]
    
    # Create prompt function for the agent
    prompt_func = create_prompt_function(store)
    
    # Create and return the ReAct agent
    agent = create_react_agent(
        llm,
        tools=tools,
        prompt=prompt_func,
        store=store  # Pass store for memory operations
    )
    
    # Wrap the agent to add logging
    def logged_agent(state, config, store):
        """Wrapper for the response agent that adds logging."""
        # Call the underlying agent using invoke() method instead of direct calling
        result = agent.invoke(state, config=config)
        
        # Log relevant actions if found in the result
        if hasattr(result, 'messages'):
            for msg in result.messages:
                if hasattr(msg, 'name') and msg.name == 'write_email':
                    # Log email writing actions
                    try:
                        content = msg.content
                        log_agent_action('write_email', {'recipient': content.split("'")[0]})
                    except:
                        # If parsing fails, log with generic details
                        log_agent_action('write_email', {'details': 'Email sent'})
                elif hasattr(msg, 'name') and msg.name == 'schedule_meeting':
                    # Log meeting scheduling actions
                    log_agent_action('schedule_meeting', {'details': msg.content})
        
        return result
    
    return logged_agent