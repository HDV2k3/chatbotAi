# import numpy as np
# import nltk
# # nltk.download('punkt')
# from nltk.stem.porter import PorterStemmer
# stemmer = PorterStemmer()


# def tokenize(sentence):
#     """
#     split sentence into array of words/tokens
#     a token can be a word or punctuation character, or number
#     """
#     return nltk.word_tokenize(sentence)


# def stem(word):
#     """
#     stemming = find the root form of the word
#     examples:
#     words = ["organize", "organizes", "organizing"]
#     words = [stem(w) for w in words]
#     -> ["organ", "organ", "organ"]
#     """
#     return stemmer.stem(word.lower())


# def bag_of_words(tokenized_sentence, words):
#     """
#     return bag of words array:
#     1 for each known word that exists in the sentence, 0 otherwise
#     example:
#     sentence = ["hello", "how", "are", "you"]
#     words = ["hi", "hello", "I", "you", "bye", "thank", "cool"]
#     bag   = [  0 ,    1 ,    0 ,   1 ,    0 ,    0 ,      0]
#     """
#     # stem each word
#     sentence_words = [stem(word) for word in tokenized_sentence]
#     # initialize bag with 0 for each word
#     bag = np.zeros(len(words), dtype=np.float32)
#     for idx, w in enumerate(words):
#         if w in sentence_words: 
#             bag[idx] = 1

#     return bag
import numpy as np
import re

def tokenize(sentence):
    """
    Tách câu thành mảng từ/tokens.
    """
    # Sử dụng regex để tách từ dựa trên khoảng trắng và dấu câu
    tokens = re.findall(r'\b\w+\b', sentence)
    return tokens

def stem_word(word):
    """
    Tìm gốc từ đơn giản bằng cách loại bỏ các hậu tố phổ biến.
    """
    suffixes = ['ing', 'ed', 'es', 's', 'ly']  # Các hậu tố phổ biến
    for suffix in suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]  # Trả về gốc từ
    return word  # Nếu không có hậu tố, trả về từ gốc

def bag_of_words(tokenized_sentence, words):
    """
    Trả về mảng bag of words:
    1 cho mỗi từ đã biết có trong câu, 0 nếu không có.
    """
    # Stemming mỗi từ
    sentence_words = [stem_word(word) for word in tokenized_sentence]
    # Khởi tạo bag với 0 cho mỗi từ
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words: 
            bag[idx] = 1

    return bag

# Ví dụ sử dụng
if __name__ == "__main__":
    sentence = "Xin chào, bạn có khỏe không?"
    words = ["xin", "bạn", "khỏe", "tạm biệt"]
    
    tokenized = tokenize(sentence)
    print("Tokenized:", tokenized)
    
    bag = bag_of_words(tokenized, words)
    print("Bag of Words:", bag)
