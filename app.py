import streamlit as st
import plotly.express as px
import pandas as pd
from agents import FoodOrderAgent
from database import OrderDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Restaurant Order Bot",
    page_icon="🍕",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            st.error("Please set your OpenAI API key in the .env file")
            st.stop()
        st.session_state.agent = FoodOrderAgent(groq_api_key)
    if 'customer_name' not in st.session_state:
        st.session_state.customer_name = ""

def main():
    """Main application function"""
    initialize_session_state()
    
    st.title("🍕 Restaurant Order Bot")
    st.markdown("Welcome to our restaurant! I can help you view our menu and place orders.")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Order Chat", "Dashboard"])
    
    if page == "Order Chat":
        chat_interface()
    elif page == "Dashboard":
        dashboard()

def chat_interface():
    """Chat interface for ordering"""
    
    # Customer name input
    if not st.session_state.customer_name:
        with st.form("customer_form"):
            st.write("Please enter your name to start ordering:")
            name = st.text_input("Your Name")
            submitted = st.form_submit_button("Start Ordering")
            
            if submitted and name:
                st.session_state.customer_name = name
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Hello {name}! Welcome to our restaurant. How can I help you today? You can ask to see our menu or place an order."
                })
                st.rerun()
    
    else:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        
        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Convert message history to agent format
                        chat_history = [
                            ("human" if msg["role"] == "user" else "assistant", msg["content"])
                            for msg in st.session_state.messages[:-1]
                        ]
                        
                        response = st.session_state.agent.process_message(
                            f"Customer: {st.session_state.customer_name}. Request: {prompt}",
                            chat_history
                        )
                        
                        # Ensure we have a valid response
                        if not response:
                            response = "I didn't understand that. Could you please rephrase?"
                        
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    except Exception as e:
                        error_msg = f"System error: {str(e)}"
                        st.error("Sorry, something went wrong. Please try again.")
                        print(error_msg)
        # Quick action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🍽️ Show Menu"):
                # menu_prompt = "Can you show me the complete menu?"
                # st.session_state.messages.append({"role": "user", "content": menu_prompt})
                # # Get menu response
                # response = st.session_state.agent.process_message(
                #     f"Customer name: {st.session_state.customer_name}. User message: {menu_prompt}"
                # )
                # print(response,9999999999999999999999999)
                # st.session_state.messages.append({"role": "assistant", "content": response})
                # st.rerun()
                try:
                    menu_prompt = "Show me the complete menu with all categories and items"
                    st.session_state.messages.append({"role": "user", "content": menu_prompt})
                    
                    # Directly invoke the database tool if needed
                    if hasattr(st.session_state.agent, 'database_tool'):
                        response = st.session_state.agent.database_tool.run({
                            "action": "get_menu"
                        })
                    else:
                        response = st.session_state.agent.process_message(
                            f"Customer: {st.session_state.customer_name}. Request: {menu_prompt}"
                        )
                    print(response,555555555555555555555555)
                    if not response:
                        print(3333333333333333333333333333)
                        response = "Here's our menu:\n" + "\n".join(
                            f"- {item['name']}: ${item['price']:.2f}" 
                            for item in st.session_state.agent.db.get_menu()
                        )
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response
                    })
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Failed to load menu: {str(e)}")
                    print(f"Menu error: {str(e)}")
        
        with col2:
            if st.button("🍕 Popular Items"):
                popular_prompt = "What are your most popular items?"
                st.session_state.messages.append({"role": "user", "content": popular_prompt})
                
                response = st.session_state.agent.process_message(
                    f"Customer name: {st.session_state.customer_name}. User message: {popular_prompt}"
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button("🆕 New Chat"):
                st.session_state.messages = []
                st.session_state.customer_name = ""
                st.rerun()

def dashboard():
    """Dashboard showing order analytics"""
    st.header("📊 Restaurant Dashboard")
    
    # Get analytics data
    db = OrderDatabase()
    analytics = db.get_order_analytics()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Orders", analytics['total_orders'])
    
    with col2:
        st.metric("Total Revenue", f"${analytics['total_revenue']:.2f}")
    
    with col3:
        avg_order = analytics['total_revenue'] / max(analytics['total_orders'], 1)
        st.metric("Average Order Value", f"${avg_order:.2f}")
    
    # Popular items chart
    if analytics['popular_items']:
        st.subheader("Most Popular Items")
        
        items_df = pd.DataFrame(analytics['popular_items'], columns=['Item', 'Orders'])
        
        fig = px.bar(
            items_df, 
            x='Orders', 
            y='Item',
            orientation='h',
            title="Top 5 Most Ordered Items"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Menu overview
    st.subheader("Current Menu")
    menu_items = db.get_menu()
    
    if menu_items:
        menu_df = pd.DataFrame(menu_items)
        
        # Group by category
        category_summary = menu_df.groupby('category').agg({
            'name': 'count',
            'price': ['min', 'max', 'mean']
        }).round(2)
        
        category_summary.columns = ['Items Count', 'Min Price', 'Max Price', 'Avg Price']
        st.dataframe(category_summary)

if __name__ == "__main__":
    main()
