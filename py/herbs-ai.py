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
        // Make sure that all names in all languages are included.
        // Dictionary with name types as keys (Name, Pharmaceutical, Botanical, Chinese, Common, Other) and a list as values.
        // Include the title of the page as the name of the herb. If there are multiple names in the header, include all of them.
            // Examples: 
            {"Name": ["beng da wan", "lei gong gen"]}
            {"Pharmaceutical": ["Herba Centella asiatica"]}
            {"Biological": ["Hydrocotyle erecta L. F.", "Centella asiatica, L.", "Haliotis asinina  (耳鲍)"]}
            {"Chemical": ["sodium borate", "disodium tetraborate 四硼酸鈉 (Na2B4O7·10H2O)"]}
            {"Common": ["Ginseng", "Jinseng", "Hindi: ब॒हमामानडुकी, bemgsag, brahma manduki, brahmanduki, brahmi (North India, West India), gotu kola, khulakhudi, mandookaparni, mandukaparni (South India), mandukparni, Thankuni, 北印度語)", "Sanskrit: brahamamanduki, brahma manduki, brahmi, divya, jalneem, mandukaparni, mandukparni, nandukparni, thankuni (梵語)", "Nepalese:braahamii (brahami), brahambuti, ghodtaapre (ghodtapre), ghorataap (ghortap), kholca ghayn (尼泊爾語)", "English :Asiatic pennywort,  Indian pennywort, Indian navelwort, gotu kola (Sinhalese origin)(英 語)"}
                    // Include the geography or language of the names if given
            {"Other name": ["han ke cao 蚶殼草", "lei gong cao 雷公草", "lei gong teng 雷公藤 (not to be confused with tripterygium wilfordii", "ben ko wan 崩口碗"]}
            {"Chinese": ["崩大碗", "雷公根", "果實", "花", "崩大碗"]}
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
            "Pinyin Pronunciation":[
                //return if listed
                // Array of strings Pronuncuation in Cantonese:
                // Example: ["苘 is pronounced as qiǒng,  also as qǐng"]
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
        // Do not summarize. Preserve the full original content exactly as presented, including all details, explanations, and descriptions without condensing or simplifying.
        // Do not omit any details. Ensure all content is preserved. If different parts of an herb or animal are used to treat different conditions, maintain that distinction in the output.
        //Specify if the medicinal effect was observed on humans or animals.
        //If specified, indicate which part of the herb or animal is used to treat each specific malady. Clearly associate the part (e.g., root, leaf, bark, shell, liver, horn) with the condition it is used to treat.
        ]
    ],
    "Medical Function: [
        //Array of strings for medical functions describing positive function of the herb
        //Example: ["ridding of itchiness of mosquito bites by applying externally.","strengthening circulation and blood vessels", "The juice can increase the platelet count of people diagnosed with dengue fever", "improving memory: The essential oil of  monoterpenoids, including bornyl acetate, α-pinene, β-pinene and γ-terpinene, are reported to inhibit acetylcholinesterase", "neuroprotective effect on rats that have been experimentally induced to have Parkinson's disease", "anti-wrinkle of skin. Asiaticoside has been demonstrated to increase collagen synthesis thus performing an anti-wrinkle activity", "The extract of beng da wan decreases the Abeta in lab mice", etc]
            // Do not omit any details. Ensure all content is preserved. If different parts of an herb or animal are used to treat different conditions, maintain that distinction in the output.
            // If a specific experiment or research is described, do not draw general conclusions. Only report the findings as they are presented. Specify whether the experiment was conducted on humans or animals.
            //Specify if the medicinal effect was observed on humans or animals.
            //Provide as many details as you can find. Do not summarize or generalize. Ensure the original context and depth of the data are maintained. Example: ["effect on blood sugar: giving domesticated rabbits venous injection of 2 yu zhu extract of 0.5/kg, has caused the blood sugar to lower, but stomach introduction has caused the blood sugar to rise initially and to lower eventually. It can obviously inhibit the effect of of raising blood sugar by the epinephrine."]
            //If a medical function describes a Traditional Chinese Medicine (TCM) healing process, provide the full explanation exactly as stated. Do not omit any details or simplify TCM concepts—preserve the full description. Do not take single meanings out of context. Preserve the full explanation as presented, ensuring that all details and nuances are maintained. Example ["Clears heat and toxin, nodules", "Expels externally contracted wind heat as in common cold"]

    // "Dosage" is Text describing dosage
    "Dosage": "string", 

    "Samples of Formulae": "string"
    //is text describing the recepies, preparation and applications 
    //If there are directions on how to use an herb, animal part, medicinal formula, or recipe, including details on the combination and the malady it treats, categorize it under ‘Samples of Formulae.’ Ensure the usage instructions, combinations, and specific conditions are clearly preserved. Example: ["For treatment of cardiac exhaustion: use with Aminophylline and hydrochlorothiazide", "For treatment of high lipids: use with shan zha", "For treatment of  age spots: use with ju hua , jiang can, can yong, bo he"]
    //Include English transaltion of TCM herb in brackets immediately after the TCM name. Use the format: TCM name (English name). Example: Composition: Cang Er Zi (Xanthium fruit) 9g, Bo He (Peppermint / Field Mint) 6g, Xin Yi Hua (Magnolia flower) 15g, Bai Zhi (Angelica dahurica root) 9g.


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
        //Specify if any ingredients are produced through processes such as hydrolysis with hydrochloric acid or other chemical treatments. Clearly describe the process used and link it to the resulting ingredient.
    
    }

    "References": [
        // Array of strings for references
        // Include the numbered references to the studies mentioned at the bottom of the page. Preserve the exact citation format, including the reference number and full source information (e.g., journal name, year, volume, page numbers, or URL). Examples: ‘[1] Afr J Tradit Complement Altern Med. 2009; 6(1): 9–16.’, ‘[2] Angiology. 2001 Oct;52 Suppl 2:S15-18.’, ‘[3] http://zipcodezoo.com/Plants/C/Centella_asiatica/’, ‘[23] Food Chemistry, 121 (2010), 1231–1235’, '[21] 中國醫藥報， 2006-11-17'
        //Include any ‘Further Reading’ links or resources mentioned in the data. Preserve the full URLs and list them as they appear, without omission. Examples include: ‘http://www.paper.edu.cn/index.php/default/famous/famous_detail/2087/’ and ‘http://www.tuftsmedicalcenter.org/apps/Healthgate/Article.aspx?chunkiid=21763#ref16’
        // Mention the whole list of references, all references and sources listed, without exception. Do not omit any source regardless of format. 
        ]


    "Further Reading": [
        // Array of strings for further reading
        // Additional sources of information which are not numbered and don't fit "References"
        // Example: ["http://www.paper.edu.cn/index.php/default/famous/famous_detail/2087/", "http://www.tuftsmedicalcenter.org/apps/Healthgate/Article.aspx?chunkiid=21763#ref16"]

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
                model="gpt-4.5-preview-2025-02-27",  # Using a more capable model for extraction
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

                        f"4. Do not duplicate information. Ensure no repetition of details across different fields.\n\n"
                        f"5. If a specific experiment or research is described, do not draw general conclusions. Only report the details and findings of the experiment. If it mentioned in the original text, specify if the experiment was done on humans or animals.\n\n"
                        f"6. If there is a list of points, include them all, ensuring none are omitted.\n\n"
                        f"7. Include all the details. Do not omit any information, no matter how small.\n\n"
                        f"8. Specify if details are relevant to specific parts of the herb or animal rather than the whole herb. Clearly identify the parts, such as the shell, bark, seeds, flesh, etc.\n\n"
                        f"9. Preserve all Traditional Chinese Medicine (TCM) terms mentioned in the data, such as ‘damp heat,’ ‘pixu,’ and any other relevant TCM concepts, without omission or modification.\n\n"
                        f"10. Provide as many details as you can find. Do not summarize or generalize. Ensure the original context and depth of the data are maintained.\n\n"
                        f"11. If any numbers are mentioned (e.g., dosages, quantities, durations in experiments), do not omit them. Preserve all numerical values exactly as stated in the source.\n\n"
                        f"12. Reduce the interpretive or creative tone by 25%. Focus on accurate, neutral reporting of the information, with minimal inference or embellishment.\n\n"
                        f"13. If the Chinese version of the content contains additional details not present in the English version, translate it into English while preserving all nuances and small details. Ensure that no information is lost or omitted in the translation.\n\n"
                        f"14. Be as complete as possible. Include all available information, preserving every detail, no matter how minor. Do not omit, condense, or generalize any part of the content.\n\n"
                        f"15. If the content contains a reference number linked to the reference list at the bottom of the page, include the number and ensure it correctly corresponds to the appropriate reference in the list. \n\n"
                        f"16. If quantities of the herb or mineral are mentioned in the original text, make sure to gather and include this information accurately. Do not omit any measurements or dosage details."
                        f"17. If there is a variation of the herb, mineral, or animal that has a specific property, clearly specify the variation along with the associated property. Do not generalize—identify the exact type or subspecies when given."
                        f"18. Include the English name of a TCM herb, animal or plant in brackets immediately after the original TCM name. For example: yiyiren (coix seed), baikouren (white cardamom), xingren (apricot kernel), kufan (calcined alum), huangbai (phellodendron), hai jin (lygodium spore), jin qian cao (lysimachia / gold coin grass), mu tong (akebia stem), che qian zi (plantain seed), she xiang (musk), Physeter catodon L (sperm whale)."
                        f"19. Do not repeat in brackets after the sentence whether the experiment was done on humans or animals. Simply mention in the text if it was an animal experiment. If the original text does not specify, assume it was conducted on humans and do not add any note about it."
                        f"20. Include all the information found at the bottom of the page, up to but not including ‘Sponsor’s Ads by Google.’ Do not omit or summarize any part of this content. Ensure all information is preserved and accurately placed into the appropriate field in the schema."


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


def extract_herb_structure():
    """Process multiple herb pages"""

    start_num = 20
    end_num = 25
    filenames = glob('./text/*')[start_num:end_num]
    results = []
    for filename in tqdm(filenames):
        print(filename)
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()

        # Process the herb page
        result = extract_structured_data(text, filename)
        result['Original Text'] = text
        url = 'http://alternativehealing.org/{}'.format(filename.split('.txt')[0].split('/')[-1])

        result['original_url'] = url
        results.append(result)

        output_filename = './json/final/ai_herbs_{}_{}_final.json'.format(start_num, end_num-1)

        # Save intermediate results after each herb
        json.dump(results, open(output_filename, 'w', encoding="utf-8"), indent=4, ensure_ascii=False)

    return results



def translate_to_chinese(herb_data):
    """
    Translate herb data from English to Chinese
    """
    print(f'Translating data for {herb_data.get("Names", {}).get("Common", ["Unknown herb"])[0]}')

    try:
        completion = client.chat.completions.create(
            model="gpt-4.5-preview-2025-02-27",  # Using a more capable model for translation
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
    results = json.load(open('./json/ai_herbs.json', 'r', encoding="utf-8"))
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
        json.dump(translated_results, open('./json/ai_herbs_chinese.json', 'w', encoding="utf-8"),
                  indent=4, ensure_ascii=False)

    return translated_results

extract_herb_structure()
# translate_herbs_to_chinese()
#add_urls()
# get_herbs()