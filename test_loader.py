from document_loader import load_text_from_file

# Change this to any test file you have
file_path = "F:\\AI_documents\\incoming\\sample_test.txt"

try:
    content = load_text_from_file(file_path)
    print("✅ File loaded successfully!\n")
    print(content[:1000])  # Print first 1000 characters
except Exception as e:
    print("❌ Error loading file:", e)
