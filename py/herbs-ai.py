from openai import OpenAI
import json
import os
from glob import glob
from tqdm import tqdm
import re
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key)
num_retries = 3


# Define the exact schema expected for each field
SCHEMA = """
{
    "Names": {
        // Dictionary with name types as keys (Common, Pharmaceutical, Botanical, Chinese) and a list as values.
        // Example: {"Common": ["Ginseng", "Jinseng"], "Botanical": ["Panax ginseng"], "Chinese": ["人参"]}
    },
    "Type": "string", // One of: "Formula", "Herb", "Chemical", "Animal", "Mineral", "Qigong", "Acupuncture", "Massage", "Diet"
    "Maladies Treated": [
        // Array of strings for conditions treated
        // Example: ["Fatigue", "Weak immunity", "Poor digestion"]
    ],
    "Preparation": "string", // Text describing preparation methods and dosage
    "Geography": [
        // Array of strings for regions where found/used
        // Example: ["China", "Korea", "Northeastern Asia"]
    ],
    "Properties": [
        // Array of strings for herb properties
        // Example: ["Warm", "Sweet", "Slightly bitter"]
    ],
    "Meridians": [
        // Array of strings for affected meridians/organs
        // Example: ["Spleen", "Lung", "Heart"]
    ],
    "Contraindications": "string", // Text describing warnings and adverse effects
    "Research": "string", // Text summarizing research findings
    "Notes": "string", // Additional information as text
    "Chemical Ingredients": {
        // Array of strings listing chemical components
        // Example: ["Ginsenosides", "Polysaccharides"]
    }
}
"""

def extract_structured_data(text, filename):
    """
    Extract all structured data from text in a single query
    """
    print(f'Processing {filename}')

    for _ in range(num_retries):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Using a more capable model for extraction
                messages=[
                    {"role": "system", "content": (
                        "You are a data extraction specialist for herbal medicine. Your task is to extract structured information "
                        "from text about herbs, treatments, and medicinal plants following a precise schema. "
                        "You MUST follow the exact data structure specified, using the correct data types for each field."
                    )},
                    {"role": "user", "content": (
                        f"Extract information from the text and format it according to this EXACT schema:\n\n"
                        f"{SCHEMA}\n\n"
                        f"Rules for extraction:\n"
                        f"1. ALWAYS use the specified data types - dictionaries, arrays, or strings as indicated\n"
                        f"2. If information for a field is not available, use an empty dictionary {{}}, empty array [], or empty string \"\" as appropriate\n"
                        f"3. Return ONLY valid JSON\n\n"
                        f"TEXT TO EXTRACT FROM:\n{text}"
                    )}
                ]
            )

            # Clean and parse JSON response
            content = completion.choices[0].message.content
            content = content.replace('```json', '').replace('```', '').strip()

            return json.loads(content)

        except json.JSONDecodeError as e:
            print(f"JSON parse error for {filename}: {e}, retrying...")
        except Exception as e:
            print(f"Error processing {filename}: {e}, retrying...")

    # Return empty structure if all retries fail
    return {
        "Names": {},
        "Type": "",
        "Maladies Treated": [],
        "Preparation": "",
        "Geography": [],
        "Properties": [],
        "Meridians": [],
        "Contraindications": "",
        "Research": "",
        "Notes": "",
        "Chemical Ingredients": {}
    }


def get_herbs():
    """Process multiple herb pages"""

    results = json.load(open('./ai_herbs_detailed.json', 'r', encoding="utf-8"))
    filenames = glob('./text/*')

    for filename in tqdm(filenames):
        print(filename)
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()

        # Process the herb page
        result = extract_structured_data(text, filename)
        result['Original Text'] = text
        results.append(result)

        # Save intermediate results after each herb
        json.dump(results, open('./ai_herbs_detailed.json', 'w', encoding="utf-8"), indent=4, ensure_ascii=False)

    return results

def add_urls():
    results = json.load(open('./ai_herbs_detailed.json', 'r', encoding="utf-8"))
    filenames = glob('./text/*')
    for i, filename in enumerate(filenames):
        url = 'http://alternativehealing.org/{}'.format(filename.split('.txt')[0].split('/')[-1])
        print(url)
        results[i]['original_url'] = url

    json.dump(results, open('./ai_herbs_detailed.json', 'w', encoding="utf-8"), indent=4, ensure_ascii=False)

    # print(results)

add_urls()
# get_herbs()