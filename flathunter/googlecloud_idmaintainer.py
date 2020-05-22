import logging
import firebase_admin
import traceback
from firebase_admin import credentials
from firebase_admin import firestore

from flathunter.config import Config

class ConnectionWrapper:

    def __init__(self, db):
        self.db = db

    def __enter__(self):
        # Return a new client for this thread
        return firestore.client()

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False
        return True

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

    def connect(self):
        return ConnectionWrapper(self.db)

    def add(self, expose_id, connection=None):
        self.__log__.debug('add(' + str(expose_id) + ')')
        self.db.collection(u'exposes').document(str(expose_id)).set({ u'id': expose_id })

    def get(self, connection=None):
        res = []
        for doc in self.db.collection(u'exposes').stream():
            res.append(doc.to_dict()[u'id'])

        self.__log__.info('already processed: ' + str(len(res)))
        self.__log__.debug(str(res))
        return res
