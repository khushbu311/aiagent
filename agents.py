from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
import json
import re
from database import OrderDatabase
from rag_system import MenuRAG
from pydantic import Field
from typing import Any
from pydantic import PrivateAttr
from langchain_groq import ChatGroq

class DatabaseTool(BaseTool):
    """Custom tool for database interactions"""
    name = "database_tool"
    description = "Tool for interacting with the restaurant database to get menu items, create orders, and retrieve analytics"
    db: Any = Field(default=None, exclude=True)  # Using Any type for flexibility

    def __init__(self, db: OrderDatabase):
        super().__init__()
        self.db = db
    
    def _run(self, action: str, **kwargs) -> str:
        """Execute database operations"""
        print(action,77777777777777777777777)
        try:
            if action == "get_menu":
                menu_items = self.db.get_menu()
                if not menu_items:
                    return "Our menu is currently empty. Please check back later."
                
                # Group items by category
                menu_by_category = {}
                for item in menu_items:
                    if item['category'] not in menu_by_category:
                        menu_by_category[item['category']] = []
                    menu_by_category[item['category']].append(item)
                
                # Build formatted menu string
                menu_str = "Here's our complete menu:\n\n"
                for category, items in menu_by_category.items():
                    menu_str += f"=== {category.upper()} ===\n"
                    for item in items:
                        menu_str += f"- {item['name']}: ${item['price']:.2f}"
                        if 'description' in item:
                            menu_str += f" - {item['description']}"
                        menu_str += "\n"
                    menu_str += "\n"
                
                return menu_str
            
            elif action == "create_order":
                customer_name = kwargs.get('customer_name')
                items = kwargs.get('items', [])
                total_amount = kwargs.get('total_amount', 0)
                
                order_id = self.db.create_order(customer_name, items, total_amount)
                return f"Order created successfully with ID: {order_id}"
            
            elif action == "get_analytics":
                analytics = self.db.get_order_analytics()
                return json.dumps(analytics, indent=2)
            
            else:
                return f"Unknown action: {action}"
        
        except Exception as e:
            return f"Error executing database operation: {str(e)}"

class MenuSearchTool(BaseTool):
    """Tool for searching menu using RAG"""
    name = "menu_search"
    description = "Search menu items using natural language queries. Use this when users ask about specific foods, categories, or want recommendations."
    rag_system: Any = Field(default=None, exclude=True)
    def __init__(self, rag_system: MenuRAG):
        super().__init__()
        self.rag_system = rag_system
    
    def _run(self, query: str) -> str:
        """Search menu using RAG"""
        try:
            print(query,555555555555555555)
            results = self.rag_system.search_menu(query)
            if not results:
                return "No menu items found for your query."
            
            response = f"Found {len(results)} menu items:\n\n"
            for item in results:
                response += f"• {item['name']} - ${item['price']:.2f} ({item['category']})\n"
            
            return response
        except Exception as e:
            return f"Error searching menu: {str(e)}"

class OrderParsingTool(BaseTool):
    """Tool for parsing order information from user messages"""
    name = "order_parser"
    description = "Parse user messages to extract order information including items and quantities"
    db: Any = Field(default=None, exclude=True)  # Using Any type for flexibility

    def __init__(self, db: OrderDatabase):
        super().__init__()
        self.db = db
    
    def _run(self, user_message: str) -> str:
        """Parse order from user message"""
        try:
            menu_items = self.db.get_menu()
            menu_dict = {item['name'].lower(): item for item in menu_items}
            
            # Simple parsing logic - can be enhanced with NLP
            parsed_items = []
            total_amount = 0
            
            # Look for patterns like "2 pizza", "one burger", etc.
            words = user_message.lower().split()
            
            for i, word in enumerate(words):
                # Check for quantities
                quantity = 1
                if word.isdigit():
                    quantity = int(word)
                    if i + 1 < len(words):
                        item_word = words[i + 1]
                    else:
                        continue
                elif word in ['one', 'a', 'an']:
                    quantity = 1
                    if i + 1 < len(words):
                        item_word = words[i + 1]
                    else:
                        continue
                else:
                    item_word = word
                
                # Find matching menu items
                for menu_name, menu_item in menu_dict.items():
                    if item_word in menu_name or any(item_word in part for part in menu_name.split()):
                        parsed_items.append({
                            'name': menu_item['name'],
                            'quantity': quantity,
                            'price': menu_item['price'],
                            'total': quantity * menu_item['price']
                        })
                        total_amount += quantity * menu_item['price']
                        break
            
            if parsed_items:
                return json.dumps({
                    'items': parsed_items,
                    'total_amount': total_amount,
                    'success': True
                })
            else:
                return json.dumps({
                    'items': [],
                    'total_amount': 0,
                    'success': False,
                    'message': 'No valid menu items found in your order.'
                })
        
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e)
            })

class FoodOrderAgent:
    """Main agent for handling food orders"""
    db: Any = Field(default=None, exclude=True)  # Using Any type for flexibility

    def __init__(self, groq_api_key: str):
        self.db = OrderDatabase()
        
        # Initialize RAG system
        menu_items = self.db.get_menu()
        self.rag_system = MenuRAG(menu_items)
        
        # Initialize tools
        self.database_tool = DatabaseTool(self.db)
        self.menu_search_tool = MenuSearchTool(self.rag_system)
        self.order_parsing_tool = OrderParsingTool(self.db)
        
        # Initialize LLM
        self.llm = ChatGroq(
            temperature=0.7,
            groq_api_key=groq_api_key,
            model="llama3-70b-8192",  # Fallback to older version
            max_tokens=8192
        )
        
        # Create tools list
        self.tools = [
            self.database_tool,
            self.menu_search_tool,
            self.order_parsing_tool
        ]
        
        # Create agent
        self.setup_agent()
    
    def setup_agent(self):
        """Setup the conversational agent"""
        system_message = """You are a friendly AI assistant for a restaurant. Your job is to:

1. Help customers view the menu
2. Take food orders and process them
3. Answer questions about menu items
4. Provide recommendations

Guidelines:
- Always be polite and helpful
- When showing menu, organize by categories
- For orders, confirm items and total cost before processing
- Ask for customer name when taking orders
- Use the RAG system to find relevant menu items
- Parse orders carefully and confirm details

Available tools:
- database_tool: Access menu, create orders, get analytics
- menu_search: Search menu items using natural language
- order_parser: Parse order information from user messages

Remember to always confirm order details before processing!"""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )
    
    def process_message(self, message: str, chat_history: List = None) -> str:
        """Process user message and return response"""
        if chat_history is None:
            chat_history = []
        
        try:
            response = self.agent_executor.invoke({
                "input": message,
                "chat_history": chat_history
            })
            return response["output"]
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."