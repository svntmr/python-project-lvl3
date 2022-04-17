from pathlib import Path

TESTS_PATH = Path(__file__).parent


def get_test_resource_path(current_file, *relative_path) -> Path:
    return Path(current_file).joinpath(*relative_path).resolve(strict=True)


def tests_resources_path(*relative_path) -> Path:
    file_operations_resources_path = f"{TESTS_PATH}/resources"
    return get_test_resource_path(file_operations_resources_path, *relative_path)
