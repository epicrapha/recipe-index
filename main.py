from infer import find_recipes

def main(input: str, output_file_name: str):

    import json
    result = find_recipes(input, 3)
    result = json.dumps(result, indent=2)

    with open(output_file_name, "w") as json_file:
        json_file.write(result)

    return result

if __name__ == "__main__":
    output_file_name = "result.json"
    queries = [
        "chocolate butter sugar eggs flour",
        "salmon lemon dill cream",
        "beef tomato potato carrot",
    ]
    output = main(input=queries[0], output_file_name=output_file_name)
    print(output)
