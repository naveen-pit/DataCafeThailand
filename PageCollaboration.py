import uuid
from google.cloud import bigquery
from MongoDB import MongoDBManager
client = bigquery.Client()
def query(query_string ):
    query_job = client.run_async_query(str(uuid.uuid4()), query_string)
    query_job.begin()
    query_job.result()  # Wait for job to complete.
    destination_table = query_job.destination
    destination_table.reload()
    data=[]
    for row in destination_table.fetch_data():
        data.append(row)
    return data
def get_page_dict():
    query_string = "SELECT user_id,page_url FROM [datacafethailand:social_insight.customer_connection_profile] where source = 'Facebook'"
    data = query(query_string)
    page_dict={}
    for row in data:
        page_id = row[0]
        page_url = row[1]
        page_dict[page_id]=page_url
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
        page_url = page_dict[page_id]
        page_score[page_id] ={'count':count,'page_url':page_url}
    return page_score
if __name__=="__main__":
    mongo = MongoDBManager('PageCollab')
    page_dict = get_page_dict()
    page_id ='129558990394402' 
    page_url = page_dict[page_id]
    page_score = get_pages_interacted_with_users(page_id,page_dict) #khaosod
    data = {'page_id':page_id,'page_url': page_url,'page_score':page_score}
    mongo.insert_one('page_score',data)
