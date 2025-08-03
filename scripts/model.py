#!/usr/bin/env python3
"""
scripts/model.py - Simple AI Model Setup
This script sets up and tests our AI chatbot system
"""

# Import what we need
import os
from datetime import datetime

# AI stuff
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai


def test_database():
    """Test if our database is working"""
    print("🧪 Testing database...")

    try:
        # Connect to our database
        db_folder = "models/vector_db"

        if not os.path.exists(db_folder):
            print("❌ Database not found! Run: python setup.py build")
            return False

        client = chromadb.PersistentClient(path=db_folder)
        collection = client.get_collection("nuclear_knowledge")

        # Check how many documents we have
        count = collection.count()
        print(f"📊 Database has {count} searchable chunks")

        if count == 0:
            print("❌ Database is empty!")
            return False

        # Test searching the database
        results = collection.query(
            query_texts=["reactor safety systems"],
            n_results=3
        )

        if results and results['documents'] and results['documents'][0]:
            print("✅ Database search test passed!")
            print(f"🔍 Found {len(results['documents'][0])} results for test query")
            return True
        else:
            print("❌ Database search returned no results")
            return False

    except Exception as error:
        print(f"❌ Database test failed: {error}")
        return False


def test_ai_model():
    """Test if our text-to-numbers AI model works"""
    print("🤖 Testing AI embedding model...")

    try:
        # Load the model
        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Test it with some text
        test_text = "Nuclear reactor safety is very important"
        embedding = model.encode([test_text])

        print(f"✅ AI model working! Created {len(embedding[0])} numbers from text")
        return True

    except Exception as error:
        print(f"❌ AI model test failed: {error}")
        return False


def create_chatbot_system():
    """Create the main chatbot system that can answer questions"""
    print("💬 Creating chatbot system...")

    class NuclearChatbot:
        """Simple chatbot that answers nuclear questions"""

        def __init__(self):
            """Set up the chatbot"""
            print("🔧 Setting up chatbot components...")

            # Load the text-to-numbers model
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

            # Connect to our database
            client = chromadb.PersistentClient(path="models/vector_db")
            self.collection = client.get_collection("nuclear_knowledge")

            print("✅ Chatbot components ready!")

        def find_relevant_info(self, question, num_results=5):
            """Find information related to the question"""

            # Search our database for relevant information
            results = self.collection.query(
                query_texts=[question],
                n_results=num_results
            )

            # Get the text from the results
            if results and results['documents'] and results['documents'][0]:
                documents = results['documents'][0]

                # Remove duplicates but keep order
                unique_docs = []
                for doc in documents:
                    if doc not in unique_docs:
                        unique_docs.append(doc)

                # Combine all the relevant text
                context = "\n\n---\n\n".join(unique_docs)
                return context
            else:
                return "No relevant information found in database."

        def generate_answer(self, api_key, context, question):
            """Use Google AI to generate an answer"""

            try:
                # Set up Google AI
                genai.configure(api_key=api_key)

                # Create the prompt for Admiral Rickover
                system_instructions = """
You are Admiral Hyman G. Rickover. You are direct, demanding, and focused on nuclear safety and excellence. 
You have no patience for slopiness or incomplete answers. Your responses should be authoritative and 
technically accurate, emphasizing the importance of following procedures and maintaining the highest standards.
"""

                user_prompt = f"""
Based on this nuclear information, answer the question in Admiral Rickover's voice:

NUCLEAR INFORMATION:
{context}

QUESTION: {question}

Answer as Admiral Rickover would - direct, technically sound, and emphasizing safety and excellence.
"""

                # Generate the answer
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(system_instructions + "\n\n" + user_prompt)

                return response.text.strip()

            except Exception as error:
                return f"Error generating answer: {error}"

        def answer_question(self, api_key, question):
            """Complete process: find info and generate answer"""

            # Step 1: Find relevant information
            context = self.find_relevant_info(question)

            # Step 2: Generate answer
            answer = self.generate_answer(api_key, context, question)

            return answer, context

    # Test the chatbot
    try:
        chatbot = NuclearChatbot()
        print("✅ Chatbot system created successfully!")

        # Save the chatbot class to a file so the main app can use it
        chatbot_code = '''
# This file contains our simple chatbot system
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

class NuclearChatbot:
    """Simple chatbot that answers nuclear questions"""

    def __init__(self):
        """Set up the chatbot"""
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.PersistentClient(path="models/vector_db")
        self.collection = client.get_collection("nuclear_knowledge")

    def find_relevant_info(self, question, num_results=5):
        """Find information related to the question"""
        results = self.collection.query(query_texts=[question], n_results=num_results)

        if results and results['documents'] and results['documents'][0]:
            documents = results['documents'][0]
            unique_docs = []
            for doc in documents:
                if doc not in unique_docs:
                    unique_docs.append(doc)
            context = "\\n\\n---\\n\\n".join(unique_docs)
            return context
        else:
            return "No relevant information found in database."

    def generate_answer(self, api_key, context, question):
        """Use Google AI to generate an answer"""
        try:
            genai.configure(api_key=api_key)

            system_instructions = """
You are Admiral Hyman G. Rickover. You are direct, demanding, and focused on nuclear safety and excellence. 
You have no patience for slopiness or incomplete answers. Your responses should be authoritative and 
technically accurate, emphasizing the importance of following procedures and maintaining the highest standards.
"""

            user_prompt = f"""
Based on this nuclear information, answer the question in Admiral Rickover's voice:

NUCLEAR INFORMATION:
{context}

QUESTION: {question}

Answer as Admiral Rickover would - direct, technically sound, and emphasizing safety and excellence.
"""

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(system_instructions + "\\n\\n" + user_prompt)
            return response.text.strip()

        except Exception as error:
            return f"Error generating answer: {error}"

    def answer_question(self, api_key, question):
        """Complete process: find info and generate answer"""
        context = self.find_relevant_info(question)
        answer = self.generate_answer(api_key, context, question)
        return answer, context
'''

        # Save the chatbot code
        os.makedirs("models", exist_ok=True)
        with open("models/simple_chatbot.py", "w", encoding="utf-8") as f:
            f.write(chatbot_code)

        print("💾 Chatbot code saved to models/simple_chatbot.py")
        return True

    except Exception as error:
        print(f"❌ Error creating chatbot: {error}")
        return False


