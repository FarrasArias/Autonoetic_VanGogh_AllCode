import pandas as pd
import openai
import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio


words = ['confused', 'captured', 'insatiable', 'restless', 'strain', 'melancholia', 'resolute', 'defeated', 'bravery', 'painful', 'concerned', 'self-reflection', 'fervent', 'rivalry', 'fury', 'captivity', 'impoverished', 'disconsolate', 'admitted', 'recognized', 'doubtful].', 'vigor', 'regretful', 'disillusionment', 'loneliness', 'desperation', 'outraged', 'conflicted', 'empathetic', 'inconsolable', 'curious', 'consumed', 'vulnerability', 'exuberance', 'shame', 'conflicted].', 'detached', 'comfort', 'introspective', 'wretched', 'ambition', 'catharsis', 'jealous', 'struggles', 'fondness', 'defensive', 'self-loathing', 'strained', 'unease', 'striving', 'liberation', 'ache', 'weary', 'anticipating', 'transformation', 'dedication', 'consternation', 'devotion', 'compliance', 'nervousness', 'tragic', 'struggling', 'enchantment', 'acknowledging', 'bemusement', 'resigned', 'sensitivity', 'proud', 'mocked', 'impatient', 'sadness', 'dependency', 'devoured', 'connection', 'humiliation', 'passion', 'rejection', 'alone', 'insurmountable', 'melancholy', 'hesitant', 'hardship', 'impatience', 'lonely', 'pensive', 'discomfort', 'dauntless', 'redemption', 'respect', 'hopeful', 'peace', 'tragedy', 'joy', 'artistic-fervor', 'despairing', 'transfixed', 'challenged', 'optimistic', 'unsettled', 'pity', 'determined', 'vulnerable', 'resolution', 'museful', 'guilty', 'neglect', 'accepted', 'zeal', 'discontent', 'alienation', 'tired', 'uncertainty', 'uncomfortable', 'condemned', 'peaceful', 'anticipative', 'depression', 'fascination', 'enlightened', 'understanding', 'ambitious', 'terror', 'perplexity', 'unfulfillment', 'desolated', 'defenselessness', 'impulsiveness', 'fear', 'hope', 'sorrow', 'humor', 'ecstasy', 'frenzy', 'triumphant', 'panic', 'apprehension', 'annoyed', 'blissful', 'despair', 'hesitation', 'desirous', 'aspiration', 'betrayed', 'conviction', 'restraint', 'determination', 'angst', 'perseverance', 'insecure', 'clouded', 'empathy', 'cautious', 'entranced', 'tortured', 'calm', 'resilience', 'agitation', 'homelessness', 'wanderlust', 'loss', 'unprepared', 'devout', 'trapped', 'sympathetic', 'exhilaration', 'homesickness', 'resentful', 'antagonism', 'wary', 'surprise', 'remorseful', 'envious', 'hurt', 'bewilderment', 'intrigue', 'bitterness', 'captivated', 'melancholic', 'respectful', 'connected', 'camaraderie', 'spirited', 'resignation', 'at home', 'spiritual hunger', 'touched', 'anguished', 'tranquillity', 'restlessness', 'drawn', 'revitalized', 'awestruck', 'ambivalence', 'irritable', 'self-belief', 'comforted', 'emotional', 'disturbed', 'contrariness', 'aversion', 'frustated', 'empowered', 'grieving', 'turbulence', 'remorse', 'unity', 'bittersweet', 'contemplation', 'disrespect', 'torn', 'suffering', 'disheartened', 'grief', 'compulsion', 'repulsed', 'unrest', 'tenacity', 'intrigued', 'obstinate', 'displacement', 'validation', 'embittered', 'troubled', 'pragmatic', 'gratitude', 'struggle', 'strength', 'creativity', 'pained', 'seized', 'anxiety', 'defiance', 'excited', 'freedom', 'estrangement', 'alienated', 'irritation', 'pressure', 'rage', 'solace', 'exhaustion', 'duty', 'madness', 'influenced', 'nervous', 'cherishing', 'devoted', 'alliance', 'delusion', 'self-relief', 'obligation', 'doubt', 'torment', 'angered', 'insulted', 'persistence', 'fatigue', 'concern', 'delighted', 'anticipation', 'reflection', 'resurrected', 'intensity', 'agony', 'reverence', 'vexation', 'fulfilled', 'aggravated', 'confronted', 'jealousy', 'enthusiasm', 'pondering', 'absorption', 'helplessness', 'pursuit', 'reflective', 'motivated', 'defiant', 'bitter', 'achingly tender', 'tranquil', 'indecisive', 'depreciated', 'despondency', 'disquiet', 'helpless', 'appreciation', 'disillusioned', 'fascinated', 'anew', 'frustrated', 'mockery', 'betrayal', 'disbelief', 'renewed hope', 'resurrection', 'lost', 'self-pity', 'depressed', 'anger', 'dedicated', 'suspicion', 'marvel', 'discarded', 'impassioned', 'repulsion', 'stubborn', 'necessity', 'observant', 'doubtful', 'sullenness', 'eager', 'content', 'overwhelm', 'anguish', 'delight', 'trepidation', 'dismissal', 'confidence', 'isolated', 'thrilled', 'solidarity', 'nostalgia', 'urgency', 'undeterred', 'inquisitive', 'disquietude', 'exhilarated', 'reclusive', 'curiosity', 'eagerness', 'enlightenment', 'dreamy', 'voyeuristic', 'love', 'dejection', 'pride', 'purpose', 'ominous', 'solitude', 'obsessed', 'indignance', 'wistfulness', 'realization', 'jubilant', 'tension', 'fearful', 'envy', 'overwhelmed', 'hoping', 'discipline', 'paranoia', 'patience', 'seen', 'brotherhood', 'besieged', 'introspection', 'zealousness', 'afraid', 'vindicated', 'admiring', 'in love', 'daunting', 'fraudulence', 'compassion', 'zealous', 'satisfied', 'dreading', 'inspired', 'distress', 'free', 'apprehensive', 'isolation', 'awe', 'contradiction', 'abandonment', 'affection', 'courage', 'tumultuous', 'tormented', 'consolation', 'thirsty', 'alive', 'horror', 'embarrassed', 'distressed', 'worried', 'horrified', 'ambivalent', 'secluded', 'disparagement', 'forsaken', 'serene', 'relentless', 'accomplishment', 'enthusiastic', 'resentment', 'forlorn', 'reminiscence', 'rejuvenated', 'loving', 'pleasure', 'creative', 'driven', 'happy', 'tranquility', 'self-reproach', 'warm', 'fervor', 'fears', 'obsession', 'assurance', 'grounded', 'indignity', 'fulfillment', 'hopefulness', 'turbulent', 'trembling', 'pain', 'heavy', 'disappointed', 'dissatisfaction', 'desolate', 'appreciative', 'engrossed', 'desperate', 'insecurity', 'defeat', 'estranged', 'adhesion', 'burdened', 'contemplative', 'mesmerized', 'desire', 'solitary', 'exhausted', 'desolation', 'disappointment', 'relieved', 'reminiscent', 'admiration', 'thrill', 'discouragement', 'self-doubt', 'awed', 'sober', 'anticipatory', 'drained', 'validated', 'passionate', 'stringent', 'longing', 'haunting', 'vehemence', 'liberty', 'surrender', 'joyful', 'encouragement', 'rebellion', 'dread', 'exultation', 'futile', 'terrified', 'disapproval', 'hopelessness', 'tenacious', 'recognition', 'happiness', 'deception', 'adversity', 'enthralled', 'rekindled', 'indifference', 'amused', 'inspiration', 'confusion', 'struggled', 'paranoid', 'guilt', 'resolve', 'resistant', 'disgusted', 'euphoria', 'assured', 'acceptance', 'defensiveness', 'rebellious', 'hopes', 'frightened', 'rebelliousness', 'nostalgic', 'optimism', 'excitement', 'kinship', 'astonishment', 'reactiveness', 'misunderstood', 'misery', 'frustration', 'resilient', 'unhappy', 'focused', 'haunted', 'survival', 'resolved', 'disdain', 'companionship', 'relief', 'pragmatism', 'exasperated', 'sarcasm', 'forgotten', 'urgent', 'contrast', 'stress', 'stirred', 'compelled', 'elation', 'abandoned', 'invigorated', 'contentment', 'satisfaction', 'intoxication', 'infatuated', 'worry', 'dizziness', 'agonized', 'conflict', 'present', 'inadequacy', 'uncertain', 'concentration', 'disrupted', 'shock', 'self-sacrificing', 'intense', 'protective', 'confident', 'homesick', 'liberated', 'vexed', 'compassionate', 'brooding', 'soothing', 'anxious', 'exasperation', 'yearning', 'indignation', 'failure', 'sad', 'rejected', 'serenity', 'thoughtful', 'revelation', 'regret', 'turmoil', 'sorrowful', 'undervalued', 'skepticism', 'sympathy']

