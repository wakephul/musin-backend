from api.src.managers import file_handling

def create_output_folder(execution_code):

    output_folder = f"simulations/output/{execution_code}/"
    output_folder = file_handling.create_folder(output_folder)

    return output_folder