#!/usr/bin/env python
# coding=utf-8
from pagescrapper import FacebookAPI

facebook_app_id = '130322947605081'
facebook_app_secret = 'b6cd5df082edac590a802fe1ba100bc4'
graph_api_version = 2.10
facebook_api = FacebookAPI(facebook_app_id, facebook_app_secret, graph_api_version)

# posts = facebook_api.get_posts(pages='samakhom', limit=5)
# for post in posts:
#     print(post)
#     print(posts[post])

comments = facebook_api.get_post_comments(post_ids=['308945857094_10155596320902095'], limit=None)
for comment in comments:
    print(comment)
    print(comments[comment])