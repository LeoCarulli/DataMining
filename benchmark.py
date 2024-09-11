import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from integrated_v8 import execute_query, handle_conversation, template


prompts = [
    "show me the 5 projects with the highest revenue",
    "show me the 5 projects with the lowest revenue",
]

expected_outputs = [
    [(476, 66611384.828), (211, 5727396.05), (239, 5121813.23), (179, 4882967.0), (253, 4776494.54)],
    [(201, -1730677.98), (270, -246571.87), (151, -132934.65), (283, -127116.0), (476, -98896.67)],
]

db_path = "./mi_base_de_datos.db"


def test_model(prompts, expected_outputs, db_path, chain):
    responses_correct = 0
    responses_time = []
    
    for prompt, expected_output in zip(prompts, expected_outputs):
        start_time = time.time()
        print(prompt)
        query, _ = handle_conversation(prompt, "", db_path, max_attempts=5, chain=chain)
        if "Unable to generate a valid SQL query" in query:
            print(prompt, query)
        else:
            output, columns_names = execute_query(query, db_path)
            stop_time = time.time()
            if output == expected_output:
                responses_correct += 1
            responses_time.append(stop_time - start_time)
            print(output)
    
    print(f"Correct responses: {responses_correct}/{len(prompts)}")
    print(f"Average time for correct responses: {sum(responses_time) / len(responses_time)} sec")
    print(f"Max time for correct responses: {max(responses_time)} sec")
    print(f"Min time for correct responses: {min(responses_time)} sec")
        

model_parameters = [
        {"model": "sqlcoder"},
    {
        "model": "sqlcoder",
        "num_ctx": 4096,
        "num_predict": -1,
        "temperature":0.5,
        "tfs_z": 1,
        "top_k": 40,
        "top_p": 0.5,
    }
]

for model_parameter in model_parameters:
    model = OllamaLLM(**model_parameter)
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    print(model_parameter)
    test_model(prompts, expected_outputs, db_path, chain)
    print("\n\n\n")
