import re


class ContentProcessor:

    CONTENT_REGEX = r"[^a-zA-Z0-9]"

    @staticmethod
    def find_content(text):
        content = re.sub('[^A-Za-z \n]+', ' ', text)                                          # Remove all special signs
        content = re.sub('\n+', ' ', content)                                                 # Replace newline by space
        content = re.sub(' +', ' ', content)                                                  # Strip multiple spaces
        content = " ".join(filter(lambda w: len(w) > 1, content.split()))                     # Remove single letters
        longest_40_words = sorted(content.split(), key=lambda x: len(x), reverse=True)[:40]
        content = " ".join(filter(lambda w: w in longest_40_words, content.split()))          # Remove short words
        return content
