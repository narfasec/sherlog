from datetime import datetime
from pyArango.connection import *
import uuid
import os

class DBConnection:
    def __init__(self, log,):
        self.db_url = os.environ['DB_URL']
        self.db_username = os.environ['DB_USERNAME']
        self.db_password = os.environ['DB_PASSWORD']
        self.db_name = os.environ['DB_NAME']
        self.conn = Connection(arangoURL=self.db_url,username=self.db_username, password=self.db_password)
        self.log = log
        self.association_collection = "childOf"

    def list_to_collection(self,collection,list):
        '''
        Turn list of results into arangoDB collections
        '''
        self.log.info(f'[list_to_collection] Start')
        db = self.conn[self.db_name]
        if not db.hasCollection(collection):
            coll = db.createCollection(name=collection)
        else:
            coll = db[collection]
        
        for i in list:
                try:
                    doc=coll[i["arn"].replace("/",":")]
                except Exception as e:
                    doc = coll.createDocument()
                    doc._key = i["arn"].replace("/",":")

                for k in i:
                    if k != "arn":
                        doc[k]=i[k]
                doc.save()

        self.log.info(f'[list_to_collection] End')

        return 1

    def create_association(self,associations):
        '''
        Create associations in arango db
        '''
        db = self.conn[self.db_name]
        if not db.hasCollection(self.association_collection):
            coll = db.createCollection(name=self.association_collection,className='Edges')
        for a in associations:
            childId=a['childId'].replace("/",":")
            parentId=a['parentId'].replace("/",":")
            aql="INSERT { _from: \"resource_tags/"+childId+"\", _to: \"public_resources/"+parentId+"\" } INTO "+self.association_collection
            queryResult = db.AQLQuery(aql)
        self.log.info(f'[create_association] End')
        return 1