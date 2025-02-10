import requests 
from datetime import datetime  
import os 
import sys
import subprocess
import random
import string

def generate_random_text(length):
    # 定义字符集：包括大小写字母和数字
    characters = string.ascii_letters + string.digits
    # 使用 random.choices() 从字符集中随机选择字符
    random_text = ''.join(random.choices(characters, k=length))
    return random_text

class Github:
    def __init__(self, username, token, repo_path):
        self.username = username
        self.token = token 
        self.repo_path = repo_path
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.file_path = f"{repo_path}/autogit.txt"
    
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
            params={"page": page, "type": "private"})
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
        today = datetime.utcnow().strftime('%Y-%m-%d')
        print(f"==> UTC日期: {today}")
        params = {
            'since': f'{today}T00:00:00Z',
            'until': f'{today}T23:59:59Z',
        }
        resp = self.perform_get_request(
            url=url,
            params=params
        )
        has_commit = len(resp) > 0
        print(f'==> 今日是否有Commit: {has_commit}')
        return has_commit

    def get_today_committed_repos(self) -> list:
        repos = self.get_repos()
        res = []
        for repo in repos:
            repo_name = repo['name']
            print(f"=> 正在检查: {repo_name}")
            # if(self.check_today_commits(repo_name)):
            #     res.append(repo_name)
        return res 

    def run_git_cmd(self, cmd: str):
        # splited_cmd = cmd.split()
        cmd = f"cd {self.repo_path} && {cmd}"
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
    
    def git_add(self):
        self.run_git_cmd('git add .')
        
    def git_commit(self):
        self.run_git_cmd('git commit -m "auto git"')
    
    def git_push(self):
        self.run_git_cmd('git push')
    
    def update_file(self):
        with open(self.file_path, "a") as f:
            f.write(generate_random_text(20))        

    def auto_commit(self):
        self.update_file()
        self.git_add()
        self.git_commit()
        self.git_push()
    
def main():
    username = os.environ.get('AUTOGIT_USERNAME')
    token = os.environ.get('AUTOGIT_TOKEN')
    repo_path = os.environ.get('AUTOGIT_REPO_PATH')
    
    if username is None:
        print("[Error] environment variable AUTOGIT_USERNAME unsetted")
        sys.exit()
    if token is None:
        print("[Error] environment variable AUTOGIT_TOKEN unsetted")
        sys.exit()
    if repo_path is None:
        print("[Error] environment variable AUTOGIT_REPO_PATH unsetted")
        sys.exit()
    
    github = Github(
        username=username,
        token=token,
        repo_path=repo_path)
    commited_repos = github.get_today_committed_repos()
    # print(f"今天commit的仓库有: {commited_repos}")
    if len(commited_repos) == 0:
        print("今日没有commit, 正在自动commit...")
        # github.auto_commit()
    else:
        print(f"今日{commited_repos}仓库已经有commit, 程序退出...")
    
if __name__ == "__main__":
    main()
        