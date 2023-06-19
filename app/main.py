"""
This module provides a FastAPI application for managing blog posts.

It includes the following functionality:

Connecting to a PostgreSQL database.
Retrieving all posts, latest post, and a specific post from the database.
Creating a new post and saving it to the database.
Deleting a post from the database.
Updating an existing post in the database.
The Post class is defined as a Pydantic BaseModel, representing a blog post. It has the following attributes:

title (str): The title of the blog post.
content (str): The content of the blog post.
is_published (Optional[bool], optional): Indicates whether the post is published or not. Defaults to True if not specified.
The FastAPI application routes are defined as follows:

GET /: Returns a simple "Hello World!" message.
GET /posts: Retrieves all posts from the database.
GET /posts/latest: Retrieves the latest post from the database.
GET /posts/{id}: Retrieves a specific post based on the provided ID.
POST /posts: Creates a new post and saves it to the database.
DELETE /posts/{id}: Deletes a specific post from the database.
PUT /posts/{id}: Updates an existing post in the database.
Note: The module assumes a PostgreSQL database named "fastapi" running on the local host with the following credentials: user="postgres", password="12321". It uses the psycopg library to connect to the database and execute queries.

Usage example:

Start the FastAPI application using uvicorn module_name:app --reload.
Access the application routes using a web browser or an API client like cURL or Postman.
Please make sure to configure the PostgreSQL database and adjust the credentials according to your setup before running this module.
"""

import time
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row


app = FastAPI()


class Post(BaseModel):
    """
    A class representing a blog post.
    Attributes:
    title (str): The title of the blog post.
    content (str): The content of the blog post.
    is_published (Optional[bool], optional): Indicates whether the post is published or not.
        Defaults to True if not specified.
    """
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
    cursor.execute("""SELECT * FROM POSTS WHERE ID = %s""" % (id))
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
    index = cursor.execute(f"""SELECT ID FROM POSTS WHERE ID = {id}""")
    if not index:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No posts found with the provided id."
        )
    cursor.execute(f"""DELETE FROM POSTS WHERE ID = {id}""")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, payload: Post):
    cursor.execute(
        """UPDATE POSTS SET TITLE = %s, CONTENT = %s, IS_PUBLISHED = %s WHERE ID = %s""",
        (payload.title, payload.content, payload.is_published, id),
    )
    conn.commit()
    cursor.execute("""SELECT * FROM POSTS WHERE ID = %s""" % (id))
    post_found = cursor.fetchone()
    if not post_found:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No posts found with the provided id."
        )
    return {"data": post_found}
