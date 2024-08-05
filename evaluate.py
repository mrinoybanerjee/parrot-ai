"""Evaluation script for Parrot-AI conversational AI engine."""

import time
import os
import statistics
import logging
from typing import Dict
import requests
from requests.exceptions import RequestException
import nltk
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
import seaborn as sns
import psutil
from tabulate import tabulate

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BACKEND_URL = "http://localhost:8000"
TOKENIZER = AutoTokenizer.from_pretrained("distilbert-base-uncased")
MODEL = AutoModel.from_pretrained("distilbert-base-uncased")

# Download necessary NLTK data
nltk.download('punkt', quiet=True)


def get_hardware_info():
    """Gather hardware information of the system."""
    cpu_info = psutil.cpu_freq()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "CPU": f"{psutil.cpu_count()} cores @ {cpu_info.current:.2f}MHz",
        "RAM": f"{ram.total / (1024**3):.2f} GB",
        "Disk": f"{disk.total / (1024**3):.2f} GB"
    }


def check_backend_status() -> bool:
    """Check if the backend server is running and accessible."""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        logger.info("Backend server response status code: %d", response.status_code)
        logger.info("Backend server response content: %s", response.text[:100])
        return (response.status_code == 200 and
                "Parrot-AI backend is running" in response.text)
    except RequestException as e:
        logger.error("Error checking backend status: %s", str(e))
        return False


def measure_latency(method: str, url: str, payload: Dict = None) -> Dict:
    """Measure the latency of a request to the specified endpoint."""
    try:
        start_time = time.time()
        if method.lower() == 'get':
            response = requests.get(url, timeout=(5, 120))
        elif method.lower() == 'post':
            response = requests.post(url, json=payload, timeout=(5, 120))
        else:
            raise ValueError("Unsupported HTTP method")
        end_time = time.time()
        latency = end_time - start_time
        return {
            "latency": latency,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None
        }
    except RequestException as e:
        logger.error("Error in measure_latency: %s", str(e))
        return {"latency": float('inf'), "status_code": None, "response": None}


def count_tokens(text: str) -> int:
    """Count the number of tokens in the given text using the BERT tokenizer."""
    return len(TOKENIZER.encode(text))


