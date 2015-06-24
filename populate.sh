set -e -x 

echo "For a new machine, run asv on all  the commits that have been benchmarked on other machines"

git checkout master
git pull origin master
asv run -k EXISTING --machine vsp-fah-nvidia
git add -u results
git add results
git commit -m "New results" -a || true
git pull origin master
git merge origin master --no-edit
git commit -m "New results" -a || true
git push origin master
asv publish
asv gh-pages
