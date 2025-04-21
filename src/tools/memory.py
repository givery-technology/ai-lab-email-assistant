#!/usr/bin/env python
# coding: utf-8

"""
Memory tool functions for the Email Assistant application.

This module provides tools for managing and searching memory in the email assistant.
"""

from langmem import create_manage_memory_tool, create_search_memory_tool


def create_memory_tools(namespace_template):
    """
    Create tools for managing and searching memory.
    
    Args:
        namespace_template: Template for the memory namespace, typically includes
                            user_id placeholder.
    
    Returns:
        tuple: (manage_memory_tool, search_memory_tool) - Tools for memory operations.
    """
    manage_memory = create_manage_memory_tool(
        namespace=namespace_template
    )
    
    search_memory = create_search_memory_tool(
        namespace=namespace_template
    )
    
    return manage_memory, search_memory