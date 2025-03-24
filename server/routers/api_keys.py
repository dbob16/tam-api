from fastapi import APIRouter, Request, HTTPException
from dao import *

router = APIRouter()

@router.get("/api_keys/")
def get_api_keys(request:Request, api_key:str=None):
    if API_PW and not check_api_key(api_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    conn, cur = session()
    cur.execute("SELECT * FROM api_keys ORDER BY pc_name")
    results = cur.fetchall()
    conn.close()
    if not results:
        return []
    r_l = []
    for r in results:
        r_d = {"api_key": r[0], "pc_name": r[1], "ip_addr": r[2]}
        r_l.append(r_d)
    return r_l

@router.post("/genapi/")
def gen_api(request:Request, in_req:ApiRequest):
    if API_PW and API_PW != in_req.inp_pw:
        raise HTTPException(status_code=401, detail="Password is not correct")
    if 'x-real-ip' in request.headers:
        client_ip = request.headers['x-real-ip']
    else:
        client_ip = request.client.host
    rtn_key = create_api_key()
    conn, cur = session()
    cur.execute(f"INSERT INTO api_keys (api_key, pc_name, ip_addr) VALUES (\"{rtn_key}\", \"{in_req.pc_name}\", \"{client_ip}\")")
    conn.commit()
    conn.close()
    return {"api_key": rtn_key}

@router.delete("/delapi/")
def del_api(request:Request, auth_key:str=None, api_key:str=None, pc_name:str=None):
    if API_PW and not check_api_key(auth_key, request):
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if api_key and pc_name:
        conn, cur = session()
        cur.execute(f"DELETE FROM api_keys WHERE api_key = \"{api_key}\" AND pc_name = \"{pc_name}\"")
        conn.commit()
        conn.close()
        return {"success": True, "response": f"Deleted key {api_key} and {pc_name}"}
    elif api_key:
        conn, cur = session()
        cur.execute(f"DELETE FROM api_keys WHERE api_key = \"{api_key}\"")
        conn.commit()
        conn.close()
        return {"success": True, "response": f"Deleted key {api_key}"}
    elif pc_name:
        conn, cur = session()
        cur.execute(f"DELETE FROM api_keys WHERE pc_name = \"{pc_name}\"")
        conn.commit()
        conn.close()
        return {"success": True, "response": f"Deleted key {pc_name}"}
    else:
        return {"success": False, "response": "Nothing provided, can't act"}
