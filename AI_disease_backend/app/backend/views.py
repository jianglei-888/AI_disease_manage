from fastapi import APIRouter,UploadFile, File, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from lang_chain_core.rag_core import rag
import os
import shutil
backend=APIRouter()
templates=Jinja2Templates(directory='./app/backend/templates')
# 使用静态资源【static】和模板
# backend.mount('./static',StaticFiles(directory='static'))
# backend.mount('./media',StaticFiles(directory='media'))
# 上传目录
os.makedirs("uploads", exist_ok=True)
# ==================== 路由 ====================
@backend.get("/")
def index(request: Request):
    return templates.TemplateResponse(request,"index.html", context={"msg": None, "error": None})

@backend.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    try:
        save_path = f"uploads/{file.filename}"
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        cnt = rag.load_file(save_path) # 把文档插入到向量数据库的逻辑
        return templates.TemplateResponse(request,"index.html", {"msg": f"上传成功：{file.filename}，切分 {cnt} 块"})
    except Exception as e:
        return templates.TemplateResponse(request,"index.html", {"error": f"上传失败：{str(e)}"})

@backend.post("/search")
async def search(request: Request, question: str = Form(...)):
    try:
        chain = rag.get_chain()
        answer = chain.invoke(question)
        return templates.TemplateResponse(request,"result.html", {
            "question": question,
            "answer": answer
        })
    except Exception as e:
        return templates.TemplateResponse(request,"index.html", {
            "error": f"查询失败：{str(e)}"
        })