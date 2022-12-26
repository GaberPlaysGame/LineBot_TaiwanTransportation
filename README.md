## 簡介
能夠查詢台灣捷運工程訊息的 Line Bot，可以透過輸入指令來去了解相關的捷運訊息，並且可以透過網路爬蟲來取得最新的工程新聞。

## 功能
以下功能由 Linebot, Django, Pytransition, BeautifulSoup 實作

### FSM
輸入 FSM 來取得該程式的有限狀態機圖示。
![FSM_diagram](https://user-images.githubusercontent.com/52413056/209543420-5a2f7da8-a0fa-47ee-8a21-227da4a47be5.png)

### 圖文選單
透過自製的圖文選單來點選想要查詢的地區，每點擊一個區域都會切換當下的狀態，並由 Linebot 告訴您可以查詢的項目。
![richmenu_image](https://user-images.githubusercontent.com/52413056/209543508-9e59de55-6d69-4654-80b6-288115739786.png)
![image](https://user-images.githubusercontent.com/52413056/209544555-29a9d78e-7550-4e30-a585-bc913c4fd15a.png)

### 新聞爬蟲與擷取
透過輸入關鍵字詞（由 Linebot 告訴您那些可以查詢），Linebot 可以透過網路爬蟲來瀏覽各捷運工程局所發布的最新消息，並擷取相關資訊。
![image](https://user-images.githubusercontent.com/52413056/209544675-4a7e504a-3012-49ab-876c-89d2e97597c1.png)

Linebot 會回傳給您標題以及連結，你可以透過連結點進網站瀏覽詳細新聞。
![image](https://user-images.githubusercontent.com/52413056/209544699-073fc506-8f6f-4f89-847a-636b558fa7eb.png)

若是沒有搜尋到任何最新的新聞資訊，則 Linebot 會跳出錯誤提示並建議您更改關鍵字。
![image](https://user-images.githubusercontent.com/52413056/209544748-c26e9df4-cf6b-4ca5-b2d3-d23175bacb29.png)

### 透過json來擷取路線簡介

透過輸入關鍵字並加上「簡介」可以得到該路線的簡介與路線圖資訊（**僅限台北捷運、新北捷運**）
![image](https://user-images.githubusercontent.com/52413056/209544769-1c411e32-9a19-4cc0-ab9a-97b241d0415c.png)

## 版本 Changelog
### ver1.1
* 添加了簡介功能，目前僅限台北捷運路線可以使用。
* 台北捷運、新北捷運的路線目前被整理在一個json檔內存取。

### ver1.0
* 初始發布
