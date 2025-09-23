from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
import time
import json

with open('config.json', 'r') as f:
    config = json.load(f)

id_ = config['user']['id']      # user id
pw_ = config['user']['pw']      # user pw

url = config['video']['class_url']                  # classroom url
chapter = config['video']['chapter']                # Chapter you want to watch
video_limit = config['video']['video_limit']      # number of videos to scan and play

# time(hh:mm:ss) -> seconds
def to_seconds(time_str: str) -> int:
    if len(time_str) > 6:
        h, m, s = map(int, time_str.split(":"))
        return h*3600 + m*60 + s
    else:
        m, s = map(int, time_str.split(":"))
        return m*60 + s

# print videos title, remain time
def print_video_info(title: str, start_time: int, end_time: int, remain_time: int):
    print(f'Playing... [{title}]', end=" ")
    # print(f'{start_time//3600:02d}:{start_time//60:02d}:{start_time%6:02d}', end=" - ")
    # print(f'{end_time//3600:02d}:{end_time//60:02d}:{end_time%6:02d}', end=" ")
    print(f'- {remain_time//3600:02d}:{remain_time//60:02d}:{remain_time%6:02d}')


# Chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # browser window maximize
driver = webdriver.Chrome(options=options)
# for Syncronizing. wait for 10 seconds until driver finish its work
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://www.kmooc.kr/")

    # click login tab
    login_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "로그인")))
    login_link.click()

    # enter email(id)
    email_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/main/div[2]/div/div/form/div/div[1]/input")))
    email_box.click()
    email_box.send_keys(id_)
    email_box.send_keys(Keys.TAB)

    # enter password
    password_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/main/div[2]/div/div/form/div/div[2]/input")))
    password_box.send_keys(pw_)

    # click login button
    login_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/main/div[2]/div/div/form/div/div[4]/button[1]")))
    login_button.click()

    # after login, pop up the alert window. then click accept
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present()).accept()
    except TimeoutException:
        print("Timeout error")
    except NoAlertPresentException:
        print("No alert found")

    # wait for page loading
    wait.until(lambda d: d.execute_script(
        "return document.readyState") == "complete")
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div[3]/header/div[1]/div/div/div[2]/div[1]/a")))  # my classroom

    driver.get(url)

    # create xpath value with chapter value
    print(f'\nChapter : {chapter}')
    xpath = [
        '/html/body/div[3]/div[5]/div[2]/div/div/div/div[2]/div[3]/div/ul/li[',
        ']/div[3]/ul/li[',
        ']/div/div/div[2]/div/a/span'
    ]

    videos = []

    # we don't know how many videos in a chapter, so we try to detect the videos from 1 to the variable that you defined.
    for i in range(5, video_limit+1):
        try:
            video = driver.find_element(
                By.XPATH, xpath[0]+str(chapter)+xpath[1]+str(i)+xpath[2])
        except Exception as e:
            print('Video detecting complete.')
            break
        txt = video.text.split('\n')[0]
        if (txt[:2] == str(chapter)+'.'):
            videos.append(video)  # store video object to listq
            print(f'{txt}')

    print(f'\nTotal number of vidoes : {len(videos)}\n')

    # while iterating the videos list, play videos
    for video in videos:
        video_title = video.text.split('\n')[0]
        main = driver.current_window_handle
        origin_handles = set(driver.window_handles)  # store number of windows
        video.click()

        # wait for new window
        # when new window is open, detect that number of windows increased
        try:
            wait.until(lambda d: len(
                set(d.window_handles) - origin_handles) >= 1)
            new_handle = (set(driver.window_handles) - origin_handles).pop()
            # swtich the focus to the new window
            driver.switch_to.window(new_handle)
        except TimeoutException:
            pass

        alert_shown = False
        current_time = '00:00:00'

        # If you played a video before, the watching history is stored.
        # Then, alert window asks if you want to resume video from the last position.
        try:
            # if the alert is occured, click accept button
            alert = wait.until(EC.alert_is_present())

            # extract the last position form the alert window
            plain_current_time = alert.text
            first_colon = plain_current_time.find(':')
            current_time = plain_current_time[first_colon-2:first_colon+6]

            alert.accept()
            alert_shown = True
        except TimeoutException:
            pass
        except NoAlertPresentException:
            pass

        if alert_shown:
            print("### Resuming video from the last position. ###")
        else:
            print("### Starting video from the beginning. ###")
            try:
                # if you are watching the video for the first time, click the play button
                play_button = driver.find_element(
                    By.CLASS_NAME, 'vjs-big-play-button')
                play_button.click()

            except Exception as e:
                print('Not Found (404) -> play_button')

        # video length
        video_time = wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "vjs-duration-display"))).text
        remain_time = to_seconds(video_time) - to_seconds(current_time)

        print_video_info(video_title, to_seconds(current_time),
                         to_seconds(video_time), remain_time)

        # wait for the remaining time of the video plus an extra 30 seconds
        time.sleep(remain_time+30)

        # close the video window and switch back to the previous window
        driver.close()
        driver.switch_to.window(main)

        # wait for page loading
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[3]/div[5]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/a")))

        print(f'Complete. {video_title}')

finally:
    driver.get(url)
    time.sleep(10)
    driver.quit()
