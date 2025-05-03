from dotenv import load_dotenv
from openai import OpenAI
import openai
import os

# Set up your OpenAI API key
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)
models = client.models.list()

# Function to upload the dataset
def upload_dataset(file_path):
    print("Uploading dataset...")
    try:
        response = client.files.create(
            file=open(file_path, "rb"),
            purpose="fine-tune"
        )
        print(f"File uploaded successfully. File ID: {response.id}")
        return response.id
    except Exception as e:
        print(f"Error uploading dataset: {e}")
        return None

# Function to start fine-tuning
def start_fine_tune(file_id, model="curie"):
    print("Starting fine-tuning...")
    try:
        response = client.fine_tuning.jobs.create(
            training_file=file_id,
            model=model
        )
        print(f"Fine-tuning job created. Job ID: {response.id}")
        return response.id
    except Exception as e:
        print(f"Error starting fine-tune: {e}")
        return None

# Function to track fine-tune job status
def track_fine_tune(job_id):
    print("Tracking fine-tune job...")
    try:
        while True:
            status = client.fine_tuning.jobs.retrieve(id=job_id)
            print(f"Status: {status['status']}")
            if status["status"] in ["succeeded", "failed"]:
                break
    except Exception as e:
        print(f"Error tracking fine-tune job: {e}")

# Function to test the fine-tuned model
def test_fine_tuned_model(model_id, prompt, max_tokens=50):
    print("Testing fine-tuned model...")
    try:
        response = client.chat.completions.create(
            model=model_id,
            prompt=prompt,
            max_tokens=max_tokens
        )
        print("Generated Completion:")
        print(response.choices[0].text.strip())
    except Exception as e:
        print(f"Error testing fine-tuned model: {e}")

# Main function
if __name__ == "__main__":
    # Path to your JSONL dataset
    dataset_path = "database.jsonl"
    model = 'gpt-3.5-turbo'

    # Upload the dataset
    file_id = upload_dataset(dataset_path)
    print(file_id)

    if file_id:
        # Start fine-tuning
        job_id = start_fine_tune(file_id, model)
        print(job_id)

        if job_id:
            # Track the fine-tuning process
            track_fine_tune(job_id)

            # Test the fine-tuned model
            # Replace "fine-tuned-model-id" with the actual model ID from the job details
            fine_tuned_model_id = job_id
            test_prompt = "Explain Newton's second law of motion."
            test_fine_tuned_model(fine_tuned_model_id, test_prompt)
