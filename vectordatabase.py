from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection
)

class VectorDB():
    def __init__(self, embeding_size:int=384):
        # Connect to Milvus (running locally or in a cluster)
        connections.connect(alias="default", host="127.0.0.1", port="19530")

        # Define schema for the collection
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embeding_size)
        ]
        schema = CollectionSchema(fields, description="Sentence Embeddings Collection")

        # Create collection
        self.collection_name = "sentence_embeddings"
        self.collection = Collection(name=self.collection_name, schema=schema)
    
    def insert_data(self, vectors):

        # Insert data into the collection
        data = [list(range(len(vectors))), vectors]  # Milvus expects data in columnar format
        self.collection.insert(data)

        # Load the collection into memory
        self.collection.load()

        print(f"Inserted {len(vectors)} vectors into the collection '{self.collection_name}'.")

    # def getAllDatabase():


    # def search(query_vector):
        
