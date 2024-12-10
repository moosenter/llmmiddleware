from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection, MilvusClient, utility
)
import os

class VectorDB():
    def __init__(self, database_path:str, embeding_size:int=384, max_length:int=1000):
        # Connect to Milvus (running locally or in a cluster)

        uri = database_path
        host = os.getenv("MILVUS_HOST", "localhost")
        port = os.getenv("MILVUS_PORT", "19530")
        user = os.getenv("MILVUS_USER", "")
        password = os.getenv("MILVUS_PASSWORD", "")
        db_name = os.getenv("MILVUS_DB_NAME", "default")
        token = os.getenv("MILVUS_TOKEN", "")

        self.database_path = database_path
        if uri:
            connections.connect(uri=uri, user=user, password=password, token=token)
        else:
            connections.connect(host=host, port=port, user=user, password=password, token=token)

        # Define schema for the collection
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embeding_size),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=max_length)
        ]
        self.schema = CollectionSchema(fields, description="Knowledge Base Collection")
        self.index_params = {
            "index_type": "HNSW",  # Use IVF or HNSW for large datasets
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        self.collection_name = "knowledge_base"
    
    def create_db(self):
        # Create collection
        self.collection = Collection(name=self.collection_name, schema=self.schema)
        self.collection.create_index(field_name="embedding", index_params=self.index_params)

    def getCollection(self):
        self.collection = Collection(self.collection_name)
    
    def insert_data(self, embeddings, texts):

        # Insert data into the collection
        data = [embeddings, texts]  # Milvus expects data in columnar format
        self.collection.insert(data)
        self.collection.flush()

        print(f"------ Inserted {len(embeddings)} vectors into the collection '{self.collection_name}'. ------")

    def query_topk(self, query_vector, topk=5):

        results = self.collection.search(
            data=[query_vector],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},  # Adjust nprobe for recall
            limit=topk,  # Retrieve top-5 most relevant documents
            output_fields=["text"]
        )

        retrieved_docs = [result.entity.get('text') for result in results[0]]
        return retrieved_docs
    
    def getAllData(self):

        # Query all data from the collection
        results = self.collection.query(
            limit=1000,
            expr="",
            output_fields=['id','text']  # Specify the fields to retrieve
        )

        # Print the results
        for result in results:
            print(result)

    def drop_collection(self) -> None:
        """Drop a collection."""
        if utility.has_collection(self.collection_name):
            collection = Collection(self.collection_name)
            collection.drop()
            print(f"Collection '{self.collection_name}' dropped.")

        
