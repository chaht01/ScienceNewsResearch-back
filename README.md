> How to deploy?
You just commit and push your code to `deploy` branch.
But be careful not to commit and merge your database and setting file (db.sqlite3, cq_backend/settings.py)
If you don't know how to do that precisely, just do like below

In case in your own branch,
```
    git add .
    git reset HEAD db.sqlite3
    git reset HEAD cq_backend/settings.py
    git commit -m "your commit message"
    
    git checkout deploy
    git merge <your branch name> --no-ff
    git push origin deploy

```

After that, login to server using 
```
    ssh -i <your/pem file path/name.pem> ubuntu@ec2-13-209-74-251.ap-northeast-2.compute.amazonaws.com
    cd /srv/ScienceNewsResearch-back
```
command on your terminal. You can download name.pem if you are authorized user of above server. 
And then, just pull remote origin/deploy source by 
```
    git pull
```

> What if I change my model or make some migrations?
If you change your model and migrate correctly, there must be some new files in `cq/migrations`. 
It means that after you pull source code from remote, you also should apply migrations to server's database.
So after pull source with above command, 
```
    source /srv/ScienceNewsResearch-back/v2env/bin/activate
    cd /srv/ScienceNewsResearch-back/
    python manage.py migrate
```