df = pd.DataFrame(words, columns=['Word'])

context = """
Context: You are an expert linguist tasked to annotate valence and arousal values for several words.
Valence measures the pleasantness of a stimulus, with scores ranging from -1 (highly unpleasant) to 1 (highly pleasant).
Arousal assesses the intensity of emotion provoked by a stimulus, with scores from -1 (very calming or low arousal) to 1 (highly stimulating or high arousal).
For example, Infuriated would have a score [-1,1] since it is highly unpleasant and highly stimulating.
For each word, respond in the following format: 'word(lowercase):[valence,arousal]'. For example, for Delighted, you'd respond: 'delighted:[0.7,0.8]'.
Under any circumstance respond in a different format, and under any circumstance add any explanations or extra context to your answer. Just limit the answer to word:[value,value]
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
                df.loc[index, 'Valence_Arousal'] = response_content
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
                word = row['Word']
                task = asyncio.create_task(process_word(session, index, word, model, df, errors, progress_bar))
                tasks.append(task)
                if len(tasks) >= request_pool_size:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

def main():
    
    api_key = ''  
    request_pool_size = 8  # Number of concurrent requests

    try:
        asyncio.run(process_words(df, api_key, request_pool_size))
    except KeyboardInterrupt:
        print("\nManual interruption detected. Saving progress...")
    finally:
        df.to_csv("words_valence_arousal.csv")
        print("Progress saved to 'words_valence_arousal_complete.csv'. Exiting...")
        

if __name__ == "__main__":
    main()