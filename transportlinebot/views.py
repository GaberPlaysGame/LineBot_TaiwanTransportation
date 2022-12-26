from bs4 import BeautifulSoup

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage

from .fsm import FSMModel 
from .db import MRT_Route_DB

import requests

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

base_url = "https://" + settings.ALLOWED_HOSTS[0]

machine = FSMModel(
    states=['default', 'Taipei', 'Taichung', 'Tainan', 'Kaoshiung'],
    transitions=[
        {'trigger': 'state_MRT_Taipei', 'source': ['default', 'Taichung', 'Tainan', 'Kaoshiung'], 'dest': 'Taipei', 'conditions': 'state_MRT_Taipei'},
        {'trigger': 'state_MRT_Taichung', 'source': ['Taipei', 'default', 'Tainan', 'Kaoshiung'], 'dest': 'Taichung', 'conditions': 'state_MRT_Taichung'},
        {'trigger': 'state_MRT_Tainan', 'source': ['Taipei', 'Taichung', 'default', 'Kaoshiung'], 'dest': 'Tainan', 'conditions': 'state_MRT_Tainan'},
        {'trigger': 'state_MRT_Kaoshiung', 'source': ['Taipei', 'Taichung', 'Tainan', 'default'], 'dest': 'Kaoshiung', 'conditions': 'state_MRT_Kaohsiung'},
        {'trigger': 'state_default', 'source': ['Taipei', 'Taichung', 'Tainan', 'Kaoshiung'], 'dest': 'default', 'conditions': 'state_default'},
    ],
    initial='default', 
    show_conditions=True, 
    use_pygraphviz=False,
)

