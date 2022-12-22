import pickle
import random
import time
from random import randint as rd
import requests
import undetected_chromedriver as uc
from PIL import Image, ImageEnhance
from deep_translator import GoogleTranslator
from fake_useragent import UserAgent
from gtts import gTTS
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

length = 0

body_split = []
comments = []
comments_link = []
comments_length = []
comments_chosen = []
comment_amount = 0

title_length = 0
body_length = 0
body_con_length = []

audios = []
images = []
post_link = ""
post_title = ""
body_count = 0
sub_reddit = ['AskReddit', 'tifu', 'relationships', 'relationship_advice', 'AmItheAsshole', 'confessions', 'confession',
              'legaladvice']
voice = ["banmai", "thuminh", "myan", "giahuy", "ngoclam", "leminh", "minhquang", "linhsan", "lannhi"]
effects = [['left', 'right'], ['right', 'left'], ['top', 'bottom'], ['bottom', 'top']]
# mildlyinteresting
comment_count = 0



def Translate(text):
    try:
        result = GoogleTranslator(source='auto', target='vi').translate(text)
    except:
        result = text
    return result


def Resize(name, w, h):
    image = Image.open(f"{name}.png")
    w_im, h_im = image.size
    print(name, w_im, w)
    if w_im > w:
        w_im = w - 30
        h_im = int((h_im * (w - 30)) / w)
        new_image = image.resize((w_im, h_im))
        new_image.save(f'{name}.png')


def Enhance(image):
    try:
        im = Image.open(image)
        im_out = ImageEnhance.Sharpness(im).enhance(2)
        im_out.save(image)
    except:
        pass


def Screenshot(driver, element, name, check):
    time.sleep(2)
    if check:
        ele = driver.find_element(by="xpath",
                                  value="/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[5]/div/div/div/div[1]/div/div/div/div[2]")
        driver.execute_script("arguments[0].scrollIntoView(true);", ele)
    time.sleep(1)
    element.screenshot(f"{name}.png")


def Download_mp3(choice, text, name, voice_id, speed):
    global audio_time

    if not choice:
        ## ENGLISH
        tts = gTTS(text)
        tts.save(f"{name}.mp3")
    else:
        ## VIETNAMESE
        # voice: banmai, thuminh, myan, giahuy, ngoclam, leminh, minhquang, linhsan, lannhi
        # speed: -3 -> 3
        payload = Translate(text)
        url = 'https://api.fpt.ai/hmi/tts/v5'
        headers = {
            'api-key': FPT_API,
            'speed': speed,
            'voice': voice[voice_id]
        }
        response = requests.request('POST', url, data=payload.encode('utf-8'), headers=headers)
        error = response.json()['error']
        if not error:
            link = response.json()['async']
            t = requests.get(link)
            while not t:
                time.sleep(1)
                t = requests.get(link)
            with open(f"{name}.mp3", 'wb') as f:
                f.write(t.content)
        else:
            f = open(f"{name}.mp3", 'wb')
            f.close()
    try:
        audio = MP3(f"{name}.mp3")
        duration = audio.info.length
        print(name, duration)
        return duration
    except:
        return 0


