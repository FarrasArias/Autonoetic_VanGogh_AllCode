from chatbots.chatbot_openai_vangogh import ChatbotVanGogh
from rags.rag import RAG
from ragchain import RAGChain
from colorama import init, Fore
import pandas as pd
import numpy as np
import time

init()

model_endpoint = "https://api.openai.com/v1/chat/completions"
api_key =  ""

def filter_dataframe(df, column_name, filter_values):
    """Filters a DataFrame based on a column's values.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        column_name (str): The name of the column for filtering.
        filter_values (pd.Series or np.ndarray): Values to match in the column.

    Returns:
        pd.DataFrame: The filtered DataFrame.

    Raises:
        ValueError: If filter_values is not a Series or array.
    """
    if not isinstance(filter_values, (pd.Series, np.ndarray)):
        raise ValueError("filter_values must be a pandas Series or numpy array")

    return df[df[column_name].isin(filter_values)]

def main():
    df = pd.read_csv("./data/final_cognitive_27mar.csv", index_col=0)
    df.reset_index(drop=True, inplace=True)  # Ensure consistent indexing

    column_to_vectorize = "augmented_passage"
    bio_metadata = {
        "order": 1,
        "name": "Diary Entries", 
        "context": "Excerpts from Van Gogh's fictional diary. Use for information and lexical style." 
    }

    rag_bio = RAG("chunks_augmented_context_van_gogh_bio", db=df[column_to_vectorize], num_results=5, metadata=bio_metadata)
    rag_chain = RAGChain([rag_bio])

    character_data_dir = "./model_custom_inits/DefaultCharacter.json"
    model_data_dir = "./model_custom_inits/DefaultModel.json"
    VanGogh = ChatbotVanGogh(model_endpoint,character_data_dir,model_data_dir,api_key)

    #df_q = pd.read_csv("./questions2.csv")
    #questions = list(df_q[df_q.columns[0]].to_numpy())#[:2]
    #print(questions)
    #counter = 0
    #q_a = []

    while True: #REAL
    #for question in questions:
        results_h = None
        chat_memory_of_chat_memory = None        

        user_input = input("> ") #REAL
        #user_input = question
        print(Fore.GREEN+user_input+Fore.RESET)
        
        start_time = time.time()
        results, master_prompt = rag_chain.make_master_prompt(user_input, return_result_list=True)
        #_, results = rag_bio.similarity_search(user_input)
        history_chat = list(filter(lambda x: True if "chathistory:" in x else False, results))
        #print(Fore.GREEN+"resalts"+Fore.RESET,history_chat)
        if len(history_chat) != 0:
            relevant_history = str(history_chat[0])
            #relevant_history = str(history_chat[0])
            #print(Fore.RED+"resalts"+Fore.RESET,relevant_history)
            results_h, master_prompt_h = rag_chain.make_master_prompt(relevant_history, return_result_list=True, from_chat=True)
            #print(Fore.RED+"HHHHHHH"+Fore.RESET, results_h)
            results_h_2 = list(filter(lambda x: True if "chathistory:" in x else False, results))
            if "chathistory:" in results_h[1]:
                chat_memory_of_chat_memory = {"uid":9999, 'chatHistory':results_h[1]}
            else:
                if results_h[1] in results:
                # Delete the existing occurrence
                    results = np.delete(results, np.where(results == results_h[1]))
                
                #results = np.insert(results, 0, "chatMem"+results_h[1])
                results = np.insert(results, 0, results_h[1])
            
        filtered = filter_dataframe(df,column_to_vectorize, results)
        
        if results_h is not None:
            new_data = {'uid': 999, 'chatHistory': results_h_2[0]}
            
            filtered = pd.concat([filtered, pd.DataFrame(new_data, index=[len(filtered)])], ignore_index=True)

            #filtered.loc[len(filtered.index)] = new_data 
        if chat_memory_of_chat_memory is not None:
            filtered = pd.concat([filtered, pd.DataFrame(chat_memory_of_chat_memory, index=[len(filtered)])], ignore_index=True)

            #filtered.loc[len(filtered.index)] = chat_memory_of_chat_memory 

        #print("RAG prompt: \n" + Fore.GREEN + master_prompt + Fore.RESET)
        print(filtered)
        print("letter count:",filtered["uid"].apply(lambda x: 1 if str(x)[0:2] == "50" else 0).sum())
        user, chatbot, context = VanGogh.process_and_chat(user_input, filtered, "vangogh", start_time)
        rag_chain._rags[0].encoder.add_history(user["content"],chatbot["content"]) #REAL
        
        #q_a.append((user["content"], chatbot))
        #q_a.append((user["content"], chatbot["content"], context["content"]))
    
        #df_5 = pd.DataFrame(q_a, columns=["Question", "Answer", "Context"])
        #df_5.to_csv("q_a_c.csv")
        
if __name__ == "__main__":
    main()
    

#make temperature inversely proportional to cosine similarity