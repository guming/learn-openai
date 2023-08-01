import os
import openai
import pandas as pd
from sklearn.model_selection import train_test_split

import time
from functools import wraps
import tiktoken
from io import BytesIO
import seaborn as sns

df = pd.read_csv('data/output.csv')
df.to_json("data/training_data_1.jsonl", orient="records", lines=True)
df = df.head(10000)
print(df)
df = df.drop_duplicates(subset=["prompt"])
df["prompt"] = df["prompt"].apply(lambda x: str(x) + " ->")
df["completion"] = df["completion"].apply(lambda x: str(x) + "")
train_df, valid_df = train_test_split(df, test_size=0.1, random_state=42)
train_df.to_json("data/training_data_prepared_train.jsonl", orient="records", lines=True)
valid_df.to_json("data/training_data_prepared_valid.jsonl", orient="records", lines=True)

openai.api_key = os.getenv("OPENAI_API_KEY")

def upload_file(file_name: str) -> str:
  upload_response = openai.File.create(
    file=open(file_name, "rb"),
    purpose="fine-tune"
  )
  return upload_response.id

train_file_id = upload_file("data/training_data_prepared_train.jsonl")
valid_file_id = upload_file("data/training_data_prepared_valid.jsonl")

n_epochs = 2
n_classes = 2
model = "ada"
positive = "1"
fine_tuning_job = openai.FineTune.create(
    training_file=train_file_id, 
    validation_file=valid_file_id, 
    compute_classification_metrics=True,
    classification_n_classes=n_classes,
    n_epochs=n_epochs,
    model=model,
    classification_positive_class=positive
)

def get_tokenizer(text: str) -> list[int]:
  return tiktoken.encoding_for_model(text)

enc = get_tokenizer("gpt-3.5-turbo")
for k in df["completion"].unique().tolist():
  print(k, enc.encode(k))

def retry_until_not_none(sleep_time: float=0) -> str:
  """
  Decorator that retries the execution of a function 
  until response is not None.
  """
  def decorate(func):
      @wraps(func)
      def wrapper(*args, **kwargs):
          response = None
          while response is None:
              response = func(*args, **kwargs)
              time.sleep(sleep_time)
          return response
      return wrapper
  return decorate

@retry_until_not_none(sleep_time=300)
def retrieve_model_name(job_id: str) -> str:
    return openai.FineTune.retrieve(id=job_id).fine_tuned_model

print(fine_tuning_job.id)

fine_tuned_model = retrieve_model_name(fine_tuning_job.id)

print(fine_tuned_model)

fine_tuning_job = openai.FineTune.retrieve(id=fine_tuning_job.id)
results = openai.File.download(fine_tuning_job.result_files[0].id)
df = pd.read_csv(BytesIO(results))
accuracy = df[df["classification/accuracy"].notnull()]["classification/accuracy"].to_list()
df = pd.DataFrame({"accuracy": accuracy, "epochs": range(1, n_epochs+1)})
sns.lineplot(data=df, x="epochs", y="accuracy").set(title='Validation Accuracy /Epochs');


def create_completion(
  prompts: list[str],
  fine_tuned_model: str, 
  suffix_separator: str, 
  max_tokens: int) -> list[str]:
    prompts = [prompt + suffix_separator for prompt in prompts]
    answer = openai.Completion.create(
        model=fine_tuned_model,
        prompt=prompts,
        max_tokens=max_tokens,
        temperature=0
    )
    completions = [answer["choices"][i]["text"].strip() for i in range(len(answer["choices"]))]
    return completions

results=create_completion(["代开发票，联系电话：021-29876556"], fine_tuned_model, " ->", 1)
print(results)