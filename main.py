from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient


app = FastAPI(title="Simple CMS")
templates = Jinja2Templates(directory="templates")


client = MongoClient("mongodb://localhost:27017/")
db = client["simple_cms_db"]
posts_collection = db["posts"]

 
@app.get("/", response_class=HTMLResponse)
@app.get("/posts", response_class=HTMLResponse)
def list_posts(request: Request):
    # Compulsory: Complete content must NOT be sent to post-list page
    posts = list(posts_collection.find({}, {"content": 0}).sort("_id", -1))
    return templates.TemplateResponse(request=request, name="index.html", context={"posts": posts})




@app.get("/posts/new", response_class=HTMLResponse)
def new_post_form(request: Request):
    return templates.TemplateResponse(request=request, name="create.html")




@app.post("/posts")
def create_post(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    content: str = Form(...)
):
    if not title.strip() or not author.strip() or not content.strip():
        return templates.TemplateResponse(
            request=request,
            name="create.html",
            context={
                "error": "All fields (Title, Author, Content) are required!",
                "title": title,
                "author": author,
                "content": content
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )


    created_at = datetime.now().strftime("%d %B %Y")

    new_post = {
        "title": title.strip(),
        "author": author.strip(),
        "content": content.strip(),
        "created_at": created_at
    }

    posts_collection.insert_one(new_post)
    return RedirectResponse(url="/posts", status_code=status.HTTP_303_SEE_OTHER)




@app.get("/posts/{id}", response_class=HTMLResponse)
def view_post(request: Request, id: str):
    try:
        post = posts_collection.find_one({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Post ID format")

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(request=request, name="detail.html", context={"post": post})