mrt_db = MRT_Route_DB()

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):     # 如果有訊息事件
                text = event.message.text
                FSM_command = ['fsm', 'finite state machine']
                line_lists_newtaipei = [
                    '環狀線', '北環段', '南環段', '環狀線北環段', '環狀線南環段', '環狀線南北環', '環狀線南北環段',
                    '萬大樹林線', '萬大中和樹林線', '萬大線', '樹林線',
                    '三鶯線',
                    '安坑輕軌', 
                    '淡海輕軌', '八里輕軌',
                    '深坑輕軌',
                    '五股泰山輕軌', '五泰輕軌',
                    '泰山板橋輕軌', '泰板輕軌',
                    '民生汐止線', '汐東捷運','汐東線',
                ]
                line_lists_keelung = [
                    '汐東線', '汐東捷運', '基隆捷運', '基捷',
                ]
                line_lists_taoyuan = [
                    '桃園捷運綠線', '綠線',
                    '桃園捷運機場線', '機場線', '機捷', '機場捷運',
                    '桃園捷運棕線', '棕線',
                ]
                line_lists_taichung = [
                    '綠線', '彰化延伸段', '大坑延伸段',
                    '藍線',
                    '橘線', '機場線',
                    '大平霧線',
                ]
                line_lists_tainan = [
                    '綠線',
                    '藍線',
                    '深綠線',
                ]
                line_lists_kaohsiung = [
                    '紅線', '岡山延伸線', '岡山路竹延伸線', '林園延伸線',
                    '橘線',
                    '環狀輕軌', '大順路', '高雄輕軌', '輕軌',
                    '紫線', '燕巢學園線', '青線', 
                    '黃線', '高雄捷運黃線', '捷運黃線', 
                    '旗津線', 
                ]
                if text.lower() in FSM_command:
                    CreateFSM()
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(original_content_url= base_url + "/static/" + machine.fsm_filename,
                                         preview_image_url= base_url + "/static/" + machine.fsm_filename))
                elif text == '返回':
                    machine.state_default(event)
                    print(machine.state)
                    test_msg = "已返回到主頁。\n您可以透過選擇下方圖文選單來點擊您想要查詢的區域，再透過輸入路線資訊來查詢相關工程新聞。"
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=test_msg)    
                    )
                elif text == '捷運 台北都會區':
                    machine.state_MRT_Taipei(event)
                    print(machine.state)
                    route = [
                        '● (BR) 文湖線',
                        '● (R) 淡水信義線',
                        '● (G) 松山新店線',
                        '● (O) 中和新蘆線',
                        '● (BL) 板南線',
                        '● (Y) 環狀線',
                        '● (LG) 萬大線', 
                        '● (SB) 民生汐止線/汐東捷運',
                        '● (LB) 三鶯線', 
                        '● (K) 安坑輕軌',
                        '● (V) 淡海輕軌',
                        '● (V) 八里輕軌',
                        '● (S) 深坑輕軌',
                        '● (F) 五股泰山輕軌',
                        '● (F) 泰山板橋輕軌',
                        '● (G) 綠線',
                        '● (BR) 棕線',
                        '● (A) 機捷',
                        '● (KL) 基隆捷運',
                    ]
                    test_msg = '請輸入你想查詢的路線建設資訊，若要了解路線，請在名稱後方加上"簡介" (目前僅支援台北捷運路線)，並以空白分隔\n'
                    counter = 0
                    for i in route:
                        counter += 1
                        test_msg = test_msg + i
                        if counter != len(route):
                            test_msg += '\n'
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=test_msg)    
                    )
                elif text == '捷運 台中都會區':
                    machine.state_MRT_Taichung(event)
                    print(machine.state)
                    route = [
                        '● (1) 綠線',
                        '● (2) 藍線',
                        '● (3) 橘線',
                        '● (4) 大平霧線',
                    ]
                    test_msg = '請輸入你想查詢的路線建設資訊\n'
                    counter = 0
                    for i in route:
                        counter += 1
                        test_msg = test_msg + i
                        if counter != len(route):
                            test_msg += '\n'
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=test_msg)    
                    )
                elif text == '捷運 台南都會區':
                    machine.state_MRT_Tainan(event)
                    print(machine.state)
                    route = [
                        '● (G) 綠線',
                        '● (B) 藍線',
                        '● (DG) 深綠線',
                    ]
                    test_msg = '請輸入你想查詢的路線建設資訊\n'
                    counter = 0
                    for i in route:
                        counter += 1
                        test_msg = test_msg + i
                        if counter != len(route):
                            test_msg += '\n'
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=test_msg)    
                    )
                elif text == '捷運 高屏都會區':
                    machine.state_MRT_Kaoshiung(event)
                    print(machine.state)
                    route = [
                        '● (R) 紅線',
                        '● (O) 橘線',
                        '● (Y) 黃線',
                        '● (P) 紫線',
                        '● (C) 輕軌',
                    ]
                    test_msg = '請輸入你想查詢的路線建設資訊\n'
                    counter = 0
                    for i in route:
                        counter += 1
                        test_msg = test_msg + i
                        if counter != len(route):
                            test_msg += '\n'
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=test_msg)    
                    )   
                elif machine.state == 'Taipei':
                    return_msg = ""
                    intro = False
                    if "簡介" in text:
                        text = text.removesuffix('簡介')
                        text = text.strip()
                        intro = True
                    if intro:
                        info = mrt_db.search(mode=0, text=text)
                        if info != None:
                            line_bot_api.push_message(
                                event.source.user_id,
                                ImageSendMessage(original_content_url= base_url + "/static/" + info['image_route'],
                                                preview_image_url= base_url + "/static/" + info['image_route'])
                            )
                            return_msg = info['description']
                        info = mrt_db.search(mode=1, text=text)
                        if info != None and mrt_db.search(mode=0, text=info['chi_name']) == None:
                            line_bot_api.push_message(
                                event.source.user_id,
                                ImageSendMessage(original_content_url= base_url + "/static/" + info['image_route'],
                                                preview_image_url= base_url + "/static/" + info['image_route'])
                            )
                            return_msg = info['description']
                    else:
                        info = mrt_db.search(mode=0, text=text)
                        if info != None:
                            page = 1
                            response_page = "https://www.dorts.gov.taipei/News.aspx?n=41977EB83537C82B&sms=72544237BBE4C5F6&page=" + str(page) + "&PageSize=20" 
                            response = requests.get(response_page)
                            soup = BeautifulSoup(response.text, "html.parser")
                            titles = soup.find_all("a", href=True, title=True)
                            for title in titles:
                                for i in info['search_name']:
                                    if ("News_Content.aspx?" in title['href'] and i in title['title']):
                                        return_msg += f"https://www.dorts.gov.taipei/{title['href']}\n{title['title']}\n"
                                        break
                            
                        info = mrt_db.search(mode=1, text=text)
                        if info != None:
                            response_page = "https://www.dorts.ntpc.gov.tw/news" 
                            response = requests.get(response_page)
                            soup = BeautifulSoup(response.text, "html.parser")
                            titles = soup.find_all("a",{"class": "d-block text-black text-decoration-none"})
                            for title in titles:
                                for i in info['search_name']:
                                    title_text = title.select_one("span").getText()
                                    if (text in title_text):
                                        try:
                                            return_msg += f"https://www.dorts.ntpc.gov.tw{title['href']}\n{title_text}\n"
                                        except KeyError:
                                            pass

                        if text in line_lists_keelung:
                            response_page = "https://www.rb.gov.tw/news_list.php?lmenuid=11&smenuid=49" 
                            response = requests.get(response_page)
                            soup = BeautifulSoup(response.text, "html.parser")
                            titles = soup.find_all("a", href=True, title=True)
                            for title in titles:
                                if (text in title['title']):
                                    return_msg += f"https://www.rb.gov.tw/{title['href']}\n{title['title']}\n"

                        if text in line_lists_taoyuan:
                            response_page = "https://dorts.tycg.gov.tw/announcement/breaking-news" 
                            response = requests.get(response_page)
                            soup = BeautifulSoup(response.text, "html.parser")
                            a_s = soup.find_all("a", href=True)
                            for a in a_s:
                                title_text = ""
                                if ("detail-news?" in a['href']):
                                    children = a.findChildren("div", {"class": "col-md-8 text-left"})
                                    title_text = children[0].getText()
                                if (text in title_text):
                                    try:
                                        return_msg += f"https://dorts.tycg.gov.tw{a['href']}\n{title_text}\n"
                                    except KeyError:
                                        pass
                            
                    if return_msg == "":
                        return_msg = "很抱歉，最近沒有任何關於此搜尋結果的新消息。建議您更改搜尋關鍵詞。"
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=return_msg)    # 回復傳入的訊息文字
                    )
                elif machine.state == 'Taichung':
                    return_msg = ""
                    if text in line_lists_taichung:
                        for i in range(1, 6):
                            page = i
                            response_page = "https://www.taichung.gov.tw/8868/8872/9962/Lpsimplelist?Page=" + str(page) + "&PageSize=30&type=" 
                            response = requests.get(response_page)
                            soup = BeautifulSoup(response.text, "html.parser")
                            titles = soup.find_all("a", href=True, title=True)
                            for title in titles:
                                if ("post" in title['href'] and text in title['title']):
                                    return_msg += f"https://www.taichung.gov.tw{title['href']}\n{title['title']}\n"
                    if return_msg == "":
                        return_msg = "很抱歉，最近沒有任何關於此搜尋結果的新消息。建議您更改搜尋關鍵詞。"
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=return_msg)    # 回復傳入的訊息文字
                    )
                elif machine.state == 'Tainan':
                    return_msg = ""
                    if text in line_lists_tainan:
                        response_page = "https://traffic-tsb.tainan.gov.tw/RTO/Announcement/C010001" 
                        try:
                            response = requests.get(response_page)
                            soup = BeautifulSoup(response.text, "html.parser")
                            titles = soup.find_all("a",{"class": "txt-link"})
                            for title in titles:
                                title_text = title.getText()
                                if (text in title_text):
                                    try:
                                        return_msg += f"https://traffic-tsb.tainan.gov.tw{title['href']}\n{title_text}\n"
                                    except KeyError:
                                        pass
                        except requests.exceptions.SSLError:
                            return_msg += "很抱歉，您存取的搜尋網站目前無法存取地區憑證，但你仍可以試圖訪問該網站：" + response_page
                    if return_msg == "":
                        return_msg = "很抱歉，最近沒有任何關於此搜尋結果的新消息。建議您更改搜尋關鍵詞。"
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=return_msg)    # 回復傳入的訊息文字
                    )
                elif machine.state == 'Kaohsiung':
                    return_msg = ""
                    if text in line_lists_kaohsiung:
                        for i in range(1, 3):
                            page = i
                            response_page = "https://mtbu.kcg.gov.tw/Activities/C002100?PageNumber=" + str(page)
                            response = requests.get(response_page)
                            soup = BeautifulSoup(response.text, "html.parser")
                            titles = soup.find_all("a",{"class": "txt-link"})
                            for title in titles:
                                title_text = title.getText().strip()
                                if (text in title_text):
                                    try:
                                        return_msg += f"https://mtbu.kcg.gov.tw/{title['href']}\n{title_text}\n"
                                    except KeyError:
                                        pass
                    if return_msg == "":
                        return_msg = "很抱歉，最近沒有任何關於此搜尋結果的新消息。建議您更改搜尋關鍵詞。"
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text=return_msg)    # 回復傳入的訊息文字
                    )
                else:
                    line_bot_api.reply_message(  
                        event.reply_token,
                        TextSendMessage(text="很抱歉，我不認識這個關鍵詞或指令，建議您更換關鍵詞。")    # 回復傳入的訊息文字
                    )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def CreateFSM():
    with open('./static/' + machine.fsm_filename, 'bw') as f:
        machine.get_graph().draw(f, format="png", prog='dot')