def calculate_cosine_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts using BERT embeddings."""
    inputs1 = TOKENIZER(text1, return_tensors="pt", padding=True, truncation=True)
    inputs2 = TOKENIZER(text2, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs1 = MODEL(**inputs1)
        outputs2 = MODEL(**inputs2)
    embedding1 = outputs1.last_hidden_state.mean(dim=1).squeeze()
    embedding2 = outputs2.last_hidden_state.mean(dim=1).squeeze()
    cosine_sim = F.cosine_similarity(embedding1.unsqueeze(0),
                                     embedding2.unsqueeze(0), dim=1)
    return cosine_sim.item()


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def generate_result_tables(results):
    """Generate result tables from the evaluation data."""
    headers = ["API", "Mean", "Median", "Min", "Max"]
    table_data = []
    for api, data in results.items():
        latencies = [r['latency'] for r in data if r['status_code'] == 200]
        if latencies:
            table_data.append([
                api,
                f"{statistics.mean(latencies):.4f}",
                f"{statistics.median(latencies):.4f}",
                f"{min(latencies):.4f}",
                f"{max(latencies):.4f}"
            ])
    return tabulate(table_data, headers=headers, tablefmt="pipe")


def visualize_results(results, similarity_scores, levenshtein_scores):
    """Generate visualizations for the evaluation results."""
    sns.set_style("whitegrid")
    sns.set_palette("muted")

    # Ensure assets folder exists
    assets_folder = "assets"
    os.makedirs(assets_folder, exist_ok=True)

    # Latency distribution
    plt.figure(figsize=(10, 6))
    latencies = {api: [r['latency'] for r in data if r['status_code'] == 200]
                 for api, data in results.items()}
    sns.boxplot(data=latencies)
    plt.title("Latency Distribution by API")
    plt.ylabel("Latency (seconds)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_folder, "latency_distribution.png"))
    plt.close()

    # Response time vs request number
    plt.figure(figsize=(10, 6))
    for api, data in results.items():
        valid_latencies = [r['latency'] for r in data if r['status_code'] == 200]
        sns.lineplot(x=range(len(valid_latencies)), y=valid_latencies, label=api)
    plt.title("Response Time vs Request Number")
    plt.xlabel("Request Number")
    plt.ylabel("Response Time (seconds)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(assets_folder, "response_time_vs_request.png"))
    plt.close()

    # Similarity and Levenshtein scores
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    sns.boxplot(y=similarity_scores, ax=ax1)
    ax1.set_title('Distribution of Cosine Similarity Scores')
    ax1.set_ylabel('Cosine Similarity')
    sns.boxplot(y=levenshtein_scores, ax=ax2)
    ax2.set_title('Distribution of Levenshtein Distances')
    ax2.set_ylabel('Levenshtein Distance')
    plt.tight_layout()
    plt.savefig(os.path.join(assets_folder, 'similarity_levenshtein.png'))
    plt.close()


def main():
    """Main function for the evaluation script."""
    logger.info("Starting evaluation of Parrot-AI...")

    hardware_info = get_hardware_info()

    if not check_backend_status():
        logger.error("Backend server is not accessible. Please ensure it's running.")
        return

    logger.info("Backend server is accessible. Proceeding with evaluation.")

    # Perform evaluations
    root_results = [measure_latency('get', f"{BACKEND_URL}/") for _ in range(50)]

    conversation_payload = {
        "engine": "OpenAI",
        "role_dict": {
            "role1": {"name": "User", "action": "asking questions"},
            "role2": {"name": "Assistant", "action": "providing answers"}
        },
        "language": "English",
        "scenario": "General conversation",
        "proficiency_level": "Intermediate",
        "learning_mode": "Conversation",
        "session_length": "Short"
    }
    conv_results = [measure_latency('post', f"{BACKEND_URL}/generate_conversation",
                                    conversation_payload) for _ in range(50)]

    summary_results = [measure_latency('post', f"{BACKEND_URL}/generate_summary",
                                       conversation_payload) for _ in range(50)]

    results = {
        "Root Endpoint": root_results,
        "Generate Conversation": conv_results,
        "Generate Summary": summary_results
    }

    # Calculate similarity and Levenshtein scores
    similarity_scores = []
    levenshtein_scores = []
    expected_response = "This is a sample expected response."
    for result in conv_results:
        if result['response'] and 'response1' in result['response']:
            actual_response = result['response']['response1']
            similarity_scores.append(calculate_cosine_similarity(expected_response,
                                                                 actual_response))
            levenshtein_scores.append(levenshtein_distance(expected_response,
                                                           actual_response))

    result_tables = generate_result_tables(results)
    visualize_results(results, similarity_scores, levenshtein_scores)

    avg_similarity = statistics.mean(similarity_scores) if similarity_scores else 0
    avg_levenshtein = statistics.mean(levenshtein_scores) if levenshtein_scores else 0

    markdown = f"""
# Parrot-AI Evaluation Results

## Hardware Configuration
{tabulate(hardware_info.items(), tablefmt="pipe")}

## Performance Metrics Explanation
- **Latency**: Time taken for the server to respond to a request.
- **Response Time**: Total time including network latency and server processing time.
- **Throughput**: Number of requests processed per second.
- **Cosine Similarity**: Measure of similarity between expected and
                    actual responses (1.0 is identical, 0.0 is completely different).
- **Levenshtein Distance**: Measure of the difference between expected and
                    actual responses (lower is better).

## Latency Results
{result_tables}

## Response Quality Metrics
- **Average Cosine Similarity Score**: {avg_similarity:.4f}
- **Average Levenshtein Distance**: {avg_levenshtein:.2f}

## Visualizations
![Latency Distribution](assets/latency_distribution.png)
![Response Time vs Request](assets/response_time_vs_request.png)
![Similarity and Levenshtein Scores](assets/similarity_levenshtein.png)

### Interpretation of Visualizations
1. **Latency Distribution**: Shows the distribution of
                 response times for each API endpoint.
2. **Response Time vs Request Number**: Illustrates how response
                 time varies over multiple requests.
3. **Similarity and Levenshtein Scores**: Displays the
                 distribution of response quality metrics.
"""
    with open("EVALUATION_RESULTS.md", "w") as f:
        f.write(markdown)

    logger.info("Evaluation complete. Results have been saved to EVALUATION_RESULTS.md")


if __name__ == "__main__":
    main()
