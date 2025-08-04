## 6. README.md - Documentation
```markdown
# Food Order Chatbot

A sophisticated AI-powered chatbot for taking restaurant food orders, built with Streamlit, LangChain, and RAG (Retrieval-Augmented Generation).

## Features

- **Intelligent Chatbot**: Natural language processing for order taking
- **RAG System**: Enhanced responses using menu knowledge base
- **Custom Agents**: LangChain agents with custom database tools
- **Order Management**: Complete order processing and storage
- **Analytics Dashboard**: Insights into sales and popular items
- **User-Friendly Interface**: Clean Streamlit interface

## Architecture

### Components
1. **RAG System** (`rag_system.py`): Vector-based menu search using ChromaDB
2. **Database Layer** (`database.py`): SQLite database for orders and menu
3. **Agent System** (`agents.py`): LangChain agents with custom tools
4. **Frontend** (`app.py`): Streamlit interface

### Database Schema
- **orders**: Stores customer orders with items and totals
- **menu**: Restaurant menu items with categories and prices

## Installation

1. Clone the repository:
```bash
git clone https://github.com/khushbu311/aiagent.git
cd aiagent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Start Ordering**: Enter your name to begin
2. **View Menu**: Ask "Show me the menu" or use the quick button
3. **Place Orders**: Say something like "I want 2 pizzas and 1 burger"
4. **Get Recommendations**: Ask "What's popular?" or "What do you recommend?"
5. **View Dashboard**: Check analytics and popular items

## Technical Implementation

### RAG System
- Uses GROQAI embeddings for menu item vectorization
- ChromaDB for efficient similarity search
- Contextual menu recommendations

### Agent Architecture
- **DatabaseTool**: Custom tool for database operations
- **MenuSearchTool**: RAG-powered menu search
- **OrderParsingTool**: Natural language order parsing
- **FoodOrderAgent**: Main conversational agent

### Key Features
- Multi-item order processing
- Natural language understanding
- Order confirmation and validation
- Real-time analytics
- Persistent chat history

## API Integration

The system uses GROQ's GPT-3.5-turbo for natural language processing. Make sure to:
- Sign up and obtain an API key from https://console.groq.com
- Use the llama3-70b-8192 model for optimized inference performance
- Integrate using the Groq-compatible OpenAI-style API endpoint
- Monitor latency, throughput, and usage from the Groq console


## Testing

Test the chatbot with various scenarios:
- Simple orders: "I want a pizza"
- Complex orders: "2 burgers, 1 salad, and 3 drinks"
- Menu queries: "What desserts do you have?"
- Recommendations: "What's good here?"


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
```

## 7. .env.example
```
GROQ_API_KEY=your_groq_api_key_here
```

This implementation provides:

✅ **Complete RAG System**: Menu search using vector embeddings
✅ **Custom Agents**: LangChain agents with specialized tools
✅ **Database Integration**: SQLite with custom database tool
✅ **Streamlit Frontend**: User-friendly chat interface
✅ **Order Processing**: Multi-item order handling
✅ **Analytics Dashboard**: Sales insights and popular items
✅ **Documentation**: Comprehensive setup and usage guide

The system handles natural language orders, provides menu recommendations, and stores all data persistently. The modular design makes it easy to extend and customize for different restaurant needs.