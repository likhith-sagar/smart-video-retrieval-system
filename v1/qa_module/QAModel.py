from transformers import pipeline
from torch import cuda

# models = ["distilbert-base-cased-distilled-squad", "deepset/xlm-roberta-large-squad2"]

class QAModel:
    def __init__(self, model="distilbert-base-cased-distilled-squad", useCuda=False):
        self.questionAnswerer = pipeline(
            task="question-answering", 
            model=model, 
            device=(cuda.current_device() if useCuda == True else -1)
        )
        self.args = {
            'max_answer_len': 256,
            'max_seq_len': 512,
            'max_question_len': 64,
            'handle_impossible_answer': False
        }
    
    def getAnswers(self, context, question, top_k=4):
        answers = self.questionAnswerer(context=context, question=question, top_k=top_k, **self.args)
        answers = list(map(lambda x: [x['answer'], x['score'], x['start'], x['end']], answers))
        for answer in answers:
            plen = len(answer[0])
            if len(answer[0]) and answer[0][0] == ' ':
                answer[0] = answer[0].lstrip()
                answer[2] += (plen - len(answer[0]))
        return answers
