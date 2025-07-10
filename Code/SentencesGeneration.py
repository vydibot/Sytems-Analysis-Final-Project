import pandas as pd
from collections import Counter

class SentencesGeneration:
    def __init__(self, sentence_csv_path, processed_dict):
        """
        Args:
            sentence_csv_path (str): Path to templates_generation.csv (from TemplatesGeneration)
            processed_dict (dict): {row_id: {word: count, ...}, ...} from NormalizedInput
        """
        self.sentence_csv_path = sentence_csv_path
        self.processed_dict = processed_dict
        self.sent_df = pd.read_csv(sentence_csv_path)
        self.final_sentences = []

    def combine_sentences_per_row(self):
        # For each row, select sentences to cover all original word occurrences
        for row_id, word_count_dict in self.processed_dict.items():
            original_bag = []
            for word, count in word_count_dict.items():
                original_bag.extend([word] * count)
            original_counter = Counter(original_bag)
            n_words = len(original_bag)

            row_sentences = self.sent_df[self.sent_df['id'] == row_id]['sentence'].tolist()
            sentence_word_lists = [s.split() for s in row_sentences]

            used_counter = Counter()
            selected_sentences = []
            # Greedily select sentences (longest first) until all words are covered
            for words, sent in sorted(zip(sentence_word_lists, row_sentences), key=lambda x: -len(x[0])):
                temp_counter = Counter(words)
                # Only add if it doesn't exceed original word counts
                if all(used_counter[w] + temp_counter[w] <= original_counter[w] for w in temp_counter):
                    selected_sentences.append(sent)
                    used_counter += temp_counter
                if sum(used_counter.values()) == n_words:
                    break

            # Strict check: ensure the combined sentence uses exactly the same words and counts
            final_counter = Counter()
            for sent in selected_sentences:
                final_counter += Counter(sent.split())
            # Add missing words if any
            missing_words = list((original_counter - final_counter).elements())
            if missing_words:
                print(f"Row {row_id}: Adding missing words to match input: {missing_words}")
                selected_sentences.append(' '.join(missing_words))
                final_counter += Counter(missing_words)
            # Final check
            if final_counter != original_counter:
                print(f"ERROR: Row {row_id} - Final sentence does not match original word counts even after adding missing words.")
                print(f"Original: {dict(original_counter)}")
                print(f"Final:    {dict(final_counter)}")

            self.final_sentences.append({
                "id": row_id,
                "combined_sentence": " ".join(selected_sentences)
            })

    def save(self, output_path="sentences_generation.csv"):
        # Save the final combined sentences per row to CSV
        pd.DataFrame(self.final_sentences).to_csv(output_path, index=False)
        print(f"Combined sentences saved to {output_path}")
