#!/usr/bin/env python3
"""
Simple Vertex AI Index Creation
Uses the correct modern API syntax
"""

import json
from datetime import datetime
from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import IndexServiceClient, IndexEndpointServiceClient
from google.cloud.aiplatform_v1.types import Index, IndexEndpoint, DeployedIndex


def create_index_with_modern_api():
    """Create Vertex AI index using the correct modern API"""

    project_id = "mylittlerickover-prod"
    region = "us-central1"

    # Your uploaded data
    gcs_uri = "gs://mylittlerickover-prod-nuclear-vertex-final/nuclear_corpus_final_20250802_130023.jsonl"

    print("🗃️ Creating Vertex AI Vector Search Index")
    print(f"📁 Data: {gcs_uri}")
    print(f"🎯 Project: {project_id}")
    print("=" * 50)

    try:
        # Initialize the client
        client = IndexServiceClient()
        parent = f"projects/{project_id}/locations/{region}"

        print("📊 Configuring index...")

        # Create index configuration
        index = Index()
        index.display_name = "nuclear-rickover-index"
        index.description = "Nuclear SRO Training Corpus - 7146 chunks"

        # Set up metadata
        index.metadata = Index.IndexMetadata()
        index.metadata.contents_delta_uri = gcs_uri

        # Configure the index
        index.metadata.config = Index.IndexMetadata.Config()
        index.metadata.config.dimensions = 768
        index.metadata.config.approximate_neighbors_count = 50
        index.metadata.config.distance_measure_type = Index.IndexMetadata.Config.DistanceMeasureType.COSINE_DISTANCE

        # Set algorithm config
        index.metadata.config.algorithm_config = Index.IndexMetadata.Config.AlgorithmConfig()
        index.metadata.config.algorithm_config.tree_ah_config = Index.IndexMetadata.Config.AlgorithmConfig.TreeAhConfig()
        index.metadata.config.algorithm_config.tree_ah_config.leaf_node_embedding_count = 500
        index.metadata.config.algorithm_config.tree_ah_config.leaf_nodes_to_search_percent = 10

        print("🚀 Creating index (this takes 15-30 minutes)...")

        # Create the index
        operation = client.create_index(parent=parent, index=index)

        print("⏱️  Waiting for index creation to complete...")
        result = operation.result(timeout=1800)  # 30 minutes

        print("✅ Index created successfully!")
        print(f"   📋 Name: {result.display_name}")
        print(f"   🆔 ID: {result.name.split('/')[-1]}")

        return result

    except Exception as e:
        print(f"❌ Index creation failed: {e}")
        return None


def create_endpoint_and_deploy(index):
    """Create endpoint and deploy the index"""

    project_id = "mylittlerickover-prod"
    region = "us-central1"

    print("\n🌐 Creating Index Endpoint")
    print("=" * 30)

    try:
        # Create endpoint
        client = IndexEndpointServiceClient()
        parent = f"projects/{project_id}/locations/{region}"

        endpoint = IndexEndpoint()
        endpoint.display_name = "nuclear-rickover-endpoint"
        endpoint.description = "Nuclear SRO Training Assistant Endpoint"
        endpoint.public_endpoint_enabled = True

        print("🔧 Creating endpoint...")
        operation = client.create_index_endpoint(parent=parent, index_endpoint=endpoint)
        endpoint_result = operation.result(timeout=600)  # 10 minutes

        print("✅ Endpoint created!")
        print(f"   📋 Name: {endpoint_result.display_name}")
        print(f"   🆔 ID: {endpoint_result.name.split('/')[-1]}")

        # Deploy index to endpoint
        print("\n🚀 Deploying index to endpoint (10-20 minutes)...")

        deployed_index = DeployedIndex()
        deployed_index.id = "nuclear-rickover-deployed"
        deployed_index.index = index.name
        deployed_index.display_name = "Nuclear Rickover Deployed"

        # Set machine resources
        deployed_index.dedicated_resources = DeployedIndex.DedicatedResources()
        deployed_index.dedicated_resources.machine_spec = DeployedIndex.DedicatedResources.MachineSpec()
        deployed_index.dedicated_resources.machine_spec.machine_type = "e2-standard-2"
        deployed_index.dedicated_resources.min_replica_count = 1
        deployed_index.dedicated_resources.max_replica_count = 3
        deployed_index.enable_access_logging = True

        # Deploy
        deploy_operation = client.deploy_index(
            index_endpoint=endpoint_result.name,
            deployed_index=deployed_index
        )

        print("⏱️  Deploying index...")
        deploy_result = deploy_operation.result(timeout=1800)  # 30 minutes

        print("✅ Index deployed successfully!")

        return endpoint_result

    except Exception as e:
        print(f"❌ Endpoint creation/deployment failed: {e}")
        return None


def save_final_config(index, endpoint):
    """Save the final configuration"""

    config = {
        "project_id": "mylittlerickover-prod",
        "region": "us-central1",
        "endpoint_id": endpoint.name.split('/')[-1],
        "deployed_index_id": "nuclear-rickover-deployed",
        "index_id": index.name.split('/')[-1],
        "endpoint_resource_name": endpoint.name,
        "index_resource_name": index.name,
        "embedding_model": "textembedding-gecko@003",
        "embedding_dimensions": 768,
        "num_chunks": 7146,
        "deployment_time": datetime.now().isoformat(),
        "deployment_status": "complete",
        "deployment_method": "modern_api",
        "storage_path": "gs://mylittlerickover-prod-nuclear-vertex-final/nuclear_corpus_final_20250802_130023.jsonl"
    }

    # Save configuration
    with open("vertex_ai_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n💾 Configuration saved to vertex_ai_config.json")
    return config


def main():
    """Main deployment function"""

    print("🚀 Nuclear Rickover - Vertex AI Index Creation")
    print("Using your uploaded data from Cloud Storage")
    print("=" * 55)

    try:
        # Step 1: Create the index
        index = create_index_with_modern_api()
        if not index:
            print("❌ Index creation failed!")
            return False

        # Step 2: Create endpoint and deploy
        endpoint = create_endpoint_and_deploy(index)
        if not endpoint:
            print("❌ Endpoint deployment failed!")
            return False

        # Step 3: Save configuration
        config = save_final_config(index, endpoint)

        # Success!
        print(f"\n" + "🎉" * 20)
        print("DEPLOYMENT COMPLETE!")
        print("🎉" * 20)

        print(f"\n📊 FINAL SUMMARY:")
        print(f"   🔍 Nuclear documents: 7146 searchable chunks")
        print(f"   🤖 Embedding: Text Multilingual Embedding 002")
        print(f"   🌐 Endpoint: {endpoint.display_name}")
        print(f"   🆔 Endpoint ID: {config['endpoint_id']}")
        print(f"   💾 Config: vertex_ai_config.json")

        print(f"\n🚀 READY TO USE:")
        print(f"   streamlit run app_vertex.py")

        return True

    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Admiral Rickover demands excellence in nuclear operations!")
    print("Creating world-class nuclear training assistant...\n")

    success = main()

    if success:
        print(f"\n✅ SUCCESS! Admiral Rickover would be proud.")
        print(f"Your nuclear training assistant is ready for service!")
    else:
        print(f"\n❌ Mission failed. Debugging required.")
        print(f"Check Google Cloud authentication and API access.")