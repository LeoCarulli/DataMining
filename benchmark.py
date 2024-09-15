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
    "revenue for project 23 in april 2024",
    "show me 5 projects with the sum of most terminations in april 2024",
    "show me the 5 projects with more terminations in april 2024",
    "what active projects are owned by SVP_Anon_7",
    "show me the all kpi data for SVP called SVP_Anon_3 on march 2024",
    "show me top 5 projects with highest revenue for SVP_Anon_3",
    ]

expected_outputs = [
    [(476, 66611384.828), (211, 5727396.05), (239, 5121813.23), (179, 4882967.0), (253, 4776494.54)],
    [(201, -1730677.98), (270, -246571.87), (151, -132934.65), (283, -127116.0), (476, -98896.67)],
    [(735116.337)],
    [(285, 17), (179, 14), (253, 11), (239, 7), (280, 5)],
    [(475, 1), (467, 1), (465, 1), (457, 1), (456, 1)],
    [(3),(89),(90),(95),(97),(114),(120),(123),(136),(170),(209),(235),(239),(279),(282),(316),(359),(373),(376),(431),(440),(475)],
    [(201, 5.0, 6.9, 'KPI #2 Operations - Calls per day - >= 5 = 100; <5 calls = 0', '2024-01-01', '2024-03-31', '1970-01-01', 'Yes', 'SH', 'No', 'Weekly', None, None, '2024-03-31', '2024-Q1', 'Audrey Herrera', 'Maintain & Grow'), (201, 1.0, 0.95, 'KPI #1 Sales - TRx Cycles - Target >= 42,832 for Q1 = 100; <= 0', '2024-01-01', '2024-03-31', '1970-01-01', 'Yes ', 'SH', 'No', 'Weekly', None, None, '2024-03-31', '2024-Q1', 'Audrey Herrera', 'Maintain & Grow'), (404, 30.0, 30.0, 'Days to fill < 30 days', '2024-01-01', '2024-03-31', '1970-01-01', 'Yes - Syneos Health Roster', 'Client', 'No', 'Monthly', None, None, '2024-03-31', '2024-Q1', 'Jennifer Diaz', None), (404, 0.9, 0.95, '90 of ARMs minimum 3 days with in-person interactions over 85 weeks', '2024-01-01', '2024-03-31', '1970-01-01', 'Yes - Client CRM', 'Client', 'No', 'Weekly/Monthly', None, None, '2024-03-31', '2024-Q1', 'Jennifer Diaz', None), (404, 1.0, 1.0, 'ARMs post minimum of 10 account plans with goals by 1/26', '2024-01-01', '2024-03-31', '1970-01-01', 'Manager reporting', 'Client', 'No', 'Weekly/Monthly', None, None, '2024-03-31', '2024-Q1', 'Jennifer Diaz', None), (404, 1.0, 1.0, 'Minimum one meeting with sales matrix partner per month', '2024-01-01', '2024-03-31', '1970-01-01', 'Manager reporting', 'Client', 'No', 'Monthly', None, None, '2024-03-31', '2024-Q1', 'Jennifer Diaz', None), (404, 0.85, 0.89, 'Turnover <=3 per Quarter', '2024-01-01', '2024-03-31', '1970-01-01', 'Yes - Internal Reporting', 'Client', 'No', 'Monthly', None, None, '2024-03-31', '2024-Q1', 'Jennifer Diaz', None), (404, 0.9, 1.0, '90 of Team Minimum 8 In-Person at 85 of weeks', '2024-01-01', '2024-03-31', '1970-01-01', 'Yes - Client CRM', 'Client', 'No', 'Weekly/Monthly', None, None, '2024-03-31', '2024-Q1', 'Jennifer Diaz', None), (404, 0.85, 1.0, '85 of ARMs 1.5 Field Ride quarterly', '2024-01-01', '2024-03-31', '1970-01-01', 'No - Syneos Data', 'Client', 'No', 'Monthly', None, None, '2024-03-31', '2024-Q1', 'Jennifer Diaz', None), (410, 4.0, 8.0, 'Calls per day', '2024-01-01', '2024-12-31', '1970-01-01', 'Yes Internal Reporting/Veeva Output', 'Client', None, 'Weekly/Monthly', None, None, '2024-03-31', '2024-Q1', 'Daphne George', 'Drive Performance'), (410, 1.0, 0.8, 'Field Coaching Report completion', '2024-01-01', '2024-12-31', '1970-01-01', 'Yes Internal Reporting', 'Client', None, 'Quarterly', None, None, '2024-03-31', '2024-Q1', 'Daphne George', 'Drive Performance'), (410, 0.85, 0.94, 'Retention of FRM Team', '2024-01-01', '2024-12-31', '1970-01-01', 'Yes Internal Reporting', 'Client', None, 'Quarterly', None, None, '2024-03-31', '2024-Q1', 'Daphne George', 'Drive Performance'), (410, 0.7, 0.82, 'Reach on targeted customers', '2024-01-01', '2024-12-31', '1970-01-01', 'Yes Internal Reporting', 'Client', None, 'Weekly/Monthly', None, None, '2024-03-31', '2024-Q1', 'Daphne George', 'Drive Performance')],
    [(281, 3168029.2100000004), (201, 2080676.31), (404, 1543421.63), (188, 1079156.77), (422, 764448.83)]


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
