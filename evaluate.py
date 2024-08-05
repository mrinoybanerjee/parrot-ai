""" Evaluation script for Parrot-AI conversational AI engine. """

import time
import os
import concurrent.futures
import statistics
import logging
from typing import Dict, List, Tuple
import requests
from requests.exceptions import RequestException, Timeout
from tqdm import tqdm
import nltk
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import psutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"
TOKENIZER = AutoTokenizer.from_pretrained("distilbert-base-uncased")
MODEL = AutoModel.from_pretrained("distilbert-base-uncased")

# Download necessary NLTK data
nltk.download('punkt', quiet=True)


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


def measure_latency(endpoint: str, payload: Dict) -> Tuple[float, Dict]:
    """Measure the latency of a request to the specified endpoint."""
    try:
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/{endpoint}", json=payload, 
                                 timeout=(5, 120))
        response.raise_for_status()
        end_time = time.time()
        return end_time - start_time, response.json()
    except Timeout:
        logger.error("Timeout error in measure_latency: Request took too long.")
        return float('inf'), {}
    except ConnectionError:
        logger.error("Connection error in measure_latency: Could not connect.")
        return float('inf'), {}
    except RequestException as e:
        logger.error("Error in measure_latency: %s", str(e))
        return float('inf'), {}


def count_tokens(text: str) -> int:
    """Count the number of tokens in the given text using the BERT tokenizer."""
    return len(TOKENIZER.encode(text))


def calculate_cosine_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts using BERT embeddings."""
    # Tokenize and get embeddings
    inputs1 = TOKENIZER(text1, return_tensors="pt", padding=True, truncation=True)
    inputs2 = TOKENIZER(text2, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs1 = MODEL(**inputs1)
        outputs2 = MODEL(**inputs2)
    # Use mean pooling to get sentence embeddings
    embedding1 = outputs1.last_hidden_state.mean(dim=1).squeeze()
    embedding2 = outputs2.last_hidden_state.mean(dim=1).squeeze()
    # Calculate cosine similarity
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


def load_test(endpoint: str, payload: Dict, num_requests: int) -> List[float]:
    """Perform a load test on the specified endpoint."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(measure_latency, endpoint, payload)
            for _ in range(num_requests)
        ]
        results = [
            future.result()[0]
            for future in tqdm(
                concurrent.futures.as_completed(futures),
                total=num_requests,
                desc="Load Testing"
            )
        ]
    return [r for r in results if r != float('inf')]  # Filter out timeout results


def analyze_response_time_vs_length(endpoint: str,
                                    payloads: List[Dict]) -> List[Tuple[int, float]]:
    """Analyze response time vs input length."""
    results = []
    for payload in tqdm(payloads, desc="Analyzing response time vs length"):
        input_length = len(payload['input_text'].split())
        latency, _ = measure_latency(endpoint, payload)
        if latency != float('inf'):
            results.append((input_length, latency))
        time.sleep(1)  # Add a small delay to avoid overwhelming the server
    return results


