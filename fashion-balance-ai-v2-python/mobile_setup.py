"""Set a phone-reachable URL without printing or replacing other .env secrets."""
import argparse
from pathlib import Path
from urllib.parse import urlsplit
from dotenv import set_key

ROOT = Path(__file__).resolve().parent


def configure(value):
    parsed = urlsplit(value)
    if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:
        raise ValueError('Use an HTTP(S) origin without path, credentials, query or fragment.')
    if parsed.hostname in ('localhost','127.0.0.1','::1'):
        raise ValueError('A phone needs the PC LAN IP or a public HTTPS domain, not localhost.')
    target = ROOT/'.env'
    if not target.exists():
        raise ValueError('Create .env from .env.example and configure your database first.')
    origin = parsed.scheme+'://'+parsed.netloc
    set_key(str(target),'APP_BASE_URL',origin)
    print('Mobile URL configured:',origin+'/mobile.html')
    print('Restart Python. Use this same origin on the PC and the phone.')


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',required=True,help='Example: http://192.168.0.10:3000')
    args = parser.parse_args()
    configure(args.url)
