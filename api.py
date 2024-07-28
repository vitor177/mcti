import environ
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File
import datetime


USERNAME = "joaomendonca@isi-er.com.br"
PASSWORD = "Yikisme24%"
SHAREPOINT_SITE = "https://senairn.sharepoint.com/sites/isi-er"
SHAREPOINT_SITE_NAME = env('sharepoint_site_name')
SHAREPOINT_DOC = env('sharepoint_doc_library')

class SharePoint:
    def _auth(self):
        conn = ClientContext(SHAREPOINT_SITE).with_credentials(
            UserCredential(
                USERNAME,
                PASSWORD
            )
        )
        return conn

    def _get_files_list(self, folder_name):
        conn = self._auth()
        target_folder_url = f'{SHAREPOINT_DOC}/{folder_name}'
        root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
        root_folder.expand(["Files", "Folders"]).get().execute_query()
        return root_folder.files