def visualize_results(latencies, output_speeds, similarity_scores, levenshtein_scores,
                      response_time_vs_length):
    """Generate high-quality visualizations for the evaluation results."""
    sns.set_style("whitegrid")
    sns.set_palette("deep")
    
    # Ensure assets folder exists
    assets_folder = "assets"
    os.makedirs(assets_folder, exist_ok=True)

    # Latency and Output Speed
    if latencies and output_speeds:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        sns.histplot(latencies, ax=ax1, kde=True, color='blue')
        ax1.set_title('Distribution of Latencies', fontsize=16)
        ax1.set_xlabel('Latency (seconds)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        
        sns.histplot(output_speeds, ax=ax2, kde=True, color='green')
        ax2.set_title('Distribution of Output Speeds', fontsize=16)
        ax2.set_xlabel('Output Speed (tokens/second)', fontsize=12)
        ax2.set_ylabel('Frequency', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(assets_folder, 'latency_output_speed.png'), dpi=300)
        plt.close()
    else:
        logger.warning("Not enough data to plot latency and speed distributions.")
    
    # Response Time vs Input Length
    if response_time_vs_length:
        plt.figure(figsize=(12, 8))
        x, y = zip(*response_time_vs_length)
        sns.regplot(x=x, y=y, scatter_kws={'alpha':0.5}, line_kws={'color': 'red'})
        plt.title('Response Time vs Input Length', fontsize=16)
        plt.xlabel('Input Length (words)', fontsize=12)
        plt.ylabel('Response Time (seconds)', fontsize=12)
        plt.savefig(os.path.join(assets_folder, 'response_time_vs_length.png'), dpi=300)
        plt.close()
    else:
        logger.warning("Not enough data to plot response time vs input length.")
    
    # Similarity and Levenshtein scores
    if similarity_scores and levenshtein_scores:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        sns.boxplot(y=similarity_scores, ax=ax1, color='purple')
        ax1.set_title('Distribution of Cosine Similarity Scores', fontsize=16)
        ax1.set_ylabel('Cosine Similarity', fontsize=12)
        
        sns.boxplot(y=levenshtein_scores, ax=ax2, color='orange')
        ax2.set_title('Distribution of Levenshtein Distances', fontsize=16)
        ax2.set_ylabel('Levenshtein Distance', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(os.path.join(assets_folder, 'similarity_levenshtein.png'), dpi=300)
        plt.close()
    else:
        logger.warning("Not enough data to plot similarity score distributions.")


def get_hardware_info():
    """Get hardware information of the system."""
    cpu_info = (
        f"CPU: {platform.processor()} "
        f"({psutil.cpu_count(logical=False)} cores, "
        f"{psutil.cpu_count(logical=True)} threads)"
    )
    ram_info = f"RAM: {round(psutil.virtual_memory().total / (1024.0 ** 3))} GB"
    disk_info = f"Disk: {round(psutil.disk_usage('/').total / (1024.0 ** 3))} GB total"
    os_info = f"OS: {platform.system()} {platform.release()}"

    return f"{cpu_info}\n{ram_info}\n{disk_info}\n{os_info}"


def main():
    """Main function for the evaluation script."""
    logger.info("Starting evaluation of Parrot-AI...")

    if not check_backend_status():
        logger.error("Backend server is not accessible. Please ensure it's running.")
        return

    logger.info("Backend server is accessible. Proceeding with evaluation.")

    test_cases = [
        {
            "input": "Hello, how are you?",
            "expected": "I'm doing well, thank you for asking. How can I assist you?"
        },
        {
            "input": "Can you explain the concept of machine learning in simple terms?",
            "expected": "Machine learning is a branch of artificial intelligence where "
                        "computers learn from data and improve their performance on a "
                        "task without being explicitly programmed."
        },
        {
            "input": "What are some effective strategies for learning a new language?",
            "expected": "Effective strategies for learning a new language include: "
                        "1. Consistent practice, 2. Immersion in the language, "
                        "3. Using language learning apps, "
                        "4. Watching movies or TV shows in the target language, "
                        "and 5. Finding a language exchange partner."
        }
    ]

    latencies = []
    output_speeds = []
    similarity_scores = []
    levenshtein_scores = []

    for i, case in enumerate(test_cases):
        logger.info("Testing case %d: %s", i+1, case['input'][:50])
        payload = {
            "engine": "OpenAI",
            "role_dict": {
                "role1": {"name": "User", "action": "asking questions"},
                "role2": {"name": "Assistant", "action": "providing answers"}
            },
            "language": "English",
            "scenario": "General conversation",
            "proficiency_level": "Intermediate",
            "learning_mode": "Conversation",
            "session_length": "Short",
            "input_text": case["input"]
        }
        latency, response = measure_latency("generate_conversation", payload)

        if isinstance(response, dict) and 'response1' in response:
            output = response['response1']
            logger.info("Case %d output: %s", i+1, output[:100])

            if latency != float('inf'):
                latencies.append(latency)
                output_speed = count_tokens(output) / latency if latency > 0 else 0
                output_speeds.append(output_speed)
                logger.info("Case %d latency: %.2f seconds", i+1, latency)
                logger.info("Case %d output speed: %.2f tokens/second", i+1,
                            output_speed)

            similarity_score = calculate_cosine_similarity(case["expected"], output)
            similarity_scores.append(similarity_score)
            logger.info("Case %d cosine similarity score: %.2f", i+1, similarity_score)

            levenshtein_score = levenshtein_distance(case["expected"], output)
            levenshtein_scores.append(levenshtein_score)
            logger.info("Case %d Levenshtein distance: %d", i+1, levenshtein_score)
        else:
            logger.error("Case %d failed: Unexpected response format", i+1)
            logger.error("Response: %s", response)

        time.sleep(5)  # 5-second delay between requests

    # Load testing
    logger.info("Performing load test...")
    load_test_results = load_test("generate_conversation", payload, 5)

    # Response time vs input length analysis
    logger.info("Analyzing response time vs input length...")
    response_time_vs_length_payloads = [
        {**payload, "input_text": " ".join(["test"] * i)} for i in range(10, 110, 10)
    ]
    response_time_vs_length = (analyze_response_time_vs_length(
        "generate_conversation", response_time_vs_length_payloads))

    # Calculate and log results
    avg_latency = statistics.mean(latencies) if latencies else float('inf')
    avg_output_speed = statistics.mean(output_speeds) if output_speeds else 0
    avg_similarity = statistics.mean(similarity_scores) if similarity_scores else 0
    avg_levenshtein = statistics.mean(levenshtein_scores) if levenshtein_scores else 0

    load_test_avg = (statistics.mean(load_test_results)
                     if load_test_results else float('inf'))
    load_test_95th = (statistics.quantiles(load_test_results, n=20)[-1]
                      if len(load_test_results) >= 20 else None)
    logger.info("Average Latency: %.2f seconds", avg_latency)

    logger.info("Average Output Speed: %.2f tokens/second", avg_output_speed)
    logger.info("Average Cosine Similarity Score: %.2f", avg_similarity)
    logger.info("Average Levenshtein Distance: %.2f", avg_levenshtein)
    logger.info("Load Test - Average response time: %.2f seconds", load_test_avg)
    if load_test_95th is not None:
        logger.info("Load Test - 95th percentile response time: %.2f seconds",
                    load_test_95th)
    else:
        logger.warning("Not enough data to calculate 95th percentile response time")

    # Visualize results
    visualize_results(latencies, output_speeds, similarity_scores, levenshtein_scores,
                      response_time_vs_length)
    
    # Get hardware information
    hardware_info = get_hardware_info()
    logger.info("Hardware Information:\n%s", hardware_info)

    # Generate markdown for README
    markdown = f"""
## Performance/Evaluation Results

Automated evaluation of Parrot-AI using sophisticated metrics and techniques.
Here are the results:

- **Average Latency**: {avg_latency:.2f} seconds
- **Average Output Speed**: {avg_output_speed:.2f} tokens/second
- **Average Cosine Similarity Score**: {avg_similarity:.2f}
- **Average Levenshtein Distance**: {avg_levenshtein:.2f}

**Load Test Results** (5 concurrent requests):
- Average response time: {load_test_avg:.2f} seconds
"""
    if load_test_95th is not None:
        markdown += f"- 95th percentile response time: {load_test_95th:.2f} seconds\n"
    else:
        markdown += "- 95th percentile response time: Not enough data\n"

    markdown += """
These metrics demonstrate Parrot-AI's performance across various dimensions:
- The latency and output speed indicate the system's responsiveness.
- The cosine similarity score shows how well responses align with expected outputs.
- The Levenshtein distance shows the degree of difference between responses.
- Load test results demonstrate the system's ability to handle concurrent requests.

For detailed visualizations of these results, please refer to the following images:
- [Latency and Output Speed Distribution](latency_output_speed.png)
- [Response Time vs Input Length](response_time_vs_length.png)
- [Similarity and Levenshtein Scores](similarity_levenshtein.png)

**Hardware Information**:
```
{hardware_info}
```
"""
    with open("EVALUATION_RESULTS.md", "w") as f:
        f.write(markdown)

    logger.info("Evaluation complete. Results have been saved to EVALUATION_RESULTS.md")


if __name__ == "__main__":
    main()
