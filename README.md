# Systematic Analysis of Kaggle Competition: Santa 2024

📝 **Authors**:  
- Jairo Arturo Barrera Mosquera (`20222020142`)  
- Gabriela Martinez Silva (`20231020205`)  
📅 **Date**: JUNE 2025  

---

## 🎯 Competition Overview
**Goal**: Minimize perplexity of scrambled Christmas-themed text passages by reordering words into coherent sequences.  
**Evaluation Metric**: Average perplexity (lower = better) using the **Gemma 2 9B** language model.  

### 🗂 Dataset
- **Data Structure**: Jumbled passages from Christmas stories.  
- **Submission Data**: Submissions must permute words in `sample_submission.csv`.  
- **Constraints**:  
  - Words can only be reordered (*no modifications/additions/deletions*).  
  - Valid permutations must include all original words.  

---

## 🔍 System Analysis

### 📥 Input
- Scrambled word sequences (1 per row).  
- **Functional Requirements**:  
  - Process sentences *as-provided* by Kaggle.  

### 🏗️ Architecture

The system follows a modular pipeline to transform scrambled text into coherent output, simulating part of the expected behavior in a full solution:

1.  **NormalizedInput**
    - **Function**: Loads `sample_submission.csv`, normalizes words (lowercase, removes punctuation), and creates a per-row word count dictionary.
    - **Output**: `processed_dict` → input for linguistic processing.

2.  **TemplatesGeneration**
    - **Function**: Uses SpaCy to tag words with parts of speech (POS), applies grammatical templates to create valid sentence permutations.
    - **Output**: `templates_generation.csv` → candidate sentences per row.

3.  **SentencesGeneration**
    - **Function**: Combines candidate sentences intelligently to cover all original words, avoiding overuse and maximizing reuse.
    - **Output**: `sentences_generation.csv` → final output for submission.

Each module is implemented in Python and validated with intermediate outputs.

---

### ⚙️ System Requirements

**Functional Requirements (FRs):**
* **Sentence Usage:** Operate only on shuffled sentences provided by Kaggle.
* **Word Constraints:** No addition, deletion, or modification of words.
* **Sequence Length Handling:** Must process rows of varying lengths.

**Non-Functional Requirements (NFRs):**
* **Perplexity Optimization:** Final permutations should reduce language model perplexity.
* **Grammatical Coherence:** Reordered sentences must follow valid English grammar.

---

### 📉 Sensitivity and Chaos

- **Sensitivity**: Small changes in word order significantly impact perplexity scores.
- **Chaos**: Due to $n!$ permutations, exhaustive evaluation is infeasible. Templates help constrain possibilities.
- **Mitigation**: POS tagging and structured templates help reduce entropy and enforce order.

---

### 💻 Workshop 3: Simulation Pipeline

#### Modules:

1. **`normalized_input.py`**
   - Reads raw CSV.
   - Cleans and normalizes text.
   - Outputs word count dictionary per row.

2. **`templates_generation.py`**
   - Receives normalized word bags.
   - Tags parts of speech with SpaCy.
   - Generates sentence candidates using grammatical templates.
   - Saves to `templates_generation.csv`.

3. **`sentences_generation.py`**
   - Combines candidate sentences per row.
   - Ensures words are not overused and maximizes coverage.
   - Saves final sentences to `sentences_generation.csv`.

#### Code

📸 See implementation code [Simulation](/Script)

