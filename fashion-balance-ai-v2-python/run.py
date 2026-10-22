"""One Python process serves both React screens and APIs, including on a phone."""
from pathlib import Path
import os
from dotenv import load_dotenv
import uvicorn
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')

if __name__=='__main__':
    os.chdir(ROOT)
    uvicorn.run('app:app',host='0.0.0.0',port=int(os.getenv('PORT','3000')),proxy_headers=False)
