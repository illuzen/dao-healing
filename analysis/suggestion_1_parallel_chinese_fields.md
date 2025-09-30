# Suggestion 1: Add Parallel Chinese Fields for Medical Information

## Problem
Currently, the structured fields in the JSON contain primarily English content, while the Chinese translations exist only in the unstructured "Original Text" field. This makes the bilingual information inaccessible for practical use.

## Proposed Solution
Add parallel Chinese fields for all medical and descriptive content to create a truly bilingual dataset.

### Implementation Structure

For each herb entry, add the following parallel Chinese fields:

```json
{
  "Maladies_Treated": [
    "Edema",
    "Difficulty in urination",
    "Painful urination"
  ],
  "Maladies_Treated_CN": [
    "水腫",
    "小便不利",
    "尿痛"
  ],
  
  "Medical_Function": [
    "Diuretic effect",
    "Anti-tumor effect"
  ],
  "Medical_Function_CN": [
    "利尿作用",
    "抗腫瘤作用"
  ],
  
  "Properties": [
    "Sweet",
    "Bland",
    "Neutral"
  ],
  "Properties_CN": [
    "甘",
    "淡",
    "平"
  ],
  
  "Dosage": "10–20 g. Concentrated extract: 0.5–2 g.",
  "Dosage_CN": "10～20公克；濃縮中藥：0.5～2公克。",
  
  "Contraindications": "Do not use when there are no symptoms of damp-heat.",
  "Contraindications_CN": "無濕熱者忌用。"
}
```

### Benefits
1. **Clear separation**: English and Chinese content are clearly separated but linked
2. **No duplication**: Each language has its own field, preventing mixed or duplicate content
3. **Easy access**: Applications can easily access either language version
4. **Maintains structure**: Preserves the existing JSON structure while enhancing it

### Extraction Method
To populate these fields, parse the "Original Text" content using these patterns:

1. Look for bilingual pairs marked by HTML structure:
   - English content followed by Chinese (marked with Chinese class or after "主治﹕")
   - Section headers like "Actions & Indications:" followed by "主治﹕"

2. Common patterns to identify:
   - "Medical functions:" / "藥理﹕"
   - "Actions & Indications:" / "主治﹕"
   - "Properties" / "性味﹕"
   - "Dosage:" / "用量﹕"
   - "Cautions:" / "禁忌﹕"

### Example Extraction for zhu ling (豬苓):

From Original Text:
```
Actions & Indications:
主治﹕
for edema, edema caused by pyelitis, difficulty in urination...
水腫，腎盂炎水腫，小便不利，尿痛，急性尿道炎...
```

Would become:
```json
{
  "Maladies_Treated": [
    "Edema",
    "Edema caused by pyelitis",
    "Difficulty in urination",
    "Painful urination",
    "Acute inflammation of the urethra"
  ],
  "Maladies_Treated_CN": [
    "水腫",
    "腎盂炎水腫",
    "小便不利",
    "尿痛",
    "急性尿道炎"
  ]
}
```

### Priority Fields for Parallel Chinese Addition
1. **High Priority** (Medical/Clinical Information):
   - Maladies_Treated → Maladies_Treated_CN
   - Medical_Function → Medical_Function_CN
   - Contraindications → Contraindications_CN
   - Dosage → Dosage_CN

2. **Medium Priority** (TCM Properties):
   - Properties → Properties_CN
   - Meridians → Meridians_CN
   - Samples_of_Formulae → Samples_of_Formulae_CN

3. **Lower Priority** (Already partially bilingual):
   - Chemical_Ingredients (already contains some Chinese)
   - Names section (already has Chinese names)

## Next Steps
1. Create a parsing script to extract Chinese content from "Original Text"
2. Map the extracted Chinese to corresponding English fields
3. Validate that all content is properly paired without duplication
4. Update the JSON structure with the new parallel fields

This approach ensures that both languages are fully represented in a structured, accessible format while avoiding any content duplication.