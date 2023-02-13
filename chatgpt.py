import re
import requests
import zipfile
import openai
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

OPENAI_API_KEY="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"
client_id = '6b1a6f71fcf20d399f4d56fbbc0424de' #'자신의 App ID'
client_secret = '6b1a6f71fcf20d399f4d56fbbc0424defb94e6b627600a1c52770f27e3908c0f3f33a6fd' #'자신의 Secret Key'
access_token = '6a3d87f49d00e5312e3b79b792bc7882_8d9164f3c4488b6da4904fbd9dcd1926' #'발급 받은 access token'
code = '4ba9962439178f839c68efacd8657d2f7ca01f23e653855829806fbd72466b7e04145274' #'발급 받은 가장 최신의 Authentication Code'
redirect_uri = 'https://richrobo.tistory.com/' #'자신의 블로그 주소'
blogName = 'richrobo' #'블로그 이름 (https://XXX.tistory.com 에서 XXX의 값)'
tags = ''
output = 'json'						#고정값
grant_type = 'authorization_code'   #고정값 
visibility = 3  #0은 비공개, 3은 공개 발행
category =  0

# def getToken():
#     url = 'https://www.tistory.com/oauth/access_token?'
#     data = {
#             'client_id': client_id,
#             'client_secret': client_secret,
#             'redirect_uri': redirect_uri,
#             'code': code,
#             'grant_type': grant_type
#             }
#     r = requests.get(url, data)
#     global access_token
#     access_token = r.text
#     print(access_token)
    
def postWrite(title, content):
        title = '[주식용어] ' + title
        url = 'https://www.tistory.com/apis/post/write?'
        data = {
                 'access_token': access_token,
                 'output': output,
                 'blogName': blogName,
                 'title': title,
                 'content': content,
                 'visibility': visibility,
                 'category': category,
                 'tag': tags,
                 }
        r = requests.post(url, data=data)
        print('자동 포스팅 성공')
        return r.text

def generate_text(prompt):
    # 모델 엔진 선택
    model_engine = "text-davinci-003"

    # 맥스 토큰
    max_tokens = 3500

    # 블로그 생성
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.3,      # creativity
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return completion

def extract_tags(body):
    hashtag_pattern = r'(#+[a-zA-Z0-9(_)]{1,})'
    hashtags = [w[1:] for w in re.findall(hashtag_pattern, body)]
    hashtags = list(set(hashtags))
    tag_string = ""
    for w in hashtags:
        # 3글자 이상 추출
        if len(w) > 3:
            tag_string += f'{w}, '
    tag_string = re.sub(r'[^a-zA-Z, ]', '', tag_string)
    tag_string = str(tag_string.strip()[:-1])[1:-1]
    return tag_string

def get_file(filename):
    with open(filename, 'r') as f:
        data = f.read()
    return data

def make_prompt(prompt, topic='<<TOPIC>>', category='<<CATEGORY>>'):
    if topic:
        prompt = prompt.replace('<<TOPIC>>', topic)
    if category:
        prompt = prompt.replace('<<CATEGORY>>', category)
    return prompt



prompt_example = f'''Write blog posts in markdown format.
Write the theme of your blog as what is "<<TOPIC>>" and its category is "<<CATEGORY>>".
Highlight, bold, or italicize important words or sentences.
Please include the company's address, stock recommendations and other helpful information(opening and closing hours) as a list style.
Please make the entire blog less than 10 minutes long.
The audience of this article is 20-40 years old.
Create several hashtags and add them only at the end of the line.
Add a summary of the entire article at the beginning of the blog post.
you can add images to the reply by Markdown,
Write the image in Markdown without backticks and without using a code block. 
Use the Unsplash API ([https://source.unsplash.com/1600x900/?)](https://source.unsplash.com/1600x900/?)).
the query is just some tags that describes the image] ## DO NOT RESPOND TO INFO BLOCK ##
Next prompt is give me a picture for blog cover fits to this article.'''

with st.sidebar:
    st.markdown('''
**API KEY 발급 방법**
1. https://beta.openai.com/ 회원가입
2. https://beta.openai.com/account/api-keys 접속
3. `create new secret key` 클릭 후 생성된 KEY 복사
    ''')
    value=''
    apikey = st.text_input(label='OPENAI API 키', placeholder='OPENAI API키를 입력해 주세요', value=value)

    if apikey:
        st.markdown(f'OPENAI API KEY: `{apikey}`')

    st.markdown('---')

# Preset Container
preset_container = st.container()
preset_container.subheader('1. 설정')
tab_single, tab_multiple = preset_container.tabs(['1개 생성', '여러개 생성'])

col1, co12 =  tab_single.columns(2)

