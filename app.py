import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests

st.title("AI 新聞/部落格摘要工具 🤓")
st.markdown("在下方空欄位中輸入新聞或部落格文章的網址")

# 讓使用者輸入他們的 OpenAI API 金鑰
api_key = st.text_input("請輸入您的 OpenAI API 金鑰", type="password")
openai.api_key = api_key

# 取得用戶輸入的 URL
URL_ = st.text_input("輸入網址")
button = st.button("摘要")

# 當使用者輸入 URL 且點擊"摘要"按鈕後，開始處理摘要
if URL_ and button and api_key:
    try:
        st.success("正在摘要文章，請稍候...")

        # 從網址獲取頁面內容並解析
        r = requests.get(URL_)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.find_all(['h1', 'p'])
        text = [result.text for result in results]
        ARTICLE = ' '.join(text)

        # 將文章內容分割成一個一個的句子
        ARTICLE = ARTICLE.replace('.', '.<eos>')
        ARTICLE = ARTICLE.replace('?', '?<eos>')
        ARTICLE = ARTICLE.replace('!', '!<eos>')

        # 將文章分割成大小為 max_chunk 的多個塊
        max_chunk = 1000
        sentences = ARTICLE.split('<eos>')
        current_chunk = 0
        chunks = []
        for sentence in sentences:
            if len(chunks) == current_chunk + 1:
                if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                    chunks[current_chunk].extend(sentence.split(' '))
                else:
                    current_chunk += 1
                    chunks.append(sentence.split(' '))
            else:
                chunks.append(sentence.split(' '))

        # 將每一塊轉換成文字
        for chunk_id in range(len(chunks)):
            chunks[chunk_id] = ' '.join(chunks[chunk_id])

        # 對每一塊進行摘要並輸出
        summaries = []
        for chunk in chunks:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"請讀完這篇部落格並使用繁體中文摘要成文章: {chunk}"}
                ],
            )
            summary = response['choices'][0]['message']['content']
            summaries.append(summary)

        text = ' '.join(summaries)
        st.write(text)

    except openai.error.AuthenticationError:
        st.error("您的 OpenAI API 金鑰無效，請檢查並重新輸入。")

# 如果使用者尚未輸入 API 金鑰，則顯示一條提示訊息
if not api_key:
    st.warning("請輸入您的 OpenAI API 金鑰以啟用摘要功能。")
