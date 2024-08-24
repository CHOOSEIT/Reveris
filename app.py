from openaiAPI import query_openai_with_history, openai_show_usage

messages = [
    {"role": "user", "content": "Hello, how are you ?"},
]

answer = query_openai_with_history(messages)

print(answer)

openai_show_usage()