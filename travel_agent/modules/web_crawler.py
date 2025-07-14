import asyncio
import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urljoin

from config.settings import USER_AGENTS, REQUEST_INTERVAL

class WebCrawler:
    """负责从各种网站抓取旅行相关信息。"""

    def __init__(self):
        self.session = requests.Session()

    async def _fetch_url(self, url: str) -> str:
        """
        异步获取指定URL的内容。
        Args:
            url: 目标URL。
        Returns:
            网页内容字符串。
        Raises:
            requests.exceptions.RequestException: 如果请求失败。
        """
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            await asyncio.sleep(REQUEST_INTERVAL) # 避免频繁请求
            response = await asyncio.to_thread(self.session.get, url, headers=headers, timeout=10)
            response.raise_for_status() # 检查HTTP错误
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            raise

    def _parse_html(self, html_content: str):
        """
        解析HTML内容并返回BeautifulSoup对象。
        Args:
            html_content: 网页内容字符串。
        Returns:
            BeautifulSoup对象。
        """
        return BeautifulSoup(html_content, 'html.parser')

    async def get_destination_info(self, destination: str) -> dict:
        """
        抓取目的地基本信息（气候、文化、最佳旅行时间）。
        这是一个示例，实际需要针对特定旅游网站进行爬取。
        Args:
            destination: 旅行目的地名称。
        Returns:
            包含目的地信息的字典。
        """
        print(f"Crawling destination info for: {destination}")
        # 示例：假设从某个旅游百科网站获取信息
        search_url = f"https://baike.baidu.com/item/{destination}"
        try:
            html = await self._fetch_url(search_url)
            soup = self._parse_html(html)
            # 实际解析逻辑会更复杂，这里仅作示意
            description = soup.find("div", class_="lemma-summary")
            climate = soup.find(string="气候")
            culture = soup.find(string="文化")

            return {
                "description": description.text.strip() if description else "",
                "climate": climate.find_next("dd").text.strip() if climate else "",
                "culture": culture.find_next("dd").text.strip() if culture else "",
                "best_travel_time": "", # 需要更复杂的逻辑来提取
            }
        except Exception as e:
            print(f"Could not get destination info for {destination}: {e}")
            return {"description": "", "climate": "", "culture": "", "best_travel_time": ""}

    async def get_attraction_info(self, attraction_name: str, destination: str) -> dict:
        """
        抓取景点信息（门票价格、开放时间、推荐指数、图片）。
        Args:
            attraction_name: 景点名称。
            destination: 目的地名称。
        Returns:
            包含景点信息的字典。
        """
        print(f"Crawling attraction info for: {attraction_name} in {destination}")
        # 实际需要针对携程、去哪儿等网站进行爬取
        # 示例：这里返回模拟数据
        return {
            "name": attraction_name,
            "description": f"{attraction_name}是{destination}的著名景点。",
            "ticket_price": random.uniform(50, 200),
            "opening_hours": "09:00 - 17:00",
            "recommendation_index": random.randint(80, 100),
            "image_url": "https://via.placeholder.com/300x200?text=Attraction+Image"
        }

    async def get_food_info(self, food_name: str, destination: str) -> dict:
        """
        抓取美食信息（特色餐厅、小吃、价格范围）。
        Args:
            food_name: 美食名称。
            destination: 目的地名称。
        Returns:
            包含美食信息的字典。
        """
        print(f"Crawling food info for: {food_name} in {destination}")
        # 实际需要针对大众点评等网站进行爬取
        return {
            "name": food_name,
            "description": f"{food_name}是{destination}的特色美食。",
            "price_range": f"¥{random.uniform(20, 100):.2f} - ¥{random.uniform(100, 300):.2f}",
            "image_url": "https://via.placeholder.com/300x200?text=Food+Image"
        }

    async def get_transportation_info(self, origin: str, destination: str, date: str) -> dict:
        """
        抓取交通信息（往返交通工具、价格、时间）。
        Args:
            origin: 出发城市。
            destination: 目的地城市。
            date: 出发日期。
        Returns:
            包含交通信息的字典。
        """
        print(f"Crawling transportation info from {origin} to {destination} on {date}")
        # 实际需要针对12306、航旅纵横等网站进行爬取
        return {
            "type": "飞机",
            "estimated_cost": random.uniform(500, 2000),
            "duration": "3小时",
            "notes": "建议提前预订机票"
        }

    async def get_accommodation_info(self, destination: str, check_in_date: str, check_out_date: str) -> dict:
        """
        抓取住宿信息（酒店、民宿价格区间）。
        Args:
            destination: 目的地城市。
            check_in_date: 入住日期。
            check_out_date: 退房日期。
        Returns:
            包含住宿信息的字典。
        """
        print(f"Crawling accommodation info for {destination} from {check_in_date} to {check_out_date}")
        # 实际需要针对美团、飞猪等网站进行爬取
        return {
            "name": "舒适酒店",
            "price_range": random.uniform(200, 800),
            "address": f"{destination}市中心",
            "notes": "含早餐，交通便利"
        }

# 示例用法 (仅用于测试)
async def main():
    crawler = WebCrawler()
    # info = await crawler.get_destination_info("三亚")
    # print(info)
    # attraction = await crawler.get_attraction_info("天涯海角", "三亚")
    # print(attraction)
    # food = await crawler.get_food_info("海鲜", "三亚")
    # print(food)
    # transport = await crawler.get_transportation_info("北京", "三亚", "2025-08-01")
    # print(transport)
    # accommodation = await crawler.get_accommodation_info("三亚", "2025-08-01", "2025-08-04")
    # print(accommodation)

if __name__ == "__main__":
    asyncio.run(main())
