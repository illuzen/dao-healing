
from openai import OpenAI
import json
import os
from glob import glob
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key)
num_retries = 3

SCHEMA = """ {       

    "Names": {
        // Make sure that all names in all languages are included.
        // Dictionary with name types as keys (Name, Pharmaceutical, Botanical, Chinese, Common, Other) and a list as values.
        // Include the title of the page as the name of the herb. If there are multiple names in the header, include all of them.
            // Examples: 
            {"Name": ["beng da wan", "lei gong gen"]}
            {"Pharmaceutical": ["Herba Centella asiatica"]}
            {"Botanical": ["Hydrocotyle erecta L. F.", "Centella asiatica, L."]}
            {"Common": ["Ginseng", "Jinseng", "Hindi: ब॒हमामानडुकी, bemgsag, brahma manduki, brahmanduki, brahmi (North India, West India), gotu kola, khulakhudi, mandookaparni, mandukaparni (South India), mandukparni, Thankuni, 北印度語)", "Sanskrit: brahamamanduki, brahma manduki, brahmi, divya, jalneem, mandukaparni, mandukparni, nandukparni, thankuni (梵語)", "Nepalese:braahamii (brahami), brahambuti, ghodtaapre (ghodtapre), ghorataap (ghortap), kholca ghayn (尼泊爾語)", "English :Asiatic pennywort,  Indian pennywort, Indian navelwort, gotu kola (Sinhalese origin)(英 語)"}
                    // Include the geography or language of the names if given
            {"Other name": ["han ke cao 蚶殼草", "lei gong cao 雷公草", "lei gong teng 雷公藤 (not to be confused with tripterygium wilfordii", "ben ko wan 崩口碗"]}
            {"Chinese": ["崩大碗", "雷公根"]}
            // Provide a complete list of all names. Do not omit any names, including variations, synonyms, or regional/geographical distinctions. If multiple names came from the same region, then group them together. Example:"Nepalese:braahamii (brahami), brahambuti, ghodtaapre (ghodtapre), ghorataap (ghortap), kholca ghayn (尼泊爾語)"

            "Pronunciation in Korean":[
                //return if listed
                // Array of strings Pronuncuation in Korean
                // Example: ["byeongpul"]
            ],

            "Pronunciation in Japanese":[
                //return if listed
                // Array of strings Pronuncuation in Japanese
                // Example: ["tsubo kusa"]
            ],

            "Pronunciation in Cantonese":[
                //return if listed
                // Array of strings Pronuncuation in Cantonese:
                // Example: ["bang1 daai6 wun2"]
            ],

    },

    

    "Type": "string", // One of: "Formula", "Herb", "Chemical", "Animal", "Mineral", "Qigong", "Acupuncture", "Massage", "Diet"


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


    "Maladies Treated": [
        // Array of strings for conditions treated, maladies, TCM patterns of disharmony
        // Example: ["Fatigue", "Weak immunity", "Poor digestion", "Damp heat","Cold dampness", "Glaucoma", "Hot flashes"]
        // Classify medical terms into two categories: ‘Malady’ and ‘Medical Function.’ Maladies refer to negative health conditions (e.g., bronchitis, arthritis), while Medical Functions refer to positive health effects (e.g., improving memory, enhancing circulation). If a term represents a positive function rather than a malady, classify it under ‘Medical Function.’
        // Do not omit any details. Ensure all content is preserved. If different parts of an herb or animal are used to treat different conditions, maintain that distinction in the output.
        //Specify if the medicinal effect was observed on humans or animals.
        ]
    ],
    "Medical Function: [
        //Array of strings for medical functions describing positive function of the herb
        //Example: ["ridding of itchiness of mosquito bites by applying externally.","strengthening circulation and blood vessels", "The juice can increase the platelet count of people diagnosed with dengue fever", "improving memory: The essential oil of  monoterpenoids, including bornyl acetate, α-pinene, β-pinene and γ-terpinene, are reported to inhibit acetylcholinesterase", "neuroprotective effect on rats that have been experimentally induced to have Parkinson's disease", "anti-wrinkle of skin. Asiaticoside has been demonstrated to increase collagen synthesis thus performing an anti-wrinkle activity", "The extract of beng da wan decreases the Abeta in lab mice", etc]
            // Do not omit any details. Ensure all content is preserved. If different parts of an herb or animal are used to treat different conditions, maintain that distinction in the output.
            // If a specific experiment or research is described, do not draw general conclusions. Only report the findings as they are presented. Specify whether the experiment was conducted on humans or animals.
            //Specify if the medicinal effect was observed on humans or animals.
            //Provide as many details as you can find. Do not summarize or generalize too much. Ensure the original context and depth of the data are maintained. Example: ["effect on blood sugar: giving domesticated rabbits venous injection of 2 yu zhu extract of 0.5/kg, has caused the blood sugar to lower, but stomach introduction has caused the blood sugar to rise initially and to lower eventually. It can obviously inhibit the effect of of raising blood sugar by the epinephrine."]
            //If a medical function describes a Traditional Chinese Medicine (TCM) healing process, provide the full explanation exactly as stated. Do not omit any details or simplify TCM concepts—preserve the full description. Do not take single meanings out of context. Preserve the full explanation as presented, ensuring that all details and nuances are maintained. Example ["Clears heat and toxin, nodules", "Expels externally contracted wind heat as in common cold"]

    // "Dosage" is Text describing dosage
    "Dosage": "string", 

    "Samples of Formulae": "string"
    //is text describing the recepies, preparation and applications 
    //If there are directions on how to use an herb, animal part, medicinal formula, or recipe, including details on the combination and the malady it treats, categorize it under ‘Samples of Formulae.’ Ensure the usage instructions, combinations, and specific conditions are clearly preserved. Example: ["For treatment of cardiac exhaustion: use with Aminophylline and hydrochlorothiazide", "For treatment of high lipids: use with shan zha", "For treatment of  age spots: use with ju hua , jiang can, can yong, bo he"]

    
    "Contraindications": "string", // Text describing warnings and adverse effects

    "Research": "string", // Text summarizing research findings. 
        //Put all text summarizing medicinal research and medical findings in the ‘Research’ field. This includes studies, experiments, and any other research-related content regarding the efficacy, uses, or effects of herbs, animal parts, or medicinal treatments.

    "Notes": "string", 
    // Additional information as text
    // Put everything that doesn’t fit the format of the schema above and the specified fields in the ‘Notes’ section. Do not repeat information if it has already been stated in another field of the schema.
    // Do not include information related to the structure and elements of the site: website navigation elements, advertising, translated by and copyright notices.
    // Do not include information by whom the information is compiled. Example: "Compiled by Joe Hing kwok Chu 朱興國編譯."


    "Chemical Ingredients": {
        // Array of strings listing chemical components
        // Example: ["Ginsenosides", "Polysaccharides", "Asiatic Acid (C30H48O5)", "The shell of Haliotis discus hannai Ino （H. gigantea discus Reeve）contain more than 90% calcium carbonate and organic substance of about 3.67%. The inorganic elements are: Na, Mg, Al, Si, K, Fe, P, Ti, Mn, Cu, Ni, Sr, Zn, Cl, S, I and among them the ions of phosphates, silcates, sulfates exit. It also contain choline and conchiolin."]
        // Provide details about the specific part of the herb or animal that contains each chemical, ensuring all relevant information about the source is included.
        
    }
} """


