set -e -x

echo "For a new machine, run asv on all  the commits that have been benchmarked on other machines"

git checkout master
git pull origin master
asv run -k EXISTING
git add -u results
git add results
git commit -m "New results" -a || true
git push origin master
asv publish
asv gh-pages
