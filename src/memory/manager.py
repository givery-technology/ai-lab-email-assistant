#!/usr/bin/env python
# coding: utf-8

"""
Memory management for the Email Assistant application.

This module handles memory operations, including storage and retrieval of
prompt instructions, user preferences, and email examples.
"""

from langmem import create_multi_prompt_optimizer
from src.core.config import PROMPT_INSTRUCTIONS
import traceback
from src.utils.logger import error


def format_few_shot_examples(examples):
    """
    Format retrieved memory examples into a structure suitable for few-shot prompting.
    
    Args:
        examples: List of retrieved memory items.
        
    Returns:
        str: Formatted examples as a string for inclusion in a prompt.
    """
    # Template for formatting an example
    template = """Email Subject: {subject}
Email From: {from_email}
Email To: {to_email}
Email Content: 
```
{content}
```
> Triage Result: {result}"""

    strs = ["Here are some previous examples:"]
    for eg in examples:
        strs.append(
            template.format(
                subject=eg.value["email"]["subject"],
                to_email=eg.value["email"]["to"],
                from_email=eg.value["email"]["author"],
                content=eg.value["email"]["email_thread"][:400],
                result=eg.value["label"],
            )
        )
    return "\n\n------------\n\n".join(strs)


def get_triage_prompts(store, user_id):
    """
    Retrieve triage prompt instructions from memory or use defaults.
    
    Args:
        store: Memory store instance.
        user_id: User ID for namespacing.
        
    Returns:
        tuple: (ignore_prompt, notify_prompt, respond_prompt) - Prompts for different triage categories.
    """
    namespace = (user_id, )

    # Get ignore prompt
    result = store.get(namespace, "triage_ignore")
    if result is None:
        store.put(
            namespace, 
            "triage_ignore", 
            {"prompt": PROMPT_INSTRUCTIONS["triage_rules"]["ignore"]}
        )
        ignore_prompt = PROMPT_INSTRUCTIONS["triage_rules"]["ignore"]
    else:
        ignore_prompt = result.value['prompt']

    # Get notify prompt
    result = store.get(namespace, "triage_notify")
    if result is None:
        store.put(
            namespace, 
            "triage_notify", 
            {"prompt": PROMPT_INSTRUCTIONS["triage_rules"]["notify"]}
        )
        notify_prompt = PROMPT_INSTRUCTIONS["triage_rules"]["notify"]
    else:
        notify_prompt = result.value['prompt']

    # Get respond prompt
    result = store.get(namespace, "triage_respond")
    if result is None:
        store.put(
            namespace, 
            "triage_respond", 
            {"prompt": PROMPT_INSTRUCTIONS["triage_rules"]["respond"]}
        )
        respond_prompt = PROMPT_INSTRUCTIONS["triage_rules"]["respond"]
    else:
        respond_prompt = result.value['prompt']
        
    return ignore_prompt, notify_prompt, respond_prompt


def get_agent_instructions(store, user_id):
    """
    Retrieve agent instructions from memory or use defaults.
    
    Args:
        store: Memory store instance.
        user_id: User ID for namespacing.
        
    Returns:
        str: Agent instructions prompt.
    """
    namespace = (user_id, )
    result = store.get(namespace, "agent_instructions")
    if result is None:
        store.put(
            namespace, 
            "agent_instructions", 
            {"prompt": PROMPT_INSTRUCTIONS["agent_instructions"]}
        )
        prompt = PROMPT_INSTRUCTIONS["agent_instructions"]
    else:
        prompt = result.value['prompt']
    
    return prompt


