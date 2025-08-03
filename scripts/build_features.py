# Nuclear Embeddings Pre-computation
print("Importing all the libraries...")
import json  # for reading JSON files
import numpy as np  # for math operations on arrays
import torch  # for GPU operations
from sentence_transformers import SentenceTransformer  # for creating embeddings
from google.cloud import storage  # for Google Cloud Storage
from google.colab import auth, files  # for Google Colab authentication
import pickle  # for saving our data
from datetime import datetime  # for timestamps
import time  # for timing our operations

print("All libraries imported successfully!")

# STEP 1: Connect to Google Cloud
print("Connecting to Google Cloud...")
print("You might need to click some buttons to give permission...")
auth.authenticate_user()
print(" Connected to Google Cloud!")

# STEP 2: Download our nuclear documents from the cloud
print("📚 Getting our nuclear documents from the cloud...")


def get_nuclear_documents_from_cloud():
    print("Creating connection to Google Cloud Storage...")
    my_storage_client = storage.Client(project="mylittlerickover-prod")
    my_bucket = my_storage_client.bucket("mylittlerickover-prod-nuclear-vertex-final")

    # The name of our file with all the nuclear documents
    my_file_name = "nuclear_corpus_final_20250802_130023.jsonl"
    print(f"Looking for file: {my_file_name}")

    my_blob = my_bucket.blob(my_file_name)


    file_content = my_blob.download_as_text()
    print("File downloaded successfully!")

    # Now let's turn the file content into a list of documents
    list_of_documents = []
    lines_in_file = file_content.strip().split('\n')

    print("Processing each line in the file...")
    for line_number, single_line in enumerate(lines_in_file):
        if single_line.strip():  # make sure the line isn't empty
            try:
                document = json.loads(single_line)  # convert JSON text to Python object
                list_of_documents.append(document)

                # Show progress every 1000 documents
                if (line_number + 1) % 1000 == 0:
                    print(f"Processed {line_number + 1} documents so far...")

            except json.JSONDecodeError:
                print(f"Warning: Couldn't read line {line_number + 1}, skipping it...")
                continue

    print(f"✅ Successfully loaded {len(list_of_documents)} nuclear document chunks!")
    return list_of_documents


# Actually get the documents
nuclear_documents = get_nuclear_documents_from_cloud()

# Let's look at the first document
print("\n📖 Here's what the first document looks like:")
print(f"Title: {nuclear_documents[0].get('title', 'No title')}")
print(f"Content preview: {nuclear_documents[0].get('content', 'No content')[:150]}...")

# STEP 3: Set up our AI model that will create embeddings
print("\n Setting up our AI embedding model...")

# Check if we have a GPU available (this makes things much faster)
if torch.cuda.is_available():
    my_device = 'cuda'
    print("🎉 Great! We have a GPU available!")
else:
    my_device = 'cpu'
    print("⚠️ No GPU found, using CPU (this will be slower)")

print(f"Using device: {my_device}")

