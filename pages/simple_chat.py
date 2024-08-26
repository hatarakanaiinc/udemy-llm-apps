import streamlit as st
import openai

st.title("simple chat")

user_message = st.text_input("どうしましたか？")

if user_message:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    st.write(completion.choices[0].message.content)
