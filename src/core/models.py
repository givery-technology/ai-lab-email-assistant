#!/usr/bin/env python
# coding: utf-8

"""
Data models for the Email Assistant application.

This module defines the data models, types, and schemas used throughout the application,
including the Router model for email classification and State type for managing application state.
"""

from typing_extensions import TypedDict, Literal, Annotated, NotRequired
from pydantic import BaseModel, Field
from langgraph.graph import add_messages


class Router(BaseModel):
    """
    Model for analyzing and classifying emails.
    
    This model is used with the LLM to define the expected output structure
    for email classification decisions.
    """

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["ignore", "respond", "notify"] = Field(
        description="The classification of an email: 'ignore' for irrelevant emails, "
        "'notify' for important information that doesn't need a response, "
        "'respond' for emails that need a reply",
    )


class State(TypedDict):
    """
    Application state type definition for the LangGraph state management.
    
    This defines the structure of the state that flows through the LangGraph nodes.
    The add_messages annotation ensures proper handling of message accumulation.
    """
    
    email_input: dict
    messages: Annotated[list, add_messages]
    classification: NotRequired[str]  # To store email classification result
    reasoning: NotRequired[str]  # To store reasoning behind the classification


class EmailInput(TypedDict):
    """
    Structure for email input data.
    
    This defines the expected format for email data throughout the application,
    ensuring consistency in how emails are represented.
    """
    
    author: str  # Sender's email address and name
    to: str  # Recipient's email address and name
    subject: str  # Email subject line
    email_thread: str  # Full email content/thread