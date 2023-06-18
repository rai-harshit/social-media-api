from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    is_published: Optional[bool] = True


my_posts = []

while True:
    try:
        conn = psycopg.connect(
            host="localhost",
            dbname="fastapi",
            user="postgres",
            password="12321",
            row_factory=dict_row,
        )
        cursor = conn.cursor()
        print("DB connection successfully")
        break
    except Exception as e:
        print("Connecting to DB failed")
        print(f"Error : {e}")
        time.sleep(3)


def find_post(id: int):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id: int):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM POSTS""")
    fetched_posts = cursor.fetchall()
    return {"data": fetched_posts}


@app.get("/posts/latest")
def get_latest_post():
    cursor.execute("""SELECT * FROM POSTS ORDER BY CREATED_AT DESC LIMIT 1""")
    latest_post = cursor.fetchone()
    if latest_post is None:
        return {"data": "No posts found. Try creating a post first."}
    return {"data": latest_post}


@app.get("/posts/{id}")
def get_posts(id: int):
    cursor.execute(f"""SELECT * FROM POSTS WHERE ID = {id}""")
    post_found = cursor.fetchone()
    if not post_found:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No posts found with the provided id."
        )
    return {"data": post_found}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: Post):
    print(payload)
    cursor.execute(
        """INSERT INTO POSTS(TITLE, CONTENT, IS_PUBLISHED) VALUES (%s, %s, %s) RETURNING *""",
        (payload.title, payload.content, payload.is_published),
    )
    saved_post = cursor.fetchone()
    conn.commit()
    return {"data": saved_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = cursor.execute(f"""SELECT ID FRoM POSTS WHERE ID = {id}""")
    if not index:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No posts found with the provided id."
        )
    cursor.execute(f"""DELETE FROM POSTS WHERE ID = {id}""")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, payload: Post):
    index = find_index_post(id)
    if not index:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No posts found with the provided id."
        )
    post_dict = payload.dict()
    post_dict["id"] = id
    my_posts[index] = post_dict
    return {"data": post_dict}
