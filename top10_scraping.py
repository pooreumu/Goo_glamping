from bs4 import BeautifulSoup
from selenium import webdriver
import time
import config
from selenium.webdriver.common.keys import Keys

from pymongo import MongoClient
client = MongoClient(config.Mongo_key)
db = client.dbsparta

driver = webdriver.Chrome('./chromedriver')  # 드라이버를 실행합니다.

url_glamping = "https://pcmap.place.naver.com/accommodation/list?query=%EA%B8%80%EB%9E%A8%ED%95%91&x=126.9783880&y=37.5666100&from=nx&fromNxList=true&businessCategory=accommodation&level=top&entry=pll&ts=1646638133449&mapUrl=https%3A%2F%2Fmap.naver.com%2Fv5%2Fsearch%2F%25EA%25B8%2580%25EB%259E%25A8%25ED%2595%2591%3FplaceSearchOption%3Dfrom%3Dnx%2526fromNxList%3Dtrue%2526businessCategory%3Daccommodation%2526entry%3Dpll%2526level%3Dtop%2526x%3D126.8335106%2526y%3D37.6446876&sortingOrder=reviewCount#"
url_naver = "https://www.naver.com/"

driver.get(url_glamping)  # 드라이버에 해당 url의 웹페이지를 띄웁니다.
time.sleep(5)  # 페이지가 로딩되는 동안 5초 간 기다립니다.

#naver place에서는 스크롤을 내리려면 화면을 한번 클릭해 줘야 한다.
body = driver.find_element_by_css_selector("#_pcmap_list_scroll_container > ul > li:nth-child(1) > div.Yd6yR > div > a:nth-child(2) > span") #클릭할 화면의 위치 지정
body.click() # 화면 클릭
time.sleep(1) # 1초 간 대기

#10개의 글램핑장 정보를 가져오기 위해 스크롤을 내려준다
for c in range(0,4) :
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN) # 키보드에 있는 pgdn자판을 눌렀을때와 같은 효과
    time.sleep(1) # 1초 간 대기

req = driver.page_source  # html 정보를 가져옵니다.



soup = BeautifulSoup(req, 'html.parser')  # 가져온 정보를 beautifulsoup으로 파싱해줍니다.

list = soup.select("#_pcmap_list_scroll_container > ul > li")

for a in list:
    title = a.select_one('div.kqlfc > a > div.YQSTs > div > span').text

    driver.get(url_naver)  # 드라이버에 해당 url의 웹페이지를 띄웁니다.
    time.sleep(2)  # 페이지가 로딩되는 동안 2초 간 기다립니다.
    element = driver.find_element_by_id("query") #검색창의 위치를 지정한다, naver에서는 id값이 query이다
    element.click() #검색창을 클릭해준다.
    element.send_keys(title) #검색창에 title을 입력한다.
    driver.find_element_by_id("search_btn").click() # 검색버튼을 누른다.
    time.sleep(1)  # 1초 간 대기
    req1 = driver.page_source  # html 정보를 가져옵니다.
    soup1 = BeautifulSoup(req1, 'html.parser')  # 가져온 정보를 beautifulsoup으로 파싱해줍니다.
    if title != '글램비 글램핑' :
        homepage = soup1.select_one("#place_main_ct > div > section > div > div.ct_box_area > div.bizinfo_area > div > div:nth-child(4) > div > a")['href']
    else:
        homepage = soup1.select_one("#place_main_ct > div > section > div > div.ct_box_area > div.bizinfo_area > div > div:nth-child(3) > div > a")['href']

    img1 = a.select_one('div.Yd6yR > div > a:nth-child(1) > span > div')['style'].split('url')[1].strip('(");')
    img2 = a.select_one('div.Yd6yR > div > a:nth-child(2) > span > div')['style'].split('url')[1].strip('(");')
    img3 = a.select_one('div.Yd6yR > div > a:nth-child(3) > span > div')['style'].split('url')[1].strip('(");')
    doc = {
        'title': title,
        'img1': img1,
        'img2': img2,
        'img3': img3,
        'homepage': homepage
    }
    db.top10.insert_one(doc)
    print(doc)

driver.quit()