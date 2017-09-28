import uuid
from google.cloud import bigquery
from MongoDB import MongoDBManager
from datetime import datetime
client = bigquery.Client()
def query(query_string,use_legacy=True):
    query_job = client.run_async_query(str(uuid.uuid4()), query_string)
    query_job.use_legacy_sql = use_legacy
    query_job.begin()
    query_job.result()  # Wait for job to complete.
    destination_table = query_job.destination
    destination_table.reload()
    data=[]
    for row in destination_table.fetch_data():
        data.append(row)
    return data
def get_page_dict():
    query_string = """SELECT user_id, page_url,category,name  FROM [datacafethailand:a19.page_info_new]"""
    data = query(query_string)
    page_dict={}
    for row in data:
        page_id = row[0]
        page_url = row[1]
        category = row[2]
        name = row[3]
        page_dict[page_id]={'page_id':page_id,'page_url':page_url,'category':category,'score':[],'name':name}
    return page_dict
def get_pages_interacted_with_users(page_id,page_dict):
    query_string = """select page_id,count(*) as count from  
        (SELECT user_id,page_id FROM [datacafethailand:a19.page_user_count] where user_id in 
        (SELECT user_id FROM [datacafethailand:a19.page_post_user] where page_id='"""+page_id+"""' group by user_id)
        )
        group by page_id"""
    data = query(query_string)
    page_score = {}
    for row in data:
        page_id = row[0]
        count = row[1]
        page_url = page_dict[page_id]['page_url']
        category =  page_dict[page_id]['category']
        page_score[page_id] ={'count':count,'page_url':page_url,'category':category}
    return page_score
def generate_page_score_tuple(page_score):
    page_score_tuple_list=[]
    for page_id in page_score:
        page_score_tuple = (page_score[page_id]['count'],page_score[page_id]['page_url'],page_score[page_id]['category'])
        page_score_tuple_list.append(page_score_tuple)
    return page_score_tuple_list
def get_num_intersect_unique_users(page_id1,page_id2):
    query_string = """select count(*) from (
        SELECT t1.user_id FROM [datacafethailand:a19.page_post_user] t1
        inner join (SELECT user_id FROM [datacafethailand:a19.page_post_user] where page_id='"""+page_id2+"""' group by user_id) t2
        on t1.user_id = t2.user_id
        where t1.page_id='"""+page_id1+"""' group by t1.user_id
        )"""
    data = query(query_string)
    for row in data:
        return row[0]
def get_num_union_unique_users(page_id1,page_id2):
    query_string = """select count(*) from (
        (SELECT user_id FROM datacafethailand.a19.page_post_user where page_id='"""+page_id1+"""' group by user_id)
        union distinct
        (SELECT user_id FROM datacafethailand.a19.page_post_user where page_id='"""+page_id2+"""' group by user_id)
        )"""
    data = query(query_string,use_legacy=False)
    for row in data:
        return row[0]
def run_page_collab():
    call_big_query=True
    if call_big_query:
        mongo = MongoDBManager('PageCollab')
        page_dict = get_page_dict()
        for page_id in page_dict:
            page_url = page_dict[page_id]['page_url']
            page_score = get_pages_interacted_with_users(page_id,page_dict) #khaosod
            page_score_tuple_list=generate_page_score_tuple(page_score)
            page_score_tuple_list = sorted(page_score_tuple_list)
            data = {'page_id':page_id,'page_url': page_url,'page_score':page_score_tuple_list}
            mongo.insert_one('page_score',data)
    else:
        pass

if __name__=="__main__":
    print('begin')
    mongo = MongoDBManager('PageCollab')
    call_big_query=True
    if call_big_query:
        page_dict = get_page_dict()
        all_page_list = sorted(list(page_dict.keys()))
        page_list = all_page_list
        print(len(page_list))
        start_i =0
        for i in range(start_i,len(page_list)):
            
            page_id1 = page_list[i]
            if page_id1=='':
                    continue
            for j in range(len(all_page_list)):
                print('i=',i)
                print('j=',j)
                print(str(datetime.now()))
                page_id2 = all_page_list[j]
                union = get_num_union_unique_users(page_id1,page_id2)
                intersect = get_num_intersect_unique_users(page_id1,page_id2)
                jaccard_sim = 1.0*intersect/union
                page_url1 = page_dict[page_id1]['page_url']
                category1 =  page_dict[page_id1]['category']
                #page_score_tuple1 = (jaccard_sim,page_url1,category1,intersect,union)
                page_url2 = page_dict[page_id2]['page_url']
                category2 =  page_dict[page_id2]['category']
                name2 =  page_dict[page_id2]['name']
                page_score_tuple2 = (jaccard_sim,page_url2,name2,category2,intersect,union)
                page_dict[page_id1]['score'].append(page_score_tuple2)
            page_dict[page_id1]['score'] = sorted(page_dict[page_id1]['score'])
            mongo.insert_one('page_score',page_dict[page_id1])
        # for page_id in page_dict:
            
        # mongo.insert_many('page_score',page_dict.values())
    else: 
        pass
   