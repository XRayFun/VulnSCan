import argparse
import asyncio
from datetime import datetime

import aiofiles
import os

from _conf import COMMON_SUBDOMAINS, BRUTEFORCE_FILE, BRUTEFORCE_LEVEL, BRUTEFORCE_OUTPUT_FOLDER, BRUTEFORCE_OUTPUT_FORMAT
from _log import log_info, log_error
from domain import resolve_domain


async def load_subdomains_from_file(file_path):
    subdomains = []
    async with aiofiles.open(file_path, mode='r') as f:
        async for line in f:
            subdomain = line.strip()
            if subdomain and not subdomain.startswith('#'):
                subdomains.append(subdomain)
    log_info(f"Loaded {len(subdomains)} subdomains from '{file_path}'")
    return subdomains


async def find_subdomains(domains, level=BRUTEFORCE_LEVEL, brute_force_file=BRUTEFORCE_FILE, output_folder=BRUTEFORCE_OUTPUT_FOLDER, output_format=BRUTEFORCE_OUTPUT_FORMAT):
    found_ips = set()  # Для хранения уникальных IP-адресов

    async def search_subdomains(current_domain, current_level, output_file):
        if current_level > 0:
            subdomains = [f"{sub}.{current_domain}" for sub in COMMON_SUBDOMAINS]
        else:
            subdomains = [current_domain]

        if brute_force_file and current_level > 0:
            additional_subdomains = await load_subdomains_from_file(brute_force_file)
            subdomains.extend([f"{sub}.{current_domain}" for sub in additional_subdomains])

        resolved_ips = await asyncio.gather(*[resolve_domain(sub) for sub in subdomains])
        resolved_ips = list(filter(None, resolved_ips))

        for ip in resolved_ips:
            found_ips.add(ip)

        if resolved_ips:
            # Запись результатов в файл по мере их получения
            if output_file:
                if output_format == 'domain-ip':
                    await output_file.write(f"{current_domain} - {', '.join(resolved_ips)}\n")
                elif output_format == 'ip':
                    await output_file.write(f"{', '.join(resolved_ips)}\n")

        if current_level < level:
            tasks = [search_subdomains(sub, current_level + 1, output_file) for sub in subdomains]
            await asyncio.gather(*tasks)

    # Открытие файла для записи
    output_file_path = f"{output_folder}/domain.subdomain results {datetime.now()}.txt" if output_folder else None
    output_file = await aiofiles.open(output_file_path, mode='w') if output_file_path else None

    # Обработка каждого домена
    for domain in domains:
        await search_subdomains(domain, 0, output_file)

    # Закрытие файла, если он был открыт
    if output_file:
        await output_file.close()
        log_info(f"Results saved to '{output_file_path}' file")

    return list(found_ips)  # Вернуть найденные IP-адреса


async def load_domains_from_file(file_path):
    async with aiofiles.open(file_path, mode='r') as f:
        content = await f.read()
        domains = [domain.strip() for domain in content.split(',') if domain.strip()]
    log_info(f"Loaded {len(domains)} domains from '{file_path}'")
    return domains


def main(remaining_args):
    parser = argparse.ArgumentParser(description="Subdomain resolution module")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-ds', '--domains', help="Comma-separated list of domains (no spaces)")
    group.add_argument('-iF', '--input-file', help="Path to a file with comma-separated domains")

    parser.add_argument('-dBL', '--level', type=int, default=BRUTEFORCE_LEVEL,
                        help="Level of subdomain brute-forcing (default: BRUTEFORCE_LEVEL)")
    parser.add_argument('-dBF', '--brute-force-file', default=BRUTEFORCE_FILE,
                        help="Path to brute-force subdomains file (default: BRUTEFORCE_FILE)")
    parser.add_argument('-oF', '--output-folder', default=BRUTEFORCE_OUTPUT_FOLDER,
                        help="Output folder for results")
    parser.add_argument('-oFmt', '--output-format', choices=['domain-ip', 'ip'], default='domain-ip',
                        help="Output format: 'domain-ip' or 'ip' (default: 'domain-ip')")
    args = parser.parse_args(remaining_args)

    domains = []
    if args.domains:
        domains = [domain.strip() for domain in args.domains.split(',')]
    elif args.input_file:
        domains = asyncio.run(load_domains_from_file(args.input_file))

    domains = list(set(domains))

    # Запуск асинхронного поиска для всех доменов
    asyncio.run(find_subdomains(domains, args.level, args.brute_force_file, args.output_folder, args.output_format))
