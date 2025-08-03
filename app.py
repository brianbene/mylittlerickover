#!/usr/bin/env python3

# This will use Gemini to answer questions based on our precomputed embeddings
import streamlit as st
import os
import json
import base64
import numpy as np
import pickle
import torch
import google.generativeai as genai
from google.cloud import storage
from sentence_transformers import SentenceTransformer
from PIL import Image


@st.cache_resource
def load_precomputed_embeddings():
    """Load pre-computed embeddings from Cloud Storage"""
    print("⚡ Loading pre-computed nuclear embeddings...")

    try:
        storage_client = storage.Client(project="mylittlerickover-prod")
        bucket = storage_client.bucket("mylittlerickover-prod-nuclear-vertex-final")

        # Use the specific pre-computed embeddings file
        blob_name = "nuclear_embeddings_precomputed_20250802_194715.pkl"
        blob = bucket.blob(blob_name)

        print(f"📁 Loading: {blob_name}")

        # Download and deserialize
        pickled_data = blob.download_as_bytes()
        knowledge_base = pickle.loads(pickled_data)

        print(f"✅ Loaded {knowledge_base['num_documents']} pre-computed embeddings")
        print(f"📊 Embedding dimensions: {knowledge_base['embedding_dim']}")

        return knowledge_base

    except Exception as e:
        print(f"❌ Error loading embeddings: {e}")
        return None


@st.cache_resource
def load_embedding_model():
    """Load embedding model for query encoding only"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer("all-MiniLM-L6-v2")
    if device == 'cuda':
        model = model.to(device)
    print(f"🚀 Query encoder ready on {device}")
    return model, device


def search_nuclear_corpus(query, knowledge_base, query_model, top_k=5):
    """Ultra-fast vector search using pre-computed embeddings"""

    # Encode query (only step that needs computation)
    query_embedding = query_model.encode([query], convert_to_tensor=True)

    if torch.cuda.is_available():
        # GPU-accelerated similarity computation
        embeddings_tensor = torch.from_numpy(knowledge_base['embeddings']).cuda()
        similarities = torch.mm(embeddings_tensor, query_embedding.T).flatten()
        top_indices = torch.topk(similarities, top_k).indices.cpu().numpy()
        similarity_scores = similarities[top_indices].cpu().numpy()
    else:
        # CPU fallback
        query_np = query_embedding.cpu().numpy()
        similarities = np.dot(knowledge_base['embeddings'], query_np.T).flatten()
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        similarity_scores = similarities[top_indices]

    # Format results for Admiral Rickover
    context_parts = [f"NUCLEAR CORPUS SEARCH RESULTS for: \"{query}\"\n"]
    context_parts.append(
        f"[Retrieved {len(top_indices)} relevant documents from {knowledge_base['num_documents']} total chunks]\n")

    for i, idx in enumerate(top_indices):
        doc = knowledge_base['documents'][idx]
        context_parts.append(f"=== RESULT {i + 1} (Relevance: {similarity_scores[i]:.3f}) ===")
        context_parts.append(f"Title: {doc['title']}")
        context_parts.append(f"Category: {doc.get('category', 'Unknown')}")
        context_parts.append(f"Content: {doc['content'][:800]}...")
        context_parts.append("")

    return "\n".join(context_parts)


def load_atom_image():
    """function to load the atom background image"""
    try:
        # Check if atom.jpg file exists
        if os.path.exists("atom.jpg"):
            # Open the file and convert to base64 so we can use it in CSS
            with open("atom.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return encoded_string
        else:
            # If no atom image, return empty string
            return ""
    except:
        # If something goes wrong, just return empty string
        return ""


def load_rickover_picture():
    """Simple function to load Admiral Rickover's picture for the chat"""
    try:
        # Check if rickover.jpg file exists
        if os.path.exists("rickover.jpg"):
            # Use PIL to open the image
            image = Image.open("rickover.jpg")
            return image
        else:
            # If no image, return None
            return None
    except:
        # If something goes wrong, return None
        return None