def Make_video(choice, voice_id, speed):
    global title_length, body_length, length, post_link, comment_amount, body_count, body_split, post_title
    comments.clear()
    comments_link.clear()
    comments_chosen.clear()
    comments_length.clear()
    body_con_length.clear()
    body_split.clear()
    audios.clear()
    images.clear()
    length = 0


    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
    data = {'grant_type': 'password',
            'username': USERNAME,
            'password': PASSWORD}
    headers = {'User-Agent': 'MyBot/0.0.1'}
    res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    TOKEN = res.json()['access_token']
    headers['Authorization'] = f"bearer {TOKEN}"
    ## Random subreddit

    sr = sub_reddit[0]
    posts = requests.get(f"https://oauth.reddit.com/r/{sr}/hot", headers=headers)
    id = rd(1, len(posts.json()['data']['children']) - 1)
    post_link = "https://www.reddit.com" + posts.json()['data']['children'][id]['data']['permalink']
    post_title = posts.json()['data']['children'][id]['data']['title']
    post_id = posts.json()['data']['children'][id]['data']['id']
    print(post_link)

    ## Tải mp3 cho title
    sec = Download_mp3(choice, post_title, "title", voice_id, speed)
    title_length = sec
    length += sec
    length += 1

    ## Tải mp3 cho comments
    count = 0
    get_comment = requests.get(f"https://oauth.reddit.com/r/{sr}/comments/{post_id}", headers=headers)
    for comment in get_comment.json()[1]['data']['children']:
        if "automatic comment" not in comment['data']['body'] and "Tag Notice" not in comment['data']['body'] and "[removed]" not in comment['data']['body']:
            count += 1
            tmp = Download_mp3(choice, comment['data']['body'], f"comment_{count}", voice_id, speed)
            if not tmp:
                count -= 1
                continue
            comments_length.append(tmp)
            comments.append(comment['data']['body'])
            comments_link.append("https://www.reddit.com" + comment['data']['permalink'])
            print(count, comment['data']['body'])
            if count > 20:
                break
    comment_amount = count
    ## Chọn comment
    count = 0
    dem = 0
    for comment_length in comments_length:
        count += 1
        if comment_length + length <= 90:
            length += comment_length
            length += 0.2
            dem += 1
            print(count, length)
            comments_chosen.append(count)
    length -= 1
    comment_count = dem
    for id in range(comment_count):
        if id + 1 not in comments_chosen:
            if os.path.exists(f"comment_{id + 1}.mp3"):
                os.remove(f"comment_{id + 1}.mp3")

    ## Screenshot
    # Khởi tạo chrome
    option = Options()
    option.add_argument('--disable-notifications')
    # option.add_argument('--headless')
    option.add_argument('window-size=500,1440')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=option)
    driver.delete_all_cookies()
    cookie_data = pickle.load(open("reddit_cookie.cookie", "rb"))
    driver.get("https://www.reddit.com/login/")
    for cookie in cookie_data:
        driver.add_cookie(cookie)
    time.sleep(3)
    driver.get("https://www.reddit.com/")
    reddit_cookie = driver.get_cookies()
    f = open("reddit_cookie.cookie", "wb+")
    pickle.dump(reddit_cookie, f)
    f.close()
    time.sleep(2)
    driver.get(post_link)
    time.sleep(2)

    # Tắt thanh taskbar
    hidden = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div[1]/header")
    driver.execute_script("arguments[0].style.visibility='hidden'", hidden)

    # Screenshot title
    tmp = driver.find_element(By.XPATH,
                              "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[1]/div/div[3]/div[1]/div/h1")
    if choice:
        driver.execute_script("arguments[0].innerText = arguments[1]", tmp, Translate(post_title))
    screenshot_title = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[1]/div")
    time.sleep(1)
    screenshot_title.screenshot("title.png")
    Enhance("title.png")

    # Screenshot comments
    count = 0
    for id in comments_chosen:
        count += 1
        driver.get(comments_link[id - 1])
        time.sleep(3)
        try:
            comment = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[5]/div/div/div/div[1]/div/div/div/div[2]")
        except:
            comment = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[6]/div/div/div/div[1]/div/div/div/div[2]")
        tmp = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[3]/div")
        driver.execute_script("arguments[0].scrollIntoView(true);", tmp)
        time.sleep(1)
        if choice:
            try:
                ele = driver.find_element(By.XPATH,
                                          '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[5]/div/div/div/div[1]/div/div/div/div[2]/div[3]/div[2]/div/p')
            except:
                ele = driver.find_element(By.XPATH,
                                          '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[5]/div/div/div/div[1]/div/div/div/div[2]/div[4]/div[2]/div/p')
            driver.execute_script("arguments[0].innerText = arguments[1]", ele, Translate(comments[id - 1]))
            comment_papa = driver.find_element(By.XPATH,
                                               "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[3]/div[5]/div/div/div/div/div/div/div/div[2]/div[3]/div[2]/div")
            num = driver.execute_script("return arguments[0].childElementCount", comment_papa)
            num -= 1
            script = """
            var last = arguments[0].lastElementChild;
            var num = arguments[1];
            while (num--) {
                last.remove();
                last = arguments[0].lastElementChild;}
            """
            driver.execute_script(script, comment_papa, num)

        time.sleep(1)

        comment.screenshot(f"comment_{id}.png")
        Enhance(f"comment_{id}.png")
    driver.close()
    Render()


