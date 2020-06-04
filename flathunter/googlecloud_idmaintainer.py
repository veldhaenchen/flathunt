import logging
import firebase_admin
import traceback
import datetime
from firebase_admin import credentials
from firebase_admin import firestore

from flathunter.config import Config

class GoogleCloudIdMaintainer:
    __log__ = logging.getLogger(__name__)

    def __init__(self):
        project_id = Config().get('google_cloud_project_id')
        if project_id is None:
            raise Exception("Need to project a google_cloud_project_id in config.yaml")
        firebase_admin.initialize_app(credentials.ApplicationDefault(), {
          'projectId': project_id
        })
        self.db = firestore.client()

    def add(self, expose_id):
        self.__log__.debug('add(' + str(expose_id) + ')')
        self.db.collection(u'exposes').document(str(expose_id)).set({ u'id': expose_id })

    def get(self):
        res = []
        for doc in self.db.collection(u'exposes').stream():
            res.append(doc.to_dict()[u'id'])

        self.__log__.info('already processed: ' + str(len(res)))
        self.__log__.debug(str(res))
        return res

    def get_last_run_time(self):
        for doc in self.db.collection(u'executions').order_by(u'timestamp', direction=firestore.Query.DESCENDING).limit(1).stream():
            return doc.to_dict()[u'timestamp']

    def update_last_run_time(self):
        time = datetime.datetime.now()
        self.db.collection(u'executions').add({ u'timestamp': time })
        return time
