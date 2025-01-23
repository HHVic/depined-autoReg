import asyncio
import aiohttp
import random

from log import CustomLogger, delay

log = CustomLogger()

# 假设你有相应的异步函数
from file_util import read_file, save_to_file, save_to_file_fully
from api import get_referral_code, register_user, login_user, create_user_profile, confirm_user_reff


async def main():
    log.info("Processing run auto register (CTRL + C to exit)")
    await delay(3)

    existing_accounts = await read_file("data/accounts.csv")
    new_accounts = await read_file("data/register.csv")
    proxes = await read_file("data/proxies.csv")

    ref_code = []
    # 设置 aiohttp 的超时
    timeout = aiohttp.ClientTimeout(total=300)  # 30秒超时
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for index, existing_account in enumerate(existing_accounts):
            existing_email, existing_proxy, existing_token = existing_account.split(',')
            log.info(f"Try to get referral code for account: {index + 1} {existing_email}")
            reff_resp = await get_referral_code(session, existing_token, existing_proxy)

            if not reff_resp or not reff_resp.get('data', {}).get('is_referral_active'):
                log.warn(f"Referral not active: {existing_email}")
                continue

            reff_code = reff_resp['data'].get('referral_code')
            while reff_code:
                log.info(f"Found new active referral code: {reff_code}")
                ref_code.append(reff_code)
                if not new_accounts:
                    log.info("No more accounts to register")
                    break
                try:
                    if not new_accounts:
                        log.info("All account are refered.")
                        break
                    email, password = new_accounts[0].split(',')
                    proxy = random.choice(proxes)
                    token = None
                    log.info(f"Trying to register email: {email}")
                    reg_resp = await register_user(session, email, password, proxy)

                    if reg_resp and reg_resp.get('error') == 'email already registered':
                        log.info(f"Account {email} already registered")
                        login_resp = await login_user(session, email, password, proxy)

                        if login_resp and login_resp.get('data', {}).get('has_entered_referral_code'):
                            log.info(f"Account {email} already has a referral code")
                            token = login_resp['data']['token']

                            log.info(f"Trying to create profile for {email}")
                            await create_user_profile(session, token, {'step': 'username', 'username': email.split('@')[0]}, proxy)
                            await create_user_profile(session, token, {'step': 'description', 'description': "AI Startup"}, proxy)

                            await save_to_file("tokens.txt", token)
                            await save_to_file("full.csv", f"{email},{password},{proxy},{token}")
                            new_accounts.pop(0)
                            continue

                        log.info(f"Account {email} already registered but not has a referral code")
                        token = login_resp['data']['token']

                    elif not reg_resp or not reg_resp.get('data', {}).get('token'):
                        log.error(f"Failed to register account {email}")
                        continue
                    else:
                        token = reg_resp['data']['token']

                    log.info(f"Trying to create profile for {email}")
                    await create_user_profile(session, token, {'step': 'username', 'username': email.split('@')[0]}, proxy)
                    await create_user_profile(session, token, {'step': 'description', 'description': "AI Startup"}, proxy)

                    confirm_resp = await confirm_user_reff(session, token, reff_code, proxy)

                    if not confirm_resp or not confirm_resp.get('data', {}).get('token'):
                        log.error(f"Failed to confirm referral for account {email}")
                        continue

                    await save_to_file("tokens.txt", confirm_resp['data']['token'])
                    await save_to_file("proxy.txt", proxy)
                    await save_to_file("full.csv", f"{email},{password},{proxy},{confirm_resp['data']['token']}")

                    new_accounts.pop(0)

                    await delay(5)
                    reff_resp = await get_referral_code(session, existing_token, existing_proxy)
                    if not reff_resp or not reff_resp.get('data', {}).get('is_referral_active'):
                        log.warn(f"Referral not active for account: {existing_email}")
                        reff_code = None
                    else:
                        reff_code = reff_resp['data'].get('referral_code')

                except Exception as e:
                    log.error(f"Error creating account: {e}")

        log.info(f"No more referral code found for account: {existing_email}")
                # await save_to_file('referal_code.txt', reff_code)
        await save_to_file("register.csv", '\n'.join(new_accounts))

if __name__ == "__main__":
    asyncio.run(main())
