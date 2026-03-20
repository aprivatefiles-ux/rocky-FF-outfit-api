from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
import httpx
import time
import random
import string

app = FastAPI()

# ================= CONFIG =================
ADMIN_KEY = "rocky_admin_123"
FF_DRES_API = "https://ff-dres-info-api.onrender.com/info?uid="

# ================= Memory Key DB =================
keys_db = {}

# ================= Helpers =================
def generate_key(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ================= HOME =================
@app.get("/")
async def home():
    return {"status": True, "msg": "API Running 🚀"}

# ================= INFO =================
@app.get("/info")
async def info(uid: str = None, key: str = None):
    if not uid or not key:
        raise HTTPException(status_code=400, detail="uid & key required")

    # 🔐 Key check
    if key not in keys_db or keys_db[key]["status"] != "active":
        raise HTTPException(status_code=401, detail="Invalid or blocked key")

    # 🔥 Call FF-Dres Info API
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{FF_DRES_API}{uid}", timeout=15)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="FF-Dres API error")
            return StreamingResponse(BytesIO(resp.content), media_type="image/png")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# ================= ADMIN CREATE =================
@app.get("/admin/create")
async def create(admin_key: str = None, key: str = None):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    key = key or generate_key()
    keys_db[key] = {"status": "active"}
    return {"status": "created", "key": key}

# ================= ADMIN DELETE =================
@app.get("/admin/delete")
async def delete(admin_key: str = None, key: str = None):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if key in keys_db:
        del keys_db[key]
        return {"status": "deleted"}
    return {"error": "key not found"}

# ================= ADMIN BLOCK =================
@app.get("/admin/block")
async def block(admin_key: str = None, key: str = None):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if key in keys_db:
        keys_db[key]["status"] = "blocked"
        return {"status": "blocked"}
    return {"error": "key not found"}

# ================= ADMIN UNBLOCK =================
@app.get("/admin/unblock")
async def unblock(admin_key: str = None, key: str = None):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if key in keys_db:
        keys_db[key]["status"] = "active"
        return {"status": "unblocked"}
    return {"error": "key not found"}
