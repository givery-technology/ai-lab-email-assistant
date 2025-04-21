#!/usr/bin/env python
# coding: utf-8

"""
Gradio web interface for the Email Assistant application.

This module implements the user interface using Gradio, allowing users to
interact with the email assistant through a web browser.
"""

import gradio as gr
from src.utils.logger import debug, info
from src.memory.manager import optimize_prompts, load_prompts, save_prompts


def format_messages_for_chatbot(messages):
    """
    Format LangChain messages into the format expected by Gradio Chatbot.
    
    Args:
        messages: List of LangChain message objects.
        
    Returns:
        list: Formatted messages for Gradio Chatbot.
    """
    formatted_messages = []
    
    for message in messages:
        content = message.content if hasattr(message, 'content') else str(message)
        
        # Handle different message types appropriately
        if message.type == 'human':
            # Add a user message
            formatted_messages.append({
                "role": "user",
                "content": content
            })
        elif message.type == 'ai':
            # Add an assistant message
            formatted_messages.append({
                "role": "assistant",
                "content": content
            })
        elif message.type == 'tool':
            # Tool calls are shown as assistant messages with tool prefix
            tool_name = message.name if hasattr(message, 'name') else "Unknown Tool"
            tool_message = f"🛠️ Tool Call: {tool_name}\n{content}"
            formatted_messages.append({
                "role": "assistant",
                "content": tool_message
            })
        else:
            # Other message types shown as system messages
            formatted_messages.append({
                "role": "system",
                "content": f"System: {content}"
            })
    
    return formatted_messages


def process_email(email_agent, store, llm, user_id, author, to, subject, email_body):
    """
    Process an email using the Email Assistant agent.
    
    Args:
        email_agent: The LangGraph email assistant agent.
        store: Memory store instance.
        llm: Language model instance.
        user_id: User ID for memory namespacing.
        author: Email sender.
        to: Email recipient.
        subject: Email subject.
        email_body: Email content.
        
    Returns:
        tuple: (classification_result, chatbot_messages)
    """
    # Create the email input dictionary
    email_input = {
        "author": author,
        "to": to,
        "subject": subject,
        "email_thread": email_body
    }
    
    # Create the config dictionary
    config = {"configurable": {"langgraph_user_id": user_id}}
    
    # Define the initial state
    initial_state = {"email_input": email_input, "messages": []}
    
    # Invoke the email agent
    response = email_agent.invoke(initial_state, config=config)
    
    # Extract classification and reasoning
    classification = response.get("classification", "Not classified")
    reasoning = response.get("reasoning", "No reasoning provided")
    
    # Format the classification result for display
    classification_map = {
        "respond": "📧 RESPOND - This email requires a response",
        "ignore": "🚫 IGNORE - This email can be safely ignored",
        "notify": "🔔 NOTIFY - This email contains important information"
    }
    classification_text = classification_map.get(classification, f"Unknown: {classification}")
    
    # Create the classification result markdown
    classification_result = f"""
## Classification: {classification_text}

### Reasoning:
{reasoning}
"""
    
    # Format messages for the chatbot
    chatbot_messages = format_messages_for_chatbot(response.get("messages", []))
    
    info(f"Email processed - Classification: {classification}")
    
    return classification_result, chatbot_messages


