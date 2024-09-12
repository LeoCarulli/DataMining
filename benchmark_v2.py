import time
import pandas as pd

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from main import handle_conversation
from execution import execute_query
from prompt import template


prompts = [
    "show me the 5 projects with the highest revenue",
    "show me the 5 projects with the lowest revenue",
]

expected_outputs = [
    [(476, 66611384.828), (211, 5727396.05), (239, 5121813.23), (179, 4882967.0), (253, 4776494.54)],
    [(201, -1730677.98), (270, -246571.87), (151, -132934.65), (283, -127116.0), (476, -98896.67)],
]

db_path = "./mi_base_de_datos.db"


def test_model(prompts, expected_outputs, db_path, chain, max_attempts=5):
    responses_correct = 0
    responses_time = []
    
    for prompt, expected_output in zip(prompts, expected_outputs):
        start_time = time.time()
        print(prompt)
        query, _ = handle_conversation(prompt, "", db_path, max_attempts=max_attempts, chain=chain)
        if "Unable to generate a valid SQL query" in query:
            print(prompt, query)
        else:
            output, columns_names = execute_query(query, db_path)
            if output == expected_output:
                responses_correct += 1
            print(output)
        stop_time = time.time()
        responses_time.append(stop_time - start_time)
    
    return {
        "Correct responses": f"{responses_correct}/{len(prompts)}",
        "Average time for responses (sec)": int(sum(responses_time) / len(responses_time)),
        "Max time for responses (sec)": int(max(responses_time)),
        "Min time for responses (sec)": int(min(responses_time)),
    }
        

ollama_params_baseline = {"model": "sqlcoder"}
ollama_params_more_context = {
        "model": "sqlcoder",
        "num_ctx": 4096*2,
        "num_predict": -1,
        "temperature":0.5,
        "tfs_z": 1,
        "top_k": 40,
        "top_p": 0.5,
    }
ollama_params_more_temperature = {
        "model": "sqlcoder",
        "num_ctx": 4096*2,
        "num_predict": -1,
        "temperature":0.85,
        "tfs_z": 1,
        "top_k": 70,
        "top_p": 0.8,
    }
ollama_params_less_temperature = {
        "model": "sqlcoder",
        "num_ctx": 4096*2,
        "num_predict": -1,
        "temperature":0.3,
        "tfs_z": 1,
        "top_k": 25,
        "top_p": 0.3,
    }

model_parameters = [
    {"name": "baseline", "ollamaparams": ollama_params_baseline, "test_params": {"max_attempts": 1}},
    {"name": "more attemps", "ollamaparams": ollama_params_baseline, "test_params": {"max_attempts": 5}},
    {"name": "more context", "ollamaparams": ollama_params_more_context, "test_params": {"max_attempts": 5}},
    {"name": "more context and temperature", "ollamaparams": ollama_params_more_temperature, "test_params": {"max_attempts": 5}},
    {"name": "more context and less temperature", "ollamaparams": ollama_params_less_temperature, "test_params": {"max_attempts": 5}},
]

results_df = pd.DataFrame()
for params in model_parameters:
    exp_name = params["name"]
    print(f"Experiment name {exp_name}")
    model = OllamaLLM(**params["ollamaparams"])
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    print("Ollama paramas: ", params["ollamaparams"])
    results = test_model(prompts, expected_outputs, db_path, chain, **params.get("test_params", {}))
    results["ollama_params"] = params["ollamaparams"]
    results_df[exp_name] = pd.Series(results)
    print(results)
    print("\n\n")

print(results_df)
results_df.to_csv("results.csv")