def setup_page_style():
    """Setup how the page looks with CSS styling"""

    # Set basic page settings
    st.set_page_config(
        page_title="MylittleRickover",
        page_icon="⚛️",
        layout="wide"
    )

    # Try to get the atom background image
    atom_image = load_atom_image()

    # If we have an atom image, use it. If not, make a simple pattern
    if atom_image:
        background_css = f"background-image: url('data:image/jpeg;base64,{atom_image}');"
    else:
        # Make a simple atomic pattern with CSS if no image
        background_css = """
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(0, 86, 179, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(0, 86, 179, 0.05) 0%, transparent 60%);
        """

    # Apply all our CSS styling to make the page look nice
    st.markdown(f"""
    <style>
    /* Style the main app background */
    .stApp {{
        {background_css}
        background-color: #ADD8E6;
        background-size: contain;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Style the main title */
    .main-header {{
        text-align: center;
        color: #0056b3;
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(255,255,255,0.8);
    }}

    /* Style the subtitle */
    .subtitle {{
        text-align: center;
        color: #6c757d;
        font-size: 1.1em;
        margin-bottom: 30px;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }}

    /* Make chat messages semi-transparent so we can see the background */
    [data-testid="stChatMessage"] {{
        background-color: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(2px);
        border-radius: 10px;
        border: 1px solid rgba(0, 86, 179, 0.1);
    }}

    /* Hide the sidebar completely */
    .css-1d391kg {{display: none;}}
    .css-1rs6os {{display: none;}}
    section[data-testid="stSidebar"] {{display: none;}}

    /* Style for context display */
    .context-box {{
        background-color: rgba(240, 248, 255, 0.8);
        border-left: 4px solid #0056b3;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 0.8em;
        color: #333;
    }}
    </style>
    """, unsafe_allow_html=True)


def show_title():
    """Show the title and subtitle at the top of the page"""

    # Display the main title with HTML styling
    st.markdown(
        '<h1 class="main-header">⚛️ MylittleRickover</h1>',
        unsafe_allow_html=True
    )

    # Display the subtitle
    st.markdown('<p class="subtitle">Nuclear SRO Training Assistant - Enhanced with Precomputed Embeddings</p>',
                unsafe_allow_html=True)

    # Add a horizontal line to separate the header from the chat
    st.markdown("---")


def get_google_api_key():
    """Get the Google API key so we can use the AI"""

    # First, try to get the API key from environment variables
    api_key = os.environ.get("GOOGLE_API_KEY")

    # If we still don't have an API key, ask the user to enter it
    if not api_key:
        st.warning("🔑 Google API Key Required")
        st.info("Your API key should be set as an environment variable GOOGLE_API_KEY")
        api_key = st.text_input("Enter Google API Key:", type="password", key="api_key_input")

        # If user still hasn't entered a key, stop the app
        if not api_key:
            st.stop()

    return api_key


def ask_rickover_with_rag(api_key, user_question, knowledge_base, query_model):
    """Ask Admiral Rickover a question using RAG (Retrieval-Augmented Generation)"""

    try:
        # Step 1: Search the nuclear corpus for relevant information
        nuclear_context = search_nuclear_corpus(user_question, knowledge_base, query_model)

        # Step 2: Set up the Google AI with our API key
        genai.configure(api_key=api_key)

        # Step 3: Tell the AI how to act like Admiral Rickover with nuclear context
        rickover_personality = """
You are Admiral Hyman G. Rickover, the father of the nuclear navy. You are direct, demanding, and focused on nuclear safety and excellence. 
You have no patience for sloppiness or incomplete answers. Your responses should be authoritative and 
technically accurate, emphasizing the importance of following procedures and maintaining the highest standards.

You have extensive knowledge of nuclear reactor operations, safety systems, procedures, and regulations.
Use the provided nuclear information to give accurate, detailed answers about nuclear operations, safety, and procedures.
Be direct, technically sound, and always emphasize safety and excellence.

When you reference information from the nuclear corpus, be specific about procedures, regulations, and technical details.
"""

        # Step 4: Create the enhanced prompt with nuclear context
        full_prompt = f"""
Based on the following nuclear information from official sources, answer the question in Admiral Rickover's voice:

NUCLEAR CORPUS INFORMATION:
{nuclear_context}

QUESTION: {user_question}

Instructions:
- Answer as Admiral Rickover would - direct, technically sound, and emphasizing safety and excellence
- Use the provided nuclear information to give accurate, detailed responses
- Reference specific procedures, regulations, or technical details when relevant
- Be specific and provide practical guidance where appropriate
- Always emphasize nuclear safety and procedural compliance
"""

        # Step 5: Use Google's Gemini AI model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Step 6: Send our enhanced prompt and get a response
        response = model.generate_content(rickover_personality + "\n\n" + full_prompt)

        # Step 7: Return the AI's answer
        answer = response.text.strip()
        return answer

    except Exception as error:
        # If something goes wrong, return an error message
        return f"Error generating response: {error}"


