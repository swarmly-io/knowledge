import os
import json


def combine_smelting_json_files(folder_path, output_file):
    combined_data = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)

            with open(file_path) as file:
                data = json.load(file)

                # Add 'name' property to each element
                name = os.path.splitext(file_name)[0]  # Remove the extension
                data['name'] = name

                sdata = json.dumps(data).replace("minecraft:", "")
                data = json.loads(sdata)

                if 'smelting' in data['type']:
                    combined_data.append(data)

    if os.path.exists(output_file):
        os.remove(output_file)

    # Write the combined data to the output file
    with open(output_file, 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)


if __name__ == "__main__":
    # Replace with the actual folder path
    folder_path = r'C:\Users\adpla\AppData\Roaming\.minecraft\versions\1.17.1\1.17.1\data\minecraft\recipes'
    output_file = './data/smelting_recipes.json'

    combine_smelting_json_files(folder_path, output_file)
