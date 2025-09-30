# Suggestion 2: Automated Extraction of Chinese Content from "Original Text" Field

## Problem Statement
The "Original Text" field contains raw HTML with both English and Chinese content mixed together, but this bilingual information is not being utilized in the structured fields. The Chinese translations need to be systematically extracted and paired with their English counterparts.

## Proposed Solution: Pattern-Based Content Extraction

### Extraction Strategy

#### Step 1: Identify Key Chinese Section Markers
The "Original Text" contains consistent patterns that mark Chinese sections:

**Primary Markers:**
- `英文藥名﹕` (Pharmaceutical name)
- `拉丁文學名﹕` (Biological name)
- `性味﹕` (Properties)
- `歸經﹕` (Meridians)
- `藥理﹕` (Medical functions)
- `主治﹕` (Actions & Indications)
- `化學成份﹕` (Chemical ingredients)
- `用量﹕` (Dosage)
- `禁忌﹕` (Contraindications)
- `處方舉例﹕` (Samples of formulae)
- `現代研究﹕` (Modern Research)

#### Step 2: Parse Bilingual Pairs
Most sections follow this pattern:
```
English heading:
English content
Chinese heading (中文標題)﹕
Chinese content (中文內容)
```

### Extraction Algorithm

#### Pattern Recognition Rules:

1. **For Properties Section:**
   - Look for: `Properties\n(characteristics)﹕\n性味﹕`
   - Extract English: text after "Properties" before Chinese marker
   - Extract Chinese: text after "性味﹕" until next section

2. **For Medical Functions:**
   - Look for: `Medical functions:\n藥理﹕`
   - Parse numbered lists in both languages
   - Match by list position (1st English = 1st Chinese)

3. **For Maladies Treated:**
   - Look for: `Actions & Indications:\n主治﹕`
   - English list typically follows "for" or starts directly
   - Chinese list follows "主治﹕"
   - Split by commas or semicolons

4. **For Chemical Ingredients:**
   - Often already bilingual in format: `English name (Chinese name)`
   - Or parallel lists with matching order

### Example Extraction Process

**Raw Text from "Original Text":**
```
Properties
(characteristics)﹕
性味﹕

sweet, bland, 
neutral.
甘﹐淡，平。
```

**Extraction Result:**
```python
properties_en = ["sweet", "bland", "neutral"]
properties_cn = ["甘", "淡", "平"]
# Combine: ["sweet (甘)", "bland (淡)", "neutral (平)"]
```

### Implementation Approach

#### Phase 1: Build Extraction Patterns
```python
extraction_patterns = {
    'properties': {
        'en_marker': r'Properties.*?性味',
        'cn_marker': r'性味﹕\s*(.*?)(?=\n\n)',
        'separator': '﹐|，|、'
    },
    'maladies': {
        'en_marker': r'Actions & Indications:.*?主治',
        'cn_marker': r'主治﹕\s*(.*?)(?=\n\n)',
        'separator': '﹐|，|、|；'
    },
    'dosage': {
        'en_marker': r'Dosage:.*?用量',
        'cn_marker': r'用量﹕\s*(.*?)(?=\n\n)'
    }
}
```

#### Phase 2: Extract and Match Content
1. Parse "Original Text" using regex patterns
2. Clean extracted text (remove HTML tags, extra spaces)
3. Split into individual items (for array fields)
4. Match English and Chinese by position or context
5. Validate matches for consistency

#### Phase 3: Merge into Structured Fields
```python
def merge_bilingual(english_list, chinese_list):
    merged = []
    for i, en_item in enumerate(english_list):
        if i < len(chinese_list):
            cn_item = chinese_list[i]
            merged.append(f"{en_item} ({cn_item})")
        else:
            merged.append(en_item)  # No Chinese equivalent
    return merged
```

### Special Cases to Handle

#### 1. Missing Translations
Some entries may have English without Chinese or vice versa:
- Keep the available content
- Mark as incomplete if needed

#### 2. Multiple Chinese Terms for One English Term
Example: "edema" might map to both "水腫" and "浮腫"
- Include all variations: "edema (水腫/浮腫)"

#### 3. Numbered Lists
Medical functions often have numbered points:
```
1. diuretic effect...
2. anti-tumor effect...

1. 利尿作用...
2. 抗腫瘤作用...
```
Match by number sequence.

#### 4. Embedded References
Keep references like [1], [2] attached to the correct content:
```
"Diuretic effect [1] (利尿作用 [1])"
```

### Quality Assurance Checks

1. **Completeness Check:**
   - Count Chinese characters in "Original Text"
   - Verify substantial portion appears in structured fields

2. **Duplication Check:**
   - Ensure no Chinese phrase appears twice in same field
   - Check for accidental English duplication

3. **Format Consistency:**
   - All bilingual entries follow same pattern
   - Special characters properly encoded

4. **Cross-Reference Validation:**
   - Chemical names match between sections
   - Dosage units are consistent

### Expected Output Example

**Before extraction:**
```json
"Properties": ["Sweet", "Bland", "Neutral"],
"Maladies_Treated": ["Edema", "Difficulty in urination"]
```

**After extraction and merge:**
```json
"Properties": ["Sweet (甘)", "Bland (淡)", "Neutral (平)"],
"Maladies_Treated": ["Edema (水腫)", "Difficulty in urination (小便不利)"]
```

### Benefits of This Approach

1. **Automated**: Can process all 5 herbs systematically
2. **Preserves context**: Maintains relationship between English and Chinese
3. **No manual translation**: Uses existing translations from source
4. **Verifiable**: Can check against "Original Text" for accuracy
5. **Scalable**: Same patterns work for additional herbs

### Implementation Priority

1. **First**: Extract for high-value medical fields (Maladies_Treated, Medical_Function)
2. **Second**: Properties, Meridians, Dosage
3. **Third**: Chemical ingredients (partially done)
4. **Last**: References, notes (less critical)

This extraction process ensures all Chinese content from the original URLs is properly captured and integrated without creating new fields or duplicating information.