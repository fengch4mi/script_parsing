# character_quote_finder.py

import re
from pathlib import Path

def _slugify(text):
    text = text.strip().lower()
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_-]', '', text)
    return text or 'character'

def _default_output_filename(input_filename, character_name):
    stem = Path(input_filename).stem or 'script'
    return f"{stem}_{_slugify(character_name)}_quotes.txt"

def _unique_path(path):
    if not path.exists():
        return path
    for i in range(2, 1000):
        candidate = path.with_name(f"{path.stem}_{i}{path.suffix}")
        if not candidate.exists():
            return candidate
    return path

def find_quotes(filename, character_name, mode='line'):
    """
    Find quotes/dialogues containing character name
    
    Modes:
        'line' - Single line
        'paragraph' - Entire paragraph
        'dialogue' - Conversation block
    """
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    results = []
    
    if mode == 'line':
        # Line by line search
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if character_name.lower() in line.lower():
                results.append({
                    'line_number': i,
                    'text': line.strip()
                })
    
    elif mode == 'paragraph':
        # Paragraph search (separated by double newlines)
        paragraphs = content.split('\n\n')
        for i, para in enumerate(paragraphs, 1):
            if character_name.lower() in para.lower():
                results.append({
                    'paragraph_number': i,
                    'text': para.strip()
                })
    
    elif mode == 'dialogue':
        # Find dialogue blocks (lines starting with character name)
        pattern = rf'^{re.escape(character_name)}:.*?(?=\n\n|\Z)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        for i, match in enumerate(matches, 1):
            results.append({
                'dialogue_number': i,
                'text': match.group(0).strip()
            })
    
    return results

def main():
    print("=== Character Quote Finder ===\n")
    
    # Input
    filename = input("Enter filename (default: script.txt): ").strip() or 'script.txt'
    character_name = input("Enter character name: ").strip()
    
    print("\nSearch modes:")
    print("1. Line - Single lines containing name")
    print("2. Paragraph - Full paragraphs containing name")
    print("3. Dialogue - Dialogue blocks (Name: text format)")
    
    mode_choice = input("Choose mode (1/2/3, default: 1): ").strip() or '1'
    mode_map = {'1': 'line', '2': 'paragraph', '3': 'dialogue'}
    mode = mode_map.get(mode_choice, 'line')
    
    # Search
    print(f"\nSearching for '{character_name}' in {filename}...")
    results = find_quotes(filename, character_name, mode)
    
    # Display results
    print(f"\nFound {len(results)} results:\n")
    print("="*60)
    
    for result in results:
        print(result['text'])
        print("-"*60)
    
    # Save option
    save = input("\nSave results to file? (y/n): ").strip().lower()
    if save == 'y':
        default_output = _default_output_filename(filename, character_name)
        default_path = _unique_path(Path(default_output))
        if default_path.name != default_output:
            print(f"Default output exists. Using {default_path.name} instead.")

        output_choice = input(
            f"Output filename (default: {default_path.name}): "
        ).strip()
        output_file = output_choice or default_path.name

        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result['text'] + '\n\n')
                f.write('-'*60 + '\n\n')
        print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()