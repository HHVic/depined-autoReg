import aiohttp
from fake_useragent import UserAgent

from log import CustomLogger

log = CustomLogger()

ua = UserAgent()

headers = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": ua.random
}

def make_headers(token=None):
    """生成请求头"""
    hdr = headers.copy()
    hdr['Content-Type'] = 'application/json'
    if token:
        hdr['Authorization'] = f'Bearer {token}'
    return hdr

def new_agent(proxy=None):
    """根据代理类型创建代理字典"""
    if proxy:
        if proxy.startswith('http://') or proxy.startswith('https://') or \
           proxy.startswith('socks4://') or proxy.startswith('socks5://'):
            return proxy
        else:
            log.warn(f"不支持的代理类型: {proxy}")
            return None
    return None

async def get_ip(proxy):
    log.info(f"Getting IP from {proxy}")
    async with new_agent(proxy) as session:
        async with session.get('http://ip-api.com/line/') as response:
            data = await response.text()
            log.info(data)
            return data.split('\n')[0]

async def register_user(session, email, password, proxy):
    url = 'https://api.depined.org/api/user/register'
    json = {
        "email": email,
        "password": password
    }
    try:
        proxy_url = new_agent(proxy)
        async with session.post(url, json=json, headers=make_headers(), proxy=proxy_url) as response:
            if response.status == 200:
                data = await response.json()
                log.info('Register account completed')
                return data
            else:
                error_data = await response.json()
                log.error('Register account failed', error_data)
                return None
    except aiohttp.ClientError as e:
        log.error('Register account error', str(e))
        return None

async def login_user(session, email, password, proxy):
    url = 'https://api.depined.com/api/user/login'
    login_data = {
        "email": email,
        "password": password
    }
    try:
        proxy_url = new_agent(proxy)
        async with session.post(url, json=login_data, headers=make_headers(), proxy=proxy_url) as response:
            if response.status == 200:
                data = await response.json()
                log.info('用户登录成功')
                return data
            else:
                error_data = await response.json()
                log.error('登录失败:', error_data)
                return None
    except aiohttp.ClientError as e:
        log.error('登录失败:', str(e))
        return None

async def create_user_profile(session, token, payload, proxy):
    url = 'https://api.depined.org/api/user/profile-creation'
    try:
        proxy_url = new_agent(proxy)
        async with session.post(url, json=payload, headers=make_headers(token=token), proxy=proxy_url) as response:
            if response.status == 200:
                data = await response.json()
                log.info('Profile created successfully:', payload)
                return data
    except aiohttp.ClientError as e:
        log.error('Error creating profile:', str(e))
        return None

async def confirm_user_reff(session, token, referral_code, proxy=None):
    url = 'https://api.depined.org/api/access-code/referal'
    reffer_code = {
        "referral_code": referral_code
    }
    try:
        proxy_url = new_agent(proxy)
        async with session.post(url, json=reffer_code, headers=make_headers(token=token), proxy=proxy_url) as response:
            if response.status == 200:
                data = await response.json()
                log.info('Referral verification completed')
                return data
            else:
                error_data = await response.json()
                log.error('Referral verification failed', error_data)
                return None
    except aiohttp.ClientError as e:
        log.error('Referral verification error', str(e))
        return None

async def get_user_info(token, proxy):
    url = 'https://api.depined.org/api/user/details'
    async with new_agent(proxy) as session:
        try:
            async with session.get(url, headers={**headers, 'Authorization': f'Bearer {token}'}) as response:
                data = await response.json()
                return data
        except aiohttp.ClientError as error:
            log.error('Error fetching user info:', str(error))
            return None

async def get_referral_code(session, token, proxy=None):
    """获取推荐码"""
    url = 'https://api.depined.org/api/referrals/stats'
    try:
        proxy_url = new_agent(proxy)
        async with session.get(url, headers=make_headers(token), proxy=proxy_url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_data = await response.json()
                log.error('获取推荐码出错:', error_data)
                return None
    except aiohttp.ClientError as e:
        log.error('获取推荐码出错:', str(e))
        return None

async def get_earnings(token, proxy):
    url = 'https://api.depined.org/api/stats/epoch-earnings'
    async with new_agent(proxy) as session:
        try:
            async with session.get(url, headers={**headers, 'Authorization': f'Bearer {token}'}) as response:
                data = await response.json()
                return data
        except aiohttp.ClientError as error:
            log.error('Error fetching user info:', str(error))
            return None

async def connect(token, proxy):
    url = 'https://api.depined.org/api/user/widget-connect'
    async with new_agent(proxy) as session:
        try:
            payload = {"connected": True}
            async with session.post(url, json=payload, headers={**headers, 'Authorization': f'Bearer {token}'}) as response:
                data = await response.json()
                return data
        except aiohttp.ClientError as error:
            log.error(f"Error when update connection: {error.message}")
            return None

async def get_user_profile(token, proxy):
    url = 'https://api.depined.org/api/user/overview/profile'
    async with new_agent(proxy) as session:
        try:
            async with session.get(url, headers={**headers, 'Authorization': f'Bearer {token}'}) as response:
                data = await response.json()
                return data.get('data', {}).get('profile')
        except aiohttp.ClientError as error:
            log.error('Error fetching user info:', str(error))
            return None
