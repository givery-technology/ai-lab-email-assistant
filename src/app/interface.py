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
            tool_message = f"🛠️ ツール実行: {tool_name}\n{content}"
            formatted_messages.append({
                "role": "assistant",
                "content": tool_message
            })
        else:
            # Other message types shown as system messages
            formatted_messages.append({
                "role": "system",
                "content": f"システム: {content}"
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
        "respond": "📧 返信が必要 - このメールには返信が必要です",
        "ignore": "🚫 無視してよい - このメールは無視しても問題ありません",
        "notify": "🔔 通知 - このメールには重要な情報が含まれています"
    }
    classification_text = classification_map.get(classification, f"不明: {classification}")
    
    # Create the classification result markdown
    classification_result = f"""
## 分類結果: {classification_text}

### 理由:
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
    with gr.Blocks(title="メールアシスタント") as demo:
        gr.Markdown("# メールアシスタント with LangGraph メモリー")
        gr.Markdown("メールを処理し、長期記憶機能を備えたAIによる返答を得ることができます。")
        
        with gr.Row():
            # Input column
            with gr.Column():
                gr.Markdown("### メール入力")
                user_id = gr.Textbox(label="ユーザーID", value="user123", info="メモリの名前空間に使用されます")
                author = gr.Textbox(label="差出人", placeholder="例: 田中花子 <hanako.tanaka@company.com>")
                to = gr.Textbox(label="宛先", placeholder="例: 鈴木一郎 <ichiro.suzuki@company.com>")
                subject = gr.Textbox(label="件名", placeholder="APIドキュメントについての質問")
                email_body = gr.Textbox(label="メール本文", lines=10, placeholder="鈴木様\n\nAPIドキュメントを確認していたのですが...\n\n田中")
                process_button = gr.Button("メールを処理", variant="primary")
            
            # Output column
            with gr.Column():
                gr.Markdown("### メール分析")
                classification_output = gr.Markdown(label="分類結果")
                chatbot_output = gr.Chatbot(label="エージェントとのやりとり", height=400, type="messages")
                
                with gr.Accordion("フィードバックと最適化", open=False):
                    gr.Markdown("返答に対するフィードバックを提供して、アシスタントの改善に協力してください：")
                    feedback_input = gr.Textbox(
                        label="フィードバック", 
                        placeholder="例: 'メールの最後は必ず「鈴木一郎」と署名してください' または 'marketing@company.comからのメールは無視してください' または 'build@company.comからのメールは無視してください'",
                        lines=2
                    )
                    feedback_button = gr.Button("フィードバックを送信して最適化", variant="secondary")
                    optimization_result = gr.Markdown(label="最適化結果")
        
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
            with gr.TabItem("メール処理"):
                gr.Markdown("上記がメイン処理画面です。")
                
            with gr.TabItem("プロンプト管理"):
                gr.Markdown("### プロンプトの閲覧と編集")
                gr.Markdown("メールアシスタントで使用されるプロンプトをカスタマイズできます。")
                
                prompt_user_id = gr.Textbox(label="ユーザーID", value="user123", info="プロンプトを読み込み/保存するユーザーIDを入力してください")
                load_prompts_btn = gr.Button("プロンプトを読み込む")
                
                main_agent_prompt = gr.TextArea(label="メインエージェントの指示", lines=5, placeholder="メインエージェントへの指示...")
                ignore_prompt_input = gr.TextArea(label="振り分け - 無視ルール", lines=5, placeholder="メールを無視するためのルール...")
                notify_prompt_input = gr.TextArea(label="振り分け - 通知ルール", lines=5, placeholder="メール通知のルール...")
                respond_prompt_input = gr.TextArea(label="振り分け - 返信ルール", lines=5, placeholder="メールに返信するためのルール...")
                
                save_prompts_btn = gr.Button("プロンプトを保存", variant="primary")
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
                    "田中花子 <hanako.tanaka@company.com>",
                    "鈴木一郎 <ichiro.suzuki@company.com>",
                    "プロジェクト状況について",
                    "鈴木様\n\n明日、プロジェクトの状況について簡単に打ち合わせできますでしょうか？\n\nよろしくお願いいたします。\n田中"
                ],
                [
                    "user123",
                    "マーケティングチーム <marketing@company.com>",
                    "全社員 <all-staff@company.com>",
                    "【お知らせ】来週の新製品発表について",
                    "皆様\n\n来週金曜日14時から新製品発表会を開催いたします。ぜひご参加ください。\n\n以上\nマーケティングチーム"
                ],
                [
                    "user123",
                    "ビルドシステム <build@company.com>",
                    "エンジニアリング <engineering@company.com>",
                    "【警告】mainブランチのビルド失敗",
                    "ビルド #4592 がmainブランチで失敗しました。\n\n原因: 認証モジュールの単体テスト失敗\nログ詳細: https://build.company.com/4592"
                ]
            ],
            inputs=[user_id, author, to, subject, email_body]
        )
        
    return demo