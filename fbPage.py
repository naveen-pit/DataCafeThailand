access_token='EAACEdEose0cBAGq2vU8q1zYTH6vZAymQXhxFZA8RSMy3gzWO5FSEwF8nQ8AvFiZBkQy5pXAtdZAVg5JY049BZAmZAyFOZCTkVM0tImgIL9lf6McwrkpYRxQ149qd3OZBqacx4ZAZBt1IvUL7cchSaghcEWWgs4zDhORS0lZC1c9Gbak92KrqOwQjoKAEZAWQHD2HiLEZD'
access_token='130322947605081|R6sG5Gj4JOgNT6uYm3j6trji_OQ'
# url ="""https://graph.facebook.com/v2.11/
# scienceherehere/?fields=fan_count&access_token="""+access_token

import facebook
from MongoDB import MongoDBManager
graph = facebook.GraphAPI(access_token=access_token, version="2.7")
args = {'fields': 'fan_count'}

mongo = MongoDBManager('PageCollab')
page_dict=mongo.get_all_from_collection('page_dict')[0]
page_id_list = page_dict.keys()
page_id_list = sorted(page_id_list)
start = 248
for i in range(start,len(page_id_list)-1) :
    page_id = page_id_list[i]
    print(i)
    print(page_id)
    print(page_dict[page_id]['name'])
    if i==248:
        page_id = '863789570397983'
        page={'fan_count':144140}
    else:
        page = graph.get_object(page_id, **args)
    print(page['fan_count'])
    print('-------------------')
    data={
        'page_id':page_id,
        'name':page_dict[page_id]['name'],
        'fan_count':page['fan_count']
    }
    mongo.insert_one('page_like',data)
    i=i+1
print(page)