def Render():
    # random một đoạn video background bất kì
    audio = MP4("video.mp4")
    video_length = audio.info.length
    video_start = rd(0, int(video_length - length))
    video_end = video_start + length

    # Cắt video theo độ dài đã có và chỉnh lại size
    video = VideoFileClip("video.mp4").subclip(video_start, video_end)
    w, h = video.size
    video = vfx.crop(video, width=(h / 16) * 9, height=h, x_center=w / 2, y_center=h / 2)
    w, h = video.size
    effect_duration = 0.2

    # Chèn png vào video
    tmp = 0
    Resize("title", w, h)
    images.append(ImageClip("title.png").set_duration(title_length))
    tmp += title_length
    max_height = 0
    max_id = 1

    for id in comments_chosen:
        Resize(f"comment_{id}", w, h)
        image = ImageClip(f"comment_{id}.png").set_duration(comments_length[id - 1])
        images.append(image)
        tmp += comments_length[id - 1]

    for id, image in enumerate(images):
        if id != 0:
            if max_height < image.size[1]:
                max_height, max_id = image.size[1], id
            images[id] = image.set_duration(comments_length[comments_chosen[id - 1] - 1])

    images[max_id], images[1] = images[1], images[max_id]
    comments_length[comments_chosen[0] - 1], comments_length[comments_chosen[max_id - 1] - 1] = comments_length[comments_chosen[max_id - 1] - 1], comments_length[comments_chosen[0] - 1]
    tmp -= comments_length[comments_chosen[-1] - 1]

    # Chèn effect
    in_effect, out_effect = effects[random.randint(0, 3)]
    first_clip = CompositeVideoClip(
        [images[0].fx(transfx.slide_out, duration=effect_duration, side=out_effect)]).set_start(0).set_position(
        "center")
    last_clip = CompositeVideoClip(
        [images[-1].fx(transfx.slide_in, duration=effect_duration, side=in_effect)]).set_start(tmp).set_position(
        "center")

    clips = []
    tmp = title_length
    for id, clip in enumerate(images[1:-1], start=1):
        in_effect, out_effect = effects[random.randint(0, 3)]
        clips.append(CompositeVideoClip(
            [clip.fx(transfx.slide_in, duration=effect_duration, side=in_effect)])
                     .set_start(tmp)
                     .fx(transfx.slide_out, duration=effect_duration, side=out_effect)
                     )
        tmp += comments_length[comments_chosen[id - 1] - 1]

    # first_clip = CompositeVideoClip([images[0].fx(transfx.crossfadeout, duration=effect_duration)]).set_start(
    #     0).set_position("center")
    # last_clip = CompositeVideoClip([images[-1].fx(transfx.crossfadein, duration=effect_duration)]).set_start(
    #     tmp).set_position("center")
    # clips = []
    # tmp = title_length
    # for id, clip in enumerate(images[1:-1], start=1):
    #     in_effect, out_effect = effects[random.randint(0, 3)]
    #     clips.append(CompositeVideoClip(
    #         [clip.fx(transfx.crossfadein, duration=effect_duration)])
    #                  .set_start((tmp))
    #                  .fx(transfx.crossfadeout, duration=effect_duration)
    #                  )
    #     tmp += comments_length[comments_chosen[id - 1] - 1]

    middle_clip = CompositeVideoClip(clips).set_position("center")

    clip = (
            [first_clip] + [middle_clip] + [last_clip]
    )

    # Chèn mp3 vào video
    tmp = 0
    audios.append((AudioFileClip("title.mp3").set_start(tmp)))
    tmp += title_length

    for id in comments_chosen:
        audios.append((AudioFileClip(f"comment_{id}.mp3")))
    audios[max_id], audios[1] = audios[1], audios[max_id]

    for i, audio in enumerate(audios):
        if i != 0:
            audios[i] = audio.set_start(tmp)
            tmp += comments_length[comments_chosen[i - 1] - 1]

    new_audio = CompositeAudioClip(audios)
    video.audio = new_audio

    final = CompositeVideoClip([video] + clip)
    final.write_videofile("final.mp4", codec="libx264", audio_codec="aac", preset="ultrafast", fps=60, threads=24,
                          ffmpeg_params=["-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-pix_fmt", "yuv420p"], )


