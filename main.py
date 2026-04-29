import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

def main():
    load_dotenv()
    aname = "aiaiaaaaaiiiiiiiiiiiiiiiiiiiiiii"
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print("api_key已讀取")
        
    else:
        print("api_key 未被讀取")
        return

    llm = ChatOpenAI(
        model=os.getenv("MODEL"),
        base_url=os.getenv("BASE_URL"),
        api_key=api_key
    )

    result = llm.invoke("請自我介紹")
    print(result.content)

if __name__ == "__main__":
    main()
    
   