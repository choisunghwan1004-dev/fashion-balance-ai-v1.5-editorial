"""Move V1.8 public photos to private storage without guessing their owner."""
from pathlib import Path
import re
import shutil
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')
import db


def migrate():
    source,destination = ROOT/'public/uploads',ROOT/'private/uploads'
    destination.mkdir(parents=True,exist_ok=True)
    if not source.exists():
        print('No legacy public uploads. Existing V1.9 private photos stay private.')
        return
    files = list(source.iterdir())
    plan = []
    # Validate everything before the first move. Ambiguous owners require human review.
    for file in files:
        if not file.is_file() or not re.fullmatch(r'[a-f0-9-]+\.(jpg|png|webp)',file.name):
            raise ValueError('Unexpected photo filename; review the uploads folder.')
        if (destination/file.name).exists():
            raise ValueError('Destination file already exists. Compare files before retrying.')
        owners = db.query('SELECT DISTINCT owner_user_id FROM fashion_items WHERE image_url=%s AND owner_user_id IS NOT NULL',('/uploads/'+file.name,))
        if len(owners)>1:
            raise ValueError('Ambiguous photo ownership. Resolve it before migrating.')
        plan.append((file,owners))
    for file,owners in plan:
        if owners:
            db.query('INSERT INTO private_photos(filename,user_id) VALUES(%s,%s) ON DUPLICATE KEY UPDATE user_id=VALUES(user_id)',(file.name,owners[0]['owner_user_id']))
        shutil.move(str(file),str(destination/file.name))
    source.rmdir()
    print(f'{len(plan)} photos moved. Unassigned photos are kept private without ownership claims.')


if __name__=='__main__':
    migrate()