# Load our embedding model
print("Loading the sentence transformer model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Move the model to GPU if available
print(f"Moving model to {my_device}...")
embedding_model = embedding_model.to(my_device)

print(f"✅ Model is ready and running on {my_device}!")

# STEP 4: Create embeddings for all our documents
print("\n Now we'll create embeddings for all our nuclear documents...")
print("This is the slow part, but we only have to do it once!")

# First, let's extract just the text content from each document
all_document_texts = []
all_document_ids = []

print("Extracting text from each document...")
for i, document in enumerate(nuclear_documents):
    text_content = document.get('content', '')  # get the content, or empty string if none
    document_id = document.get('id', f'doc_{i}')  # get the id, or make one up

    all_document_texts.append(text_content)
    all_document_ids.append(document_id)

    # Show progress every 5000 documents
    if (i + 1) % 5000 == 0:
        print(f"Extracted text from {i + 1}/{len(nuclear_documents)} documents")

print(f"✅ Extracted text from all {len(all_document_texts)} documents!")

# Now let's create embeddings in batches (so we don't run out of memory)
print("\nCreating embeddings in batches...")
how_many_at_once = 32  # Process 32 documents at a time (adjust if you get memory errors)
all_embedding_batches = []  # We'll store each batch here

total_batches = (len(all_document_texts) + how_many_at_once - 1) // how_many_at_once
print(f"We'll process {total_batches} batches of {how_many_at_once} documents each")

start_time = time.time()

for batch_number in range(0, len(all_document_texts), how_many_at_once):
    current_batch_number = batch_number // how_many_at_once + 1

    # Get the texts for this batch
    batch_end = min(batch_number + how_many_at_once, len(all_document_texts))
    current_batch_texts = all_document_texts[batch_number:batch_end]

    print(f"Processing batch {current_batch_number}/{total_batches} ({len(current_batch_texts)} documents)...")

    # Create embeddings for this batch
    batch_embeddings = embedding_model.encode(
        current_batch_texts,
        convert_to_tensor=True,
        show_progress_bar=False  # We'll show our own progress
    )

    # Move embeddings back to CPU and convert to numpy
    batch_embeddings_numpy = batch_embeddings.cpu().numpy()
    all_embedding_batches.append(batch_embeddings_numpy)

    # Show estimated time remaining
    if current_batch_number % 10 == 0:
        elapsed_time = time.time() - start_time
        estimated_total_time = elapsed_time * total_batches / current_batch_number
        estimated_remaining = estimated_total_time - elapsed_time
        print(f"   Estimated time remaining: {estimated_remaining / 60:.1f} minutes")

# Combine all the batches into one big array
print("\nCombining all batches into one big embedding matrix...")
final_embeddings_matrix = np.vstack(all_embedding_batches)

print(f"✅ Created embeddings! Shape: {final_embeddings_matrix.shape}")
print(f"   Number of documents: {final_embeddings_matrix.shape[0]}")
print(f"   Embedding size for each document: {final_embeddings_matrix.shape[1]}")

# STEP 5: Package everything up nicely
print("\n📦 Packaging everything into a nice data structure...")

# Create our complete knowledge base
nuclear_knowledge_base = {
    'embeddings_matrix': final_embeddings_matrix.astype(np.float32),  # Use float32 to save memory
    'all_documents': nuclear_documents,
    'document_ids': all_document_ids,
    'model_used': 'all-MiniLM-L6-v2',
    'embedding_dimensions': final_embeddings_matrix.shape[1],
    'total_documents': len(nuclear_documents),
    'creation_date': datetime.now().isoformat(),
    'device_used_for_creation': my_device,
    'notes': 'Pre-computed embeddings for fast nuclear document search'
}

# Calculate file size
size_in_bytes = final_embeddings_matrix.nbytes
size_in_mb = size_in_bytes / 1024 / 1024

print(f"Our knowledge base contains:")
print(f"   - Total documents: {nuclear_knowledge_base['total_documents']}")
print(f"   - Embedding dimensions: {nuclear_knowledge_base['embedding_dimensions']}")
print(f"   - Approximate size: {size_in_mb:.1f} MB")
print(f"   - Created on: {nuclear_knowledge_base['creation_date']}")

# STEP 6: Save everything to Google Cloud Storage
print("\n☁️ Saving our knowledge base to Google Cloud Storage...")


def save_knowledge_base_to_cloud(knowledge_base_data, file_name):
    print(f"Connecting to Google Cloud Storage...")
    storage_client = storage.Client(project="mylittlerickover-prod")
    bucket = storage_client.bucket("mylittlerickover-prod-nuclear-vertex-final")

    print(f"Creating blob for file: {file_name}")
    blob = bucket.blob(file_name)

    print("Converting our data to pickle format...")
    # Use pickle to save our Python object
    pickled_knowledge_base = pickle.dumps(knowledge_base_data, protocol=pickle.HIGHEST_PROTOCOL)
    pickled_size_mb = len(pickled_knowledge_base) / 1024 / 1024

    print(f"Uploading {pickled_size_mb:.1f} MB to cloud storage...")
    blob.upload_from_string(pickled_knowledge_base, content_type='application/octet-stream')

    print(f"✅ Successfully uploaded {file_name}!")
    return file_name


# Create a filename with current timestamp
current_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
knowledge_base_filename = f"nuclear_embeddings_precomputed_{current_timestamp}.pkl"

# Actually save it
saved_filename = save_knowledge_base_to_cloud(nuclear_knowledge_base, knowledge_base_filename)

# STEP 7: Test our fast search function
print("\n Testing our fast search function...")


def search_nuclear_documents(user_query, number_of_results=5):
    print(f"Searching for: '{user_query}'")

    # Turn the user's query into an embedding
    print("Creating embedding for the query...")
    query_embedding = embedding_model.encode([user_query], convert_to_tensor=True)
    query_embedding_numpy = query_embedding.cpu().numpy()

    # Calculate how similar the query is to each document
    print("Calculating similarities with all documents...")
    similarity_scores = np.dot(final_embeddings_matrix, query_embedding_numpy.T).flatten()

    # Find the most similar documents
    print(f"Finding top {number_of_results} most similar documents...")
    top_document_indices = np.argsort(similarity_scores)[-number_of_results:][::-1]

    # Prepare the results
    search_results = []
    for position, doc_index in enumerate(top_document_indices):
        result = {
            'rank': position + 1,
            'similarity_score': float(similarity_scores[doc_index]),
            'document_data': nuclear_documents[doc_index],
            'document_title': nuclear_documents[doc_index].get('title', 'No title'),
            'content_preview': nuclear_documents[doc_index].get('content', '')[:200] + "..."
        }
        search_results.append(result)

    return search_results


# Test the search with a sample query
test_query = "nuclear reactor safety"
print(f"\nTesting search with query: '{test_query}'")
test_results = search_nuclear_documents(test_query, 3)

print(f"\nTop 3 results for '{test_query}':")
for result in test_results:
    print(f"\n{result['rank']}. {result['document_title']}")
    print(f"   Similarity: {result['similarity_score']:.3f}")
    print(f"   Preview: {result['content_preview']}")

# FINAL SUCCESS MESSAGE
print("\n" + "=" * 60)
print("🎉 SUCCESS! Pre-computation is complete!")
print("=" * 60)
print(f"📁 Your embeddings are saved as: {saved_filename}")
print(f"📊 Total documents processed: {len(nuclear_documents)}")
print(f"💾 File size: {size_in_mb:.1f} MB")
print("\n🚀 Next steps:")
print("1. Update your Cloud Run app to download this file")
print("2. Load the embeddings instead of computing them each time")
print("3. Enjoy super fast nuclear document search!")
print("\n💡 Pro tip: Save this filename somewhere safe!")
print(f"   Filename: {saved_filename}")