def create_gradio_interface(email_agent, store, llm):
    """
    Create the Gradio web interface for the Email Assistant.
    
    Args:
        email_agent: The LangGraph email assistant agent.
        store: Memory store instance.
        llm: Language model instance.
        
    Returns:
        gr.Blocks: The Gradio interface.
    """
    with gr.Blocks(title="Email Assistant") as demo:
        gr.Markdown("# Email Assistant with LangGraph Memory")
        gr.Markdown("Process emails and get AI-powered responses with long-term memory capabilities.")
        
        with gr.Row():
            # Input column
            with gr.Column():
                gr.Markdown("### Email Input")
                user_id = gr.Textbox(label="User ID", value="user123", info="Used for memory namespacing")
                author = gr.Textbox(label="From", placeholder="e.g., Alice Smith <alice.smith@company.com>")
                to = gr.Textbox(label="To", placeholder="e.g., John Doe <john.doe@company.com>")
                subject = gr.Textbox(label="Subject", placeholder="Quick question about API documentation")
                email_body = gr.Textbox(label="Email Body", lines=10, placeholder="Hi John,\n\nI was reviewing the API documentation...")
                process_button = gr.Button("Process Email", variant="primary")
            
            # Output column
            with gr.Column():
                gr.Markdown("### Email Analysis")
                classification_output = gr.Markdown(label="Classification Result")
                chatbot_output = gr.Chatbot(label="Agent Interaction", height=400, type="messages")
                
                with gr.Accordion("Provide Feedback & Optimize", open=False):
                    gr.Markdown("Help improve the assistant by providing feedback on responses:")
                    feedback_input = gr.Textbox(
                        label="Feedback", 
                        placeholder="E.g., 'Always sign your emails with John Doe' or 'Ignore emails from marketing@company.com'",
                        lines=2
                    )
                    feedback_button = gr.Button("Submit Feedback & Optimize", variant="secondary")
                    optimization_result = gr.Markdown(label="Optimization Result")
        
        # Set up state for storing messages
        saved_messages_state = gr.State([])
        
        # Function to process email and save messages
        def process_and_save_messages(user_id, author, to, subject, email_body):
            classification, messages = process_email(
                email_agent, store, llm, user_id, author, to, subject, email_body
            )
            return classification, messages, messages
        
        # Connect the button to the processing function that saves messages
        process_button.click(
            process_and_save_messages,
            inputs=[user_id, author, to, subject, email_body],
            outputs=[classification_output, chatbot_output, saved_messages_state]
        )
        
        # Function to handle feedback and optimize prompts
        def handle_feedback(user_id, messages, feedback):
            return optimize_prompts(store, llm, user_id, messages, feedback)
        
        # Connect the feedback button to the optimization function
        feedback_button.click(
            handle_feedback,
            inputs=[user_id, saved_messages_state, feedback_input],
            outputs=[optimization_result]
        )
        
        # Add tabs for main interface and prompt editing
        with gr.Tabs():
            with gr.TabItem("Email Processing"):
                gr.Markdown("This is the main email processing interface above.")
                
            with gr.TabItem("Prompt Management"):
                gr.Markdown("### View and Edit Prompts")
                gr.Markdown("View and customize the prompts used by the Email Assistant.")
                
                prompt_user_id = gr.Textbox(label="User ID", value="user123", info="Enter the user ID to load/save prompts for")
                load_prompts_btn = gr.Button("Load Prompts")
                
                main_agent_prompt = gr.TextArea(label="Main Agent Instructions", lines=5, placeholder="Instructions for the main agent...")
                ignore_prompt_input = gr.TextArea(label="Triage - Ignore Rules", lines=5, placeholder="Rules for ignoring emails...")
                notify_prompt_input = gr.TextArea(label="Triage - Notify Rules", lines=5, placeholder="Rules for email notifications...")
                respond_prompt_input = gr.TextArea(label="Triage - Respond Rules", lines=5, placeholder="Rules for responding to emails...")
                
                save_prompts_btn = gr.Button("Save Prompts", variant="primary")
                prompt_status = gr.Markdown()
                
                # Function to handle prompt loading
                def handle_load_prompts(user_id):
                    return load_prompts(store, user_id)
                
                # Function to handle prompt saving
                def handle_save_prompts(user_id, main_prompt, ignore_prompt, notify_prompt, respond_prompt):
                    return save_prompts(store, user_id, main_prompt, ignore_prompt, notify_prompt, respond_prompt)
                
                # Connect the load button
                load_prompts_btn.click(
                    handle_load_prompts,
                    inputs=[prompt_user_id],
                    outputs=[main_agent_prompt, ignore_prompt_input, notify_prompt_input, respond_prompt_input]
                )
                
                # Connect the save button
                save_prompts_btn.click(
                    handle_save_prompts,
                    inputs=[prompt_user_id, main_agent_prompt, ignore_prompt_input, notify_prompt_input, respond_prompt_input],
                    outputs=[prompt_status]
                )
        
        # Add example inputs
        gr.Examples(
            [
                [
                    "user123",
                    "Alice Smith <alice.smith@company.com>",
                    "John Doe <john.doe@company.com>",
                    "Quick question about API documentation",
                    "Hi John,\n\nI was reviewing the API documentation for the new authentication service and noticed a few endpoints seem to be missing from the specs. Could you help clarify if this was intentional or if we should update the docs?\n\nSpecifically, I'm looking at:\n- /auth/refresh\n- /auth/validate\n\nThanks!\nAlice"
                ],
                [
                    "user123",
                    "Marketing Team <marketing@company.com>",
                    "All Staff <all-staff@company.com>",
                    "Exciting New Product Launch Next Week!",
                    "Hello everyone,\n\nWe're thrilled to announce our exciting new product launch next week! Join us for the virtual event on Friday at 2pm.\n\nBest regards,\nMarketing Team"
                ],
                [
                    "user123",
                    "Build System <build@company.com>",
                    "Engineering <engineering@company.com>",
                    "[ALERT] Build failure in main branch",
                    "Build #4592 has failed in main branch.\n\nFailure: Unit tests failing in auth module.\nSee build logs: https://build.company.com/4592"
                ]
            ],
            inputs=[user_id, author, to, subject, email_body]
        )
        
    return demo