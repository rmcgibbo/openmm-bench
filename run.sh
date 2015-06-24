git checkout master
git pull origin master
asv run -k NEW
git add -u results
git add results
git commit -m "New results" -a || true
git push origin master
asv publish
asv gh-pages
