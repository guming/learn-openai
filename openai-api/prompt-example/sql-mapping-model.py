import os,sys
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "Given the following SQL tables, your job is to write queries given a user’s request.\n\nCREATE TABLE Orders (\n  OrderID int,\n  CustomerID int,\n  OrderDate datetime,\n  OrderTime varchar(8),\n  PRIMARY KEY (OrderID)\n);\n\nCREATE TABLE OrderDetails (\n  OrderDetailID int,\n  OrderID int,\n  ProductID int,\n  Quantity int,\n  PRIMARY KEY (OrderDetailID)\n);\n\nCREATE TABLE Products (\n  ProductID int,\n  ProductName varchar(50),\n  Category varchar(50),\n  UnitPrice decimal(10, 2),\n  Stock int,\n  PRIMARY KEY (ProductID)\n);\n\nCREATE TABLE Customers (\n  CustomerID int,\n  FirstName varchar(50),\n  LastName varchar(50),\n  Email varchar(100),\n  Phone varchar(20),\n  PRIMARY KEY (CustomerID)\n);"
    },
    {
      "role": "user",
      "content": "Write JavaBean which mapping the tables"
    }
  ],
  temperature=0,
  max_tokens=1024,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

print(response, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

