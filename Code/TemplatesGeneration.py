import pandas as pd
import spacy
from spacy.tokens import Doc
from itertools import product
from collections import defaultdict

# Define templates for sentence generation (including passage/song related)
TEMPLATES = [
    ['determiner', 'adjective', 'noun', 'verb', 'preposition', 'determiner', 'noun'],
    ['determiner', 'adjective', 'noun'],
    ['determiner', 'noun', 'verb', 'noun'],
    ['noun', 'verb', 'noun'],
    ['noun', 'verb', 'preposition', 'noun'],  # e.g., "song plays in passage"
    ['noun', 'verb', 'determiner', 'noun'],   # e.g., "song fills the passage"
    ['noun', 'verb', 'adjective', 'noun'],    # e.g., "song inspires beautiful passage"
    ['noun', 'verb', 'conjunction', 'noun'],  # e.g., "song and passage"
    ['noun', 'verb'],
    ['noun', 'noun'],
    ['determiner', 'noun'],
]

class TemplatesGeneration:
    def __init__(self, normalized_input):
        # Initialize with normalized input and load SpaCy model
        self.normalized_input = normalized_input
        self.processed_dict = self.normalized_input.get_processed_dictionary()
        self.all_sentences = []
        self.nlp = spacy.load("en_core_web_sm")

    def classify_words_in_row(self, row_id, words):
        # Classify each word in the row by SpaCy POS
        doc = Doc(self.nlp.vocab, words=words)
        for name, proc in self.nlp.pipeline:
            doc = proc(doc)
        results = []
        for token in doc:
            pos = token.pos_.lower()
            results.append({'id': row_id, 'word': token.text, 'pos': pos})
        return results

    def group_words_by_pos_with_duplicates(self, classified_words):
        # Group word occurrences by POS, using (word, index) to track duplicates
        grouped = defaultdict(list)
        word_pos_count = defaultdict(int)
        for item in classified_words:
            pos = item['pos']
            grouped[pos].append((item['word'], word_pos_count[(item['word'], pos)]))
            word_pos_count[(item['word'], pos)] += 1
        return grouped

    def generate_sentences_for_template_with_duplicates(self, word_pos_dict, template):
        # Generate all possible sentences for a given template, using each word occurrence at most once per sentence
        if not all(pos in word_pos_dict and word_pos_dict[pos] for pos in template):
            return []
        slot_word_occurrences = [word_pos_dict[pos] for pos in template]
        all_assignments = product(*slot_word_occurrences)
        sentences = set()
        for assignment in all_assignments:
            if len(set(assignment)) == len(assignment):
                sentence = ' '.join(word for word, idx in assignment)
                sentences.add(sentence)
        return list(sentences)

    def get_largest_template(self, word_pos_dict):
        # Find the largest fillable template for the row
        for template in TEMPLATES:
            if all(pos in word_pos_dict and word_pos_dict[pos] for pos in template):
                return template
        return None

    def get_unused_words(self, all_words, used_words):
        # Return set of words not yet used in any sentence
        return set(all_words) - set(used_words)

    def generate(self):
        # Main sentence generation loop for all rows
        for row_id, word_counts in self.processed_dict.items():
            words = []
            for word, count in word_counts.items():
                words.extend([word] * count)
            classified = self.classify_words_in_row(row_id, words)
            word_pos_dict = self.group_words_by_pos_with_duplicates(classified)
            all_words = [item['word'] for item in classified]
            used_words = set()
            generated_sentences = []

            # Generate sentences for largest template
            largest_template = self.get_largest_template({k: [w for w, i in v] for k, v in word_pos_dict.items()})
            if largest_template:
                generated_sentences = self.generate_sentences_for_template_with_duplicates(word_pos_dict, largest_template)
                for sentence in generated_sentences:
                    used_words.update(sentence.split())

            # Fallback: generate sentences for unused words
            unused_words = self.get_unused_words(all_words, used_words)
            if unused_words:
                unused_word_pos_dict = {cat: [wi for wi in word_pos_dict[cat] if wi[0] in unused_words] for cat in word_pos_dict}
                for template in TEMPLATES:
                    fallback_sentences = self.generate_sentences_for_template_with_duplicates(unused_word_pos_dict, template)
                    for sentence in fallback_sentences:
                        words_in_sentence = set(sentence.split())
                        if words_in_sentence & unused_words:
                            generated_sentences.append(sentence)
                            used_words.update(words_in_sentence)
                    unused_words = self.get_unused_words(all_words, used_words)
                    if not unused_words:
                        break

            for sentence in generated_sentences:
                self.all_sentences.append({'id': row_id, 'sentence': sentence})

        # Save all generated sentences to CSV
        sentences_df = pd.DataFrame(self.all_sentences)
        sentences_df.to_csv("templates_generation.csv", index=False)
        print("All generated sentences saved to templates_generation.csv")
