import requests, logging
from settings import GITLAB_PRIVATE_TOKEN, TRELLO_KEY, TRELLO_TOKEN, TRELLO_LIST_ID


class Issue:
    def __init__(self, project, title, description):
        self.__project = project
        self.__title = title
        self.__description = description

    def create_issue(self):
        try:
            logging.info(f'Creating issue {self.__title} at project {self.__project["name"]}')
            r = requests.post(f'https://git.pti.org.br/api/v4/projects/{self.__project["id"]}/issues',
                              headers={
                                  'Content-type': 'application/json',
                                  'Private-token': GITLAB_PRIVATE_TOKEN
                              },
                              params={
                                  'title': self.__title,
                                  'description': self.__description
                              })
            logging.info(f'Criação da issue retornou o código: {r.status_code}')
            r.raise_for_status()
            return True
        except:
            return False

    def create_card(self):
        try:
            logging.info(f'Creating card {self.__title} at backlog list')
            r = requests.post(f'https://api.trello.com/1/cards',
                              params={
                                  'idList': TRELLO_LIST_ID,
                                  'keepFromSource': 'all',
                                  'key': TRELLO_KEY,
                                  'token': TRELLO_TOKEN,
                                  'name': self.__title,
                                  'desc': self.__description,
                                  'pos': 'top'
                              })
            logging.info(f'Criação do card retornou o código: {r.status_code}')
            r.raise_for_status()
            return True
        except:
            return False
