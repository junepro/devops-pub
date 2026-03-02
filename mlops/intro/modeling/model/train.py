import os, joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# 라이브러리 임포트
# joblib: 학습시킨 모델 객체를 파일(.pkl)로 저장하거나 불러올 때 사용합니다.

# CountVectorizer: 텍스트(문자)를 컴퓨터가 이해할 수 있는 숫자(단어 빈도수)로 변환합니다.

# MultinomialNB: 나이브 베이즈 분류기입니다. 텍스트 분류(스팸 메일, 의도 파악 등)에 매우 빠르고 효율적입니다.

# Pipeline: 데이터 변환(CountVectorizer)과 모델 학습(NB) 과정을 하나로 묶어주는 도구입니다.

X=[ "hi","hello","how to reset password","cancel my subscription","great service" ]
y=[ "greeting","greeting","question","complaint","praise" ]

pipeline=Pipeline([("vect",CountVectorizer()),("clf",MultinomialNB())])
pipeline.fit(X,y)

# Pipeline: "문자를 숫자로 바꾸고(vect), 그 숫자로 학습해(clf)"라는 과정을 하나의 체인으로 만듭니다. 이렇게 하면 나중에 새로운 문장을 예측할 때도 똑같은 변환 과정을 거치게 되어 편리합니다.

# pipeline.fit(X, y): 준비된 데이터를 통해 모델을 학습시킵니다.

os.makedirs("model/artifacts", exist_ok=True)
joblib.dump(pipeline, "model/artifacts/intent_model.pkl")
print("trained")


# joblib.dump: 학습이 완료된 pipeline 객체를 intent_model.pkl이라는 파일로 저장합니다.

# 이렇게 저장해두면 나중에 다시 학습할 필요 없이 파일만 불러와서 바로 **예측(predict)**에 사용할 수 있습니다.
