import re

ALPHABET_SCORES_LETTERS = 'ABCDEF'
ALPHABET_SCORE_CONST = 16.5
ALPHABET_SCORES = {'A': int(ALPHABET_SCORE_CONST * 6),
                   'B': int(ALPHABET_SCORE_CONST * 5),
                   'C': int(ALPHABET_SCORE_CONST * 4),
                   'D': int(ALPHABET_SCORE_CONST * 3),
                   'E': int(ALPHABET_SCORE_CONST * 2),
                   'F': int(ALPHABET_SCORE_CONST * 1)}
LIKE_THRESHOLD = 60

def parse_slash(raw_score: str):
    slash_pos = raw_score.find('/')
    score, score_max = raw_score[:slash_pos], raw_score[slash_pos + 1:]
    movie_score = int((float(score) / float(score_max)) * 100)

    if movie_score >= LIKE_THRESHOLD:
        return movie_score, True
    else:
        return movie_score, False


def parse_alphabet(raw_score: str):
    score = raw_score[0]

    if ALPHABET_SCORES[score] >= LIKE_THRESHOLD:
        return ALPHABET_SCORES[score], True
    else:
        return ALPHABET_SCORES[score], False

def parse_only_score(raw_score):
    score = int(raw_score)
    score_max = None

    if score <= 5:
        score_max = 5

    elif score > 5 and score <= 10:
        score_max == 100

    elif score > 10 and score <= 100:
        score_max == 100
    
    elif score > 100 and score <= 1000:
        score_max == 1000
    
    movie_score = int((float(score) / float(score_max)) * 100)
    if movie_score >= LIKE_THRESHOLD:
        return movie_score, True
    else:
        return movie_score, False