topic = col1.text_input(label='주제 입력', placeholder='주제를 입력해 주세요')
col1.markdown('(예시)')
col1.markdown('`Top 10 Restaurants you must visit when traveling to New York`')

category = co12.text_input(label='카테고리 입력', placeholder='카테고리를 입력해 주세요')
co12.markdown('(예시)')
co12.markdown('`Travel`')

def generate_blog(apikey, topic, category, prompt):
    # apikey 셋팅
    openai.api_key = apikey
    # prompt 생성
    prompt_output = make_prompt(prompt=prompt, topic=topic, category=category)
    # 글 생성
    response = generate_text(prompt_output)

    body = response.choices[0].text
    # 태그 생성
    global tags
    tags = extract_tags(body)

    intro = f"<h3 data-ke-size='size16'>Hello, this is Rich Robo. Today, we will learn about {topic} among {category}. Subscriptions and likes help Rich Robo!</h3>"
    # 첫 줄은 타이틀(제목)과 겹치기 때문에 제거하도록 합니다.
    body = '\n'.join(response['choices'][0]['text'].strip().split('\n')[1:])
    bodyarr = body.split('\n')
    for i in range(len(bodyarr)):
        if bodyarr[i].split(' ')[0] == '##':
            bodyarr[i] = ' '.join(bodyarr[i].split(' ')[1:])
            bodyarr[i] = f'<h2 data-ke-size="size16">{bodyarr[i]}</h2>'
        # elif bodyarr[i].split(' ')[0] == '*' or '-':
        #     bodyarr[i] = ' '.join(bodyarr[i].split(' ')[1:])
        #     bodyarr[i] = f'<li data-ke-size="size16">{bodyarr[i]}</li>'
        else:
            bodyarr[i] = f'<p data-ke-size="size16">{bodyarr[i]}</p>'
    body = '\n'.join(bodyarr)
    postWrite(topic, intro+body)


    

with tab_single:
    # Prompt Container
    prompt_container = st.container()
    prompt_container.subheader('2. 세부지침')
    prompt_container.markdown('[tip 1] **세부지침**은 [구글 번역기](https://translate.google.com/)로 돌려서 **영어로** 입력해 주세요')
    prompt_container.markdown('[tip 2] `<<TOPIC>>`은 입력한 주제로 `<<CATEGORY>>`는 입력한 카테고리로 **치환**됩니다.')
    prompt_container.markdown('(예시)')
    prompt_container.markdown(f'''
    ```
    {prompt_example}''')

    prompt = prompt_container.text_area(label='세부지침 입력', 
                                        placeholder='지침을 입력해 주세요',  
                                        key='prompt1',
                                        height=250)

    # 미리보기 출력
    if prompt:
        prompt_output = make_prompt(prompt=prompt, topic=topic, category=category)

        prompt_container.markdown(f'```{prompt_output}')

    # 블로그 생성
    if apikey and topic and category and prompt:
        button = prompt_container.button('생성하기')

        if button:
            generate_blog(apikey=apikey, topic=topic, category=category, prompt=prompt)
            check_btn = prompt_container.button('완료')

with tab_multiple:
    file_upload = st.file_uploader("파일 선택(csv)", type=['csv'])
    if file_upload:
        df = pd.read_csv(file_upload)
        df['topic'] = df.apply(lambda x: x['topic'].replace('<<KEYWORD>>', x['keyword']), axis=1)
        st.dataframe(df)

        # Prompt Container
        prompt_container2 = st.container()
        prompt_container2.subheader('2. 세부지침')
        prompt_container2.markdown('[tip 1] **세부지침**은 [구글 번역기](https://translate.google.com/)로 돌려서 **영어로** 입력해 주세요')
        prompt_container2.markdown('[tip 2] `<<TOPIC>>`은 입력한 주제로 `<<CATEGORY>>`는 입력한 카테고리로 **치환**됩니다.')
        prompt_container2.markdown('(예시)')
        prompt_container2.markdown(f'''
        ```
        {prompt_example}''')

        prompt2 = prompt_container2.text_area(label='세부지침 입력', 
                                              placeholder='지침을 입력해 주세요',  
                                              key='prompt2',
                                              height=250)

        total = len(df)
        button2 = prompt_container2.button(f'{total}개 파일 생성하기')

        if button2:
            generate_progress = st.progress(0)            
            st.write(f"[알림] 총{total} 개의 블로그를 생성합니다!")

            for i, row in df.iterrows():
                generate_blog(apikey=apikey, topic=row['topic'], category=row['category'], prompt=prompt2)
                st.write(f"[완료] {row['topic']}")
                generate_progress.progress((i + 1) / total)
            check_btn = prompt_container2.button('완료')
            