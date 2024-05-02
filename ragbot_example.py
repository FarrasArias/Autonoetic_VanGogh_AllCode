from requests import api
from chatbots.chatbot_openai import OpenAIChatbot
from rags.rag import RAG
from ragchain import RAGChain
from colorama import init, Fore
import pandas as pd
from openai import OpenAI

init()

model_endpoint = "https://api.openai.com/v1/chat/completions"
api_key =  ""
if api_key == "":
    print(Fore.RED + "Your api key is empty, if you're not getting responses, make sure to explicitly write it in ragbot_example.py" + Fore.RESET)

# Metadata for RAG models
VAN_GOGH_QUESTIONS_META = {
    "order": 3, 
    "name": "Interview Questions", 
    "context": "These are excerpts extracted to help you with your answer"
}
EINSTEIN_QUESTIONS_META = {
    "order": 5, 
    "name": "Einstein Facts", 
    "context": "This is not relevant to the task"
}

def davinci_call(p):
   client = OpenAI(api_key="")
   response = client.completions.create(
       model="davinci-002",
       prompt=p,
       max_tokens=300,
       temperature=0.5
       )
   return response.choices[0].text

def main():
    """Main execution loop for the chatbot application."""

    # TODO: add a force_refactor flag and implement index folder management

    rag_e = RAG("van_gogh_combined_strings", "./data/combined_strings", num_results=5, separator_value="$$", metadata=VAN_GOGH_QUESTIONS_META)
    #rag_v = RAG("vginterview", "./data/newVG2", num_results=5, metadata=VAN_GOGH_QUESTIONS_META)

    rag_chain = RAGChain([rag_e])  

    character_data_dir = "./model_custom_inits/DefaultCharacterTest.json"
    model_data_dir = "./model_custom_inits/DefaultModel.json"
    van_gogh_bot = OpenAIChatbot(model_endpoint, character_data_dir, model_data_dir, api_key) 


    df_q = pd.read_csv("./questions_steve_vg.csv")#
    questions = list(df_q[df_q.columns[0]].to_numpy())[:30]#
    print(questions)#
    counter = 0#
    q_a = []#
    #while True:#
    for question in questions:
        #user_input = input("> ")
        user_input = question
        master_prompt = rag_chain.make_master_prompt(user_input)
        #print("RAG prompt:\n" + Fore.GREEN + master_prompt + Fore.RESET) 
        #response = van_gogh_bot.chat(user_input, master_prompt, print_context=True) #REAL
        p = master_prompt + "\n Question: " + user_input + "\n Answer: Ah, " #davinci
        response = davinci_call(p)
        print("QUESTION",question)
        q_a.append((user_input,response,master_prompt))

        df_5 = pd.DataFrame(q_a, columns=["Question", "Answer","Context"])
        df_5.to_csv("q_a_c_RAG_davinci.csv")
if __name__ == "__main__":
    main()

