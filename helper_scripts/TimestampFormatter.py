

import pandas as pd
import openai
import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio

#df = pd.DataFrame(words, columns=['Word'])
df = pd.read_csv("to_convert_datetimes.csv",index_col=0)

context = """
Context: You'll get a text which shows an approximate or exact date. Your task is to convert this to a single format.
The format used will be dd/mm/yyyy. Here are the rules:
1. If the month is not known, (NaN or something like it) then assume mid-year (06).
2. If the day is not known, (NaN or something like it) then assume mid-month (15).
3. If the year is not known, (NaN or something like it) then assume 1700.
4. If the text just mentions an approximate date, convert that approximation to the closes day/month/year.
5. If the text references a range of dates, months or years, just choose the middle one, and just choose a single day/month/year.
Here are some examples:
June third of 1889 -> 03/06/1889.
Last months of 1878 -> 15/10/1878. (notice how we chose the 15th because there's no day data, and we chose month 10 because it says last months)
And so on...
IMPORTANT: Under any circumstances should you break the format. Do not add a single symbol out of line.
Just write two numbers followed by a slash followed by two numbers followed by a slash followed by four numbers.
00/00/0000.
Here is a date:
""".encode('utf-8', 'ignore').decode('utf-8')

async def process_word(session, index, word, model, df, errors, progress_bar):
    try:
        message = {'role': 'user', 'content': f"{context}\n{word}"}
        async with session.post('https://api.openai.com/v1/chat/completions',
                                json={'model': model, 'messages': [message], 'max_tokens': 60},
                                headers={'Authorization': f'Bearer {openai.api_key}'}) as resp:
            if resp.status == 200:
                #print("HERE")
                data = await resp.json()
                #print(data)
                response_content = data['choices'][0]['message']['content']
                #print(response_content)
                df.loc[index, 'timestamps'] = response_content
            else:
                #print("ORHERE")
                error_message = await resp.text()
                errors.append(f"Error at index {index}, Word: {word}: HTTP status {resp.status}, Message: {error_message}")

            progress_bar.update(1)

    except Exception as e:
        errors.append(f"Error at index {index}, Word: {word}: {e}")

async def process_words(df, api_key, request_pool_size):
    openai.api_key = api_key
    model = 'gpt-4'  # or whichever GPT model you're using
    errors = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        with tqdm_asyncio(total=df.shape[0]) as progress_bar:
            for index, row in df.iterrows():
                word = row['Timestamp']
                task = asyncio.create_task(process_word(session, index, word, model, df, errors, progress_bar))
                tasks.append(task)
                if len(tasks) >= request_pool_size:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

def main():
    api_key = ''  # Replace with your actual API key
    request_pool_size = 8  

    try:
        asyncio.run(process_words(df, api_key, request_pool_size))
    except KeyboardInterrupt:
        print("\nManual interruption detected. Saving progress...")
    finally:
        df.to_csv("timestamp_extraction.csv")
        print("Progress saved to 'timestamp_extraction.csv'. Exiting...")
        

if __name__ == "__main__":
    main()