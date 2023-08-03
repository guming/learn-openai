import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "Given the following apis, your job is to write the unit testing code \n\napi:\nhttps://localhost:8080/users\nHttpMethod: Post\ncontent-type: application/json\nrequest body:\n{\n    \"firstname\": \"John\",\n    \"Lastname\": \"Snow\",\n    \"status\": \"Learning things\"\n  }\nresponse sample:\n  {\n    \"id\": 1,\n    \"firstname\": \"John\",\n    \"Lastname\": \"Snow\",\n    \"status\": \"Learning things\"\n  }"
    },
    {
      "role": "user",
      "content": "write property-based testing code by using Hypothesis"
    }
  ],
  temperature=0,
  max_tokens=1024,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

print(response, ..., sep=' ', end='\n', file=sys.stdout, flush=False)