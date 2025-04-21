#!/usr/bin/env python
# coding: utf-8

"""
Email triage functionality for the Email Assistant application.

This module handles the classification of incoming emails into categories
(ignore, notify, respond) based on content analysis and user preferences.
"""

from typing import Literal
from langgraph.types import Command

from src.core.models import State
from src.memory.manager import format_few_shot_examples, get_triage_prompts
from src.core.config import USER_PROFILE
from src.utils.logger import log_email_processing
from src.core.prompts import triage_system_prompt, triage_user_prompt


def triage_router(state: State, config, store, llm_router) -> Command[
    Literal["response_agent", "__end__"]
]:
    """
    Analyze an email and determine how it should be handled.
    
    This function extracts email details, retrieves relevant examples and rules from memory,
    and then classifies the email as 'ignore', 'notify', or 'respond'.
    
    Args:
        state: Current application state containing the email.
        config: Configuration object containing user settings.
        store: Memory store for retrieving and storing information.
        llm_router: Language model configured for structured output.
        
    Returns:
        Command: Indicates the next step in the workflow and any state updates.
    """
    # Extract email details from state
    author = state['email_input']['author']
    to = state['email_input']['to']
    subject = state['email_input']['subject']
    email_thread = state['email_input']['email_thread']

    # Get user ID from config for memory namespacing
    user_id = config['configurable']['langgraph_user_id']
    
    # Retrieve similar examples from memory
    examples_namespace = (
        "email_assistant",
        user_id,
        "examples"
    )
    examples = store.search(
        examples_namespace, 
        query=str({"email": state['email_input']})
    ) 
    formatted_examples = format_few_shot_examples(examples)

    # Get triage prompt instructions from memory
    ignore_prompt, notify_prompt, respond_prompt = get_triage_prompts(store, user_id)
    
    # Construct the system prompt with user profile, rules, and examples
    system_prompt = triage_system_prompt.format(
        full_name=USER_PROFILE["full_name"],
        name=USER_PROFILE["name"],
        user_profile_background=USER_PROFILE["user_profile_background"],
        triage_no=ignore_prompt,
        triage_notify=notify_prompt,
        triage_email=respond_prompt,
        examples=formatted_examples
    )
    
    # Construct the user prompt with email details
    user_prompt = triage_user_prompt.format(
        author=author, 
        to=to, 
        subject=subject, 
        email_thread=email_thread
    )
    
    # Call the language model to classify the email
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    
    # Log the email processing
    log_email_processing(state['email_input'], result.classification, result.reasoning)
    
    # Handle the classification result
    if result.classification == "respond":
        classification_text = "RESPOND - This email requires a response"
        print(f"📧 Classification: {classification_text}")
        goto = "response_agent"
        update = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Respond to the email {state['email_input']}",
                }
            ],
            "classification": result.classification,
            "reasoning": result.reasoning
        }
    elif result.classification == "ignore":
        classification_text = "IGNORE - This email can be safely ignored"
        print(f"🚫 Classification: {classification_text}")
        update = {
            "classification": result.classification,
            "reasoning": result.reasoning
        }
        goto = "__end__"
    elif result.classification == "notify":
        classification_text = "NOTIFY - This email contains important information"
        print(f"🔔 Classification: {classification_text}")
        update = {
            "classification": result.classification,
            "reasoning": result.reasoning
        }
        goto = "__end__"
    else:
        raise ValueError(f"Invalid classification: {result.classification}")
    
    return Command(goto=goto, update=update)