import pickle
import undetected_chromedriver as uc
if __name__ == '__main__':
    driver = uc.Chrome()
    driver.get("https://www.tiktok.com/upload")
    get = input("Press Enter after you have logged in")
    cookie_store = driver.get_cookies()
    f = open("tiktok_cookie.cookie", "wb+")
    pickle.dump(cookie_store, f)
    f.close()
    driver.delete_all_cookies()
    print("Tiktok cookie: Done")

    driver.get("https://www.reddit.com/")
    get = input("Press Enter after you have logged in")
    cookie_store = driver.get_cookies()
    f = open("reddit_cookie.cookie", "wb+")
    pickle.dump(cookie_store, f)
    f.close()
    print("Reddit cookie: Done")