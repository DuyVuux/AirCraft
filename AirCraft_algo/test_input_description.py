"""
Test input description generation in routes.py
"""
import json
from src.model.context import Context
from src.utils.input_describer import generate_input_description

def test_description_generation():
    print("Loading input_sample.json...")
    with open('input_sample.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Parsing Context...")
    ctx = Context.from_dict(data)
    
    print("Generating description...")
    generate_input_description(ctx, 'test_input_description.md')
    
    print(f"\n✅ Description generated successfully!")
    print(f"Check: test_input_description.md")
    
    # Show first few lines
    with open('test_input_description.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()[:20]
        print("\nFirst 20 lines:")
        print("".join(lines))

if __name__ == '__main__':
    test_description_generation()