def save_model_summary():
    """Save summary of what we set up"""
    print("📊 Saving model setup summary...")

    summary = f"""
=== AI MODEL SETUP SUMMARY ===
Date: {datetime.now()}

COMPONENTS READY:
✅ Database tested and working
✅ AI embedding model loaded
✅ Chatbot system created
✅ Integration with Google Gemini AI

FILES CREATED:
• models/simple_chatbot.py - Main chatbot system

WHAT THE SYSTEM CAN DO:
1. Take a question about nuclear topics
2. Search the database for relevant information  
3. Use AI to generate an answer as Admiral Rickover
4. Provide sources that were used

The system is now ready to run!
Next step: streamlit run app.py
"""

    # Save summary
    summary_file = "data/outputs/model_summary.txt"
    os.makedirs("data/outputs", exist_ok=True)

    with open(summary_file, 'w', encoding='utf-8') as file:
        file.write(summary)

    print(f"✅ Summary saved: {summary_file}")


def setup_model():
    """Main function to set up and test all AI components"""
    print("🚀 Starting AI model setup...")

    try:
        # Test if database works
        if not test_database():
            print("❌ Database test failed! Run: python setup.py build")
            return

        # Test if AI model works
        if not test_ai_model():
            print("❌ AI model test failed! Check your internet connection")
            return

        # Create the chatbot system
        if not create_chatbot_system():
            print("❌ Chatbot creation failed!")
            return

        # Save summary
        save_model_summary()

        print("🎉 AI model setup complete!")
        print("🚀 Ready to run: streamlit run app.py")

    except Exception as error:
        print(f"❌ Model setup failed: {error}")


# If someone runs this file directly
if __name__ == "__main__":
    setup_model()