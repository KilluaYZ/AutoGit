import requests 
import json 
from datetime import datetime  
import os 
import sys

class Github:
    def __init__(self, username, token, repo):
        self.username = username
        self.token = token 
        self.repo = repo 
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def perform_get_request(self, url = "", params = {}, headers = None):
        if headers is None :
            headers = self.headers
        response = requests.get(url=url, headers=headers, params=params)
        res = None 
        try:
            res = response.json()
        except Exception as e:
            print(f"[ERROR] GET failed {e}")
        return res
    
    def get_repos_by_page(self, page: int):
        url = f"https://api.github.com/users/{self.username}/repos"
        repos = self.perform_get_request(
            url=url, 
            params={"page": page})
        if repos is None:
            repos = []
        return repos 

    def get_repos(self) -> list:
        page = 1
        repos = []
        while True:
            tmp_repo = self.get_repos_by_page(page)
            if len(tmp_repo) == 0:
                break 
            repos += tmp_repo
            page += 1
        filted_repos = []
        for repo in repos:
            if repo['fork'] != True:
                filted_repos.append(repo)
        return filted_repos
    
    def check_today_commits(self, repo_name: str):
        url = f"https://api.github.com/repos/{self.username}/{repo_name}/commits"
        today = datetime.now().strftime('%Y-%m-%d')
        params = {
            'since': f'{today}T00:00:00Z',
            'until': f'{today}T23:59:59Z',
            'author': self.username
        }
        resp = self.perform_get_request(
            url=url,
            params=params
        )
        return len(resp) > 0

    def get_today_committed_repos(self) -> list:
        repos = self.get_repos()
        res = []
        for repo in repos:
            repo_name = repo['name']
            if(self.check_today_commits(repo_name)):
                res.append(repo_name)
        return res 

def main():
    username = os.environ.get('AUTOGIT_USERNAME')
    token = os.environ.get('AUTOGIT_TOKEN')
    repo = os.environ.get('AUTOGIT_REPO')
    if username is None:
        print("[Error] environment variable username unsetted")
        sys.exit()
    if token is None:
        print("[Error] environment variable token unsetted")
        sys.exit()
    if repo is None:
        print("[Error] environment variable repo unsetted")
        sys.exit()
    
    github = Github(
        username=username,
        token=token,
        repo=repo
        )
    print("今天commit的仓库有：")
    print(github.get_today_committed_repos())
    
if __name__ == "__main__":
    main()
        