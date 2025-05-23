1. **GitBash가 설치되어 있다는 가정하에 설명입니다.**
2. **해당 설명은 CLI로 작업하는 방법입니다.**

<br>

## Git Clone : 처음 프로젝트 파일을 받을때 최초 1회만

1. Copy url to clipboard를 클릭합니다.
![](https://i.imgur.com/qiwRK1p.png)

<br>
2. Terminal(Git Bash)를 실행시켜 원하는 경로로 이동합니다.
![](https://i.imgur.com/Ovhcr6v.png)


<br>

3. git clone <저장소 주소>를 입력하면 해당 경로에 git 폴더(DongHwa)가 생성됩니다.
![](https://i.imgur.com/GFwb0cC.png)

<br>

## Branch 사용하기 : 매번 새 작업시마다 
- 작업을 할 때 각자의 작업을 식별하고, 작업의 충돌을 방지하기 위해 branch를 사용합니다.

<br>

**프로젝트 작업은 생성된 DongHwa 폴더에서 진행합니다**
![](https://i.imgur.com/1F5qXe0.png)
1. **git checkout -b 브랜치명** : 새 작업 시작시 git bash에서 브랜치를 생성합니다.
* 브랜치명은 팀에서 정한 git rule에 따르지만, 예시에서는 편하게 각자의 이름으로 합니다.
``` bash
# 예시
git checkout -b choi
# choi라는 브랜치를 생성하고 해당 브랜치로 이동했습니다.
```
![](https://i.imgur.com/BABU2OA.png)

<br>

예시로, DongHwa 폴더에 준혁 폴더를 만들고 그 안에 test.py라는 작업물을 완성해 넣었습니다.
![](https://i.imgur.com/Qi9wKdk.png)


<br>

2. **git add** : 작업한 내용을 branch의 stage에 추가합니다.
```shell
git add . # 브랜치에 변경된 작업 전부를 추가합니다.
```

- 작업물이 추가된 후에는 git status를 통해 어떤 부분이 변경되고 추가 되었는지 확인해보는게 좋습니다.
```bash
git status
```

branch 'choi'에서, 새 파일 test.py가 추가된것을 확인했습니다.
![](https://i.imgur.com/vKxL6bq.png)
<br>

3. **git commit -m "커밋내용"** : stage에 추가된 작업물을 commit합니다.
``` bash
# 예시
# 커밋내용은 작업한 내용을 자유롭게 쓰면 됩니다. 
git commit -m "choi/test.py 작업 완료"
```
커밋이 완료되었습니다.
![](https://i.imgur.com/rswz6Mn.png)
<br>

4. **git push origin <브랜치명>** : 브랜치에 commit 된 작업을 push합니다.
* 푸시는 꼭 자기 브랜치에!
* **main에 바로 푸시하면 안됩니다.**
```bash
# 예시
git push origin choi 
```
성공적으로 업로드 되었습니다. 하지만 여기서 끝이 아닙니다!
![](https://i.imgur.com/Jy7xDVW.png)


<br>


## Pull Request(PR) : Branch에서 작업한 것을 Main에 통합하는 과정

1. DongHwa로 가면 Compare & Pull request가 뜬걸 볼수있습니다. 클릭해줍시다.
![](https://i.imgur.com/kEYgV0b.png)

<br>

2. 충돌이 없다면 Able to merge가 떠있는것을 확인할 수 있습니다. 문제가 없다면 Create pull request를 누릅니다.
* compare가 자신의 브랜치가 맞는지
* base가 main이 맞는지 확인해주세요
* description은 필수는 아니지만 작업을 하며 바뀐것에 대해 설명을 해주시는것이 좋습니다.
![](https://i.imgur.com/yEBkIGO.png)


<br>

3. Merge pull request로 Main과 병합합니다.
* 이 과정에서 Merge pull request를 누르는건 보통 팀장이 코드를 검토 후에 시행합니다.
* 일단 눌러줍시다

![](https://i.imgur.com/aXiEfSA.png)

<br>

4. 다음 작업의 혼선을 방지하기 위해 작업이 완료된 원격 브랜치를 삭제합니다.
![](https://i.imgur.com/3Kj9obd.png)

<br>


## 원격 저장소의 변동 내역을 로컬 저장소(내 컴퓨터)와 연동하기
* 작업 후 원격 저장소(github 저장소)에 변경된 내역들을 로컬 저장소(내 컴퓨터)에도 반영해야합니다.
* 이 과정에서 여러 사람들과의 협업에도 작업들을 손쉽게 가져올 수 있는 git의 장점이 드러납니다.


1. **git checkout main** : 브랜치에서 메인으로 돌아갑니다.
![](https://i.imgur.com/MIpeiNr.png)


<br>

2. **git pull origin main** : 원격 저장소의 main에서 변경된 사항을 로컬 저장소에 반영합니다.
* 이제 원격 저장소와 내 로컬 저장소의 모든 사항이 동기화 됐습니다.
![](https://i.imgur.com/qXWqkWR.png)

<br>

3. **git branch -d <브랜치명>**
* 원격과 로컬 모든 사항이 동기화 됐으니, 혼선을 방지하기 위해 사용한 로컬의 브랜치 또한 삭제합니다.
* 여기까지가 Github에서 작업 생성, 업로드, 동기화의 모든 과정입니다.
* 다시 **새 작업을 시작할때 git checkout -b 브랜치명으로 브랜치를 생성하고 같은 과정을 반복합니다.**
``` bash
# 예시
# -d는 삭제 입니다. 
git branch -d choi
```
![](https://i.imgur.com/P4JyxaP.png)