def extract_structured_data(text, filename):
    print(f'Processing {filename}')

    user_prompt = (
        "You are a data extraction specialist for herbal medicine. Your task is to extract structured information "
        "from text about herbs, treatments, and medicinal plants following a precise schema.\n"
        "You MUST follow the exact data structure specified, using the correct data types for each field.\n"
        f"Extract information from the text and format it according to this EXACT schema:\n\n{SCHEMA}\n\n"
        "Rules for extraction:\n"
        "1. ALWAYS use the specified data types...\n"
        "...\n"
        f"TEXT TO EXTRACT FROM:\n{text}"
    )

    for _ in range(num_retries):
        try:
            completion = client.completions.create(
                model="o1-2024-12-17",
                prompt=user_prompt,
            )

            content = completion.choices[0].text.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)

        except json.JSONDecodeError as e:
            print(f"JSON parse error for {filename}: {e}, retrying...")
        except Exception as e:
            print(f"Error processing {filename}: {e}, retrying...")

    return {
        "Names": {},
        "Type": "",
        "Maladies Treated": [],
        "Geography": [],
        "Properties": [],
        "Meridians": [],
        "Medical Function": [],
        "Dosage": "",
        "Samples of Formulae": "",
        "Contraindications": "",
        "Research": "",
        "Notes": "",
        "Chemical Ingredients": {}
    }


def extract_herb_structure():
    filenames = glob('./text/*')
    results = []
    for filename in tqdm(filenames[:4]):
        print(filename)
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()

        result = extract_structured_data(text, filename)
        result['Original Text'] = text
        url = 'http://alternativehealing.org/{}'.format(filename.split('.txt')[0].split('/')[-1])
        result['original_url'] = url
        results.append(result)

        json.dump(results, open('ai_herbs_test_non_chat.json', 'w', encoding="utf-8"), indent=4, ensure_ascii=False)

    return results

extract_herb_structure()



