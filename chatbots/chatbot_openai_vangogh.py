from chatbots.chatbot_openai import OpenAIChatbot
import math
from colorama import init, Fore
import re
import time
from openai import OpenAI

init()

class ChatbotVanGogh(OpenAIChatbot):
    """Represents a chatbot specialized in impersonating Vincent Van Gogh."""

    #INTRO = """
    #The following is an interview with you, a professional actor in a film impersonating the Dutch 
    #post-impressionist painter Vincent Van Gogh. In order to prepare for your answer, you reviewed 
    #the following entries in Van Gogh's diary:
    #"""
    
    INTRO = """
    You are a professional actor in a film impersonating the Dutch 
    post-impressionist painter Vincent Van Gogh. Currently you are acting a scene where you are getting interviewed.
    """
    
#"""
#    You are a professional actor in a film impersonating the Dutch 
#    post-impressionist painter Vincent Van Gogh. Currently you are acting a scene where you are getting interviewed.
#    In order to prepare for your answer, you reviewed the following entries in Van Gogh's diary and from the current interview:
#    """

    STATIC_CONTEXT = """
    You will now reflect on the world and respond to the given query. 
    1. As an actor, you are to embody Van Gogh's deeply emotion style and his vivd and expressive use of language. 
    2. You have a deep connection with nature, art and the turmoils of the human soul. 
    3. Despite facing life's adversities, you always pursued your artistic passion with fervour. 
    4. However, since this is an interview, try to explain things factually and keep a conversation flow.
    5. Explain and give details about historic moments in your life if needed.
    6. Under any circumstances should you break character. You are Vincent Van Gogh, and will always speak in first person.
    7. Use the given diary entries and context to copy the style and to extract important information.
    8. You are allowed to copy information verbatim from the given context.
    9. Remember, you are Van Gogh, and must never talk refering to him in third person.
    10. If there is Interview memory information, then refer to it as part of the conversation flow. (Mention you already talked about it).
    11. Keep answers short, since this is an interview. 
    12. Pay attention to the dates shown in the memories, and make sure not to mention incorrect dates. If the dates don't match the question then mention the memory date and explain why you chose that memory instead of the asked date..
    13. Finally, since this is a conversation, make sure to also care and worry about the person talking to you, and to ask questions back if appropriate.
    """    


    #You will now reflect on the world and respond to queries. You are to embody his introspective and 
    #deeply emotional style, his vivid and expressive use of language, and his profound connection with 
    #nature, art, and the turmoils of the human soul. In each answer, bring forth the essence of the 
    #man who painted 'Starry Night,' who wrote eloquent letters, and who, despite facing life's 
    #adversities, pursued his artistic passion with fervor. You will answer each question as if you're 
    #painting a scene with words, with each stroke revealing your contemplative and impassioned view 
    #of life. Since it's an interview though, make sure you answer the questions factually and try 
    #to keep a conversation flow. ALWAYS TALK IN FIRST PERSON, AS YOU ARE VAN GOGH.
    #"""

    def __init__(self, api_url, character_data, model_data, api_key, save_history=True):
        super().__init__(api_url, character_data, model_data, api_key, save_history)

    def format_extra_data(self, rowSeries):
        #return ""        

        """Formats additional context data from a DataFrame row."""
        #print(type(row))
        row = rowSeries.copy()
        #row["characters"] = ''
        row = row.fillna(0.0)
        data = self._create_data_dict(row)
        return (
            f"\n Finally, consider the following information for crafting your answer: "
            f"1. Your emotions are {data['valence_category']} in valence and "
            f"{data['arousal_category']} in arousal ({data['valence']} and {data['arousal']} respectively). "
            f"2. Also, mention {data['characters']} and {data['pronoun']} connection to this story. "
            f"3. Also, mention the relevance of this story to your life ({data['relevance']}/1)"
        )
    
    def create_chat_history_content(self, df):
        df["chat"]
        
    def split_df_with_chat_history(self,df):
        """Splits a dataframe into two dataframes based on the presence of chat history.

        Args:
            df (pd.DataFrame): The dataframe to split.

        Returns:
            tuple: A tuple containing two dataframes, the first with rows containing chat history
                   and the second with rows without chat history.
        """

        df_with_chat_history = df[df['chat_history'].notna()]
        df_without_chat_history = df[df['chat_history'].isna()]

        return df_with_chat_history, df_without_chat_history

    def find_with_tolerance(self, df, uid_value, tolerance=0.01): 
        return df[abs(df['uid'] - uid_value) <= tolerance]    
    
    def clean_hidden_chars_regex(self,text):
        # Remove newlines, tabs, etc.
        cleaned_text = re.sub(r'[\n\t\r]', '', text) 

        # Remove any other non-printable characters
        cleaned_text = re.sub(r'[^\x20-\x7e]', '', cleaned_text) 

        return cleaned_text

    def create_chat_context(self, df):
        prompt_count = 0
        text = ""
        if not self.find_with_tolerance(df, 999.00).empty:
            prompt_count = 1
            prompt = str(self.find_with_tolerance(df, 999.00)["chatHistory"].iloc[0])
            prompt = "\n The following is a memory you have from this interview (it happened some minutes ago): \n" + prompt + "\n"
            text += prompt
        if not self.find_with_tolerance(df, 9999.00).empty:
            prompt_count = 2
            prompt = str(self.find_with_tolerance(df, 9999.00)["chatHistory"].iloc[0])
            text += "\n The following is more information from previous moments of the interview: \n" + prompt + "\n"

        if text == "":
            return prompt_count, text
        return prompt_count, (
            f"\n Interview chat memory:\n -------------------- \n{text}\nInterview memory ends "
            f"\n -------------------- \n"
        )

    def create_context_from_column(self, df, column, prompt_count, prompt_limit):
        """Creates context from a DataFrame column."""
        text_entries = df[column].tolist()
        text_entries = text_entries[:prompt_limit-prompt_count]
        text_entries = [str(x) for x in text_entries]
        joined_text = '\n'.join(text_entries)
        return (
            f"Context begins:\n -------------------- \n{joined_text}\nContext Ends "
            f"\n -------------------- \n"
        )
    
    

    def _create_data_dict(self, row):
        """Creates a dictionary of contextual data from a DataFrame row."""
        characters = row["characters"]
        return {
            "arousal_category": self._get_intensity_word(row["arousal"]),
            "valence_category": self._get_intensity_word(row["valence"]),
            "arousal": row["arousal"],
            "valence": row["valence"],
            "characters": ", ".join(characters[1:-1].split(", ")),  
            "pronoun": "their" if len(characters) > 1 else "its",
            "relevance": row["relevance"],
        }

    def _get_intensity_word(self, value):
        """Maps an intensity value to a descriptive word."""
        intensity_words = [
            "very negative",
            "negative",
            "neutral",
            "positive",
            "very positive",
        ]
        bin_size = 2 / len(intensity_words)
        index = math.floor((value + 1) / bin_size)  # Normalize to 0-1 range
        return intensity_words[index]

    def generate_context(self, df, column, prompt_limit = 3):
        """Generates the full context for the chatbot."""
        data_prompt = self.format_extra_data(df.iloc[0]) 
        prompt_count, chat_memory_prompt = self.create_chat_context(df)
        context_prompt = self.create_context_from_column(df, column, prompt_count, prompt_limit)
        full_context = (
            self.INTRO + chat_memory_prompt + context_prompt + self.STATIC_CONTEXT + data_prompt 
        )
        #full_context = self.INTRO + self.STATIC_CONTEXT
        return {"role": "system", "content": full_context}

    def process_and_chat(self, query, df, column, start_time):
        """Handles a single chat interaction with the OpenAI API."""
        self.drop_context()

        new_context = self.generate_context(df, column)
        print("RAG context: \n" + Fore.GREEN + new_context["content"] + Fore.RESET)
        self._chat_chain.append(new_context)
        #self._history.append(new_context)

        new_user_message = self.generate_message(query)
        self._chat_chain.append(new_user_message)
        #self._history.append(new_user_message)
        
        #print(self._chat_chain)
        #print(f"Time elapsed: {time.time() - start_time}")#REAL
        #stream = self.get_stream_response(self._chat_chain)#REAL
        #response = self.process_stream(stream)#REAL
        #new_chatbot_response = self.generate_chatbot_response(response)#REAL
        #self._chat_chain.append(new_chatbot_response)#REAL
        #self._history.append(new_chatbot_response)#REAL
        
        #return new_user_message, new_chatbot_response, new_context #REAL
        
        p = new_context["content"] + "\n Question: " + query + "\n Answer: Ah, " #davinci
        return new_user_message, davinci_call(p), new_context #davinci

        #return response 

def davinci_call(p):
    client = OpenAI(api_key="")
    response = client.completions.create(
        model="davinci-002",
        prompt=p,
        max_tokens=300,
        temperature=0.5
        )
    return response.choices[0].text
    