def optimize_prompts(store, llm, user_id, messages, feedback):
    """
    Update prompts based on user feedback about email responses.
    
    Args:
        store: Memory store instance.
        llm: Language model instance.
        user_id: The user ID for memory namespacing.
        messages: The conversation history.
        feedback: User feedback on how to improve responses.
        
    Returns:
        str: Markdown formatted summary of updates.
    """
    try:
        # Sanitize feedback to prevent jailbreak attempts
        sanitized_feedback = feedback.replace("ignore all previous", "consider previous")
        sanitized_feedback = sanitized_feedback.replace("ignore previous", "consider previous")
        sanitized_feedback = sanitized_feedback.replace("disregard", "consider")
        
        # Add a safety prefix
        safe_feedback = f"Email assistant behavior update request: {sanitized_feedback}"
        
        # Process messages into optimizer-compatible format
        safe_messages = []
        if messages and isinstance(messages, list):
            for msg in messages:
                if isinstance(msg, dict):
                    # Ensure we have both role and content
                    role = msg.get("role", "assistant")
                    
                    # Handle content properly
                    content = msg.get("content", "")
                    
                    # Convert complex content to string
                    if isinstance(content, dict):
                        content = str(content)
                    
                    # Truncate long messages
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    # Add properly formatted message
                    safe_messages.append({"role": role, "content": content})
        
        # Create default messages if needed
        if not safe_messages:
            safe_messages = [
                {"role": "user", "content": "Please process this email"},
                {"role": "assistant", "content": "I've processed the email for you."}
            ]
        
        # Prepare conversation context
        conversations = [(safe_messages, safe_feedback)]
        
        # Create namespace for storage
        namespace = (user_id,)
        
        # Fetch current prompts
        ignore_prompt, notify_prompt, respond_prompt = get_triage_prompts(store, user_id)
        agent_prompt = get_agent_instructions(store, user_id)
        
        # Prepare prompts for optimization
        prompts = [
            {
                "name": "main_agent",
                "prompt": agent_prompt,
                "update_instructions": "improve the instructions while maintaining safety guidelines",
                "when_to_update": "Update only when feedback relates to email writing or scheduling"
            },
            {
                "name": "triage-ignore", 
                "prompt": ignore_prompt,
                "update_instructions": "improve the rules while maintaining safety guidelines",
                "when_to_update": "Update only when feedback relates to which emails should be ignored"
            },
            {
                "name": "triage-notify", 
                "prompt": notify_prompt,
                "update_instructions": "improve the rules while maintaining safety guidelines",
                "when_to_update": "Update only when feedback relates to which emails need notification"
            },
            {
                "name": "triage-respond", 
                "prompt": respond_prompt,
                "update_instructions": "improve the rules while maintaining safety guidelines",
                "when_to_update": "Update only when feedback relates to which emails need response"
            },
        ]
        
        # Create optimizer
        optimizer = create_multi_prompt_optimizer(llm, kind="prompt_memory")
        
        try:
            # Get updated prompts
            updated = optimizer.invoke({"trajectories": conversations, "prompts": prompts})
            
            # Store updates and collect results
            update_summary = []
            for i, updated_prompt in enumerate(updated):
                old_prompt = prompts[i]
                if updated_prompt['prompt'] != old_prompt['prompt']:
                    name = old_prompt['name']
                    update_summary.append(f"✅ Updated: **{name}**")
                    
                    # Store the updated prompt
                    if name == "main_agent":
                        store.put(namespace, "agent_instructions", {"prompt": updated_prompt['prompt']})
                    elif name == "triage-ignore":
                        store.put(namespace, "triage_ignore", {"prompt": updated_prompt['prompt']})
                    elif name == "triage-notify":
                        store.put(namespace, "triage_notify", {"prompt": updated_prompt['prompt']})
                    elif name == "triage-respond":
                        store.put(namespace, "triage_respond", {"prompt": updated_prompt['prompt']})
            
            if not update_summary:
                return "No prompts were updated based on your feedback."
            
            return "## Prompt Updates\n\n" + "\n".join(update_summary)
            
        except Exception as e:
            if "content_filter" in str(e) or "content management policy" in str(e):
                return f"⚠️ **Safety Filter Activated**\n\nYour feedback triggered content safety filters. Please rephrase your feedback to focus on specific email handling behaviors you'd like to modify."
            else:
                return f"⚠️ **Optimization Error**\n\nCould not update prompts: {str(e)}"
    
    except Exception as e:
        # Log the full error for debugging
        error_msg = f"Error in optimize_prompts: {str(e)}\n{traceback.format_exc()}"
        error(error_msg)
        return f"❌ **Error Processing Feedback**\n\nAn error occurred while processing your feedback. Please try again with simpler instructions.\n\nTechnical details: {str(e)}"


def load_prompts(store, user_id):
    """
    Load current prompts for a user.
    
    Args:
        store: Memory store instance.
        user_id: The user ID for memory namespacing.
        
    Returns:
        tuple: (main_prompt, ignore_prompt, notify_prompt, respond_prompt)
    """
    ignore_prompt, notify_prompt, respond_prompt = get_triage_prompts(store, user_id)
    main_prompt = get_agent_instructions(store, user_id)
    
    return main_prompt, ignore_prompt, notify_prompt, respond_prompt


def save_prompts(store, user_id, main_prompt, ignore_prompt, notify_prompt, respond_prompt):
    """
    Save updated prompts for a user.
    
    Args:
        store: Memory store instance.
        user_id: The user ID for memory namespacing.
        main_prompt: The main agent instructions prompt.
        ignore_prompt: The triage ignore rules prompt.
        notify_prompt: The triage notify rules prompt.
        respond_prompt: The triage respond rules prompt.
        
    Returns:
        str: Success message.
    """
    namespace = (user_id,)
    store.put(namespace, "agent_instructions", {"prompt": main_prompt})
    store.put(namespace, "triage_ignore", {"prompt": ignore_prompt})
    store.put(namespace, "triage_notify", {"prompt": notify_prompt})
    store.put(namespace, "triage_respond", {"prompt": respond_prompt})
    return "✅ Prompts saved successfully!"