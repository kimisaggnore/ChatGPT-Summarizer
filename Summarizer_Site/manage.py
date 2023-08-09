#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    filenames = os.listdir("uploads")
    for file in filenames:
        path = os.path.join("uploads", file)
        if path != os.path.join("uploads", "api_key") and path != os.path.join("uploads", "summarized_file"):
            os.remove(path)

    filenames = os.listdir("uploads/summarized_file")
    for file in filenames:
        path = os.path.join("uploads/summarized_file", file)
        os.remove(path)
    
    filenames = os.listdir("processing_files")
    for file in filenames:
        path = os.path.join("processing_files", file)
        if path == os.path.join("processing_files", "progress_file.txt") or path == os.path.join("processing_files", "progress_file_2.txt"):
            os.remove(path)

    filenames = os.listdir("processing_files/test_run_6")
    for file in filenames:
        path = os.path.join("processing_files/test_run_6", file)
        os.remove(path)

    with open(f"processing_files/ACTIVATED.txt", 'w') as file:
        file.write(str(1))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'summarizer_site.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
