# Import main pipeline classes
from NormalizedInput import NormalizedInput
from TemplatesGeneration import TemplatesGeneration
from SentencesGeneration import SentencesGeneration

# Main execution block
if __name__ == "__main__":
    csv_path = 'sample_submission.csv'
    text_column = 'text'
    # Step 1: Normalize input and get word counts per row
    ni = NormalizedInput(csv_path, text_column)
    processed_dict = ni.get_processed_dictionary()
    # Step 2: Generate all possible template-based sentences for each row
    tg = TemplatesGeneration(ni)
    tg.generate()  # Writes "templates_generation.csv"
    # Step 3: Combine sentences to cover all original words per row
    sg = SentencesGeneration("templates_generation.csv", processed_dict)
    sg.combine_sentences_per_row()
    sg.save()      # Writes "sentences_generation.csv"
