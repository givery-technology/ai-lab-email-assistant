# Email Assistant

**English version below** / **英語版は下にあります**

## メールアシスタント

LangGraph、LangChain、Azure OpenAIを使用して構築されたAIパワードメールアシスタントで、自動トリアージ、応答生成、メモリベースの学習を通じてユーザーのメール管理をサポートします。

## プロジェクト構造

```
emailAssistance/
├── docs/                   # ドキュメンテーション
│   ├── technical_blog_english.md           
│   └── technical_blog_japanese.md        
├── logs/                   # ログファイル
│   └── email_logs/         # メール特有のログ
├── scripts/                # アプリケーション実行用スクリプト
│   └── run.sh              # メイン実行スクリプト
├── src/                    # ソースコード
│   ├── app/                # ウェブインターフェース
│   │   ├── __init__.py
│   │   └── interface.py    # Gradioインターフェース
│   ├── core/               # コアアプリケーションロジック
│   │   ├── __init__.py
│   │   ├── config.py       # 設定
│   │   ├── models.py       # データモデル
│   │   └── prompts.py      # システムプロンプト
│   ├── memory/             # メモリ管理
│   │   ├── __init__.py
│   │   └── manager.py      # メモリ操作
│   ├── tools/              # エージェントツール
│   │   ├── __init__.py
│   │   ├── actions.py      # メールとカレンダーツール
│   │   └── memory.py       # メモリツール
│   ├── utils/              # ユーティリティ関数
│   │   ├── __init__.py
│   │   └── logger.py       # ロギング機能
│   ├── workflow/           # LangGraphワークフロー
│   │   ├── __init__.py
│   │   ├── graph.py        # ワークフロー定義
│   │   ├── response.py     # レスポンスエージェント
│   │   └── triage.py       # トリアージ機能
│   ├── __init__.py         # パッケージマーカー
│   └── main.py             # エントリーポイント
├── .env                    # 環境変数（作成する必要があります）
└── requirements.txt        # 依存関係
```

## 機能

- **メールトリアージ**: 受信メールを自動的に「無視」、「通知」、または「応答」に分類
- **レスポンス生成**: メールに対して文脈に適した返信を作成
- **カレンダー管理**: 予定の確認と会議のスケジュール
- **メモリシステム**: インタラクションから学習し、時間とともに改善:
  - **セマンティックメモリ**: 事実とユーザーの好みを保存
  - **エピソードメモリ**: 過去の例から学習
  - **手続き的メモリ**: フィードバックに基づいて動作を更新

## インストール

Python 3.11以上が必要です。プロジェクトをセットアップするには、次の手順に従ってください:

1. リポジトリをクローン:
   ```bash
   git clone https://github.com/givery-technology/ai-lab-email-assistant.git
   cd ai-lab-email-assistant
   ```

2. 仮想環境の作成と有効化:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. 依存関係のインストール:
   ```bash
   pip install -r requirements.txt
   ```

4. Azure OpenAI認証情報を含む`.env`ファイルを作成:
   ```
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=2023-05-15
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your_embedding_model
   ```

## 使用方法

提供されているスクリプトを使用してアプリケーションを実行:

```bash
./scripts/run.sh
```

または、Pythonから直接実行:

```bash
python -m src.main
```

これによりGradioウェブインターフェースが起動し、ブラウザで http://localhost:7860 からアクセスできます。

## 開発

プロジェクトは以下のモジュールに整理されています:

- `app`: Gradioを使用したウェブインターフェース
- `core`: 構成やデータモデルなどの基本コンポーネント
- `memory`: メモリ管理機能
- `tools`: メール、カレンダー、メモリ操作用のエージェントツール
- `utils`: ユーティリティ関数とロギング
- `workflow`: LangGraphワークフロー定義

---

# Email Assistant

An AI-powered email assistant built with LangGraph, LangChain, and Azure OpenAI that helps users manage their emails through automated triage, response generation, and memory-based learning.

## Project Structure

```
emailAssistance/
├── docs/                   # Documentation
│   ├── technical_blog_english.md           
│   └── technical_blog_japanese.md        
├── logs/                   # Log files
│   └── email_logs/         # Email specific logs
├── scripts/                # Scripts for running the application
│   └── run.sh              # Main run script
├── src/                    # Source code
│   ├── app/                # Web interface
│   │   ├── __init__.py
│   │   └── interface.py    # Gradio interface
│   ├── core/               # Core application logic
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration
│   │   ├── models.py       # Data models
│   │   └── prompts.py      # System prompts
│   ├── memory/             # Memory management
│   │   ├── __init__.py
│   │   └── manager.py      # Memory operations
│   ├── tools/              # Agent tools
│   │   ├── __init__.py
│   │   ├── actions.py      # Email and calendar tools
│   │   └── memory.py       # Memory tools
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   └── logger.py       # Logging functionality
│   ├── workflow/           # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── graph.py        # Workflow definition
│   │   ├── response.py     # Response agent
│   │   └── triage.py       # Triage functionality
│   ├── __init__.py         # Package marker
│   └── main.py             # Entry point
├── .env                    # Environment variables (create this)
└── requirements.txt        # Dependencies
```

## Features

- **Email Triage**: Automatically classify incoming emails as 'ignore', 'notify', or 'respond'
- **Response Generation**: Create contextually appropriate replies for emails
- **Calendar Management**: Check availability and schedule meetings
- **Memory System**: Learn from interactions and improve over time:
  - **Semantic Memory**: Store facts and user preferences
  - **Episodic Memory**: Learn from past examples
  - **Procedural Memory**: Update behavior based on feedback

## Installation

Python 3.11 or higher is required. Follow these steps to set up the project:

1. Clone the repository:
   ```bash
   git clone https://github.com/givery-technology/ai-lab-email-assistant.git
   cd ai-lab-email-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=2023-05-15
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your_embedding_model
   ```

## Usage

Run the application using the provided script:

```bash
./scripts/run.sh
```

Or directly with Python:

```bash
python -m src.main
```

This will start the Gradio web interface, which you can access in your browser at http://localhost:7860.

## Development

The project is organized into modules:

- `app`: Web interface with Gradio
- `core`: Essential components like configuration and data models
- `memory`: Memory management functionality
- `tools`: Agent tools for email, calendar, and memory operations
- `utils`: Utility functions and logging
- `workflow`: LangGraph workflow definition




