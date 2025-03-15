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

    results = json.load(open('ai_herbs.json', 'r', encoding="utf-8"))
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
        json.dump(results, open('ai_herbs.json', 'w', encoding="utf-8"), indent=4, ensure_ascii=False)

    return results


def add_urls():
    results = json.load(open('ai_herbs.json', 'r', encoding="utf-8"))
    filenames = glob('./text/*')
    for i, filename in enumerate(filenames):
        url = 'http://alternativehealing.org/{}'.format(filename.split('.txt')[0].split('/')[-1])
        print(url)
        results[i]['original_url'] = url

    json.dump(results, open('ai_herbs.json', 'w', encoding="utf-8"), indent=4, ensure_ascii=False)

    # print(results)


def translate_to_chinese(herb_data):
    """
    Translate herb data from English to Chinese
    """
    print(f'Translating data for {herb_data.get("Names", {}).get("Common", ["Unknown herb"])[0]}')

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Using a more capable model for translation
            messages=[
                {"role": "system", "content": (
                    "You are a bilingual expert in traditional herbal medicine specializing in both English and Chinese. "
                    "Your task is to accurately translate herbal medicine information from English to Chinese, "
                    "preserving the medical terminology and cultural context. "
                    "Be especially careful with herb names, properties, and medical terminology."
                )},
                {"role": "user", "content": (
                    f"Translate the following herbal medicine data from English to Chinese. "
                    f"Maintain the same JSON structure and data types. "
                    f"If any field already contains Chinese text, preserve it. "
                    f"For herb names, include both simplified and traditional Chinese characters if there's a difference. "
                    f"Return ONLY valid JSON with the translated content.\n\n"
                    f"{json.dumps(herb_data, ensure_ascii=False, indent=2)}"
                )}
            ]
        )

        # Clean and parse JSON response
        content = completion.choices[0].message.content
        content = content.replace('```json', '').replace('```', '').strip()

        return json.loads(content)

    except Exception as e:
        print(f"Error translating herb data: {e}")
        return herb_data  # Return original data if translation fails


def translate_herbs_to_chinese():
    """Process and translate all herbs in the dataset"""

    # Load existing data
    results = json.load(open('ai_herbs.json', 'r', encoding="utf-8"))
    translated_results = []

    for herb in tqdm(results):
        del(herb['Original Text'])

        # Translate the herb data
        translated_herb = translate_to_chinese(herb)
        translated_results.append({
            'Chinese': translated_herb,
            'English': herb
        })

        # Save intermediate results after each herb
        json.dump(translated_results, open('ai_herbs_chinese.json', 'w', encoding="utf-8"),
                  indent=4, ensure_ascii=False)

    return translated_results

translate_herbs_to_chinese()
#add_urls()
# get_herbs()