def main():
    """Main function that runs our enhanced RAG app"""

    # Set up the page styling
    setup_page_style()

    # Show the title
    show_title()

    # Load Admiral Rickover's picture for the chat avatar
    rickover_picture = load_rickover_picture()

    # Get the Google API key
    api_key = get_google_api_key()

    # Load precomputed embeddings and query model
    with st.spinner("⚡ Loading ultra-fast nuclear knowledge base..."):
        knowledge_base = load_precomputed_embeddings()
        query_model, device = load_embedding_model()

    if knowledge_base:
        st.success(f"🤖 RAG System Ready: {knowledge_base['num_documents']} precomputed embeddings loaded")
    else:
        st.error("❌ Failed to load precomputed embeddings")
        st.stop()

    # Set up the initial chat message if this is the first time
    if "messages" not in st.session_state:
        # This is Admiral Rickover's opening message
        opening_message = """I am Admiral Hyman G. Rickover's uploaded conscience, father of the nuclear navy and architect of America's nuclear propulsion program.

The nuclear program demands absolute integrity, unwavering attention to detail, and complete dedication to safety. Every component, every procedure, every decision must meet the highest standards - there are no shortcuts in nuclear operations.

**My Core Principles for Nuclear Excellence:**

1. **INTEGRITY** - You will do what is right, even when no one is watching

2. **RESPONSIBILITY** - You are personally accountable for your area of expertise  

3. **FORMALITY** - Every procedure, every communication must be precise

4. **KNOWLEDGE** - Ignorance is inexcusable. Know your systems completely

5. **QUESTIONING ATTITUDE** - Challenge everything. Complacency kills

6. **PROCEDURAL COMPLIANCE** - Procedures are written in blood. Follow them

7. **BACKUP** - Speak up when something is wrong


Go ahead and ask your question-ensure it is an intelligent one!

"""

        # Save this message in the chat history
        st.session_state.messages = [
            {"role": "assistant", "content": opening_message}
        ]

    # Display all the chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Show user messages with the default user icon
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            # Show Admiral Rickover's messages with his picture
            with st.chat_message("assistant", avatar=rickover_picture):
                st.write(message["content"])

    # Handle new user input
    user_question = st.chat_input("Ask Admiral Rickover your nuclear question...")

    if user_question:
        # Add the user's question to the chat history
        st.session_state.messages.append({"role": "user", "content": user_question})

        # Show the user's question immediately
        with st.chat_message("user"):
            st.write(user_question)

        # Generate Admiral Rickover's response using RAG
        with st.chat_message("assistant", avatar=rickover_picture):
            # Show a spinner while we're getting the response
            with st.spinner("Admiral Rickover is consulting the nuclear knowledge base..."):

                try:
                    # Get the AI's response with RAG
                    answer = ask_rickover_with_rag(api_key, user_question, knowledge_base, query_model)

                    # Show the answer
                    st.write(answer)

                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as error:
                    # If something goes wrong, show an error
                    error_message = f"⚠️ Error: {error}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})




# This runs the app when the script is executed
if __name__ == "__main__":
    main()