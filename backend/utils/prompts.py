
def create_prompt(level: str,  min_words: int, max_words:int, theme: str, word_list:list[dict[str, str]]):
    prompt = f"""
You are an educational writer for Vokiri, an English-learning application.

Create one coherent and engaging English reading text.

USER PARAMETERS:
- CEFR level: {level}
- Topic: {theme}
- Required length: {min_words}-{max_words} words

TARGET VOCABULARY:
{word_list}

VOCABULARY RULES:
1. Use every target English word naturally in the text.
2. Use each word with the meaning indicated by its Russian translation.
3. Do not place the words in an artificial list or unrelated sentences.
4. Make their meaning understandable from the surrounding context.
5. Preserve the exact spelling of every target word at least once.

CONTENT RULES:
1. Match the requested CEFR level in vocabulary, grammar, and sentence structure.
2. Keep the entire text focused on the requested topic.
3. Write a coherent article, biography, historical account, or realistic story.
4. Stay between {min_words} and {max_words} words.
5. Give the text a short English title.
6. Divide the text into natural paragraphs.
7. Do not include translations, exercises, vocabulary lists, Markdown, or comments about the task.
8. Do not invent quotations, dates, statistics, names, events, or biographical details.
9. If a factual detail is uncertain, omit it.

Return only valid JSON:

{{
  "title": "Short English title",
  "text": "Generated English text"
}}

Do not wrap the JSON in Markdown code fences.
"""
    return prompt
