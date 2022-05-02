from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import openai
from api.gpt import Example
from api.gpt import GPT
import json
import re
import random
# nltk.download('wordnet')
# nltk.download('cmudict')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('words')

API_KEY = "sk-ZvdR5aJsBMD79NEQF1ZdzvSDTOUowTBB2DU24S51"
openai.api_key = API_KEY
CIRCLED_NUMBER = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}


def rhyme(inp, level):
    entries = nltk.corpus.cmudict.entries()
    syllables = [(word, syl) for word, syl in entries if word == inp]
    rhymes = []
    for (word, syllable) in syllables:
        rhymes += [word for word,
                   pron in entries if pron[-level:] == syllable[-level:]]
    return set(rhymes)


def doTheyRhyme(word1, word2):
    # first, we don't want to report 'glue' and 'unglue' as rhyming words
    # those kind of rhymes are LAME
    if word1.find(word2) == len(word1) - len(word2):
        return False
    if word2.find(word1) == len(word2) - len(word1):
        return False

    return word1 in rhyme(word2, 1)


def get_similar_words(keyword):
    last_letters = nltk.defaultdict(list)
    words = nltk.corpus.words.words('en')
    for word in words:
        key = word[-4:]
        last_letters[key].append(word)
    return random.sample(last_letters[keyword[-4:]], 4)


def make_blank_question(file_name, question_number, blank_word_amount, use_gpt):
    # file name : 크롤링한 결과 txt file name (string)
    # question_number : 크롤링한 문제 중 변형문제를 제작할 문제 번호 (integer)
    # blank_word_amount : 빈칸의 단어 길이 (interger)
    # use_gpt : 선지 generation에 gpt를 사용할지 여부 (boolean)
    paragraph_list = [p for p in open(
        file_name, "r", encoding="utf-8") if len(p) >= 10]
    if question_number > len(paragraph_list):
        print("ERROR : Question Number out of Range")
        return
    n_gram_range = (blank_word_amount, blank_word_amount)
    if blank_word_amount == 1:
        stop_words = ["an", "are", "is", "or", "and", "can",
                      "cannot", "for", "that", "on", "with", "to", "be", "of"]
    else:
        stop_words = []
    count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit(
        [paragraph_list[question_number]])
    candidates = count.get_feature_names()

    # vertorize paragraph and candidates with BERT
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    doc_embedding = model.encode([paragraph_list[0]])

    candidate_embeddings = model.encode(candidates)
    distances = cosine_similarity(doc_embedding, candidate_embeddings)
    keywords = [candidates[index] for index in distances.argsort()[0]]
    if blank_word_amount==1:
        best_match_keyword = keywords[-2]
    else:
        best_match_keyword = keywords[-1]
    # print(keywords)
    print(best_match_keyword)
    choice_list = []
    if blank_word_amount == 1 and not use_gpt:
        choice_list = get_similar_words(best_match_keyword) # method 2
        
    else:
        gpt = GPT(engine="davinci", temperature=0.6,
                  max_tokens=blank_word_amount*5*10)  # gpt class initialize
        # number_range : 빈칸의 단어 개수에 따라서 참조할 example들이 달라짐
        number_range = {1: ["1"], 2: ["2"], 3: ["3", "4"], 4: [
            "3", "4"], 5: ["5", "6"], 6: ["7", "6"], 7: ["6", "7"]}
        with open("blank_example.json", "r", encoding="utf-8") as f:
            blank_example = json.load(f)
            for l in number_range[blank_word_amount]:
                for i in range(len(blank_example[l])):
                    gpt.add_example(Example("paragraph: "+blank_example[l][i]["paragraph"]+"\n " +
                                            blank_example[l][i]["answer"], str(blank_example[l][i]["wrong_answers"])))

            # gpt3 선지 생성 prompt
            result = gpt.submit_request("paragraph: "+paragraph_list[question_number]
                                        .replace(best_match_keyword, " <BLANK> ")+"\n "+best_match_keyword)
        result = result.choices[0].text
        result = re.sub("'", "", result.strip()[10:-1]).split(",")
        choice_list = [l.strip()for l in result]
    print(paragraph_list[question_number].replace(
        best_match_keyword, "_"*len(best_match_keyword), 1))
    if(len(choice_list)>4):
        choice_list = choice_list[:4]
    choice_list.append(best_match_keyword)
    random.shuffle(choice_list)
    answer = choice_list.index(best_match_keyword)+1
    for i in range(5):
        print(CIRCLED_NUMBER[i+1], end=" ")
        print(choice_list[i])
    print("answer is : %s" % CIRCLED_NUMBER[answer])


if __name__ == "__main__":
    make_blank_question("빈칸10.txt", 0, 1, True)