def Delete():
    audios.clear()
    if os.path.exists("title.mp3"):
        os.remove("title.mp3")
    if os.path.exists("title.png"):
        os.remove("title.png")
    for i in range(1, body_count + 1):
        if os.path.exists(f"body_{i}.mp3"):
            os.remove(f"body_{i}.mp3")
        if os.path.exists(f"body_{i}.png"):
            os.remove(f"body_{i}.png")

    for i in range(1, comment_amount + 1):
        if os.path.exists(f"comment_{i}.mp3"):
            os.remove(f"comment_{i}.mp3")
        if os.path.exists(f"comment_{i}.png"):
            os.remove(f"comment_{i}.png")
    if os.path.exists("final.mp4"):
        os.remove("final.mp4")


def Post_video(choice):
    # ua = UserAgent()
    # user_agent = ua.random
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument("--user-agent=" + user_agent)
    driver = uc.Chrome(options=options)
    driver.delete_all_cookies()
    cookie_data = pickle.load(open("tiktok_cookie.cookie", "rb"))
    driver.get("https://www.tiktok.com/upload")
    for cookie in cookie_data:
        if 'sameSite' in cookie:
            if cookie['sameSite'] == 'None':
                cookie['sameSite'] = 'Strict'
        driver.add_cookie(cookie)
    time.sleep(3)
    driver.get("https://www.tiktok.com/upload")
    cookie_store = driver.get_cookies()
    f = open("tiktok_cookie.cookie", "wb+")
    pickle.dump(cookie_store, f)
    f.close()
    time.sleep(2)
    driver.switch_to.frame(driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div/iframe"))
    time.sleep(2)
    t = driver.find_elements(By.CLASS_NAME, "jsx-2404389384")[1]
    t.send_keys(os.path.join(os.getcwd(), "final.mp4"))
    time.sleep(2)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div[1]/div[2]")))
    Caption = driver.find_element(By.XPATH,
                                  "/html/body/div[1]/div/div/div/div/div[2]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div")
    time.sleep(2)
    Caption.send_keys(Keys.CONTROL + 'a')
    time.sleep(2)
    Caption.send_keys(Keys.DELETE)
    time.sleep(1)
    if not choice:
        Caption.send_keys(
            f"{post_title} #reddit #redditstories #redditreadings #reddit_tiktok #redditstorytime #redditstoriestts")
    else:
        Caption.send_keys(
            f"{Translate(post_title)} #reddit #redditstories #redditreadings #reddit_tiktok #redditstorytime #redditstoriestts")
    time.sleep(5)
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div[2]/div[8]/div[2]/button").click()
    time.sleep(10)


def Run(choice, voice_id=0, speed=''):
    Begin = time.time()
    Make_video(choice, voice_id, speed)
    Post_video(choice)
    Delete()
    End = time.time()
    print("Time:", End - Begin)


if __name__ == '__main__':
    FPT_API = ""
    USERNAME = ""
    PASSWORD = ""
    CLIENT_ID = ""
    SECRET_KEY = ""
    Run(0, voice_id=0, speed='')

    ## REQUIREMENTS
    # Reddit API registration: Client_ID, Secret_key
    # FPT API registration: FPT API key https://fpt.ai/tts
    # Replace your Client ID, Secret key, reddit username, reddit password, FPT API key
    # Download any video for background and name it video.mp4 (Example video: https://www.youtube.com/watch?v=n_Dv4JMiwK8&t=2117s)
    # Run get_cookie.py and login tiktok and reddit to get cookie
    # Run chrome.py to get the latest chromedriver
    # Run main.py

    ## Run(Language, voice_id, voice_speed)
    # Language: 0 = English, 1 = Vietnamese
    # voice_id (only for Vietnamese): 0 = banmai, 1 = thuminh, 2 = myan, 3 = giahuy, 4 = ngoclam, 5 = leminh, 6 = minhquang, 7 = linhsan, 8 = lannhi
    # voice_speed (only for Vietnamese): -3 -> 3
